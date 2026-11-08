# SYNC/MATCH mit unserem eigenen abgesicherten Sender

[English](ISSUE_1_OWN_GUARD.md) | [Deutsch](ISSUE_1_OWN_GUARD.de.md)

**Eigentümerentscheidung, 2026-11-08:** Absicherung in Airfryer Recipes umsetzen; der Controller wird nicht geändert. In b26-Entwicklung/PR #48 implementiert. Dies ersetzt die frühere Abhängigkeit von einem Controller-Patch. Diese Änderung veröffentlicht keine neue Beta oder stabile Version. Native Abnahme steht aus.

## Verhalten

Die Zwei-Fach-Karte behält getrennte SYNC-/MATCH-Vorschauen und ergänzt außerhalb des Testmodus **SYNC bereitstellen / MATCH bereitstellen**. SYNC verwendet beide ausdrücklichen Fachentwürfe; MATCH verwendet Fach 1 für beide. Eine genaue Bestätigung listet beide Programme, Temperaturen und Zeiten. Das Backend erzwingt den Testmodus unabhängig von der UI: kein Token und kein Schreiben im Testmodus. Administratoren und normale Benutzer verwenden denselben authentifizierten Koordinator mit ganzer Gerätefreigabe.

Nach unbekanntem Ergebnis ist keine automatische Wiederholung möglich. Beide Fächer am Gerät prüfen, vorbereitete Programme dort beenden und ausdrücklich lesend neu freigeben. Weder Vorbereitung, Verwerfen noch Wiederfreigabe startet oder stoppt das Gerät. Fehler beim Speichern angenommener Einstellungen werden separat gemeldet und lösen nie erneutes Senden aus. Historien bleiben pro Fach getrennt.

## Controller bleibt unverändert

Für kombiniertes Senden unterstützt: exakt Airfryer Control **1.0.3** (`75d30c800ae79eea2254e5d4f5da31ec154398e7`) und **1.0.4-beta.1** (`ca92b375547c75b698e25a21f8a8734688174e47`). Deren vollständige `core/api.py`-Dateien sind identisch. Die Fach-Sendefunktionen `_program`/`async_send` sowie Sensor-/Entitätsquellen wurden mit der vorher geprüften beta.3 verglichen und sind unverändert; die vorhandenen Wege akzeptieren jetzt auch diese exakten Versionen. Andere Releases werden gesperrt.

Der neue Sender ruft **nicht** `sync_senden` oder `match_senden` auf, die nach einer fremden Vorprüfung intern nochmals aktualisieren. Er verwendet den geladenen Transport durch ein eigenes Delegationsobjekt pro Aufruf: Das tatsächliche `bypass_v2(..., retry=False)` verwendet seine normale Anmeldung und `_once`-Behandlung; die HTTP-Übergabe `_post` unseres Delegationsobjekts führt nach allen Anmeldewartezeiten unsere letzte Prüfung aus. Erst danach wird genau diese Anfrage dem vorhandenen Transport übergeben. Kein Attribut, keine Funktion, kein Dienst, kein Eingabeplan und keine Controller-Installation wird gepatcht oder ersetzt. Kein eigener Cloudclient, keine zusätzliche Zugangsdaten- oder Tokenspeicherung. Der Controller-Patchvorschlag wurde entfernt.

Dies ist bewusst ein eng an geprüfte Versionen gebundener Adapter für Controller-Interna, keine Kompatibilitätszusage für beliebige spätere Controller. Die native Integrationsabnahme muss die geprüften Versionen und tatsächliche Payload-Wirkung prüfen. Die Anwendung kann physische Geräteänderungen nicht einfrieren und bereits im Netzwerk befindliche Anfragen nicht zurückholen; ihre letzte Prüfung kontrolliert den neuesten bekannten HA-Bericht unmittelbar vor der Transportübergabe.

## Serverseitige Absicherung

