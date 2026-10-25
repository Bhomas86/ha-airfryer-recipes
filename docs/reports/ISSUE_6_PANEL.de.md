# Issue #6 – Admin-Rezeptverwaltung

[Deutsch](ISSUE_6_PANEL.de.md) | [English](ISSUE_6_PANEL.md)

## Umsetzung

Dieser Feature-Branch baut auf PR #14 und damit auf PR #13 auf. Er registriert eine lokale, nur für HA-Administratoren sichtbare Rezeptseite. Die Oberfläche nutzt ausschließlich die authentifizierten WebSocket-Befehle: Liste/Suche/Kategorien/Tags, Anlegen, Bearbeiten, Kopieren, bestätigtes Löschen, JSON-Export sowie Import mit Konfliktvorschau und ausdrücklicher Bestätigung. Ein optionales Beispielrezept wird nur auf Wunsch angelegt. Die Darstellung ist für schmale Smartphone-Bildschirme ausgelegt und enthält vollständige englische/deutsche Texte mit Englisch als Fallback. Die eingestellte HA-Temperatureinheit wird angezeigt; gespeichert wird weiterhin Celsius.

Gemeinsame Favoriten sind Teil des Rezeptdatensatzes und bleiben mit älteren Rezepten kompatibel. Persönliche Favoriten werden separat und nach der authentifizierten HA-Benutzer-ID gespeichert. Normale Nutzer erhalten keinen Admin-Panelzugang; das Backend erlaubt ihnen nur die Änderung ihrer eigenen persönlichen Favoriten. Geräte- und Fachsteuerung gehört nicht zu diesem Panel.

## Prüfungen und Grenzen

Automatische Offline-Tests prüfen Python-Lebenszyklus, Datenmodell, Favoriten-Persistenz, WebSocket-Rechte und die wichtigsten Frontend-Abläufe. Die Tests benutzen keine echte HA-Instanz und kein Gerät. Die Ersteinrichtung von PR #14 wurde vom Projektinhaber auf Home Assistant OS/Core 2026.10.3 bestätigt; diese neue Oberfläche wurde dort **noch nicht** installiert oder geprüft.

Für die lokale Abnahme: Nach Backup den Branch manuell installieren, HA neu starten, die neue Seitenleiste auf dem Handy öffnen und die Schritte in [der lokalen Testcheckliste](../LOCAL_TEST_CHECKLIST.de.md) durchführen. Besonders wichtig sind Rezeptänderungen mit anschließendem Neustart, persönlicher Favorit mit zweitem Nutzer, Berechtigung des normalen Nutzers und Importkonflikte. Bitte keine echte Geräteübertragung testen. HACS-/Hassfest-Checks und reale Smartphone-Darstellung müssen nach Veröffentlichung des Branches separat geprüft werden.
