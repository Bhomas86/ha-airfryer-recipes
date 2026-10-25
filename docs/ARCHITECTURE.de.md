# Architektur – Airfryer Recipes

[Deutsch](ARCHITECTURE.de.md) | [English](ARCHITECTURE.md)

**Architekturentscheidung ADR-001 / Anforderung 31: Modulare Home-Assistant-Integration.** Beschlossen am 24.10.2026. Dieses Dokument beschreibt die Zielarchitektur. Rezeptspeicher, WebSocket-API und Admin-Verwaltung sind über PR #16 gemergt. Lesende Geräteerkennung, eine adminpflichtige serverseitige Testvorschau und ihre Ansicht im Admin-Panel sind als Teile von Issue #7 implementiert; Gerätesteuerung, Dashboard und Diagnose bleiben geplant. Siehe [Prüfung des Upstream-Vertrags](reports/ISSUE_7_DISCOVERY.de.md).

## Ziel und Bereitstellung

Wir entwickeln **eine über HACS installierbare Integration** mit gemeinsamem Python-Backend und zwei enthaltenen JavaScript-Oberflächen: einer Rezeptverwaltung für Administratoren und einer Lovelace-Dashboard-Karte mit visuellem Editor. Weder zusätzliche Container noch Server, Datenbanken, Proxys oder eingehende Portfreigaben sind nötig. Als erste Geräteanbindung verwenden wir die **bestehende Airfryer-Control-Integration**. Die Rezeptverwaltung muss ohne sie funktionieren.

Die Integrationsdomain lautet `airfryer_recipes`. Home Assistant OS auf Proxmox ist eine Zielumgebung, die Lösung muss aber plattformunabhängig bleiben.

## Komponenten und Zuständigkeiten

| Baustein | Aufgabe | Darf nicht |
| --- | --- | --- |
| `recipe_model.py` und Validierung | Geräteunabhängige Rezeptdaten, MVP mit einer Garphase, später mehrphasig erweiterbar, JSON-Schema | Netzwerk verwenden oder Geräte steuern |
| Speicherung/Repository | Asynchroner Home-Assistant-`Store`, Schema-Versionen, Sicherungen, Migrationen, CRUD, Import-Vorschau und Duplikate | Airfryer Control voraussetzen |
| Authentifizierte WebSocket-API | Typisierte Lese-/Schreibbefehle, Admin-Berechtigungen, zulässige normale Bedienung, Fehlerantworten | Der Rechteprüfung im Browser vertrauen |
| Rezeptverwaltungsseite | Suche, Kategorien/Tags, Favoriten, CRUD, Import/Export, Beispiele und Gerätebilder verwalten | Ohne Backend-Prüfung Gerätebefehle senden |
| Lovelace-Karte und Editor | Responsive Gerätegrafik mit anklickbaren Fächern, Rezept/Manuell, Status/Offline, Testmodus und bewusstes Senden | Die Sicherheitslogik durch Direktaufrufe umgehen |
| Geräteerkennung/Fähigkeiten | HA-Geräte, Zonen, Status und Fähigkeiten ermitteln; bestätigte Modellprofile als Fallback | Alle Upstream-Aktionen für jedes Gerät annehmen |
| Adaptervertrag + Airfryer-Control-Adapter | Geräte/Fächer/Programme/Grenzen/Status vereinheitlichen; geprüfte Befehle an vorhandene HA-Aktionen abbilden | Zugangsdaten selbst verwalten oder Garvorgang starten |
| Befehlskoordinator | Status erneut prüfen, Berechtigungen/Sicherheit/Werte validieren, Anpassungen bestätigen lassen, im Testmodus nicht senden und Ergebnisse zurückmelden | Offline-Aufträge sammeln, automatisch wiederholen oder Heizung starten |
| Diagnose | Erlaubte technische Daten exportieren, Fehlerdatenschutz und Nutzerhinweis | Passwörter, Tokens, Cookies, IPs oder Benutzer-/Gerätekennungen exportieren |

## Schnittstelle zwischen Frontend und Backend

