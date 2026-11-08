# Controller 1.0.3: SYNC-/MATCH-Nachprüfung

[English](ISSUE_1_CONTROLLER_103.md) | [Deutsch](ISSUE_1_CONTROLLER_103.de.md)

Geprüft am 2026-11-08: stabiler `v1.0.3` mit `75d30c800ae79eea2254e5d4f5da31ec154398e7` und aktueller `v1.0.4-beta.1` mit `ca92b375547c75b698e25a21f8a8734688174e47` aus `misterm2310/airfryer-control`. Dieser Bericht ersetzt die früheren beta.3-/beta.4-Vertragsbefunde an den unten genannten Stellen. Die früheren erfolgreichen SYNC-/MATCH-Aktionstests des Eigentümers bleiben gültige lokale Nachweise; hier wurden keine neuen Gerätetests durchgeführt.

## Im Controller umgesetzt

`services.py` akzeptiert jetzt `zone1`/`zone2` mit `programm`, `temperatur`, `minuten`, die MATCH-`quelle`, `einmal`, `streng` und `zuruecksetzen`. Die Aktionen unterstützen optionale strukturierte Antworten (`ok`, `ergebnis`, `gesendet`, `revision_vorher`). `sync_plans` akzeptiert explizite Werte und weist Werte außerhalb der Grenzen im strikten Modus zurück. Aufrufer müssen weiterhin explizite Quellwerte übergeben, statt auf Standard-Eingabehelfer zu vertrauen.

`async_send_sync(..., once=True, reset=False)` gibt `retry=False` an den kombinierten Schreibaufruf weiter und vermeidet Rücksetzbefehle. Der Helfer wirft bei beschäftigten Fächern jetzt `SyncBlocked` und bricht dadurch die äußere Routine ab. Der zuvor gemeldete Fehler mit früher Rückkehr ist behoben. `readyStart: true` bleibt fest im Payload. Automatisches Rücksetzen ist weiterhin Controller-Standard; eine spätere Anbindung muss daher ausdrücklich `zuruecksetzen: false`, `einmal: true`, `streng: true` und eine Antwort anfordern.

## Verbleibender reproduzierter Fehler

`_check_and_reset` sperrt offline, Mitglieder von `BUSY` sowie Mitglieder von `PREPARED` bei deaktiviertem Rücksetzen. Die Funktion verlangt aber nicht, dass beide Fachberichte vorhanden und deren Zustände ausdrücklich sicher sind. `_zone_status` liefert bei fehlendem Fach `None`; ein unbekannter Zustand gehört ebenfalls zu keiner der beiden Mengen. Beide Fälle verlassen die Prüfung normal und erlauben `startMultiCook`.

Eine vorherige Bereitschaftsprüfung in Airfryer Recipes schließt diese Lücke nicht: Der Controller aktualisiert innerhalb seiner Aktion erneut und kann dabei einen anderen oder unvollständigen Bericht erhalten. Keine private API-Umgehung, kein Monkey-Patching und keine echte Freischaltung ergänzt.

## Offline-Experiment und Ergebnisse

Aus jeder festgeschriebenen `senden.py` wurden die tatsächlichen Funktions-/Klassen-ASTs ausgeführt: `build_sync_payload`, `_zone_status`, `SyncBlocked`, `_check_and_reset`, `async_send_sync`. Externe Coordinator-/API-Objekte wurden simuliert, Typannotationen verzögert. BUSY/PREPARED verwendeten die passenden Controller-Zustandszeichenfolgen. Explizite Pläne wurden übergeben; `once=True`, `reset=False`. Beide Aktualisierungsmethoden und der API-Schreibaufruf waren `AsyncMock`: **kein Geräte-, Cloud- oder Netzwerkaufruf**.

| Fall nach simuliertem Aktualisieren | 1.0.3 | 1.0.4-beta.1 |
| --- | --- | --- |
| Beide Fächer bereit | Ein simulierter Schreibaufruf; retry false; readyStart true | Gleich |
| Fach 1 gart | Gesperrt, null Schreibaufrufe | Gleich |
| Fach 1 vorbereitet | Gesperrt, null Schreibaufrufe | Gleich |
| Offline | Gesperrt, null Schreibaufrufe | Gleich |
| Fach 2 fehlt | **Ein simulierter Schreibaufruf** | **Ein simulierter Schreibaufruf** |
| Fach 1 unbekannt | **Ein simulierter Schreibaufruf** | **Ein simulierter Schreibaufruf** |

Dies sind zwölf isolierte Vertragsfälle, nicht die Projekttestsuite oder eine echte HA-Integrations-/Geräteabnahme. Für diese reine Dokumentationsprüfung wurde keine vollständige Suite wiederholt. Keine GitHub Actions gestartet.

## Gezielt benötigte Korrektur

Nach dem Aktualisieren sperren, solange nicht **beide** Fächer vorhanden und ausdrücklich in einem erlaubten inaktiven Zustand sind. Fehlende/unbekannte Zustände müssen vor jedem Rücksetzen/Schreiben `SyncBlocked` auslösen. An dieser Stelle zusätzlich online, fehlende Berichtsfehler und frische erfolgreiche Berichtsmetadaten prüfen. Die Prüfung vor dem kombinierten Schreiben beibehalten, auch nach einem erlaubten Rücksetzen. Regressionen für ein nach Aktualisierung fehlendes Fach und einen unbekannten Fachzustand ergänzen; beide müssen null `bypass_v2`-Aufrufe ergeben.

Minimale Reproduktion in der bestehenden Controller-Testumgebung: Coordinator simulieren, dessen `async_refresh` normal zurückkehrt, und ein Gerät mit `online=True`, `state.zones={1: SimpleNamespace(status="bereit")}` und simuliertem `api.bypass_v2` verwenden. `async_send_sync` mit zwei expliziten gültigen Plänen, `once=True`, `reset=False` aufrufen: Aktuell wird `bypass_v2` einmal aufgerufen. Mit beiden vorhandenen Fächern und Fach-1-Zustand `"unbekannt"` wiederholen; gleiches Ergebnis. Erwartet: `SyncBlocked` und null Schreibaufrufe.

Issue #1 und echte kombinierte Übertragung bleiben bis zur Korrektur, Nachprüfung und gezielten nativen Abnahme offen. Vorhandenes Senden pro Fach und Vorschau bleiben unverändert. Controller 1.0.3/1.0.4 wurde nicht allein wegen der neuen API in unsere Live-Versionsfreigabe aufgenommen.
