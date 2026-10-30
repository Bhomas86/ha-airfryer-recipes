# Issue #7 – Schnittstelle für beaufsichtigte Beta-Gerätetests

[Deutsch](ISSUE_7_BETA_SEND.de.md) | [English](ISSUE_7_BETA_SEND.md)

Stand: 30.10.2026. Modellprüfung: GPT-6.1 Sol – hoch, vom Eigentümer bestätigt.

## Umfang und Entscheidung

Der Eigentümer hat die Implementierung vor der realen Geräteabnahme und eine neue Test-Beta beauftragt. `0.1.0b3` ergänzt deshalb einen separaten, ausdrücklich bestätigten Ersttest bei weiterhin ungeprüfter Kompatibilität. Dies ersetzt für diesen Test die frühere Vorgabe, vor jeder Implementierung bereits reale Nachweise zu verlangen. Allgemeine Gerätesteuerung bleibt gesperrt; aus geschätzten Fähigkeiten entsteht keine allgemeine Sendeerlaubnis. Die vorhandene `prepare_send`-Testvorschau bleibt unverändert ohne Steueraufrufe.

Die einzige erlaubte Testkonfiguration lautet CAF-DC111S-AEU, Fach 1 oder 2, `airfry`, 170 °C, eine Minute. Nur Airfryer Control 1.0.2-beta.1 ist zugelassen. Der öffentliche Dienst `programm_senden` wird mit `variante=multi_app`, `einmal=true`, `streng=true`, `bestaetigen=false` aufgerufen. Startfähige Varianten, Zone 0/3, Raw, SYNC und MATCH sind nicht erreichbar.

## Backend und Oberfläche

`beta_send.py` kapselt die Testübertragung. `beta_prepare` und `beta_confirm` sind adminpflichtige WebSocket-Befehle. Aktuelle aktive Adminrechte werden zusätzlich aus HA gelesen, der Dienst erhält den serverseitigen Benutzerkontext. Ziel und Einstellungen kommen beim Bestätigen ausschließlich aus dem serverseitigen Token; Zusatzfelder werden abgelehnt.

Beide echten Fächer und ein bereit/aus gemeldeter Gesamtzustand sind erforderlich; aktive, vorbereitete, unbekannte und nicht gemeldete Fächer werden abgelehnt. SYNC/MATCH muss explizit 0 und die Temperatureinheit Celsius sein. Fähigkeitsdienst und Laufzeit müssen denselben maximal 15 Sekunden alten erfolgreichen Bericht und dieselbe Revision liefern. Ein neuer Bericht invalidiert die Bestätigung auch bei gleichen Werten. Zusätzlich werden Adapterinstanz, Fachzustände und Programmbereiche gebunden. Nach der letzten asynchronen Rechteprüfung wird der Zustand nochmals synchron geprüft. Geräte-/Fachzustände werden ausschließlich gelesen; keine privaten Upstream-Steuermethoden und keine eigenen Cloud-Zugangsdaten.

Tokens gelten 15 Sekunden, sind benutzergebunden und einmalig; maximal 32 sind offen, je Benutzer nur der neueste. Verbrauch erfolgt vor der erneuten Prüfung. Pro Gerät gibt es eine sofortige Sperre ohne Warteschlange. Laufende Dienstaufrufe und die Sperre bei unklarem Ergebnis bleiben über ein Integrations-Neuladen erhalten. Nach einem Fehler oder einer unvollständigen Antwort gibt es keine Wiederholung; weitere Tests für das Gerät sind bis zum HA-Neustart gesperrt. Tokens werden beim Entladen verworfen; noch nicht begonnene Übertragungen werden verhindert. Bereits abgesendete Befehle lassen sich durch Entladen nicht zurückholen.

Die Oberfläche trennt „Echten Gerätetest vorbereiten“ von „Einmalig ans Gerät senden“, nennt Gerät/Fach und exakte Werte und verlangt einen zusätzlichen Dialog vor dem echten Versuch. Ein verlorenes Ergebnis verbraucht den sichtbaren Token und zeigt „Ergebnis unklar“. Nur eine vollständig passende Dienstantwort gilt als Adapterannahme; `confirmed_on_device` und `compatibility_verified` bleiben immer `false`. Rezeptbibliothek und Import/Export werden nicht verändert.

Die WebSocket-Schemata verwenden nun das von HA bereitgestellte `voluptuous`; der bisherige nicht deklarierte `probatio`-Import wurde auch im Teststub korrigiert. Das Panel-Modul erhält eine Versionskennung gegen alten Modulcache.

## Automatische Prüfung

