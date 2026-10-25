# Backend-Prüfung – PR #13 und PR #14

[Deutsch](BACKEND_REVIEW.de.md) | [English](BACKEND_REVIEW.md)

Stand: 25.10.2026. Prüfung der GitHub-PR-Refs `a9137a6` (#13) und `bfe4f6d` (#14). Die beiden nachgewiesenen Fehler wurden anschließend im lokalen Korrektur-Branch `fix/pr13-storage-review` behoben.

## Projektstand

PR #12 ist in `main` enthalten. PR #13 implementiert Rezept-CRUD, versionierte Speicherung und bestätigten JSON-Import. PR #14 baut unmittelbar darauf auf und ergänzt neun WebSocket-Befehle. Die grafische Rezeptverwaltung aus Issue #6 ist nicht begonnen. Architektur und Roadmap enthalten teils veraltete Statusangaben.

## PR #13: Befunde

1. **Blockierend: Eine gültige Bibliothek kann nach Neustart unlesbar sein.** `RecipeRepository._commit()` erlaubt 500 Rezepte innerhalb aller Feldgrenzen. `async_load()` serialisiert den gespeicherten Zustand aber erneut und ruft `import_library_json()` auf; diese Funktion begrenzt Importe auf 1 MB. Ein reproduzierbarer Offline-Test speicherte 500 gültige Rezepte erfolgreich und erhielt beim erneuten Laden `RecipeValidationError: invalid or oversized JSON input`. Die Originaldaten wurden nicht überschrieben, aber die Integration kann nicht starten. Das Speicherformat muss getrennt vom Upload-Limit validiert und mit einem Neustarttest an den Grenzen geprüft werden.
2. **Mittel: Ein bestätigter Import verliert bei Speicherfehler sein Bestätigungstoken.** `async_confirm_import()` entfernt das Token vor `_commit()`. Ein simuliertes `OSError` ließ die Daten unverändert; nach Behebung des Fehlers wurde derselbe Versuch als abgelaufen zurückgewiesen. Ein neuer Vorschauprozess ist nötig. Ein Regressionstest fehlt.
3. **Offen: Migrationen.** Version 1 wird geprüft und spätere Versionen werden sicher abgelehnt. Eine tatsächliche Migration samt Rollback ist noch nicht implementiert. Der getrennte rollierende Snapshot ist kein vollständiges HA-Backup.

Positiv: CRUD und Schreibzugriffe sind durch einen Lock serialisiert; bestätigte Schreibfehler veröffentlichen keinen neuen In-Memory-Zustand. Vorschau, Duplikatprüfung und bewusste Konfliktstrategie sind vorhanden. Speicher und Integration setzen Airfryer Control nicht voraus. Tests für Wiederanlauf, paralleles Anlegen und simulierte Speicherfehler sind vorhanden.

## PR #14: Architektur und Sicherheit

Lesebefehle verwenden die authentifizierte HA-Verbindung; Mutationen und Import/Export nutzen serverseitig `require_admin`. Clientseitige `is_admin`-Felder werden nicht ausgewertet. Das Rezeptmodell validiert Felder und begrenzt JSON-Uploads; unerwartete Speicherfehler erscheinen für Clients ohne interne Pfade. Die API enthält keine Gerätebefehle. Die Rechteprüfung wurde nur mit einem HA-Stub getestet, nicht in einer echten HA-Instanz. PR #14 übernimmt den Speicherfehler aus PR #13. Für Issue #6 fehlen dadurch eine belastbare Neustartprüfung und ein echter HA-Test der Registrierung und Rechte.

## Prüfungen und nächste Schritte

PR #13: Kompilierung und 36 Offline-Tests bestanden. PR #14: Kompilierung und 48 Offline-Tests bestanden. GitHubs öffentliche Check-Seiten zeigen erfolgreiche Python-3.12/3.14-, Hassfest- und HACS-Checks für die untersuchten PRs; der API-Zugriff auf detaillierte PR-Metadaten war gesperrt. Die beiden gezielten Reproduktionen für den Größen- und Importfehler bestätigten die Befunde. Keine Produktcodeänderungen vorgenommen.

Die beiden Korrekturen liegen im Commit `5b3bfdc`: getrennte Validierung für lokalen Speicher und JSON-Upload sowie erneute Importbestätigung nach Speicherfehler. Zwei Regressionstests wurden ergänzt. Danach bestanden 38 Offline-Tests auf der PR-#13-Basis und 50 auf der PR-#14-Basis mit dem Korrekturcommit. Vor Issue #6 sind weiterhin echte HA-Tests erforderlich: Einrichten ohne Airfryer Control, Rezeptpersistenz nach Neustart, Sicherungswiederherstellung auf Testkopie, Admin-/Normalbenutzer-Rechte und fehlerhafte WebSocket-Anfragen. Keine Gerätebefehle nötig. GPT-6 Sol – High genügt für die Nachprüfung; bei unerwartet komplexer Migration oder einem bestätigten Rechtefehler Modellbedarf neu bewerten.
