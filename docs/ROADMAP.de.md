# Entwicklungsplan – Airfryer Recipes

[Deutsch](ROADMAP.de.md) | [English](ROADMAP.md)

**b20 (04.11.2026):** Eigentümer wünscht beide Gerätebild-Entwürfe als Karteneinstellung. A nutzt eine dünne aktive Kontur und kleine Markierungen; B nutzt unsichtbare, antippbare eingerichtete Bildbereiche mit sichtbarer Fachauswahl neben dem Foto. Bildeditor-Rechtecke bleiben zum Positionieren sichtbar. Umgesetzt; native Abnahme offen. [Einstellungen und Prüfungen](releases/0.1.0b20.de.md).

**b19 (03.11.2026):** Eigentümer bestätigt b18-Bildspeicherung nach Seitenneuladen. Nach erfolgreichem Speichern Karten derselben Seite aktualisieren, beim Wiedereinblenden nachladen und Speichern sichtbar bestätigen; Geräteberechtigungen und Garentwürfe erhalten. Neue native Aktualisierungsabnahme offen. [Korrektur und lokale Prüfungen](releases/0.1.0b19.de.md).

**b18 (03.11.2026):** b17-Karteneditor lokal bestätigt. Private Gerätebild-Galerie/Uploads und relative Fachbereiche pro Gerät mit Admin-Schreibrechten umgesetzt; native neue Abnahme offen. [Einrichtung und Grenzen](releases/0.1.0b18.de.md).

**b17 (03.11.2026):** Drei lokale b16-Freigabeprüfungen bestanden. Karteneditor um Darstellungsgrößen, unabhängige Grafikgröße und Status-/Historienanzeige ergänzt; Standardeinstellungen und Backend-Prüfungen unverändert. [Umsetzung und Prüfung](releases/0.1.0b17.de.md).

**b16-Ganzgerätefreigabe (02.11.2026):** Nach Card-/Historien-/Neustart-Grundabnahme adminverwaltete Benutzer-/Gerätefreigaben umsetzen, gemäß Eigentümerkorrektur: Alle Fächer und verfügbaren Programme gehören zur Gerätefreigabe. Begrenzte Erkennung/Historie/Testvorschau/beaufsichtigtes Senden und Entzugsprüfungen ergänzen; Rezept-/Sicherheitsverwaltung und Testfolgen bleiben adminpflichtig. 203 Python-/93 Frontend-Tests lokal bestanden; neue native Zwei-Konten-Abnahme offen. [Umsetzung und Ablauf](reports/ISSUE_8_DEVICE_ACCESS.de.md). Keine GitHub Actions.

**b15-Ressourcenregistrierung (02.11.2026):** Eigentümer bestätigt b14-Anzeige nach manueller Modulregistrierung. Dieselbe Dashboard-Ressource im Storage-Modus automatisch registrieren/aktualisieren, manuellen Eintrag/andere Ressourcen erhalten und YAML-Alternative beibehalten. Nur die aktuelle Beta veröffentlicht lassen; ältere als Entwürfe samt Tags/Code/Assets erhalten. 178 Python-/84 Frontend-Tests lokal bestanden; automatische native Abnahme offen. [Nachweis und Ablauf](reports/ISSUE_8_CARD_RESOURCES.de.md). Keine GitHub Actions.

**Card-Ladekorrektur 0.1.0b14 (02.11.2026):** Doppelte Registrierung bei bereits vorhandener Rezeptansicht reproduziert; Elementdefinition schützen und aktuelle Basisklasse direkt importieren. Vier vollständige ES-Modulladetests ergänzt; 170 Python-/84 Frontend-Tests lokal bestanden. Eigentümer bestätigt installierte b13; native Sichtbarkeit unter b14 noch offen. [Nachweis und Alternative](reports/ISSUE_8_CARD_LOADING.de.md). Keine GitHub Actions.

