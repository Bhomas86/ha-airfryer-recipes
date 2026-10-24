# Entwicklungsplan – Airfryer Recipes

[Deutsch](ROADMAP.de.md) | [English](ROADMAP.md)

**Status:** Architektur und alle **31 Anforderungen beschlossen**. Die Projektgrundlage liegt in [PR #2](https://github.com/Bhomas86/ha-airfryer-recipes/pull/2), ist aber **weder gemergt noch über HACS installierbar**. Die [Architekturbeschreibung](ARCHITECTURE.de.md) ist die Grundlage für die technische Umsetzung.

## Prioritäten und Abhängigkeiten

| Phase | Issue | Ergebnis | Voraussetzung | Prüfung |
| --- | --- | --- | --- | --- |
| 0 · Grundlage | [PR #2](https://github.com/Bhomas86/ha-airfryer-recipes/pull/2) | Rezeptmodell, JSON, Tests, 31 zweisprachige Anforderungen, Architektur, Codex-Regeln | Freigabe durch Nutzer | Python 3.12/3.14-CI, Code Review |
| 1 · Home Assistant | [#3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3) | Installierbare Integration, Einrichtung, Übersetzung, HACS-Metadaten | PR #2 | HA startet auch ohne Geräteadapter |
| 2 · Datenspeicherung | [#4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4) | Versionierter Speicher, CRUD, Migration, JSON-Import/-Export | #3 | Neustart, Migration, ungültige Daten |
| 3 · Berechtigte API | [#5](https://github.com/Bhomas86/ha-airfryer-recipes/issues/5) | Rechtegeprüfte WebSocket-Befehle | #3, #4 | Admin/Benutzer und manipulierte Requests |
| 4 · Rezeptverwaltung | [#6](https://github.com/Bhomas86/ha-airfryer-recipes/issues/6) | Responsive Admin-Seite, Deutsch und Englisch | #4, #5 | Bearbeitung ohne Airfryer, Rechte |
| 5 · Sichere Anbindung | [#7](https://github.com/Bhomas86/ha-airfryer-recipes/issues/7) | Airfryer-Control-Adapter, Gerätefähigkeiten, Befehlskoordinator, Testmodus | #3, #5 | Simulierte Sicherheitstests, lokale Cosori-Checkliste |
| 6 · Dashboard | [#8](https://github.com/Bhomas86/ha-airfryer-recipes/issues/8) | Interaktive Fächer, Rezept/Manuell, Rückmeldungen und Karteneditor | #4, #5, #7 | Smartphone/Tablet, beide Fächer, Offline |
| 7 · Individualisierung | [#9](https://github.com/Bhomas86/ha-airfryer-recipes/issues/9) | Bildergalerie, sichere Uploads, verschiebbare Fachpositionen | #8 | Skalierung, Rechte und Bildvalidierung |
| 8 · Beta-Freigabe | [#10](https://github.com/Bhomas86/ha-airfryer-recipes/issues/10) | HACS-Beta, zweisprachige Release Notes, Diagnose, optionale Fertigmeldung | #3–#8, ggf. #9 | CI, echtes HA und Gerätetests |
| Später | [#1](https://github.com/Bhomas86/ha-airfryer-recipes/issues/1) | SYNC/MATCH in Dashboard unter Verwendung vorhandener Aktionen | #7, #8 | Sicherheit und echte Gerätebestätigung |

## Arbeitsteilung

- **ChatGPT kann übernehmen:** Architektur, Rezeptdatenmodelle, Python-Hilfsfunktionen, Tests, Dokumentation, Reviews sowie kleinere abgegrenzte Branches und Pull Requests.
- **Codex übernimmt geeignete größere Pakete:** HA-Lifecycle, Admin-Seite, Adapter und Dashboard. Vor jedem Paket gelten die **vier Modellstufen** aus [AGENTS.md](../AGENTS.de.md). **GPT-5.6 Sol High ist Standard**, nicht GPT-6.1.
- **GitHub Actions:** Ausschließlich Simulationen, Unit-/statische Tests; niemals Zugang zum Heimnetz oder echten Gerät.
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
