# Anforderungen – Airfryer Recipes

[Deutsch](REQUIREMENTS.de.md) | [English](REQUIREMENTS.md)

Status: **Abgestimmte Produktanforderungen, keine Liste bereits implementierter Funktionen.**
Letzte Zusammenfassung: 24.10.2026. Projektstandard: Englisch als Fallback; Projektberichte für den Nutzer zuerst auf Deutsch und zusätzlich vollständig auf Englisch.

## Festgelegte Anforderungen

| Nr. | Entscheidung | Beschreibung |
| --- | --- | --- |
| 1 | Geräteunabhängige Rezepte (B) | Airfryer und Garkammer werden erst beim Senden ausgewählt. |
| 2 | Eine Garphase, erweiterbares Format (B) | Zu Beginn eine Phase; Datenmodell unterstützt später mehrere Phasen. |
| 3 | Separate Rezeptverwaltung (A) | Eigene Home-Assistant-Verwaltungsseite und separate Dashboard-Karte. |
| 4 | Grafisches Dashboard, Status und manuelle Bedienung | Gerätegrafik mit anklickbaren Fächern. Je Fach Rezept-Dropdown **oder** manuelle Eingabe von Programm, Temperatur und Zeit; Status/Restzeit soweit verfügbar; expliziter Senden-Button. |
| 5 | Adapter-Architektur (B) | Zuerst Airfryer Control, später weitere Integrationen. |
| 6 | Sicherheitsregel für laufende Fächer (A mit optionalem B) | Standardmäßig Änderungen während des Garens sperren. Administrator kann sie bei Geräteunterstützung im Karteneditor erlauben; Bestätigung erforderlich. Unbekannter Zustand sperrt. |
| 7 | Gerätegrafiken (C) | Wiedererkennbare Bilder für bekannte Modelle, neutrale Grafik als Fallback. |
| 8 | Manuelle Werte merken (C) | Letzte Werte pro Gerät und Fach auch nach Neustart behalten; optional als neues Rezept speichern; gespeicherte Rezepte nicht unbemerkt überschreiben. |
| 9 | Unabhängiger Mehrzonenbetrieb (B) | Beide Fächer gleichzeitig sichtbar und getrennt bedienbar. Später SYNC/MATCH im Dashboard. **Airfryer Control bietet bereits SYNC- und MATCH-Aktionen, aber noch nicht in der Geräteübersicht.** Signaturen und Geräteverhalten prüfen; siehe Issue #1. |
| 10 | Optionale Fertigmeldung (B) | Standardmäßig aus; Push aufs ausgewählte HA-Mobilgerät optional; nur bei verlässlichem Fertigstatus. |
| 11 | Erweiterte Organisation (C) | Kategorien, Favoriten, Suche, freie Tags und zuletzt verwendet. Im Rezepteditor vorhandene Kategorien wählen oder als letzte Option eine neue hinzufügen; gleich geschriebene Namen mit anderer Groß-/Kleinschreibung wiederverwenden. |
| 12 | JSON-Import/-Export (B) | Einzelne oder alle Rezepte, Validierung und Duplikatprüfung; Export mit verständlichem Dateinamen; reguläre HA-Backups bleiben bestehen. |
| 13 | Grafischer Karteneditor und Individualisierung (B+) | Status/Beschriftung/Restzeit/Größe konfigurieren; „Airfryer individualisieren“ für Bildergalerie, eigenes Bild, verschiebbare Fach-Schaltflächen mit relativen Koordinaten und Zurücksetzen. Link „Dein Modell fehlt?“ zu GitHub-Issues. |
| 14 | Automatische Erkennung und Profil-Fallback (B) | Modell, Fächer und Fähigkeiten nach Möglichkeit automatisch lesen; nur bestätigte Profile ergänzen. Nach der Adapteranbindung im Rezepteditor verifizierte Programmfunktionen als Auswahl anbieten; das Rezept bleibt geräteunabhängig. Unbekannte Fähigkeiten bleiben deaktiviert. |
| 15 | Manueller Neuversuch und Offline-Darstellung (B+) | Sende-/Fehlerstatus zeigen; Auswahl erhalten, keine automatische Wiederholung. Offline-Grafik ausgrauen, Senden sperren; unbekannten Status gesondert anzeigen. |
| 16 | Unabhängige Rezeptbibliothek (B) | Rezeptverwaltung/Import/Export bleiben auch bei fehlendem oder defektem Airfryer Control verfügbar. |
| 17 | Zwei Berechtigungsstufen (B) | Administratoren verwalten Rezepte und Sicherheitseinstellungen; normale HA-Benutzer dürfen zulässige Fächer bedienen. Backend prüft Rechte. |
| 18 | Übersetzung und Einheiten | Englisch und Deutsch wie bei Battery Flow Card; **Englisch ist Standard/Fallback**. HA-Benutzersprache und °C/°F-Einstellung übernehmen; intern Celsius. Eigene Rezeptnamen nicht automatisch übersetzen. |
| 19 | Versionierte Speicherung/Migration (B) | Lokal speichern; vor Migration sichern; ursprüngliche Daten bei Fehler erhalten; HACS-Updates überschreiben keine Rezeptdaten. |
| 20 | Kompatibilitätsanpassung (B) | Bei der Gerätebedienung nur bestätigte Programmfunktionen des gewählten Airfryers anbieten. Bei inkompatiblem Programm/Temperatur/Zeit warnen und unterstützte Alternativen anbieten; ausdrückliche Bestätigung; Originalrezept bleibt unverändert. |
| 21 | Gemeinsame/persönliche Einstellungen (C) | Gemeinsame Rezepte und Standardfavoriten; persönliche Favoriten optional; Verlauf pro Gerät/Fach. |
| 22 | Responsives Dashboard mit Größe (B) | Automatisches Layout für Smartphone/Tablet/Desktop, kompakt/normal/groß; Bild und Fachpositionen proportional. |
| 23 | Einfache Rezeptinformationen (A) | Name, Beschreibung, Kategorie/Tags, Favorit, Programm, Temperatur und Zeit; keine Rezeptbilder, Zutaten oder langen Zubereitungsschritte. |
| 24 | Dashboard zuerst, HA-Aktionen später (A + später B) | MVP mit interaktiver Karte; interne Sende-Schnittstelle für spätere Skripte/Automationen vorbereiten. |
| 25 | Sicherer Diagnoseexport (B+) | Nur freigegebene Felder, keine Zugangsdaten; Vorschau/Warnhinweis vor Export und ausdrückliche Erklärung, dass Passwörter/Tokens/Logindaten ausgeschlossen werden. |
| 26 | Optionaler Testmodus (B) | Im Karteneditor einschaltbar; vollständige Bedienung ohne echte Gerätebefehle, serverseitig durchgesetzt; geplante Werte anzeigen. |
| 27 | Geführte Einrichtung (B) | Gerät erkennen, Modell/Fächer wählen, optionale Beispielrezepte und Dashboard-Hilfe; funktioniert auch ohne Gerät. |
| 28 | Stable + Beta (B) | HACS über GitHub-Releases; optionale Vorabversionen, CI, zweisprachige Release Notes und datenschonende Migrationen. |
| 29 | Automatische und reale Tests (B) | GitHub-CI mit Mock-Geräten, lokale Testcheckliste; echte Cosori-Tests nur in eigener HA-Umgebung, kein LAN-Zugriff aus Cloud/Codex. |
| 30 | GitHub-/Codex-Prozess (B) | AGENTS.md, Anforderungen, Roadmap, Issue-/PR-Vorlagen, Feature-Branches, CI und verpflichtende Modell-/Aufgabenprüfung vor jedem Codex-Arbeitspaket. Ab 29.10.2026: ausschließlich GPT-6.1 Sol mit Denkaufwand niedrig, mittel oder hoch; ersetzt frühere Modellempfehlungen. |
| 31 | Modulare Home-Assistant-Architektur (B) | Ein HACS-Paket mit Python-Backend, separater Admin-Rezeptverwaltung und Lovelace-Dashboard, versioniertem lokalem Speicher, authentifizierter Backend-API und austauschbaren Geräteadaptern. Keine Zusatzdienste. Siehe [Architektur](ARCHITECTURE.de.md). |

