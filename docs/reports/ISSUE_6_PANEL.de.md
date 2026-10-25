# Issue #6 – Admin-Rezeptverwaltung

[Deutsch](ISSUE_6_PANEL.de.md) | [English](ISSUE_6_PANEL.md)

## Umsetzung

Dieser Feature-Branch baut auf PR #14 und damit auf PR #13 auf. Er registriert eine lokale, nur für HA-Administratoren sichtbare Rezeptseite. Die Oberfläche nutzt ausschließlich die authentifizierten WebSocket-Befehle: Liste/Suche/Kategorien/Tags, Anlegen, Bearbeiten, Kopieren, bestätigtes Löschen, JSON-Export sowie Import mit Konfliktvorschau und ausdrücklicher Bestätigung. Ein optionales Beispielrezept wird nur auf Wunsch angelegt. Die Darstellung ist für schmale Smartphone-Bildschirme ausgelegt und enthält vollständige englische/deutsche Texte mit Englisch als Fallback. Die eingestellte HA-Temperatureinheit wird angezeigt; gespeichert wird weiterhin Celsius.

Im Rezepteditor stehen vorhandene Kategorien zur Auswahl. „Neue Kategorie hinzufügen“ ist die letzte Option; ein Name, der sich nur in der Groß-/Kleinschreibung unterscheidet, übernimmt die vorhandene Schreibweise. Ein späteres Umbenennen oder Zusammenführen aller Rezepte einer Kategorie ist als eigener Folgepunkt vorgemerkt.

Gemeinsame Favoriten sind Teil des Rezeptdatensatzes und bleiben mit älteren Rezepten kompatibel. Persönliche Favoriten werden separat und nach der authentifizierten HA-Benutzer-ID gespeichert. Normale Nutzer erhalten keinen Admin-Panelzugang; das Backend erlaubt ihnen nur die Änderung ihrer eigenen persönlichen Favoriten. Geräte- und Fachsteuerung gehört nicht zu diesem Panel.

Die Panel-Einbindung nutzt Home Assistants `frontend`, `http`, `panel_custom` und `websocket_api`. Diese benötigten Komponenten sind im Integrationsmanifest deklariert; ein zuvor fehlender Eintrag für `http` wurde nach einem Hassfest-Fehler ergänzt.

## Prüfungen und Grenzen

Automatische Offline-Tests prüfen Python-Lebenszyklus, Datenmodell, Favoriten-Persistenz, WebSocket-Rechte und die wichtigsten Frontend-Abläufe. Die Tests benutzen keine echte HA-Instanz und kein Gerät. Der Projektinhaber hat die Einrichtung und die Admin-Seite auf Home Assistant OS/Core 2026.10.3 am Smartphone geöffnet. Er hat ein Rezept angelegt und bestätigt, dass Rezept und persönlicher Favorit nach einem HA-Neustart erhalten blieben. Bearbeiten, Kopieren, bestätigtes Löschen der Kopie sowie Suche nach Name, Kategorie und Favorit funktionierten ebenfalls. Die Kategorieauswahl und das Wiederverwenden von „Aufbacken“ bei Eingabe von `aufBACKen` wurden am Smartphone bestätigt. JSON-Export/-Import und Berechtigungen sind lokal noch nicht eindeutig geprüft.

Beim Smartphone-Test fehlten ein Ausstieg und die Möglichkeit, das HA-Seitenmenü zu öffnen. Der Panel-Kopf enthält nun „Verlassen“ zur HA-Startseite und einen Menüknopf, der das HA-Ereignis `hass-toggle-menu` auslöst. Der Projektinhaber bestätigte anschließend, dass beide Bedienelemente auf dem Smartphone funktionieren. Für die aktuelle Revision bestanden 9 Frontend- und 55 Python-Offline-Tests.

Für die weitere lokale Abnahme: Nach Backup den aktualisierten Branch installieren, HA neu starten und [die lokale Testcheckliste](../LOCAL_TEST_CHECKLIST.de.md) fortsetzen. Besonders wichtig sind JSON-Export/-Import, persönlicher Favorit mit zweitem Nutzer, Berechtigung des normalen Nutzers und Importkonflikte. Bitte keine echte Geräteübertragung testen. Für Code-Commit `9bc513f` bestanden auf GitHub Hassfest, HACS sowie Python 3.12 und 3.14.

Die Programmeingabe ist derzeit frei, weil noch kein Airfryer-Adapter verifizierte Gerätefunktionen liefert. Nach Issue #7 soll der Rezepteditor solche Programme als Auswahl anbieten; Issue #8 zeigt beim Senden nur Funktionen des gewählten Airfryers. Die dafür notwendige Backend-Validierung ist noch nicht implementiert.
