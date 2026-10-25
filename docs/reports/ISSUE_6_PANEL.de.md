# Issue #6 – Admin-Rezeptverwaltung

[Deutsch](ISSUE_6_PANEL.de.md) | [English](ISSUE_6_PANEL.md)

## Umsetzung

Dieser Feature-Branch baut auf PR #14 und damit auf PR #13 auf. Er registriert eine lokale, nur für HA-Administratoren sichtbare Rezeptseite. Die Oberfläche nutzt ausschließlich die authentifizierten WebSocket-Befehle: Liste/Suche/Kategorien/Tags, Anlegen, Bearbeiten, Kopieren, bestätigtes Löschen, JSON-Export sowie Import mit Konfliktvorschau und ausdrücklicher Bestätigung. Ein optionales Beispielrezept wird nur auf Wunsch angelegt. Die Darstellung ist für schmale Smartphone-Bildschirme ausgelegt und enthält vollständige englische/deutsche Texte mit Englisch als Fallback. Die eingestellte HA-Temperatureinheit wird angezeigt; gespeichert wird weiterhin Celsius.

Gemeinsame Favoriten sind Teil des Rezeptdatensatzes und bleiben mit älteren Rezepten kompatibel. Persönliche Favoriten werden separat und nach der authentifizierten HA-Benutzer-ID gespeichert. Normale Nutzer erhalten keinen Admin-Panelzugang; das Backend erlaubt ihnen nur die Änderung ihrer eigenen persönlichen Favoriten. Geräte- und Fachsteuerung gehört nicht zu diesem Panel.

## Prüfungen und Grenzen

Automatische Offline-Tests prüfen Python-Lebenszyklus, Datenmodell, Favoriten-Persistenz, WebSocket-Rechte und die wichtigsten Frontend-Abläufe. Die Tests benutzen keine echte HA-Instanz und kein Gerät. Der Projektinhaber hat die Einrichtung und die Admin-Seite auf Home Assistant OS/Core 2026.10.3 am Smartphone geöffnet. Er hat ein Rezept angelegt und bestätigt, dass Rezept und persönlicher Favorit nach einem HA-Neustart erhalten blieben. Weitere Abläufe und die Berechtigungen sind lokal noch nicht geprüft.

Beim Smartphone-Test fehlten ein Ausstieg und die Möglichkeit, das HA-Seitenmenü zu öffnen. Der Panel-Kopf enthält nun „Verlassen“ zur HA-Startseite und einen Menüknopf, der das HA-Ereignis `hass-toggle-menu` auslöst. Diese Korrektur bestand 6 Frontend- und 55 Python-Offline-Tests. Die tatsächliche Menüfunktion auf dem Smartphone muss nach Installation des aktualisierten Branches erneut geprüft werden.

Für die weitere lokale Abnahme: Nach Backup den aktualisierten Branch installieren, HA neu starten und [die lokale Testcheckliste](../LOCAL_TEST_CHECKLIST.de.md) fortsetzen. Besonders wichtig sind Rezeptänderungen mit anschließendem Neustart, persönlicher Favorit mit zweitem Nutzer, Berechtigung des normalen Nutzers und Importkonflikte. Bitte keine echte Geräteübertragung testen. HACS-/Hassfest-Checks für die aktualisierte Fassung stehen noch aus.