Für Rezeptlisten, Änderungen, Gerätefähigkeiten, Status, Testmodus-Vorschauen und Sendebefehle verwenden wir **authentifizierte Home-Assistant-WebSocket-Befehle** unter `airfryer_recipes/*`. Die folgenden Namen beschreiben das Zielprotokoll. Rezeptoperationen, adminpflichtiges `devices` und `prepare_send` als Testvorschau sind implementiert. `device_state`, `confirm_send`, Gerätepräferenzen und Diagnose bleiben geplant:

- `airfryer_recipes/list`, `get`, `create`, `update`, `duplicate`, `delete`
- `airfryer_recipes/import_preview`, `import_confirm`, `export`
- `airfryer_recipes/devices`, `device_state`, `prepare_send`, `confirm_send`
- `airfryer_recipes/preferences`, `update_preferences`, `diagnostics`

Nur Administratoren dürfen Rezepte bearbeiten/löschen/importieren, globale Vorgaben und Sicherheitsregeln ändern sowie Gerätebilder und Positionen verändern. Normale HA-Benutzer dürfen Rezepte lesen und **erlaubte** Steuerbefehle senden. Das Backend prüft den tatsächlich angemeldeten HA-Benutzer; eine Admin-Angabe aus dem Browser ist nicht vertrauenswürdig.

**Zweistufiger Versand:** Bei kompatiblen Einstellungen und einem sicher bereiten Fach kann die explizite Senden-Aktion nach Validierung direkt erfolgen. Erfordert ein Rezept abweichende Werte oder ist eine freigegebene Änderung während des Garens geplant, erzeugt das Backend eine kurz gültige Bestätigung, die Benutzer, Gerät, Fach, genaue Werte und Statusversion bindet. Erst nach erneuter Prüfung und ausdrücklicher Bestätigung wird gesendet. Ein Bestätigungstoken darf niemals selbst das Heizen starten.

## Speicherung und Datenmigration

Die Rezeptbibliothek liegt über Home Assistants asynchronem `Store` in integrationsspezifischen lokalen Speicherdaten, **nicht im Quellcodeverzeichnis**. Das Schema ist versioniert. Vor einer Migration werden die Originaldaten sicherungsfähig erhalten; unbekannte neuere Versionen werden nicht überschrieben. Geräteunabhängige Rezepte, die letzten manuellen Werte je Gerät/Fach und persönliche Favoriten sind getrennte Datenbereiche. Intern verwenden wir Celsius, die Oberfläche zeigt die in HA gewählte Einheit. JSON-Import/Export wird versioniert und validiert; Duplikatkonflikte werden vor jeder tatsächlichen Änderung angezeigt. Der Export verwendet einen kurz gültigen, an die authentifizierte HA-Sitzung gebundenen Downloadpfad; der HTTP-Endpunkt prüft die Adminrolle erneut und liefert einen verständlichen Dateinamen ohne Cache-Freigabe.

**Der Lebenszyklus von Rezeptdaten und Geräteadapter bleibt getrennt.** Wenn Airfryer Control nicht verfügbar ist, funktionieren Einrichtung, Bearbeitung und JSON-Import/Export weiter.

## Geräteadapter und sichere Steuerung

Der Adapter liefert Geräte-ID, Modell, Fach-IDs, Programme/Grenzen, Verbindungsstatus, Betriebszustand, Aktualität der Statusmeldung und Funktionskennzeichen (`sync_finish`, `match_zones`, zulässige Änderungen). Airfryer Control `1.0.2-beta.1` wird ausschließlich über den öffentlichen lesenden Dienst `faehigkeiten` verwendet; dessen Antwort wird vor der Oberfläche auf erlaubte Felder begrenzt und vereinheitlicht. Tatsächlich gemeldete Fächer stammen weiterhin aus dem aktuellen Laufzeitzustand, weil eine Fähigkeitsliste keine aktuelle Fachmeldung ist. „Unbekannt“ und „veraltet“ sind nicht gleich „offline“ und **sperren reale Sendeaktionen**. Offline-Geräte werden ausgegraut und das Senden deaktiviert. Bestätigte Modellprofile dürfen fehlende beschreibende Informationen ergänzen, aber keine riskanten Befehle ungeprüft aktivieren.

