# Airfryer Recipes für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

Geplante benutzerdefinierte Home-Assistant-Integration zur Verwaltung wiederverwendbarer Heißluftfritteusen-Rezepte. Die gespeicherten Einstellungen sollen über bestehende Home-Assistant-Integrationen an unterstützte Geräte übertragen werden.

> **Projektstatus: Frühe Entwicklungsphase.** Eine Home-Assistant-Grundstruktur und ein bestätigungsbasierter Einrichtungsdialog werden in [Issue #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3) entwickelt. Rezeptdaten-Speicherung, grafische Verwaltung, Dashboard, Geräteadapter und eine getestete HACS-Installation sind **noch nicht implementiert beziehungsweise verifiziert**.

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

- [ ] Grundstruktur der Home-Assistant-Integration und Einrichtung ([Issue #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3); erste Implementierung vorbereitet, reale HA-Prüfung fehlt)
- [ ] Dauerhafte Speicherung mit Plausibilitätsprüfung
- [ ] Grafische Rezeptverwaltung
- [ ] Lovelace-Dashboard-Karte
- [ ] Anbindung an Airfryer Control
- [ ] Geräte-/Zonenunterstützung und Fehlerbehandlung
- [ ] Automatische Tests, HACS-Metadaten und Release-Paket
- [ ] Deutsche und englische Übersetzungen

## Installation

**Noch keine getestete und installierbare Version verfügbar.** Erste HACS-Metadaten und die Einrichtungs-Grundstruktur sind vorhanden, wurden aber **noch nicht innerhalb von Home Assistant getestet**. Bitte nicht in einer produktiven HACS-Installation hinzufügen, bevor die erste geprüfte Version veröffentlicht wurde.

Der vorgesehene Einrichtungsdialog benötigt weder Airfryer noch Cloud-Zugangsdaten oder eine Internetverbindung. Der vollständige Assistent und die Rezeptverwaltung folgen in späteren Issues.

## Sicherheit und Datenschutz

- Das Übertragen von Einstellungen darf einen Heizvorgang nicht unbemerkt starten.
- Sicherheitsbeschränkungen und eine erforderliche manuelle Startbestätigung des Geräts bleiben bestehen.
- Keine VeSync-Zugangsdaten, Tokens, Gerätekennungen oder persönlichen Konfigurationsdaten in GitHub speichern.
- Rezepte sollen lokal in der Home-Assistant-Instanz verbleiben.

## Mitwirkung

Feedback, Fehlermeldungen und bestätigte Gerätekompatibilität sind über [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues) willkommen.

Dieses Projekt ist unabhängig von Cosori, VeSync und den Entwicklern von Airfryer Control.
