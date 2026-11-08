# Vorschlag für die Controller-Zustandsprüfung

[English](README.md) | [Deutsch](README.de.md)

`controller-sync-state-guard.patch` ist ein Änderungsvorschlag für `misterm2310/airfryer-control`, stabile 1.0.3, Commit `75d30c800ae79eea2254e5d4f5da31ec154398e7`. Er ist **nicht installiert**, nicht im Controller des Benutzers angewendet und nicht beim Controller-Projekt eingereicht. Er ergänzt eine sperrende Berichtsprüfung vor Rücksetzbefehlen und unmittelbar vor dem kombinierten Schreiben. Beide Fachberichte müssen vorhanden, ausdrücklich inaktiv und sicher bereit sein (vorbereitet nur während freigegebener Rücksetzvorbereitung), mit Online-/Fehlerprüfung und höchstens 15 Sekunden altem Bericht. Keine zusätzlichen Wiederholungen und kein Heizstart.

Die 15-Sekunden-Frischegrenze muss gegen den tatsächlichen erfolgreichen Aktualisierungsvertrag des Controllers geprüft werden. Dies bleibt ein Vorschlag bis zu Controller-Review, vollständigen Controller-Tests und nativer Abnahme. In einem sauberen Controller-Checkout mit `git apply --check /pfad/zu/controller-sync-state-guard.patch` prüfen, anschließend `git apply /pfad/zu/controller-sync-state-guard.patch`. Keine laufende Installation ungeprüft patchen. Unsere Tests führen nur extrahierte Funktionen mit simulierten Geräte-APIs aus.

Die extrahierte Testdatei `tests/fixtures/controller_103_sync_functions.py.txt` stammt aus `senden.py` dieses Commits, Copyright (c) 2026 misterm2310, unter MIT-Lizenz; diese liegt unverändert unter [LICENSE.airfryer-control](LICENSE.airfryer-control). Der Änderungsvorschlag behält diese Lizenz bei. Die Testdatei dient isolierten Vertragsregressionen, nicht als mitgelieferter produktiver Controller.

`multi_contract.py` von Airfryer Recipes bereitet exakte Dienstparameter vor und prüft die Werte der Rückantwort. Die Vorschau erkennt nur die zwei geprüften Versionen sowie Sperrgründe des aktuellen Berichts. Das schaltet keine echte Übertragung frei: Eine Vorprüfung schützt nicht den späteren Aktualisierungs-/Schreibschritt des Controllers. [Prüfung und offene Lücke](../reports/ISSUE_1_CONTROLLER_103.de.md).
