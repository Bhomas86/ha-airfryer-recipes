# Airfryer Recipes für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

Geplante benutzerdefinierte Home-Assistant-Integration zur Verwaltung wiederverwendbarer Heißluftfritteusen-Rezepte. Die gespeicherten Einstellungen sollen über bestehende Home-Assistant-Integrationen an unterstützte Geräte übertragen werden.

> **Projektstatus: Frühe Entwicklungsphase.** Die Home-Assistant-Grundstruktur aus Issue #3 ist gemergt. Rezeptspeicher und WebSocket-API werden in PR #13 und PR #14 geprüft. Dieser Branch ergänzt die Admin-Rezeptverwaltung für Issue #6. Die Ersteinrichtung gelang auf Home Assistant OS 2026.10.3; Rezeptfunktionen, Rechte und Speicherung nach Neustart müssen lokal geprüft werden. Dashboard und Geräteadapter sind nicht implementiert.

## Ziele

- **Rezeptbibliothek:** Rezepte mit Namen anlegen, bearbeiten, duplizieren und löschen.
- **Gespeicherte Einstellungen:** Garprogramm, Temperatur und Garzeit je Rezept hinterlegen.
- **Geräteauswahl:** Eine kompatible Heißluftfritteuse auswählen.
- **Garkammerauswahl:** Dasselbe Rezept bei unterstützten Geräten in verschiedenen Körben/Zonen verwenden.
- **Dashboard-Karte:** Gerät, Fach und Rezept über Dropdown-Menüs auswählen, Einstellungen kontrollieren und bewusst übertragen.
- **Lokale Speicherung:** Rezepte in Home Assistant statt in einer Cloud-Datenbank speichern.
- **Mehrsprachige Oberfläche:** Deutsch und Englisch sind geplant.

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

## Geplante Meilensteine

- [x] Code-Grundstruktur und Einrichtungsdialog ([Issue #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3); Einrichtung auf HA 2026.10.3 bestätigt)
- [ ] Dauerhafte Speicherung mit Plausibilitätsprüfung ([Issue #4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4); Rezept und persönlicher Favorit überstanden einen lokalen Neustart, weitere Abnahme offen)
- [ ] Grafische Rezeptverwaltung (Code im Issue-#6-Branch; Anlegen auf dem Smartphone bestätigt, weitere Abnahme offen)
- [ ] Lovelace-Dashboard-Karte
- [ ] Anbindung an Airfryer Control
- [ ] Geräte-/Zonenunterstützung und Fehlerbehandlung
- [ ] Automatische Tests, HACS-Metadaten und Release-Paket
- [ ] Deutsche und englische Übersetzungen

## Installation

**Noch keine vollständig geprüfte Veröffentlichung verfügbar.** Einrichtung, Rezeptanlage sowie Speicherung von Rezept und persönlichem Favoriten über einen Neustart wurden auf Home Assistant 2026.10.3 bestätigt. Weitere Rezeptabläufe und Berechtigungen müssen lokal noch geprüft werden. Bitte vor der ersten geprüften Version keine stabile Nutzung annehmen.

Der Einrichtungsdialog benötigt weder Airfryer noch Cloud-Zugangsdaten oder eine Internetverbindung. Die Admin-Rezeptverwaltung wird in Issue #6 getestet; der vollständige Geräteassistent folgt später.

## Sicherheit und Datenschutz

- Das Übertragen von Einstellungen darf einen Heizvorgang nicht unbemerkt starten.
- Sicherheitsbeschränkungen und eine erforderliche manuelle Startbestätigung des Geräts bleiben bestehen.
- Keine VeSync-Zugangsdaten, Tokens, Gerätekennungen oder persönlichen Konfigurationsdaten in GitHub speichern.
- Rezepte sollen lokal in der Home-Assistant-Instanz verbleiben.

## Mitwirkung

Feedback, Fehlermeldungen und bestätigte Gerätekompatibilität sind über [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues) willkommen.

Dieses Projekt ist unabhängig von Cosori, VeSync und den Entwicklern von Airfryer Control.
