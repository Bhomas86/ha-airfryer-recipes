# Geprüfte Controller-Transportquellen

[English](README.md) | [Deutsch](README.de.md)

Der Eigentümer verlangt die Absicherung ohne Controller-Änderung. Der vorherige Patchvorschlag wurde entfernt; **kein Controller-Patch ist erforderlich, installiert oder eingereicht**. Produktiv wird unser eigener abgesicherter Sender statt der Controller-SYNC-/MATCH-Aktionen verwendet. [Aktuelle Implementierung](../reports/ISSUE_1_OWN_GUARD.de.md).

Die ausschließlich für Tests extrahierten Quellen stammen aus `misterm2310/airfryer-control`, Commit `75d30c800ae79eea2254e5d4f5da31ec154398e7`, Copyright (c) 2026 misterm2310, unter MIT-Lizenz; diese liegt unverändert unter [LICENSE.airfryer-control](LICENSE.airfryer-control):

- `tests/fixtures/controller_103_sync_functions.py.txt`: tatsächliche kombinierte Sendefunktionen, um den ursprünglichen Fehler bei unbekanntem/fehlendem Fach mit simulierten Geräteaufrufen zu reproduzieren.
- `tests/fixtures/controller_103_transport.py.txt`: tatsächliche `bypass_v2`, `_once`, `_unwrap`, zusammen mit unserem Schutz und simulierter HTTP-Übergabe geprüft. Der vollständige Quelltext von `core/api.py` ist in geprüfter 1.0.3 und 1.0.4-beta.1 identisch.

Kein Controller-Code wird als produktiver Controller mitinstalliert. Unser Adapter verwendet den bereits geladenen Transport, ohne Controller-Attribute oder -Funktionen zu ersetzen. Anmeldung/Fehlerbehandlung bleiben beim Transport; abschließende Berichts-/Identitäts-/Rechte-/Ablaufprüfungen und einmalige Übergabe erzwingt unsere Integration.
