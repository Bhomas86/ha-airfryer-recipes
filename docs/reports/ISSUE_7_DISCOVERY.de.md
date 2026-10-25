# Issue #7 – Lesende Geräteerkennung und Prüfung des Sendevertrags

[Deutsch](ISSUE_7_DISCOVERY.de.md) | [English](ISSUE_7_DISCOVERY.md)

## Ergebnis und Umfang

> **Historischer Prüfstand:** Die Befunde unten gelten für Airfryer Control 1.0.1 am genannten Commit. Der Entwickler hat danach `1.0.2-beta.1` mit einem öffentlichen Beta-Vertrag veröffentlicht. Der [Abstimmungsbericht](UPSTREAM_SAFE_SEND_PROPOSAL.de.md#ergebnis-vom-25102026) und die [aktuelle Testoberfläche](ISSUE_7_DRY_RUN_UI.de.md) beschreiben den Folgestand.

PR #16 hat Speicherung, API und manuell abgenommene Rezeptverwaltung nach `main` übernommen (`2ab457f`). Dieses erste Teilpaket zu Issue #7 ergänzt ausschließlich lesende Geräteerkennung über `airfryer_recipes/devices`. Issue #7 bleibt offen. Befehlskoordinator, Testmodus-Vorschau, echte Übertragung und Programmauswahl sind weiterhin nicht implementiert.

Modellprüfung: GPT-6 Sol – High für die mehrteilige Adapter-/Sicherheitsprüfung; nach der Empfehlung wurde die Arbeit für den Modellwechsel unterbrochen und vom Eigentümer fortgesetzt. Eine höhere Modellstufe ist derzeit nicht erforderlich.

## Sicherheitsrelevante Upstream-Befunde

Geprüfte Quelle: [Airfryer Control, Commit 5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee](https://github.com/misterm2310/airfryer-control/tree/5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee), Manifestversion 1.0.1. Es wurde ausschließlich Quellcode von GitHub gelesen; keine Upstream-Funktion wurde importiert oder ausgeführt.

1. `services.py::_program` ruft `senden.py::async_send` auf. Dieser probiert bei Ablehnungen mehrere Schreibweisen aus, einschließlich einer Variante mit `workChamber=0`. Ein einziger HA-Serviceaufruf garantiert somit keinen einzelnen Geräte-Steueraufruf. Das widerspricht der Projektregel gegen automatische Wiederholungen. Dieser Service wird nicht angebunden.
2. `FryerData` hat keinen erfolgreichen Meldungszeitstempel je Gerät/Fach. Ein global erfolgreicher Koordinator-Refresh kann einzelne Gerätefehler überdecken; Fehlerpfade können alte Zustände beibehalten. HA-Entitätszeitstempel beweisen deshalb keine frische Gerätemeldung.
3. `sensor.py::ZONE_SENSORS` liefert für ein nicht gemeldetes Fach den Ersatzwert „bereit“. Dieser Wert darf keine Sendeerlaubnis begründen. Unsere Erkennung verwendet nur tatsächlich vorhandene Laufzeit-Fachmeldungen.
4. `const.py` enthält globale TwinFry-Programme und Grenzen, keine verifizierte Liste für jedes Modell. Sie werden nicht als bestätigte CAF-DC111S-AEU-Fähigkeiten übernommen.

Der Upstream dokumentiert `readyStart=true` als Bereitstellen und `false` als sofortigen Start bei einer TwinFry. Diese Quellcodeaussage ersetzt keinen lokalen Sicherheitsnachweis für alle Modelle. SYNC/MATCH, Rohbefehle und experimentelle Sendefunktionen bleiben außerhalb dieses Teilpakets.

## Implementierung

- Gerätezuordnung anhand HA-Geräteregistry, passender Konfigurationseinträge und geladener Airfryer-Control-Laufzeitdaten; keine Abfrage bei VeSync und kein erzwungener Refresh.
- Nur explizit gemeldete Fächer; unbekannte Zustände bleiben unbekannt. Offline- und fehlerhafte Daten werden nicht als sicher bereit dargestellt.
- Antwort: HA-Geräte-ID, Name, Modell, gemeldete Verbindung, Fachzustände, `freshness=unverified`, `reported_at=null`, leere Programmliste und deaktivierte Steuerfähigkeiten. „Gemeldet online“ bedeutet keine bestätigte aktuelle Verbindung.
- Cloud-Kennungen, Zugangsdaten, Rohdaten und Fehlertexte werden nicht ausgegeben. Die authentifizierte API ist kein Diagnoseexport.
- Discovery ist vorerst nur für Administratoren verfügbar. Normale Benutzer erhalten keinen Zugriff, auch mit gefälschtem `is_admin`. Gerätebezogene Rechte für die spätere normale Bedienung sind noch umzusetzen.
- Der Aufruf wird bei entladener Rezeptintegration abgewiesen. Fehlende oder inkompatible optionale Adapter verhindern die Rezeptverwaltung nicht. Keine neuen Speicherdateien oder Migrationen.
- Keine Sende-API und keine Gerätesteuerungsaufrufe. Das ist noch keine Umsetzung des geplanten serverseitigen Testmodus.

## Tatsächlich ausgeführte Prüfungen

68 Python-Offline-Tests und 10 Frontend-Tests bestanden. Die neuen Tests prüfen beide Fächer, fehlende Fachmeldungen, unbekannte Modelle/Zustände, Offline-/Fehlerdaten, mehrdeutige Zuordnung, deaktivierte Geräte, inkompatible Laufzeitdaten, Datenminimierung und API-Berechtigungen einschließlich Entladen. Der vorhandene Speicherfehler-Traceback ist ein erwarteter Negativtest. Python-Kompilierung und `git diff --check` werden vor Veröffentlichung geprüft; HACS, Hassfest und Python 3.12/3.14 über die PR-Actions.

Lokales Home Assistant: **NICHT GETESTET** für diese neue API. Die frühere Abnahme der Rezeptverwaltung gilt weiterhin nur für den geprüften Stand aus Issue #6.

## Lokale Abnahme und nächste Entscheidung

Nach Backup den gesamten Integrationsordner aus diesem Feature-Branch installieren und HA neu starten. Rezeptverwaltung ohne Airfryer Control erneut öffnen. Ein Administrator kann über eine authentifizierte HA-WebSocket-Verbindung `{"id":1,"type":"airfryer_recipes/devices"}` lesen; ohne Adapter wird eine leere Liste erwartet. Mit Adapter Modell/Fächer gegen dessen Anzeige vergleichen. Bei ausgeschaltetem Gerät darf auch ein alter gemeldeter Zustand keine Sendeerlaubnis erzeugen. Ein normaler Benutzer muss `unauthorized` erhalten. Eine [nachfolgende Admin-Oberfläche](ISSUE_7_DRY_RUN_UI.de.md) macht Geräteerkennung und Testvorschau auf dem Handy zugänglich. Keine Gerätebefehle für dieses Teilpaket ausführen.

Vor echter Übertragung ist ein überprüfbarer Adaptervertrag nötig: genau ein Steueraufruf ohne Varianten-Fallback, verlässliche erfolgreiche Meldungszeitpunkte je Gerät/Fach, bestätigte modellbezogene Programme/Grenzen und nachgewiesenes Bereitstellen ohne Heizstart. Danach folgen Koordinator, Benutzer-/Geräterechte, gebundene Einmalbestätigungen, Race-Condition-Tests und serverseitiger Testmodus. Empfehlung für dieses Folgepaket: GPT-6 Sol – High; vorher wie vereinbart pausieren.
