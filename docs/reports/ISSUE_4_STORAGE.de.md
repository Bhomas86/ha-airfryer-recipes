# Entwicklungsbericht – Issue #4: Lokaler Rezeptspeicher

[Deutsch](ISSUE_4_STORAGE.de.md) | [English](ISSUE_4_STORAGE.md)

**Entwicklungsstand:** Der Branch enthält eine erste, nicht über die Oberfläche bedienbare Rezeptverwaltung. Diese Fassung ist noch nicht auf einer realen Home-Assistant-Instanz geprüft.

## Implementiert

- Geräteunabhängiges, asynchrones Repository mit `create`, `get`, `list`, `update`, `delete` und JSON-Export.
- Versionsgeprüfte Speicherung über Home Assistants `Store` in `.storage/airfryer_recipes.recipes`. Keine separate Datenbank und kein Airfryer-Control-Zwang.
- Vor jeder Änderung wird der vorherige Snapshot unter `airfryer_recipes.recipes.backup` abgelegt. Bei beschädigten, unbekannten oder neueren Schemata wird nicht mit einer leeren Bibliothek überschrieben.
- Import mit **Vorschau und ausdrücklicher Bestätigung**: IDs/Namen werden auf Konflikte geprüft. Bereits vorhandene Rezepte können übersprungen oder mit identischer ID bewusst ersetzt werden; gleichnamige Rezepte mit anderer ID werden nicht automatisch überschrieben.
- Gleichzeitige Schreibvorgänge durch `asyncio.Lock` serialisiert. Fehlgeschlagene Schreibvorgänge übernehmen keine Änderungen in den aktuellen Repository-Zustand.
- Reine Offline-Unit-Tests ohne Home Assistant, Cloud oder Airfryer.

## Einschränkungen und verbleibende Aufgaben

- **Noch keine grafische Rezeptverwaltung oder WebSocket-API** (Issues #5 und #6).
- Noch keine persönlichen Favoriten, manuellen Geräteeinstellungen oder Verlaufsspeicherung; diese werden getrennt vom Rezeptschema umgesetzt.
- Noch **keine Transformation historischer Speicherformate**. Es gibt bisher nur Format 1; unbekannte Versionen werden absichtlich sicher abgelehnt. Bei einer späteren Schemaänderung müssen eine konkrete Migration, Rollback und zusätzliche Tests bereitgestellt werden.
- Die Snapshot-Sicherung ist eine *vorherige* Version, kein vollständiges langfristiges HA-Backup. Backups der gesamten Home-Assistant-Konfiguration bleiben erforderlich.
- Ein echter Home-Assistant-Start, Neustart und Datenwiederherstellung müssen lokal getestet werden.
- Es sind keine Gerätesteuerungsaufrufe implementiert.

## Lokale Abnahme (nicht durchgeführt)

1. Home-Assistant-Testinstanz sichern, Integration aus dem Branch installieren.
2. Einrichten, Home Assistant neu starten und die Protokolle auf Storage-/Setup-Fehler kontrollieren.
3. Rezeptdaten über ein späteres API-Testwerkzeug oder direkt im Testskript anlegen; nach Neustart auf Vollständigkeit prüfen.
4. Unbekannte Datenversion, defekte JSON-Datei und eine absichtlich fehlgeschlagene Migration ausschließlich in einer **Testkopie** prüfen.
5. Sicherungsdatei und Wiederherstellung kontrollieren, bevor dieses Issue als abgeschlossen gilt.

**Modellrichtlinie:** Für diese isolierte Repository-Implementierung GPT-5.6 Sol High als bestehender Codex-Standard. Migration komplexer alter Formate gesondert vorab prüfen; GPT-6.1 nicht ohne Freigabe einsetzen.
