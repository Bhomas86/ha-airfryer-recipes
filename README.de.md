# Airfryer Recipes für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

Benutzerdefinierte Home-Assistant-Integration zur Verwaltung wiederverwendbarer Heißluftfritteusen-Rezepte. Die gespeicherten Einstellungen sollen über bestehende Home-Assistant-Integrationen an unterstützte Geräte übertragen werden.

> **Projektstatus: Test-Beta 0.1.0b6.** Rezeptverwaltung und beaufsichtigte Einstellungsübertragung sind implementiert. Neu ist die einmal bestätigte Testfolge für beide Fächer. Der feste Airfry-Test wurde auf beiden Fächern abgenommen; die neue Folge und zusätzliche Programme stehen noch zur Geräteabnahme aus. Dashboard und SYNC/MATCH folgen später.

**Neue Test-Beta 0.1.0b5:** Separater beaufsichtigter Gerätetest mit gewählten Rezept-/manuellen Werten für CAF-DC111S-AEU und exakt Airfryer Control 1.0.2-beta.1. Nur nach ausdrücklicher Bestätigung wird einmalig übertragen; normale Gerätesteuerung bleibt gesperrt. [Installation und Test](docs/releases/0.1.0b5.de.md).

Die Testvorbereitung fordert jetzt selbst einen neuen Statusbericht an. [Korrektur der Aktualitätssperre](docs/releases/0.1.0b5.de.md).

Neu: gewählte Rezepte/manuelle Werte für alle sechs gemeldeten Programme beaufsichtigt testen. [Große Testliste](docs/reports/BETA_0_1_0B5_TEST_PLAN.de.md). Keine GitHub Actions für dieses Update.

**Neu: [Geführter Testlauf mit einer Bestätigung](docs/releases/0.1.0b6.de.md).** 132 Python-/29 Frontend-Tests lokal bestanden; keine GitHub Actions.

## Ziele

- **Rezeptbibliothek:** Rezepte mit Namen anlegen, bearbeiten, duplizieren und löschen.
- **Gespeicherte Einstellungen:** Garprogramm, Temperatur und Garzeit je Rezept hinterlegen.
- **Geräteauswahl:** Eine kompatible Heißluftfritteuse auswählen.
- **Garkammerauswahl:** Dasselbe Rezept bei unterstützten Geräten in verschiedenen Körben/Zonen verwenden.
- **Dashboard-Karte:** Gerät, Fach und Rezept über Dropdown-Menüs auswählen, Einstellungen kontrollieren und bewusst übertragen.
- **Lokale Speicherung:** Rezepte in Home Assistant statt in einer Cloud-Datenbank speichern.
- **Mehrsprachige Oberfläche:** Deutsch und Englisch werden unterstützt.

## Geplanter Ablauf

1. Ein Rezept anlegen, beispielsweise **Tiefgefrorene Brötchen**.
2. Garprogramm, Temperatur und Garzeit festlegen.
3. Die Dashboard-Karte öffnen.
4. Heißluftfritteuse, Garkammer und Rezept auswählen.
5. Einstellungen prüfen und ausdrücklich an das Gerät senden.
6. Den Garvorgang **am Gerät** starten, sofern die manuelle Bestätigung erforderlich ist.

Rezepte werden unabhängig von der Garkammer gespeichert; die Fachauswahl erfolgt erst beim Übertragen.

## Technischer Aufbau

Die Rezeptverwaltung soll von der Gerätekommunikation getrennt bleiben. Die erste Entwicklung zielt auf die Zusammenarbeit mit der Community-Integration [Airfryer Control](https://github.com/misterm2310/airfryer-control), die unterstützte Heißluftfritteusen über VeSync anbindet.

Als erstes Zielgerät dient die **Cosori Turbo Tower Pro Smart (CAF-DC111S-AEU)**. Die Übertragung von Temperatur und Garzeit an die untere Garkammer wurde bereits mit **Airfryer Control** getestet, **nicht mit diesem Projekt**. Weitere Modelle, Befehle und Garprogramme müssen noch geprüft werden.

## Entwicklungsstand

- [x] Home-Assistant-Einrichtung und HACS-Metadaten
- [x] Versionierte lokale Rezeptspeicherung und authentifizierte API
- [x] Admin-Rezeptverwaltung mit Kategorien, Suche, Favoriten und JSON-Import/-Export
- [x] Lesende Geräte-/Facherkennung und serverseitige Testvorschau
- [x] Deutsche und englische Oberfläche
- [x] HACS-Vorabversion 0.1.0b2 und dokumentierte Handy-Abnahme
- [ ] Verifizierte Modellgrenzen und sichere echte Übertragung
- [ ] Lovelace-Dashboard-Karte und Karteneditor
- [ ] SYNC/MATCH und stabile Veröffentlichung

Aktuelle Beta: 132 Python-Tests und 29 Frontend-Tests lokal bestanden. Keine GitHub Actions, HACS-/Hassfest- oder Python-3.14-Läufe für dieses Update. Der feste Airfry-Test 170 °C/eine Minute wurde auf beiden Fächern lokal abgenommen; erweiterte Programme und Werte stehen zur Abnahme aus. [Neue Testliste](docs/reports/BETA_0_1_0B5_TEST_PLAN.de.md).

## Installation

**Vorabversion, kein stabiler Release.** Vorher ein Home-Assistant-Backup erstellen. Dieses Repository als benutzerdefiniertes HACS-Integrationsrepository hinzufügen, Vorabversionen anzeigen und über „Neu herunterladen“ `v0.1.0b6` auswählen. Home Assistant neu starten und die Companion-App vollständig neu öffnen.

Die Rezeptverwaltung funktioniert ohne Airfryer Control und benötigt keine Cloud-Zugangsdaten. Für die erweiterte Geräte-Testvorschau Airfryer Control `1.0.2-beta.1` oder neuer installieren. Sie führt keine Steuerbefehle aus. Für CAF-DC111S-AEU sind die sechs gemeldeten Programme und Grenzen noch geschätzt/ungeprüft; `proof` fehlt im Upstream-Vertrag. Normale Übertragung bleibt gesperrt; der separate beaufsichtigte Beta-Test benötigt exakt Airfryer Control 1.0.2-beta.1.

Details: [Release Notes](docs/releases/0.1.0b6.de.md), [lokale Testcheckliste](docs/LOCAL_TEST_CHECKLIST.de.md) und [Roadmap](docs/ROADMAP.de.md).

## Sicherheit und Datenschutz

- Das Übertragen von Einstellungen darf einen Heizvorgang nicht unbemerkt starten.
- Sicherheitsbeschränkungen und eine erforderliche manuelle Startbestätigung des Geräts bleiben bestehen.
- Keine VeSync-Zugangsdaten, Tokens, Gerätekennungen oder persönlichen Konfigurationsdaten in GitHub speichern.
- Rezepte sollen lokal in der Home-Assistant-Instanz verbleiben.

## Mitwirkung

Feedback, Fehlermeldungen und bestätigte Gerätekompatibilität sind über [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues) willkommen.

Dieses Projekt ist unabhängig von Cosori, VeSync und den Entwicklern von Airfryer Control.
