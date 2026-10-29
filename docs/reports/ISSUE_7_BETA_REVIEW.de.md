# Issue #7 – Erneute Prüfung des Beta-Sendevertrags

[Deutsch](ISSUE_7_BETA_REVIEW.de.md) | [English](ISSUE_7_BETA_REVIEW.md)

Stand: 30.10.2026. Modellprüfung: GPT-6.1 Sol – hoch, vom Eigentümer bestätigt; Adapter-/Async- und Sicherheitsprüfung. Reine Quellcodeprüfung, keine Geräteaufrufe oder Upstream-Änderungen.

## Ergebnis

**Keine Freigabe für echte Übertragung.** Airfryer Control `beta` steht weiterhin auf [`f43a9bf8`](https://github.com/misterm2310/airfryer-control/tree/f43a9bf8ddb7cc65e27897dd92158cc06840bc08) (`1.0.2-beta.1`), `main` auf `5a3c530d`. Der Vertrag ist gegenüber der letzten Prüfung unverändert. Unsere Testvorschau bleibt serverseitig gesperrt; aus einem Beta-Dienst entsteht keine automatische Sendeerlaubnis.

## Quellcodebefunde

- `services.py::_program` bietet die öffentlichen Parameter `variante`, `einmal`, `streng` und `bestaetigen`. Der reguläre Programmdienst übergibt `allow_start=False`. `variante` muss explizit auf eine für Modell/Fach verifizierte Variante begrenzt werden; `einmal=true` allein wählt sonst nur die erste beziehungsweise gemerkte Variante. Die vorhandene Zone-0-Variante wird für unsere Anbindung nicht freigegeben.
- `senden.py::async_send(once=True)` begrenzt auf einen Variantenversuch und übergibt `retry=False`. `core/api.py::bypass_v2` benutzt dann `_once` statt `_with_relogin`. Ein nötiger Login ist vor dem Transport möglich, eine Authentifizierungswiederholung desselben Steuerbefehls ist in diesem Pfad nicht vorgesehen. Verbindungsfehler werden als unbekanntes Ergebnis behandelt. Das ist ein Quellcodenachweis, kein Geräte- oder Transporttest.
- `streng=true` verhindert stilles Begrenzen, prüft jedoch die allgemeinen Programmgrenzen. `faehigkeiten.py` kennt nur die TwinFry-Präfixe CAF-TF101S/CAF-TF102S; als bestätigtes Sendeprogramm ist nur TwinFry `airfry` eingetragen. Für CAF-DC111S-AEU bleiben Programme und Grenzen geschätzt/ungeprüft. `proof` ist weiterhin nicht durch diesen Vertrag abgedeckt.
- `coordinator.py` aktualisiert `last_report` nach erfolgreicher Geräteabfrage und `revision` bei geänderten Rohdaten bzw. Offline-Übergang. Diese Angaben gelten je Gerät, nicht als eigener Aktualitätsnachweis je Fach. Revisionsgleichheit beweist weder eine neue erfolgreiche Abfrage noch eine unveränderte Sitzung oder Fähigkeiten. Ein einzelner Fehler-/Verbindungsstatus und tatsächlich gemeldete Fächer müssen zusätzlich geprüft werden.
- `services.py::_confirm` prüft nach `async_refresh()` nur `fryer.online`, passende Werte und Bereitschaft **oder Aktivität**. Es verlangt weder eine fortgeschrittene Meldungszeit noch `connection == ok` oder einen erfolgreichen neuen Fachbericht. Bei erhaltenem Cache nach einer fehlgeschlagenen Abfrage können passende Altwerte deshalb als `bestaetigt=true` gelten. Das Feld allein beweist für unsere Anforderungen weder frische Gerätebestätigung noch ausbleibenden Heizstart.
- Der Programmdienst enthält keine für unsere Anwendung ausreichende Sperre für laufende/unklare Fächer, Einmalbestätigung oder Serialisierung. Diese Prüfungen gehören in unseren späteren Koordinator. `readyStart=true` im Payload ersetzt keinen lokalen Nachweis für CAF-DC111S-AEU.

## Nächstes abgegrenztes Paket

1. Zuerst belastbare modell-/fachbezogene Programmdaten, Grenzen und eine sichere Bereitstellvariante für CAF-DC111S-AEU belegen; `proof` ausdrücklich klären. Bis dahin keine Live-Bedienung hinzufügen.
2. Aktualität und Sitzung nachweisen; Bestätigung nur mit neuer erfolgreicher Meldung, gemeldetem Fach, passenden Werten und nicht heizendem Zustand. Upstream-`bestaetigt` nicht ungeprüft übernehmen. Diese Anforderungen können über eine unterstützte Schnittstelle oder unabhängig nachweisbare lesende Zustände erfüllt werden; private API-/Cloud-Zugriffe sind keine Ausweichlösung.
3. Erst danach Koordinator mit Benutzer-/Geräterechten, kurzlebiger gebundener Einmalbestätigung, erneuter Prüfung unmittelbar vor dem Senden und geräteweiser Sperre ohne Warteschlange umsetzen. Offline, unbekannte, veraltete oder aktive Fächer sperren; keine automatische Wiederholung.
4. Simulierte Fehler-, Race- und Null-Steueraufruf-Tests lokal durchführen; umfassende CI einmal am Abschnittsende. Reale Abnahme ausschließlich beim Eigentümer nach gesonderter implementierter Testanleitung.

## Prüfung und Grenzen

Die genannten Quelldateien wurden am festen Beta-Commit gelesen und mit unserem `command_preview.py` verglichen. Keine neue Funktion implementiert, kein Airfryer oder Home Assistant kontaktiert. Lokale Geräteabnahme und Transportverhalten: **NICHT GETESTET**. Vorhandene Handy-Abnahme von 0.1.0b2 bleibt gültig für die Testvorschau, nicht für Live-Senden. Dieser Bericht ersetzt die älteren Modellempfehlungen nicht rückwirkend; die aktuelle GPT-6.1-Sol-Regel steht in AGENTS.md.

## Actions-Budget und lokale Prüfungen dieses Pakets

Die neue Budgetregel ist in AGENTS, Anforderungen und Roadmap zweisprachig festgehalten. Automatische PR-Tests verwenden nur Python 3.12; die vollständige 3.12/3.14-Matrix ist manuell über `full_suite=true` abrufbar. Frontend-Tests laufen nur einmal. HACS/Hassfest werden automatisch auf relevante Metadaten-/Workflow-Änderungen begrenzt und bleiben manuell verfügbar. Reine Dokumentation und der anschließende Merge starten keine Code-Prüfungen. Überholte Läufe werden abgebrochen, Jobs auf zehn Minuten begrenzt.

Lokal auf Python 3.12.14 bestanden: 78 Python-Tests, der Frontend-Testbefehl `node --test tests/test_panel.mjs`, YAML-Parsing und Prüfung der Workflow-Trigger, Pfadfilter, Zeitlimits und Nebenläufigkeit sowie `git diff --check`. Der Speicherfehler-Traceback stammt aus einem erwarteten Negativtest. Keine lokale Python-3.14-, Hassfest- oder HACS-Prüfung ausgeführt; GitHub-Ausführung der neuen Workflow-Logik steht vor Veröffentlichung des PR noch aus. Dieses abgeschlossene Paket erhält einen regulären PR-Prüflauf, keinen zusätzlich gestarteten vollständigen Matrix-Lauf.