**Dashboard-Beta 0.1.0b13 (2026-11-02):** Freigegebenen neutralen Entwurf 1A mit getrennt dauerhaft gespeicherten zuletzt gesendeten Einstellungen je Fach, Rezept-/Manuell-Bedienung und grafischem Editor umgesetzt. Testvorschau voreingestellt; echte Übertragung verwendet die vorhandene beaufsichtigte Beta ausschließlich für Administratoren. Backend-Geräterechte für normale Benutzer, Personalisierung und native HA-/Companion-Abnahme bleiben offen. [Umsetzung und lokale Prüfung](reports/ISSUE_8_DASHBOARD_CARD.de.md). 170 Python-/80 Frontend-Tests lokal bestanden. Keine GitHub Actions.

**Rezeptabnahme 01.11.2026: R1/R2 als bestanden gemeldet.** Nach der Editor-Korrektur bestätigt der Eigentümer die gespeicherte Rezeptübertragung auf Fach 1 und 2. R3–R7 und restliche Editorvarianten bleiben separat offen. [Nachweis und nächste Prüfungen](reports/ISSUE_7_LOCAL_ACCEPTANCE.de.md). Dashboard samt Backend-Benutzerrechten bleibt das nächste Umsetzungspaket nach gezielter Abnahme. Nur Dokumentation; kein neuer Release und keine GitHub Actions.

**Lokale Abnahme 01.11.2026: Alle zwölf Schritte BESTANDEN.** Der Eigentümer bestätigt die vollständige geführte Folge mit sechs Programmen auf Fach 1 und 2 sowie das anschließend ausgeschaltete Gerät. [Exakte Werte und Nachweisgrenzen](reports/ISSUE_7_LOCAL_ACCEPTANCE.de.md). Nächster offener Gerätepunkt: modellabhängige Adaptergrenzen und Gären; anschließend gezielte Grenzwert-/Fehlerabnahme. Kein neues App-Update und keine GitHub Actions für diesen Dokumentationsnachtrag.

**Status (29.10.2026):** Alle 31 Anforderungen sind beschlossen. Rezeptspeicher, authentifizierte API und lokal abgenommene Admin-Verwaltung sind gemergt. PR #19 mit Geräte-Testvorschau und Programmauswahl ist seit 25.10.2026 gemergt; HACS-Vorabversion `0.1.0b2` wurde auf dem Handy erfolgreich abgenommen. PR #20 korrigiert die HACS-Versionsanzeige. Issue #7 bleibt für die sichere echte Übertragung offen: Beta-Vertrag und modellspezifische Fähigkeiten müssen lokal verifiziert werden. Danach folgt das Dashboard (#8). Siehe [Abnahmebericht](reports/ISSUE_7_DRY_RUN_UI.de.md) und [Architektur](ARCHITECTURE.de.md).

**Prüfung vom 30.10.2026:** Der unveränderte Beta-Vertrag reicht weiterhin nicht zur Live-Freigabe. Modellspezifische Nachweise und frische Gerätebestätigung fehlen; siehe [erneute Vertragsprüfung](reports/ISSUE_7_BETA_REVIEW.de.md).

**Nächstes Testpaket 0.1.0b3:** Separater beaufsichtigter Schnittstellentest vor der Geräteabnahme, vom Eigentümer beauftragt. Keine normale Gerätesteuerung oder Kompatibilitätsfreigabe. [Umsetzung und lokale Tests](reports/ISSUE_7_BETA_SEND.de.md).

**Beta-Korrektur 0.1.0b4:** Der erste lokale Versuch wurde vor dem Senden durch die Aktualitätssperre blockiert. Die Vorbereitung fordert jetzt einmal eine neue lesende Statusabfrage an. Echte Übertragung weiterhin nicht abgenommen. [Prüfbericht und Wiederholung](reports/ISSUE_7_STATUS_REFRESH.de.md).