1. Aktuelle HA-Identität und ganze Gerätefreigabe vor Rezeptauflösung oder Statusanforderung lesen. Freigabe nach Lesevorgängen und an der HTTP-Übergabe erneut prüfen. Keine Fachfreigaben oder vom Client behaupteten Administratorrechte.
2. Genau ein eindeutig zugeordnetes Registry-Gerät, geladenen Konfigurationseintrag, unveränderten Coordinator/Fryer/API und Kontoidentität, exakt CAF-DC111S-AEU und geprüfte Version verlangen. Rezepte bleiben geräteunabhängig; ihre Momentaufnahmen müssen beim Senden noch passen.
3. Lesend aktualisieren und einen erfolgreichen **neuen** Bericht nach Anforderungszeit verlangen. Beide Fächer müssen ausdrücklich vorhanden, inaktiv und bereit/aus sein. Fehlend, unbekannt, gart, pausiert, Schublade offen, vorbereitet, offline, Fehler, andere Temperatureinheit und bereits kombinierter Modus sperren. Zeitstempel mit Zeitzone, nicht zukünftig, höchstens 15 Sekunden alt; Revision gewöhnliche nichtnegative Ganzzahl.
4. Beide Phasen gegen Programm-/Modellgrenzen, gemeldete Fähigkeitenbereiche und Temperaturschritte prüfen. Kein Begrenzen oder Ersetzen.
5. Einmalbestätigung mit 15 Sekunden Gültigkeit an Benutzer, WebSocket-Lebensdauer, Gerätefreigabe, beide Phasen, Rezepte und Berichtsidentität binden. Vor Wartezeiten verbrauchen; nach Authentifizierung alles erneut prüfen. Änderungen an Zustand, Freigabe, Rezept, Konto, Laufzeit, Verbindung oder Ablauf sperren vor HTTP. Entladen und Verwerfen machen offene/laufende Bestätigungen ungültig.
6. Vorhandene gerätebezogene Busy-/Unklar-Mengen mit einzelnem Senden und Testlisten teilen. Gleichzeitige Arbeit ablehnen statt aufreihen. Unklare Ergebnisse bleiben über Integrations-Neuladen gesperrt; Wiederfreigabe verlangt ausdrückliche Bestätigung physischer Rücksetzung und frischen sicheren Zustand.
7. Festen reinen Vorbereitungs-Payload `startMultiCook` mit `readyStart: true`, geprüften App-Programmnamen, exakten Phasen, SYNC-Wartezeiten oder MATCH-Kopien und Celsius bauen; keine Timer/Rücksetzbefehle. Erwarteten Endpunkt, Gerät, Konto, Methode und Payload an der Übergabe erzwingen. Höchstens eine HTTP-Anfrage mit Gerätebefehl (normale Anmeldeanfragen können vorausgehen); fehlerhafte/Fehler-/Anmelde-/Zeitüberschreitungs-Ergebnisse wiederholen nie automatisch. Unser Adapter gibt keine rohen Fehler, Zugangsdaten oder Payloads aus und protokolliert sie nicht.

## Nachweise

**285 Python-Tests unter Python 3.12.14 und 135 Frontend-Tests bestanden.** Kompilierung, Sprach-/Dokumentationsprüfung und `git diff --check` bestanden. Python 3.14 ist in dieser Laufzeit nicht vorhanden und wurde nicht erneut geprüft. Keine GitHub Actions oder echten HA-/Cloud-/Geräte-/Mobilaufrufe. Tests verwenden nur erfundene Zugangsdaten und simuliertes HTTP.

Transporttests führen die tatsächlichen festgeschriebenen Controller-Methoden `bypass_v2`, `_once`, `_unwrap` mit unserem Delegationsobjekt und simuliertem HTTP aus. Geprüft: exaktes einmaliges Bereitstellen, fehlende/unbekannte Fächer nach Anmeldung, entzogene Rechte nach Anmeldung, Verbindungsabbruch/Entladen/Verwerfen, Ablauf, falsche Benutzerverbindung, gemeinsame Sperre, unbekannte/Anmelde-/fehlerhafte Antworten, keine Wiederholung, Historienfehler, ausdrückliche Wiederfreigabe und Verhindern einer zweiten HTTP-Anfrage. Echte Bindungslogiktests prüfen Registry-/Laufzeitidentität, neue Berichte und ein bei Aktualisierung verschwindendes Fach. Der ursprüngliche Fehlend-/Unbekannt-Fehler bleibt als separate isolierte Regression erhalten und belegt die Notwendigkeit unserer letzten Prüfung. Quellauszüge behalten die Controller-MIT-Lizenz.

## Native Abnahme vor Schließen von #1

Kandidatenstand mit geprüftem Controller 1.0.3 oder 1.0.4-beta.1 installieren und HA neu starten. Zunächst Kartentestmodus einschalten.

1. Unterschiedliche Werte in beiden Fächern wählen; SYNC-/MATCH-Vorschau prüfen. Gerät muss unverändert bleiben. Fehlendes/unbekanntes/offline Fach oder ungültige Werte müssen echtes Bereitstellen verhindern.
2. Für einen beaufsichtigten **reinen Einstellungstest** beide Fächer und kombinierten Modus am Gerät freimachen. Testmodus ausschalten, SYNC wählen, beide Werte in der Bestätigung prüfen und einmal bestätigen. Start nicht drücken. Beide gemeldeten Einstellungen/der kombinierte Modus sollen passen, ohne Heizbeginn. Vorbereitete Programme physisch beenden.
3. MATCH mit unterschiedlichen Fachentwürfen wiederholen: Beide sollen Fach 1 erhalten. Wieder physisch beenden. Dies prüft weder Temperaturgenauigkeit noch Gardauer.
4. Verworfene Bestätigung und ganze Gerätefreigabe nach Entziehen für normale Benutzer prüfen: kein Schreiben. Unabhängige Fachsteuerung, gespeicherte Historie und Fertigmeldungs-Einstellungen weiter prüfen.
5. Bei unklarem Ergebnis Gerät prüfen und vorbereitete Programme physisch beenden; erst danach ausdrücklich neu freigeben. Kein aufgereihtes oder automatisches erneutes Senden.

Tatsächliche Ergebnisse dokumentieren; Cloud-Mocks belegen keine native Gerätekompatibilität. #1 bleibt bis zu dieser gezielten Abnahme offen, **nicht** wegen einer erforderlichen Controller-Änderung.
