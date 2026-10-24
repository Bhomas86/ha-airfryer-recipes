# Entwicklungsplan – Roadmap

[Deutsch](ROADMAP.de.md) | [English](ROADMAP.md)

Aktueller Status: **Grundlagen-Pull-Request in Prüfung. Noch nicht über HACS installierbar.**

## Phase 0 – Dokumentation und unabhängiges Rezeptmodell (dieser PR)
- [x] Codex-Modellprüfung und Eskalationsregeln (`AGENTS.md`)
- [x] Anforderungen 1–30 zusammengefasst
- [x] Geräteunabhängiges Rezeptschema, Validierung, versionierter JSON-Import/-Export
- [x] Offline-Python-Unit-Tests
- [x] Erfolgreiche GitHub-CI-Läufe für Python 3.12 und 3.14
- [ ] Prüfung und Merge durch Repository-Verantwortlichen

## Phase 1 – Basis der Home-Assistant-Integration
- [ ] Manifest, HACS-Metadaten und Einrichtungsdialog
- [ ] Lokale HA-Speicherung mit asynchronem `Store`
- [ ] Sichere Datenmigrationen mit Sicherung und Wiederherstellung
- [ ] Admin-Rechte für Änderungen, normale Benutzerrechte zur Bedienung
- [ ] Backend für Anlegen/Bearbeiten/Löschen und JSON-Import/-Export mit Konfliktvorschau
- [ ] Rezeptverwaltung ohne Airfryer Control benutzbar

## Phase 2 – Grafische Rezeptverwaltung
- [ ] Administrationsoberfläche in Home Assistant, Deutsch/Englisch
- [ ] Anlegen, bearbeiten, duplizieren, löschen (mit Bestätigung) und suchen
- [ ] Kategorien, Tags, gemeinsame/persönliche Favoriten
- [ ] Optionale Beispielrezepte bei Ersteinrichtung

## Phase 3 – Geräteadapter und sichere Übertragung
- [ ] Adapter-Vertrag für Modell, Garkammern, Fähigkeiten und Online-Status
- [ ] Airfryer-Control-Adapter mit Prüfung der vorhandenen Aktionsparameter
- [ ] Kompatibilitätsprüfung für Programm, Temperatur und Zeit
- [ ] Schutz bei offline, unbekanntem Zustand und laufendem Garbetrieb
- [ ] Serverseitiger Testmodus; Wiederholung nur auf ausdrücklichen Wunsch
- [ ] Reale, beaufsichtigte Tests mit CAF-DC111S-AEU

## Phase 4 – Grafisches Dashboard
- [ ] Modellspezifische oder neutrale Gerätegrafik
- [ ] Anklickbare Fächer für Rezepte und manuelle Werte
- [ ] Responsiver Karteneditor, eigene Bilder und relative Koordinaten
- [ ] Status-/Restzeit-Anzeige und optionale Benachrichtigungen
- [ ] Eindeutige Sende-, Fehler- und Offline-Anzeige

## Phase 5 – Optionale Erweiterungen
- [ ] SYNC- und MATCH-Bedienung für vorhandene Aktionen (Issue #1)
- [ ] Home-Assistant-Aktionen für Skripte und Automationen (nach Dashboard-MVP)
- [ ] Mehrphasige Rezepte
- [ ] Weitere Geräteadapter und Gerätebilder

## Voraussetzungen für Releases
- Erfolgreiche Unit-Tests und CI
- Home-Assistant-Integrations- und Einrichtungstests vor HACS-Freigabe
- Sicherheitsprüfungen: kein unbeabsichtigter Start, keine Offline-Befehle nachholen
- **Vollständig zweisprachige Berichte, PRs, Release Notes und Benutzerdokumentation**
- Reale Tests separat dokumentieren; keine Testerfolge behaupten, die nicht durchgeführt wurden
- Stabile Releases und optionale Betas; Rezeptdaten bleiben erhalten