**Lokale Abnahme 30.10.2026: Beide Fächer BESTANDEN** für Airfry 170 °C, eine Minute, ohne Heizstart und ohne Änderung des jeweils anderen Fachs. Nächstes Paket ist die begrenzte Rezept-/manuelle Übertragung im Admin-Panel. [Abnahme und Grenzen](reports/ISSUE_7_LOCAL_ACCEPTANCE.de.md). Weitere Updates vorerst ohne GitHub Actions.

## Prioritäten und Abhängigkeiten

| Phase | Issue | Ergebnis | Voraussetzung | Prüfung |
| --- | --- | --- | --- | --- |
| 0 · Grundlage | [PR #2](https://github.com/Bhomas86/ha-airfryer-recipes/pull/2) | Rezeptmodell, JSON, Tests, 31 zweisprachige Anforderungen, Architektur, Codex-Regeln | Freigabe durch Nutzer | Python 3.12/3.14-CI, Code Review |
| 1 · Home Assistant | [#3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3) | Installierbare Integration, Einrichtung, Übersetzung, HACS-Metadaten | PR #2 | HA startet auch ohne Geräteadapter |
| 2 · Datenspeicherung | [#4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4) | Versionierter Speicher, CRUD, Migration, JSON-Import/-Export | #3 | Neustart, Migration, ungültige Daten |
| 3 · Berechtigte API | [#5](https://github.com/Bhomas86/ha-airfryer-recipes/issues/5) | Rechtegeprüfte WebSocket-Befehle | #3, #4 | Admin/Benutzer und manipulierte Requests |
| 4 · Rezeptverwaltung | [#6](https://github.com/Bhomas86/ha-airfryer-recipes/issues/6) | Responsive Admin-Seite, Deutsch und Englisch | #4, #5 | Bearbeitung ohne Airfryer, Rechte |
| 5 · Sichere Anbindung | [#7](https://github.com/Bhomas86/ha-airfryer-recipes/issues/7) | Airfryer-Control-Adapter, verifizierte Geräteliste mit Programmfunktionen, Befehlskoordinator, Testmodus | #3, #5 | Simulierte Sicherheitstests, lokale Cosori-Checkliste |
| 6 · Dashboard | [#8](https://github.com/Bhomas86/ha-airfryer-recipes/issues/8) | Interaktive Fächer, Rezept/Manuell, gerätespezifische Programmauswahl, Rückmeldungen und Karteneditor | #4, #5, #7 | Smartphone/Tablet, beide Fächer und Programmfunktionen, Offline |
| 7 · Individualisierung | [#9](https://github.com/Bhomas86/ha-airfryer-recipes/issues/9) | Bildergalerie, sichere Uploads, verschiebbare Fachpositionen | #8 | Skalierung, Rechte und Bildvalidierung |
| 8 · Beta-Freigabe | [#10](https://github.com/Bhomas86/ha-airfryer-recipes/issues/10) | HACS-Beta, zweisprachige Release Notes, Diagnose, optionale Fertigmeldung | #3–#8, ggf. #9 | CI, echtes HA und Gerätetests |
| Später | [#1](https://github.com/Bhomas86/ha-airfryer-recipes/issues/1) | SYNC/MATCH in Dashboard unter Verwendung vorhandener Aktionen | #7, #8 | Sicherheit und echte Gerätebestätigung |

**Vorgemerkter Folgepunkt zu #6:** Eine Kategorie über alle betroffenen Rezepte hinweg umbenennen oder mit einer anderen zusammenführen, etwa „Backen“ zu „Aufbacken“. Vor der Umsetzung sind Vorschau, Rechteprüfung, sichere Speicherung und Rückfallverhalten festzulegen. Die aktuelle Auswahlliste ändert bestehende Kategorien nicht automatisch.

**Programmwahl nach #7:** Die Administrator-Testvorschau liest die Programmauswahl aus dem öffentlichen Fähigkeitsdienst von Airfryer Control und kennzeichnet bestätigte, geschätzte und nicht gemeldete Werte sichtbar. Die spätere Eingabehilfe im Rezepteditor und die Sendebedienung verwenden ausschließlich verifizierte Gerätedaten und prüfen sie erneut im Backend. Ein Rezept speichert weiterhin keine feste Gerätebindung.

## Arbeitsteilung

- **ChatGPT kann übernehmen:** Architektur, Rezeptdatenmodelle, Python-Hilfsfunktionen, Tests, Dokumentation, Reviews sowie kleinere abgegrenzte Branches und Pull Requests.
- **Codex übernimmt geeignete größere Pakete:** HA-Lifecycle, Admin-Seite, Adapter und Dashboard. Vor jedem Paket gilt die [Modellrichtlinie aus AGENTS.md](../AGENTS.de.md): **ausschließlich GPT-6.1 Sol**, mit dem Denkaufwand **niedrig, mittel oder hoch**. Niedrig für einfache Aufgaben, mittel für normale Entwicklung und hoch für komplexe Architektur oder Sicherheitsaufgaben. Diese Regel gilt ab 29.10.2026 und ersetzt ältere Modellempfehlungen in Issues und Berichten.
- **GitHub Actions:** Begrenztes Kontingent: lokal gezielt prüfen, automatische PR-Prüfungen klein und pfadabhängig halten. Vollständige Python-Matrix und umfassende HACS-/Hassfest-Abnahme am Ende größerer Abschnitte bzw. vor Releases planen. Keine Code-CI für reine Dokumentation, keine zusätzlichen automatischen Merge-Läufe. Ausschließlich Simulationen, kein Zugriff auf echte Geräte oder Zugangsdaten.
- **Nutzer / lokales Home Assistant:** Installation, Neustart und reale Tests mit der Cosori anhand der [Testcheckliste](LOCAL_TEST_CHECKLIST.de.md).
- **Pull Requests:** Eigene Branches, vollständige deutsche und englische Dokumentation, Tests und Review vor dem Merge. Keine automatische Zusammenführung.

## Erste nutzbare Entwicklungsziele

**Meilenstein A – Rezeptverwaltung ohne Airfryer** nach #3–#6: Rezepte anlegen, ändern, importieren/exportieren und dauerhaft speichern, inklusive Admin-Berechtigungen.

**Meilenstein B – Sichere Übertragung ans Gerät** nach #7–#8: Cosori-Fach antippen, Rezept oder manuelle Werte einstellen und bewusst senden, ohne Fernstart der Heizung. Verbindung und Fehler sind erkennbar.

**Meilenstein C – HACS-Beta für Tester** nach #9/#10 nach Bedarf: Individualisierung, Prüfungen, Anleitungen, optionale verlässliche Fertigmeldungen, Diagnose und Veröffentlichung.

Keine konkreten Veröffentlichungstermine, bevor Installation und Sicherheitsprüfung am realen System durchgeführt wurden.

## Freigabekriterien

- Erfolgreiche CI- und Home-Assistant-Setup-Tests
- Keine blockierenden Dateizugriffe im Event-Loop
- Kein unbeabsichtigter Heizstart, Offline-Nachholen, Auto-Retry oder echte Befehle im Testmodus
- Admin-/Benutzerrechte werden vom Backend geprüft
- Sicherungen vor Migrationen und geschützter Import mit Konfliktvorschau
- **Vollständige deutsche und englische** Oberfläche, Issues, PRs, Dokumentation, Testberichte und Release Notes; Berichte zuerst auf Deutsch
- Reale Cosori-Tests nur mit den Angaben BESTANDEN / FEHLGESCHLAGEN / NICHT GETESTET dokumentieren

Beta 0.1.0b5: Auf Eigentümerwunsch beaufsichtigte Rezept-/manuelle Übertragung aller sechs aktuell gemeldeten, im geprüften Vertrag enthaltenen Programme. Keine allgemeine Modellfreigabe. [Umsetzung und Grenzen](reports/ISSUE_7_RECIPE_SEND.de.md), [60-teilige Abnahme](reports/BETA_0_1_0B5_TEST_PLAN.de.md). Ausschließlich lokal geprüft; keine GitHub Actions.

Eigentümerentscheidung: Einmalige Bestätigung der vollständigen beaufsichtigten Testliste, danach einzeln sequenzielle Schritte mit frischer Zustandsprüfung und Abbruch. Beta 0.1.0b6 enthält maximal zwölf normale Testeinstellungen auf beiden Fächern, keine automatische Garfolge. [Umsetzung und Abnahme](reports/ISSUE_7_GUIDED_BATCH.de.md). Keine GitHub Actions.

Eigentümervorgabe: Nach beaufsichtigtem Abbruch muss ein neuer Test ohne HA-Neustart möglich sein. Beta 0.1.0b7 erlaubt manuelle Wiederfreigabe erst nach frischem Bereitschaftsnachweis und verwirft alte Tokens; kein Replay. [Umsetzung und offener Abbruchgrund](reports/ISSUE_7_MANUAL_RECOVERY.de.md). Keine GitHub Actions.

Beta 0.1.0b8: Vom Eigentümer benannte Fach-Schalter zum gezielten Beenden eigener vorbereiteter Einstellungen vor Programmwechsel integrieren. Je Fach frische Kontrolle, nur turn_off, kein globales Beenden. [Verhalten und Abnahme](reports/ISSUE_7_ZONE_RESET.de.md). Keine GitHub Actions.

Beta 0.1.0b9: Beide Einzeltest-Buttons übernehmen dieselbe Formularauswahl; Bestätigung/Fehler werden ins Bild gescrollt. Dörren auf 35–95 °C begrenzen (Eigentümerangabe); Testfolge 55 °C / 360 Minuten nach erfolgreichem Einzeltest beider Fächer. Keine Mindestdauer daraus ableiten. [Korrektur und Abnahme](reports/ISSUE_7_SELECTED_TEST_SETTINGS.de.md). Keine GitHub Actions.

Beta 0.1.0b10: Sieben vom Eigentümer gemeldete Turbo-Tower-Temperaturbereiche getrennt von Adapterfähigkeiten hinterlegen und anzeigen. Beaufsichtigtes Senden erzwingt zusätzlich Modellgrenzen, behält aber die geprüften Adaptergrenzen bei; vollständige Bereiche und Gären benötigen eine Upstream-Anpassung. [Profil und Schnittmenge](reports/ISSUE_7_MODEL_TEMPERATURES.de.md). Keine GitHub Actions.

Beta 0.1.0b11: Rezept-/manuelle Bestätigungen an die WebSocket-Verbindung binden; Verwerfen vor Steuerübergabe serverseitig unterstützen, verspätete UI-Antworten und Offline-Anfragen sperren. Zwölf Rezeptübertragungen durch Routen/Repository/Sender simuliert, Daten unverändert. [Umsetzung und sieben gezielte Gerätefälle](reports/ISSUE_7_RECIPE_LIFECYCLE.de.md). Reale neue Abnahme offen; danach Dashboard samt Backend-Benutzerrechten. Gären/erweiterte Temperaturen zurückgestellt. Keine GitHub Actions.

Beta 0.1.0b12: Rezepteditor mit gemeldeten Programmen des gewählten Airfryers als Auswahlliste; exakte Kennungen speichern, alte Kennungen nur nach ausdrücklicher Auswahl und Speichern korrigieren. Freie Eingabe/fehlender Adapter bleiben unterstützt, Entwürfe bei Render-Vorgängen erhalten. [Umsetzung und erneute Rezeptabnahme](reports/ISSUE_7_EDITOR_PROGRAM_PICKER.de.md). Keine Sendefreigabe oder neuen Programme daraus ableiten. Keine GitHub Actions.
