# Issue #6 – Admin-Rezeptverwaltung

[Deutsch](ISSUE_6_PANEL.de.md) | [English](ISSUE_6_PANEL.md)

## Umsetzung

Dieser Feature-Branch baut auf PR #14 und damit auf PR #13 auf. Er registriert eine lokale, nur für HA-Administratoren sichtbare Rezeptseite. Die Oberfläche nutzt ausschließlich die authentifizierten WebSocket-Befehle: Liste/Suche/Kategorien/Tags, Anlegen, Bearbeiten, Kopieren, bestätigtes Löschen, JSON-Export sowie Import mit Konfliktvorschau und ausdrücklicher Bestätigung. Ein optionales Beispielrezept wird nur auf Wunsch angelegt. Die Darstellung ist für schmale Smartphone-Bildschirme ausgelegt und enthält vollständige englische/deutsche Texte mit Englisch als Fallback. Die eingestellte HA-Temperatureinheit wird angezeigt; gespeichert wird weiterhin Celsius.

Im Rezepteditor stehen vorhandene Kategorien zur Auswahl. „Neue Kategorie hinzufügen“ ist die letzte Option; ein Name, der sich nur in der Groß-/Kleinschreibung unterscheidet, übernimmt die vorhandene Schreibweise. Ein späteres Umbenennen oder Zusammenführen aller Rezepte einer Kategorie ist als eigener Folgepunkt vorgemerkt.

Gemeinsame Favoriten sind Teil des Rezeptdatensatzes und bleiben mit älteren Rezepten kompatibel. Persönliche Favoriten werden separat und nach der authentifizierten HA-Benutzer-ID gespeichert. Normale Nutzer erhalten keinen Admin-Panelzugang; das Backend erlaubt ihnen nur die Änderung ihrer eigenen persönlichen Favoriten. Geräte- und Fachsteuerung gehört nicht zu diesem Panel.

Die Panel-Einbindung nutzt Home Assistants `frontend`, `http`, `panel_custom` und `websocket_api`. Diese benötigten Komponenten sind im Integrationsmanifest deklariert; ein zuvor fehlender Eintrag für `http` wurde nach einem Hassfest-Fehler ergänzt.

Der JSON-Export erzeugt keinen namenlosen Browser-Blob mehr. Ein Admin erhält über WebSocket einen 30 Sekunden gültigen, an seine HA-Sitzung gebundenen Downloadpfad. Der HTTP-Endpunkt prüft die Adminrolle erneut und liefert die Datei als `Airfryer-Rezepte-Home-Assistant.json`; Caching ist deaktiviert. Damit soll verhindert werden, dass die Android-App stattdessen eine UUID als Dateinamen verwendet.

## Prüfungen und Grenzen

Automatische Offline-Tests prüfen Python-Lebenszyklus, Datenmodell, Favoriten-Persistenz, WebSocket-/HTTP-Rechte und die wichtigsten Frontend-Abläufe. Die Tests benutzen keine echte HA-Instanz und kein Gerät. Für die aktuelle Revision bestanden 10 Frontend- und 59 Python-Offline-Tests.

| Lokale Prüfung auf HA OS/Core 2026.10.3 | Ergebnis |
| --- | --- |
| Einrichtung und Admin-Seite auf dem Smartphone | **BESTANDEN** |
| Rezept anlegen; Rezept und persönlicher Favorit nach Neustart erhalten | **BESTANDEN** |
| Bearbeiten, Kopieren und bestätigtes Löschen der Kopie | **BESTANDEN** |
| Suche/Filter nach Name, Kategorie und Favorit | **BESTANDEN** |
| Kategorieauswahl; `aufBACKen` übernimmt „Aufbacken“ | **BESTANDEN** |
| HA-Seitenmenü öffnen und Panel verlassen | **BESTANDEN** |
| JSON exportieren, Datei wieder auswählen und drei gleiche IDs/Namen in der Vorschau erkennen | **BESTANDEN** |
| Neuer Dateiname `Airfryer-Rezepte-Home-Assistant.json` auf Android | **BESTANDEN** |
| Import mit `skip` bestätigen; gleiche Rezepte bleiben unverändert und werden nicht erneut angelegt | **BESTANDEN** |
| Import mit `replace_ids` bestätigen | **NICHT GETESTET** |
| Zweiter/normaler Benutzer und getrennte persönliche Favoriten | **NICHT GETESTET** |

Für die weitere lokale Abnahme bleiben die Importbestätigung mit `replace_ids`, ein persönlicher Favorit mit zweitem Nutzer und die Berechtigung des normalen Nutzers offen. Bitte keine echte Geräteübertragung testen.

Die Programmeingabe ist derzeit frei, weil noch kein Airfryer-Adapter verifizierte Gerätefunktionen liefert. Nach Issue #7 soll der Rezepteditor solche Programme als Auswahl anbieten; Issue #8 zeigt beim Senden nur Funktionen des gewählten Airfryers. Die dafür notwendige Backend-Validierung ist noch nicht implementiert.