Jeder echte Gerätebefehl läuft über den Befehlskoordinator. Während des Garens sind Änderungen standardmäßig gesperrt; ein Administrator kann die Bestätigung erlauben, sofern der Adapter und das Gerät dies unterstützen. Nie unbeabsichtigt aus der Ferne heizen, manuelle Startpflicht respektieren. Keine Warteschlange nach Verbindungsrückkehr und keine automatische Wiederholung. Im serverseitigen Testmodus erfolgen **null reale Gerätesteuerungsaufrufe**. Rückmeldungen unterscheiden „vom Adapter angenommen“ und „vom Gerät bestätigt“, wenn Letzteres nicht prüfbar ist.

Erstes reales Testgerät ist die **Cosori Turbo Tower Pro Smart CAF-DC111S-AEU**. Über Airfryer Control wurden Temperatur und Zeit bereits erfolgreich an das untere Fach 2 übertragen. **SYNC und MATCH sind vorhandene Upstream-Aktionen**, müssen vor einer UI-Freigabe aber auf exakte Parameter, Reihenfolge und Geräteverhalten getestet werden (Issue #1).

## Oberfläche und Bilddateien

Zwei JavaScript-Einstiegspunkte dürfen gemeinsame TypeScript-/Lit-Komponenten nutzen, werden aber als lokal gebündelte, versionierte Dateien mit der Integration ausgeliefert. Keine CDN-Abhängigkeit zur Laufzeit. Die Registrierung nutzt unterstützte Home-Assistant-Mechanismen und vermeidet synchrone Dateizugriffe im Event-Loop. Mitgelieferte Gerätebilder sind eigene bzw. korrekt lizenzierte Illustrationen. Eigene Uploads werden lokal mit Größen-/Formatkontrolle und authentifiziertem Zugriff gespeichert. Die antippbaren Fachpositionen verwenden relative Koordinaten. Für unbekannte Modelle gibt es eine neutrale Grafik und den GitHub-Link „Modell fehlt?“.

**Englisch (`en`) bleibt UI-Standardsprache/Fallback**, Deutsch (`de`) wird vollständig unterstützt. Projektberichte, Issues, PRs, Dokumente und Release Notes sind **vollständig zweisprachig und bei Berichten Deutsch zuerst**, mit jeweils `*.md` und `*.de.md`.

## Qualität und Reihenfolge

1. Grundlagen-PR #2 prüfen und zusammenführen.
2. Manifest, HACS-Grundstruktur, Einrichtungsdialog und Start ohne Airfryer Control.
3. Dauerhafter Rezeptspeicher, Migrationen, CRUD und Import/Export.
4. WebSocket-API mit geprüften Admin-/Benutzerrechten.
5. Grafische Rezeptverwaltung und Übersetzungen.
6. Geräteadapter, Befehlskoordinator und simulierte Sicherheitstests.
7. Grafisches Lovelace-Dashboard, Gerätebilder und responsiver Editor.
8. Lokale Cosori-Tests; optional Fertigmeldungen, Diagnose und Beta. SYNC/MATCH anschließend.

Jede Phase bekommt abgegrenzte Issues/PRs, Offline-Tests und eine zweisprachige Prüfung. HACS-Tauglichkeit wird erst nach erfolgreicher Installation und Einrichtung in Home Assistant behauptet.

## Entwicklerreferenzen

- [Home-Assistant-Integration](https://developers.home-assistant.io/docs/creating_component_index/)
- [Eigene Panels](https://developers.home-assistant.io/docs/frontend/custom-ui/creating-custom-panels/)
- [WebSocket-Erweiterungen](https://developers.home-assistant.io/docs/frontend/extending/websocket-api)
- [Übersetzungen](https://developers.home-assistant.io/docs/internationalization/core/)
- [Airfryer Control](https://github.com/misterm2310/airfryer-control)