## Zentrale Nutzerführung

1. Administrator legt geräteunabhängiges Rezept mit einer Garphase an.
2. Nutzer wählt kompatiblen Airfryer und tippt eine Garkammer in der Grafik an.
3. Nutzer wählt ein Rezept oder gibt Programm, Temperatur und Zeit manuell ein.
4. Die Integration prüft Verbindung, Gerätefähigkeiten, Wertebereiche und Garzustand; bei Abweichungen werden ausdrücklich zu bestätigende Alternativen angeboten.
5. Nutzer überträgt die Einstellungen **bewusst**. Geräteeigene Sperren und manueller Start bleiben erhalten.
6. Verlässliche Status-/Fertigmeldungen werden pro Fach angezeigt.

## Sicherheits- und Datenschutzregeln

- Niemals unbeabsichtigt einen Heizvorgang starten; keine Umgehung per zeitgesteuertem Fernstart.
- Keine gepufferten Befehle bei Wiederverbindung, keine automatische Wiederholung.
- Testmodus bedeutet **null echte Steuerbefehle aus dem Backend**.
- Offline/unbekannter Zustand sperrt das Senden; Änderungen beim Garen nur bei Admin-Freigabe, Bestätigung und Geräteunterstützung.
- Berechtigungen und Sicherheitsprüfungen immer im Backend erzwingen.
- Diagnoseexport ausschließlich mit erlaubten, nicht sensiblen Feldern.

