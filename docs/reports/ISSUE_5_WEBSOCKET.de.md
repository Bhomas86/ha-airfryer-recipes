# Issue #5 – Authentifizierte Rezept-WebSocket-API

[Deutsch](ISSUE_5_WEBSOCKET.de.md) | [English](ISSUE_5_WEBSOCKET.md)

## Umfang und Abhängigkeit

Diese Implementierung baut **auf der noch offenen Issue-#4-Speicherimplementierung aus PR #13** auf. Der Pull Request richtet sich zunächst gegen deren Feature-Branch, nicht gegen `main`.

Die Home-Assistant-WebSocket-Schnittstelle erlaubt angemeldeten Benutzern, Rezepte aufzulisten und einzeln zu lesen. Änderungen sind **serverseitig auf HA-Administratoren begrenzt**. Rechte aus Browserdaten wie `is_admin` werden ignoriert. Keine Cloud, keine Geräteadapter und **keine Gerätebefehle**.

## Schnittstelle

Jede Anfrage nutzt das normale Home-Assistant-WebSocket-Format: `{"id": 1, "type": "airfryer_recipes/list"}`. Die übrigen Parameter und Resultate sind:

| Befehl | Berechtigung | Zusätzliche Daten | Ergebnis |
| --- | --- | --- | --- |
| `list` | Benutzer | – | `recipes` |
| `get` | Benutzer | `recipe_id` | `recipe` |
| `create` | Admin | `recipe` ohne ID | `recipe` mit Server-ID |
| `update` | Admin | `recipe` mit ID | Aktualisiertes `recipe` |
| `duplicate` | Admin | `recipe_id`, `name` | Kopie mit neuer ID |
| `delete` | Admin | `recipe_id` | `deleted` |
| `import_preview` | Admin | `payload` (JSON-Text) | Vorschau, Konflikte und kurzlebiges `token` |
| `import_confirm` | Admin | `token`, optional `policy` | `imported` |
| `export` | Admin | – | Versionierter JSON-Text in `payload` |

Der vollständige Befehlstyp erhält immer den Präfix `airfryer_recipes/`. Konfliktstrategie: `skip` (Standard) oder `replace_ids` (nur identische IDs).

## Sicherheits- und Qualitätsregeln

- `require_admin` prüft den echten HA-Benutzer vor schreibenden Funktionen.
- JSON-Felder werden durch das bestehende Rezeptmodell mit Längen- und Wertebereichsgrenzen geprüft.
- Fehler haben strukturierte Codes, unerwartete interne Speicherfehler werden nicht mit vertraulichen Details an Clients ausgegeben.
- Beim Unload sperrt die API mangels aktiven Repository-Zugangs.
- Die API ruft keine Airfryer-/VeSync-Aktionen auf.
- **Persönliche Favoriten**, Geräteeinstellungen und Steuerrechte für Fach-/Gerätekombinationen sind noch nicht implementiert; sie gehören in spätere Aufgaben. Die aktuelle API enthält keine Benutzerpräferenzen.
- Authentifizierte Administratoren können JSON exportieren; UI-Bestätigung vor Löschvorgängen muss in Issue #6 ergänzt werden.

## Testplan

GitHub Actions prüft offline die Berechtigungen, Mutationen, Importvorschau, doppelte Bestätigung, fehlerhafte Werte, Unload-Verhalten und Übersetzungen. Diese Tests simulieren Home Assistant und **ersetzen keine echte Installation**.

**Vereinbarung zum lokalen Test:** Keine separate Testinstanz. Der erste reale Test erfolgt mit der grafischen Rezeptverwaltung aus **Issue #6** auf der bestehenden Home-Assistant-Instanz, nach einer Sicherung. Keine frühen Testbefehle an den Airfryer.

**Modellrichtlinie:** GPT-5.6 Sol High bleibt die vom Nutzer beibehaltene Codex-Standardeinstellung; die tatsächliche VS-Code-Auswahl ist hier nicht überprüfbar. Für einen tieferen Sicherheitsreview kann GPT-6 Sol High empfohlen werden; GPT-6.1 Sol High nur bei begründetem Ausnahmefall.
