# Issue #7 – Testvorschau und verbindlicher Sendevertrag

[Deutsch](ISSUE_7_COMMAND_CONTRACT.de.md) | [English](ISSUE_7_COMMAND_CONTRACT.md)

## Ergebnis

PR #17 ist gemergt. Dieses Folgepaket ergänzt `airfryer_recipes/prepare_send` als ausschließlich serverseitige Testvorschau für Administratoren. Sie validiert ein gewünschtes Programm, Celsius-Temperatur und Minuten gegen die geräteunabhängigen Rezeptgrenzen, liest das Ziel erneut aus der lesenden Erkennung und liefert Werte und Sperrgründe. Es gibt keinen Steueraufruf, keine Warteschlange und keine Umschaltung auf Live-Betrieb. Das ist eine erste Koordinatorstufe; Issue #7 ist damit weiterhin nicht vollständig umgesetzt.

Modellprüfung: Die Empfehlung GPT-6 Sol – High wurde vor diesem Folgepaket ausgesprochen, die Arbeit unterbrochen und anschließend vom Eigentümer fortgesetzt. Diese Stufe bleibt für die Adapter-/Async-Prüfung geeignet.

## Zusätzlicher Upstream-Befund

Geprüfte Revision bleibt [5a3c530](https://github.com/misterm2310/airfryer-control/tree/5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee). In `core/api.py` verwendet `bypass_v2()` die Methode `_with_relogin()`. Bei einem Authentifizierungsfehler meldet sie sich erneut an und führt dieselbe Anfrage nochmals aus. Auch ein Aufruf von `async_send(..., only=...)` mit fester Variante garantiert deshalb keine einmalige Übertragung. Die privaten Methoden `_post` oder die Zugangsdaten des Upstream werden nicht als Umgehung verwendet.

Zusammen mit den [vorherigen Befunden](ISSUE_7_DISCOVERY.de.md) ergibt sich: Die bestehenden öffentlichen Aktionen und der direkte API-Aufruf erfüllen den benötigten Sendevertrag nicht. Es wurde kein Fehler in der Rezeptpersistenz festgestellt. Keine fremden Repositorys wurden verändert und keine Upstream-Issues oder Nachrichten veröffentlicht.

## Benötigter Vertrag vor Live-Betrieb

Diese Anforderungen sind ein Entwurf für eine unterstützte Upstream-Schnittstelle, keine bereits verfügbaren Funktionen:

1. Ein expliziter Aufruf zum **Bereitstellen ohne Heizstart** mit exakt Modell, Fach, Programm, Celsius-Temperatur und Minuten. Keine freie Methode, keine Rohdaten, kein gemeinsames Fach 0 als Fallback und keine experimentelle Startvariante.
2. Höchstens ein Steuer-Transportversuch je bewusster Bestätigung. Eine nötige Anmeldung kann vor diesem Versuch abgeschlossen werden; nach dessen Beginn gibt es weder Variantenwechsel noch Authentifizierungs-Replay noch automatische Wiederholung. Timeout/Verbindungsabbruch nach Versand bedeutet „Ergebnis unbekannt“ und nicht „sicher fehlgeschlagen“.
3. Erfolgreicher Erfassungszeitpunkt und Revision pro Gerät/Fach, expliziter Online-/Fehlerstatus und tatsächlich gemeldete Fächer. Ein Fehler macht alte Daten nicht wieder frisch. Wiederverbindung, neue Gerätesitzung und geänderte Fähigkeiten müssen bestehende Bestätigungen ungültig machen. Ein globaler Koordinator- oder HA-Entitätszeitstempel reicht nicht.
4. Modell-/Fach-/Programmgrenzen mit nachvollziehbarer Quelle. Globale TwinFry-Konstanten dürfen keine unbestätigten CAF-DC111S-AEU-Funktionen freischalten. Keine stille Begrenzung oder Ersetzung von Werten.
5. Ein unabhängiger Geräte-Sicherheitsnachweis für Bereitstellen ohne Heizstart und Fachisolation; standardmäßig keine Änderungen an laufenden, pausierten, vorheizenden, offenen oder unbekannten Fächern. Spätere Änderungen während des Garens benötigen zusätzlich ausdrückliche Geräteunterstützung, Admin-Freigabe und erneute Bestätigung.
6. Rückmeldung unterscheidet abgelehnt, vom Adapter angenommen, am Gerät bestätigt und Ergebnis unbekannt. Ein erfolgreicher HA-Aufruf alleine darf nicht als Gerätebestätigung gelten.

Der spätere Koordinator muss zusätzlich authentifizierte Benutzer-/Geräterechte, eine begrenzte Zahl kurz gültiger Einmalbestätigungen mit Benutzer, Ziel, exakten Werten, Richtlinie und Statusrevision, erneute Prüfung unmittelbar vor Versand und Serialisierung pro physischem Gerät umsetzen. Parallel eingehende Anfragen dürfen keine Warteschlange bilden; belegte Geräte werden abgewiesen. Selbst lokale Sperren verhindern keine Zustandsänderung durch einen physischen Tastendruck oder eine andere App; die Geräteschutzmechanismen müssen erhalten bleiben. Diese Live-Funktionen werden in diesem Paket ausdrücklich noch nicht implementiert.

## Implementierte API

Authentifizierter Administrator, Integration geladen:

```json
{"id":1,"type":"airfryer_recipes/prepare_send","device_id":"HA-GERAETE-ID","zone_id":1,"settings":{"program":"airfry","temperature_c":170,"duration_minutes":8}}
```

Die Antwort enthält `mode=dry_run`, `live_send_enabled=false`, `transmitted=false`, `accepted_by_adapter=false`, `confirmed_on_device=false`, die validierten Wunschwerte und `blocking_reasons`. Ungeprüfter Vertrag, ungeprüfte Aktualität und unbekannte Programmgrenzen bleiben immer Sperrgründe. Weitere Gründe zeigen Offline-/Unknown-Verbindung und nicht bereite Fächer. Auch bei gemeldetem „bereit“ entsteht keine Sendeerlaubnis. Die Wunschwerte sind keine verifizierten Geräte-Payloads und werden weder auf unterstützte Werte angepasst noch persistiert.

Zusatzfelder wie `dry_run=false`, `live_send_enabled=true`, rohe Gerätebefehle oder ein gefälschtes `is_admin` werden abgewiesen. Normale und nicht angemeldete Benutzer erhalten keine Testvorschau; normale Bedienung mit Geräteberechtigungen folgt später. Fehlendes Gerät oder nicht gemeldetes Fach ergibt `target_not_found`; nach Entladen `not_configured`. Es gibt weiterhin keinen `confirm_send`-Befehl und keine Bestätigungstoken, die eine Übertragung freigeben könnten. Eine [nachfolgende Admin-Oberfläche](ISSUE_7_DRY_RUN_UI.de.md) macht genau diese Testvorschau auf dem Handy zugänglich.

## Prüfung und lokale Abnahme

75 Python-Offline-Tests und 10 Frontend-Tests bestanden; Kompilierung und `git diff --check` bestanden. Die zusätzlichen Tests prüfen beide Fächer, unveränderte Werte, fehlende Ziele, erneutes Lesen je Anfrage, laufende/offline/unbekannte Zustände, ungültige Werte und Zusatzfelder, vorgetäuschte Live-Fähigkeit, Berechtigungen, Entladen und null Serviceaufrufe. Ein absichtlich ausgelöster Speicherfehler im bisherigen Test erzeugt weiterhin einen erwarteten Traceback. Tests der späteren Live-Races, Einmalbestätigungen und Adaptersteuerung sind noch nicht vorhanden, weil diese Funktionen fehlen. Die PR-Actions prüfen HACS, Hassfest und Python 3.12/3.14.

Lokales HA und Gerät: **NICHT GETESTET**. Nach Backup und Installation des gesamten Integrationsordners neu starten. Mit einem Administrator zuerst `devices` lesen, dann für eine tatsächlich gemeldete HA-Geräte-ID und Fach-ID die obige Anfrage über eine authentifizierte HA-WebSocket-Verbindung senden. Erwartet werden ausschließlich Testmodus, unveränderte Wunschwerte und Sperrgründe; am Gerät darf nichts geändert werden. Mit normalem Benutzer `unauthorized` prüfen, Rezeptverwaltung weiterhin testen. Ohne Adapter gibt es kein gültiges Ziel. Diese manuelle API-Prüfung darf wie vereinbart bis zur Oberfläche warten.

## Entscheidung über das weitere Vorgehen

Dieser Abschnitt beschreibt die Entscheidung am ursprünglichen Prüfstand. Der Eigentümer hat den Entwickler anschließend kontaktiert. Airfryer Control `1.0.2-beta.1` stellt nun den angefragten öffentlichen Beta-Vertrag bereit; Einzelheiten stehen im [Ergebnis der Upstream-Abstimmung](UPSTREAM_SAFE_SEND_PROPOSAL.de.md#ergebnis-vom-25102026). PR #19 verwendet zunächst nur den lesenden Dienst `faehigkeiten`. Echte Übertragung bleibt bis zur lokalen Vertragsabnahme und zu ausreichenden modellbezogenen Nachweisen gesperrt.