## Nicht Teil der ersten Version / spätere Erweiterungen

- Ausführung mehrerer Garphasen (Datenformat bleibt darauf vorbereitet).
- SYNC/MATCH-Schaltflächen im Dashboard (Issue #1): Aktionen sind in Airfryer Control vorhanden; Payload, Geräteunterstützung und korrekte Reihenfolge sind noch zu testen.
- Home-Assistant-Aktionen für Automationen und Sprachsteuerung.
- Rezeptbilder, Zutatenlisten und vollständige Kochanleitungen.
- Weitere Adapter außer Airfryer Control.

## Validierung und Abnahme

- Mit Airfryer Control bereits real getestet: **Cosori Turbo Tower Pro Smart CAF-DC111S-AEU**, Temperatur- und Zeitübertragung an Fach 2.
- Das bestätigt **noch nicht** SYNC/MATCH oder Funktionen in diesem neuen Projekt.
- Vor stabilen Releases: Codeprüfung, automatisierte Tests und dokumentierte lokale Testergebnisse.

Umsetzungsstand zu Anforderungen 14/15/26: Issue #7 liefert lesende Geräteerkennung mit deaktivierten Steuerfähigkeiten. Airfryer Control `1.0.2-beta.1` ergänzt den öffentlichen lesenden Dienst `faehigkeiten`; die Administrator-Vorschau übernimmt daraus ausschließlich erlaubte Programme, Bereiche, Herkunft, Verbindung, Meldezeit und Revision. Geschätzte oder nicht gemeldete Programme bleiben sichtbar ungeprüft und erteilen niemals eine Sendeerlaubnis. Die adminpflichtige API `prepare_send` und ihre [Handy-Oberfläche](reports/ISSUE_7_DRY_RUN_UI.de.md) bleiben serverseitig erzwungener Testmodus und können nicht übertragen. Siehe [Sendevertrag](reports/ISSUE_7_COMMAND_CONTRACT.de.md) und [Prüfbericht](reports/ISSUE_7_DISCOVERY.de.md).
