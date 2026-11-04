# Airfryer Recipes für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

**[b22: Abschlussprüfung und geprüfte Speicherung](docs/releases/0.1.0b22.de.md).** Favoritenansammlung und falsche Speicherbestätigung bei stillen HA-Store-Fehlern korrigiert. Python-3.12-/3.14- und Frontend-Prüfungen bestanden. [Prüfung, Abnahme und offene Nachweise](docs/reports/FINAL_REVIEW.de.md).

**[b21: Controller-Beta, volle Temperaturen und Gären](docs/releases/0.1.0b21.de.md).** Beaufsichtigtes Senden verlangt exakt Airfryer Control 1.0.3-beta.3. Der große Lauf prüft jetzt 44 Einstellungen samt allen Temperaturgrenzen und Gären 30/31 °C. B steht im Karteneditor zuerst/als Standard; vorhandene Auswahlen bleiben erhalten.

**[b20: A oder B wählen](docs/releases/0.1.0b20.de.md).** Karteneditor → Fachauswahl auf dem Bild: dezente Markierung oder unsichtbare Touchbereiche. Bei B bleiben die gespeicherten Fächer auf dem Foto antippbar; Rechtecke zum Positionieren bleiben im Bildeditor sichtbar.

**[b19: Darstellung direkt aktualisieren](docs/releases/0.1.0b19.de.md).** Nach Darstellung speichern laden Karten auf derselben Seite die gespeicherte Grafik ohne Seitenneuladen nach. Speichern unter b18 ist nach Neuladen bestätigt; die neue native Aktualisierungsabnahme bleibt offen.

**[b18: Gerätebilder](docs/releases/0.1.0b18.de.md).** Admin-Karteneditor → Airfryer individualisieren: neutrale Galerie, private Bilder und relative Fachbereiche.

**[b17: Darstellungsoptionen](docs/releases/0.1.0b17.de.md).** Kartengröße, Grafikgröße und Status-/Historienanzeige im grafischen Editor. Drei lokale Freigabeprüfungen bestanden.

**[b16: Ganze Geräte freigeben](docs/reports/ISSUE_8_DEVICE_ACCESS.de.md).** Admins geben einem normalen HA-Benutzer ausdrücklich ein ganzes Gerät mit allen Fächern und verfügbaren Programmen frei. Standardmäßig keine Freigaben; Rezept-/Sicherheitsverwaltung bleibt adminpflichtig. Nur die aktuelle Beta bleibt veröffentlicht.

Benutzerdefinierte Home-Assistant-Integration zur Verwaltung wiederverwendbarer Heißluftfritteusen-Rezepte. Die gespeicherten Einstellungen sollen über bestehende Home-Assistant-Integrationen an unterstützte Geräte übertragen werden.

> **Projektstatus: Test-Beta 0.1.0b22.** Grundlegendes Card-Senden beider Fächer, Wiederverwendung nach physischem Zurücksetzen, Fachhistorie und Erhalt über Neustart sind vom Eigentümer bestätigt. Ganzgerätefreigaben für Benutzer sind samt Backend-Prüfung umgesetzt; drei lokale Freigabeprüfungen bestanden; beide Gerätebildvarianten sind bestätigt; 44-Schritt-Rückmeldungsfolge und Gären-Rezeptablauf sind bestätigt. Neue Cards beginnen im Testmodus; echtes Senden bleibt beaufsichtigte Beta. Der korrigierte b22-Speicher-/Neustartweg benötigt noch native Abnahme; Release-Kandidat bleibt ausstehend.

**[Dashboard-Card hinzufügen](docs/reports/ISSUE_8_DASHBOARD_CARD.de.md):** Nach dem Update HA neu starten, App vollständig neu öffnen, dann Dashboard → Bearbeiten → Karte hinzufügen → Airfryer Recipes. Kein Dashboard wird automatisch geändert. Zuerst den Testmodus aktiviert lassen.

**[Lokale Abnahme: sechs Programme, beide Fächer bestanden](docs/reports/ISSUE_7_LOCAL_ACCEPTANCE.de.md).** Nachweis für die dokumentierten Beispielwerte; keine allgemeine Freigabe aller Grenzen.

**Neue Test-Beta 0.1.0b5:** Separater beaufsichtigter Gerätetest mit gewählten Rezept-/manuellen Werten für CAF-DC111S-AEU und exakt Airfryer Control 1.0.2-beta.1. Nur nach ausdrücklicher Bestätigung wird einmalig übertragen; normale Gerätesteuerung bleibt gesperrt. [Installation und Test](docs/releases/0.1.0b5.de.md).

Die Testvorbereitung fordert jetzt selbst einen neuen Statusbericht an. [Korrektur der Aktualitätssperre](docs/releases/0.1.0b5.de.md).

