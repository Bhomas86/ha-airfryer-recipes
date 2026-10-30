# Entwicklungsplan – Airfryer Recipes

[Deutsch](ROADMAP.de.md) | [English](ROADMAP.md)

**Status (29.10.2026):** Alle 31 Anforderungen sind beschlossen. Rezeptspeicher, authentifizierte API und lokal abgenommene Admin-Verwaltung sind gemergt. PR #19 mit Geräte-Testvorschau und Programmauswahl ist seit 25.10.2026 gemergt; HACS-Vorabversion `0.1.0b2` wurde auf dem Handy erfolgreich abgenommen. PR #20 korrigiert die HACS-Versionsanzeige. Issue #7 bleibt für die sichere echte Übertragung offen: Beta-Vertrag und modellspezifische Fähigkeiten müssen lokal verifiziert werden. Danach folgt das Dashboard (#8). Siehe [Abnahmebericht](reports/ISSUE_7_DRY_RUN_UI.de.md) und [Architektur](ARCHITECTURE.de.md).

**Prüfung vom 30.10.2026:** Der unveränderte Beta-Vertrag reicht weiterhin nicht zur Live-Freigabe. Modellspezifische Nachweise und frische Gerätebestätigung fehlen; siehe [erneute Vertragsprüfung](reports/ISSUE_7_BETA_REVIEW.de.md).

**Nächstes Testpaket 0.1.0b3:** Separater beaufsichtigter Schnittstellentest vor der Geräteabnahme, vom Eigentümer beauftragt. Keine normale Gerätesteuerung oder Kompatibilitätsfreigabe. [Umsetzung und lokale Tests](reports/ISSUE_7_BETA_SEND.de.md).

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
