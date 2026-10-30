# Lokale Testcheckliste – Gerätetests

[Deutsch](LOCAL_TEST_CHECKLIST.de.md) | [English](LOCAL_TEST_CHECKLIST.md)

**Dieses Projekt enthält lesende Geräteerkennung, aber noch keinen Sendeadapter und kein Dashboard.**
Die folgenden Tests erst durchführen, wenn die jeweilige Funktion implementiert
und eine manuell installierbare Beta verfügbar ist. Reale Tests erfolgen
ausschließlich im eigenen Home Assistant; Cloud Codex und GitHub Actions
erhalten keinen Zugriff auf Heimnetz oder echte VeSync-Geräte.

Für v0.1.0b3 gilt ausschließlich der separate [beaufsichtigte Ersttest](reports/ISSUE_7_BETA_SEND.de.md#lokale-gerateabnahme). Die allgemeinen Live-/Dashboard-Prüfungen unten bleiben bis zu ihrer Implementierung ausstehend.

## Vor jedem realen Gerätetest

- [ ] Home-Assistant-, HACS- und Adapter-Versionen notieren.
- [ ] Backup und funktionierende Airfryer-Control-Integration überprüfen.
- [ ] Gerät leer, frei und unter Aufsicht betreiben.
- [ ] Testmodus prüfen: **kein echter Gerätebefehl**.
- [ ] Live-Modus erfordert ausdrücklich „Senden“.
- [ ] Aktuellen Zustand jedes Fachs prüfen; veraltete Daten sind kein Nachweis für Bereitschaft.
- [ ] Manuellen Start am Gerät und keine unerwartete Heizungsaktivierung bestätigen.

## Unabhängige Fächer prüfen

- [ ] Im Admin-Panel gemeldetes Gerät/Fach wählen; Testvorschau zeigt ausdrücklich, dass nichts übertragen wurde.
- [ ] Mit Airfryer Control `1.0.2-beta.1` oder neuer prüfen, dass das Programm-Dropdown `faehigkeiten` entspricht; geschätzte/ungeprüfte Einträge sind sichtbar gekennzeichnet und ein nicht gemeldetes Programm aus einem gespeicherten Rezept wird nicht still ersetzt.
- [ ] Gespeichertes Rezept und manuelle Werte getrennt in der Testvorschau prüfen; Wunschwerte bleiben unverändert.
- [ ] Geräteabfrage ohne/mit fehlerhaftem Airfryer Control beeinträchtigt die Rezeptverwaltung nicht.
- [ ] Testvorschau auf Deutsch und Englisch sowie mit °C/°F-Benutzereinstellung prüfen.
- [ ] Testmodus an Fach 1: keine echte Übertragung.
- [ ] Testmodus an Fach 2: keine echte Übertragung.
- [ ] Unterstützte Werte an das ruhende Fach 1 senden und am Gerät prüfen.
- [ ] Unterstützte Werte an das ruhende Fach 2 senden und am Gerät prüfen.
- [ ] Das jeweils andere Fach darf nicht unbeabsichtigt verändert werden.
- [ ] Programm, Solltemperatur und Zeit einzeln prüfen, sofern unterstützt.
- [ ] Während des Garens muss die Standardsperre greifen.
- [ ] Nach Admin-Freigabe: Bestätigung und Geräteunterstützung vor Änderung prüfen.
- [ ] Es darf kein automatischer Heizstart erfolgen.
- [ ] Offline-/Unbekannt-Zustand: Senden gesperrt und Bild ausgegraut.
- [ ] Verbindung unterbrechen/wiederherstellen: keine automatischen Wiederholungen.
- [ ] Airfryer-Control-Integration deaktivieren: Rezeptverwaltung funktioniert weiter.

## Daten und Übersetzung

- [ ] Ohne Airfryer Control die Admin-Seitenleiste „Airfryer Recipes“ auf dem Handy öffnen; keine horizontale Überläufe.
- [ ] Rezept anlegen, bearbeiten, kopieren und nach Bestätigung löschen; nach HA-Neustart bleiben gespeicherte Rezepte erhalten.
- [ ] Im Rezepteditor vorhandene Kategorie wählen; „Neue Kategorie hinzufügen“ steht zuletzt und übernimmt bei abweichender Groß-/Kleinschreibung den vorhandenen Namen.
- [ ] Gemeinsame und persönliche Favoriten getrennt prüfen; persönliche Favoriten eines zweiten Benutzers bleiben unabhängig.
- [ ] JSON-Importvorschau mit gleichen Namen/IDs prüfen und erst nach bewusster Auswahl übernehmen; Export mit dem Dateinamen `Airfryer-Rezepte-Home-Assistant.json` prüfen.
- [ ] Mit normalem Benutzer: Admin-Panel nicht öffnen und Schreib-WebSocket-Befehle nicht ausführen können.
- [ ] Erstellen, Bearbeiten, Löschen, Duplizieren, Exportieren und Importieren in beiden Sprachen.
- [ ] Ungültiges JSON und zukünftige Schemanummer importieren: Daten unverändert.
- [ ] Migration inklusive Sicherung und Rückfall anhand einer Testkopie prüfen.
- [ ] Normale Benutzer dürfen Rezepte/Sicherheitseinstellungen nicht ändern.
- [ ] Darstellung °C/°F, gerätespezifische Grenzwerte und Warnungen prüfen.
- [ ] Diagnosevorschau auf Geheimnisse prüfen, bevor etwas geteilt wird.
- [ ] Deutsche und englische Berichte und Release Notes inhaltlich abgleichen.

## Später: SYNC / MATCH (nicht Bestandteil des MVP)

- [ ] Exakte Home-Assistant-Aktionen und erforderliche Reihenfolge prüfen.
- [ ] Beide Fächer mit unterschiedlichen Zeiten konfigurieren.
- [ ] SYNC nur bei gültigem, unterstütztem Gerätezustand ausführen.
- [ ] Geräteanzeige und manuellen Start prüfen.
- [ ] MATCH getrennt testen und identische Facheinstellungen prüfen.
- [ ] Bei nicht unterstütztem Modell beide Schaltflächen ausblenden/sperren.

Jeden Test als **BESTANDEN / FEHLGESCHLAGEN / NICHT GETESTET** mit
nachvollziehbaren Beobachtungen dokumentieren.
