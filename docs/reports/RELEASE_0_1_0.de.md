# Abschließende Releasebedingungen — 0.1.0

[English](RELEASE_0_1_0.md) | [Deutsch](RELEASE_0_1_0.de.md)

Eigentümerauftrag vom 2026-11-09 erlaubt ausdrücklich PR #49 zusammenzuführen, abschließende Actions zu starten und anschließend den neuen Release-PR zusammenzuführen sowie stabile 0.1.0 zu veröffentlichen — **nur nach erfolgreichen Prüfungen**. Dies hebt die frühere Actions-Pause für dieses Releasepaket auf; keine wiederholte Merge-/Veröffentlichungsfreigabe erforderlich. Die Download-Dateinamenkorrektur akzeptiert der Eigentümer ohne weiteren nativen Handytest. PR #49 wurde vor Erstellung dieses Releasezweigs zusammengeführt.

## Prüffähiger finaler Umfang

Der Releasezweig setzt Manifest-/Frontend-/Cacheversionen auf 0.1.0, ersetzt Beta-Wortlaut der normalen Karte durch reines Bereitstellen/manuellen Start und fasst veraltete Beta-READMEs zu aktuellen zweisprachigen Einrichtungs-/Supportanleitungen zusammen. Stabile DE/EN-Release-Notes und die ausdrückliche Freigabe werden festgehalten. Keine Änderung von Steuer-, Rechte-, Speicher-, Diagnose- oder Benachrichtigungsalgorithmen; keine Schemamigration.

Funktionale Eigentümerabnahme siehe [b26-Abnahme](B26_ACCEPTANCE_AND_DOWNLOAD.de.md). Unser Umfang mit einem Gerät und expliziten Controller-Versionen, gekoppelten Transport-Interna, konservativen Zustandsprüfungen, manuellem Start und ohne Wiederholung/allgemeine Modellfreigabe bleibt erhalten. Keine echten Geräte-/Cloud-/Handytests durch CI behauptet.

## Erforderliche Prüfungen und Nachweise

Einen Release-PR mit `[full-ci]` im Titel und Commit ohne Skip-CI erstellen. Geändertes Manifest löst HACS/Hassfest aus; Frontend-/Versionsänderungen lösen die vollständige Python-3.12-/3.14-Matrix und Frontend-Tests aus. So wird derselbe Code nicht vor/nach Merge doppelt vollständig geprüft. Alle Jobergebnisse kontrollieren und Lauf-URLs samt exakt geprüftem PR-Kopf in PR-Beschreibung und GitHub-Release festhalten.

Bei fehlgeschlagener erforderlicher Prüfung weder zusammenführen noch veröffentlichen. Relevante Fehler in diesem Zweig korrigieren, die für den geänderten Stand erforderlichen Prüfungen wiederholen und Erfolg abwarten. Keine sachfremden Workflowänderungen oder Umgehung fehlgeschlagener Prüfungen.

Nach grünen Ergebnissen PR-Kopf erneut lesen und mit erwarteter SHA zusammenführen. Prüfen, dass der neue main-Commit denselben Dateibaum wie der geprüfte PR-Kopf hat. Tag `v0.1.0` an diesen main-Commit setzen. Zweisprachigen stabilen Release (`prerelease: false`) vorbereiten und Tag, Manifestversion sowie Dateibaum vor Veröffentlichung prüfen. Alle älteren Tags/Commits/Assets erhalten. Erst nach verifizierter stabiler Veröffentlichung die aktuell veröffentlichte Beta auf Entwurf setzen, damit HACS stabile 0.1.0 als aktuellen Release anbietet. Abschließend Release-Liste und Issue-/PR-Zustände prüfen.

#10 nach erforderlicher Validierung und stabiler Veröffentlichung schließen. #1 ist nach Eigentümerabnahme bereits abgeschlossen; kein neuer Gerätetest verlangt. Historische Berichte behalten ihre ursprünglichen Nachweisgrenzen, einschließlich nicht verfügbarer zwischenzeitlicher 3.14-Läufe und des ersetzten Controller-Patchvorschlags.