Lokal bestanden: 101 Python-Tests unter Python 3.12.14, 20 Frontend-Tests mit `node tests/test_panel.mjs`, Python-Kompilierung und `git diff --check`. Neue Tests decken echte Null-Steueraufrufe bei Vorbereitung/Sperren, beide Fächer, Zeit-/Versions-/Modellgrenzen, Adminverlust, Zustandssprünge, Tokenverbrauch/-ablauf, Gleichzeitigkeit, Abbruch und Neuladen sowie unbekannte Antworten ab. Die bestehende Speicherfehler-Ausgabe ist ein erwarteter Negativtest. Eine Prüfung der nativen HA-Schemata in einer vollständigen HA-Laufzeit war lokal nicht verfügbar; die API-Tests verwenden HA-Stubs.

Für diesen abgeschlossenen Abschnitt wird genau ein PR-Lauf mit `[full-ci]` für Python 3.12/3.14, einmalige Frontend-Tests, HACS und Hassfest angefordert. Keine zusätzlichen Zwischenläufe oder erneute Tests unveränderter Stände. Die neue Kennzeichnung ist in AGENTS dokumentiert.

## Lokale Geräteabnahme

Vorher Backup; Airfryer Control exakt 1.0.2-beta.1 und Airfryer Recipes v0.1.0b3 installieren, HA neu starten, App vollständig neu öffnen. Nur beaufsichtigt am leeren Gerät testen. Die Fähigkeiten bleiben als geschätzt/ungeprüft gekennzeichnet.

1. Rezeptverwaltung öffnen. Zuerst die bisherige Geräte-Testvorschau prüfen: ausdrücklich nichts übertragen, am Gerät keine Änderung.
2. Beide Fächer am Gerät in bereit/aus versetzen, vorbereitete Programme abbrechen, Celsius wählen und SYNC/MATCH deaktivieren. Nicht auf Start drücken. In der Geräteauswahl die Cosori und Fach 1 wählen.
3. Im separaten Bereich „Beaufsichtigter Beta-Gerätetest“ den echten Test vorbereiten und den Hinweis bestätigen. Bei einer Aktualitätssperre einen neuen erfolgreichen Airfryer-Control-Bericht abwarten und zügig erneut vorbereiten. Die bloße Geräteabfrage erzwingt keine neue Cloud-Meldung.
4. Gerät, Fach 1, Airfry, 170 °C und eine Minute in der Bestätigung prüfen. Nur wenn diese Angaben stimmen, innerhalb von 15 Sekunden „Einmalig ans Gerät senden“ wählen und bestätigen. Bei zwischenzeitlicher Meldung/Zustandsänderung wird ohne Steuerbefehl abgebrochen; neu vorbereiten.
5. Bei Adapterannahme direkt am Gerät kontrollieren: richtiges Fach, Airfry, 170 °C, eine Minute; anderes Fach unverändert; **kein Heizen**, manueller Start weiterhin erforderlich. Nicht auf Start drücken. Nur der Eigentümer kann diese Punkte als BESTANDEN bestätigen.
6. Das vorbereitete Programm am Gerät abbrechen. Beide Fächer wieder bereit/aus und einen neuen Bericht abwarten. Danach denselben Test für Fach 2 durchführen; Fach 1 muss unverändert bleiben.
7. Bei unklarem Ergebnis nicht erneut senden. Zustand am Gerät prüfen und Test beenden. Ein vollständiger HA-Neustart entfernt die lokale Unklarheitssperre, ist aber kein Nachweis, dass ein vorheriger Befehl nicht ankam. Erst nach geklärtem Gerätezustand und beendeten alten Anfragen erneut testen. Bei Heizstart oder Änderung des falschen Fachs am Gerät stoppen und keine weiteren Versuche ausführen.
8. Normale Benutzer dürfen Testbereich und Befehle nicht benutzen. Rezeptverwaltung, Favoriten und Import/Export anschließend prüfen. Falls nötig auf v0.1.0b2 zurückgehen und HA neu starten; das Rezeptformat wurde nicht geändert.

Rückmeldung je Fach: **BESTANDEN / FEHLGESCHLAGEN / NICHT GETESTET**, angezeigtes Ergebnis, Programm/Temperatur/Zeit am Gerät, anderes Fach unverändert ja/nein, Heizstart ja/nein. Bei einer Sperre den angezeigten Grund nennen. Keine Zugangsdaten, Gerätekennungen oder Rohdiagnosen veröffentlichen.

## Grenzen

Geräteabnahme: **NICHT GETESTET**. Kein Nachweis für `proof`, andere Programme, freie Werte oder Änderungen während des Garens. Pollingdaten verhindern keine Änderungen durch physische Tasten oder andere Apps zwischen Prüfung und Übertragung. Keine automatische Gerätebestätigung; ein akzeptierter Cloud-Befehl reicht dafür nicht. Erst nach dokumentierter lokaler Abnahme den Testumfang erweitern; Issue #7 bleibt offen.