Neu: gewählte Rezepte/manuelle Werte für alle sechs gemeldeten Programme beaufsichtigt testen. [Große Testliste](docs/reports/BETA_0_1_0B5_TEST_PLAN.de.md). Keine GitHub Actions für dieses Update.

**Neu: [Geführter Testlauf mit einer Bestätigung](docs/releases/0.1.0b6.de.md).** 132 Python-/29 Frontend-Tests lokal bestanden; keine GitHub Actions.

**[Neu: Test nach manuellem Zurücksetzen wieder freigeben](docs/releases/0.1.0b7.de.md).** 138 Python-/31 Frontend-Tests lokal bestanden; keine GitHub Actions.

**[Neu: Fach-Einstellungen vor Programmwechsel gezielt beenden](docs/releases/0.1.0b8.de.md).** 145 Python-/32 Frontend-Tests lokal bestanden; keine GitHub Actions.

**[Neu: Gewählte Einzeltest-Werte übernehmen und Dörrtest korrigieren](docs/releases/0.1.0b9.de.md).** 147 Python-/36 Frontend-Tests lokal bestanden; keine GitHub Actions.

**[Neu: Turbo-Tower-Temperaturprofil und Adaptervergleich](docs/releases/0.1.0b10.de.md).** 150 Python-/38 Frontend-Tests lokal bestanden; keine GitHub Actions.

**[Neu: Rezeptbestätigung und Verbindungswechsel](docs/releases/0.1.0b11.de.md).** 163 Python-/50 Frontend-Tests lokal bestanden; keine GitHub Actions. [Sieben gezielte Geräteprüfungen](docs/reports/ISSUE_7_RECIPE_LIFECYCLE.de.md).

**[Neu: Programmauswahl im Rezepteditor](docs/releases/0.1.0b12.de.md).** 164 Python-/59 Frontend-Tests lokal bestanden; keine GitHub Actions. [Vorhandenes Rezept ausdrücklich korrigieren](docs/reports/ISSUE_7_EDITOR_PROGRAM_PICKER.de.md).

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
- [x] Erste Lovelace-Dashboard-Card mit grafischem Editor (beaufsichtigte Beta; normale Benutzer benötigen Ganzgerätefreigaben)
- [ ] SYNC/MATCH und stabile Veröffentlichung

Aktuelle Beta: 212 Python-Tests und 104 Frontend-Tests lokal bestanden. Keine GitHub Actions, HACS-/Hassfest- oder Python-3.14-Läufe für dieses Update. Grundlegendes Card-Senden/Historie/Neustart lokal abgenommen; neue native Rechteabnahme offen. [Dashboard-Verhalten und Prüfungen](docs/reports/ISSUE_8_DASHBOARD_CARD.de.md). Ganzgerätefreigaben sind umgesetzt; Personalisierung bleibt geplant.

## Installation

**Vorabversion, kein stabiler Release.** Vorher ein Home-Assistant-Backup erstellen. Dieses Repository als benutzerdefiniertes HACS-Integrationsrepository hinzufügen, Vorabversionen anzeigen und über „Neu herunterladen“ `v0.1.0b22` auswählen. Home Assistant neu starten und die Companion-App vollständig neu öffnen.

Die Rezeptverwaltung funktioniert ohne Airfryer Control und benötigt keine Cloud-Zugangsdaten. Für die erweiterte Geräte-Testvorschau Airfryer Control `1.0.2-beta.1` oder neuer installieren. Sie führt keine Steuerbefehle aus. Für CAF-DC111S-AEU sind die sechs gemeldeten Programme und Grenzen noch geschätzt/ungeprüft; `proof` fehlt im Upstream-Vertrag. Normale Übertragung bleibt gesperrt; der separate beaufsichtigte Beta-Test benötigt exakt Airfryer Control 1.0.2-beta.1.

Details: [Release Notes](docs/releases/0.1.0b22.de.md), [Dashboard-Einrichtung/-Prüfungen](docs/reports/ISSUE_8_DASHBOARD_CARD.de.md), [lokale Testcheckliste](docs/LOCAL_TEST_CHECKLIST.de.md) und [Roadmap](docs/ROADMAP.de.md).

## Sicherheit und Datenschutz

- Das Übertragen von Einstellungen darf einen Heizvorgang nicht unbemerkt starten.
- Sicherheitsbeschränkungen und eine erforderliche manuelle Startbestätigung des Geräts bleiben bestehen.
- Keine VeSync-Zugangsdaten, Tokens, Gerätekennungen oder persönlichen Konfigurationsdaten in GitHub speichern.
- Rezepte sollen lokal in der Home-Assistant-Instanz verbleiben.

## Mitwirkung

Feedback, Fehlermeldungen und bestätigte Gerätekompatibilität sind über [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues) willkommen.

Dieses Projekt ist unabhängig von Cosori, VeSync und den Entwicklern von Airfryer Control.
