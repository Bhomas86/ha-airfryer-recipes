# Issue #7 – Aktualitätssperre bei der Testvorbereitung

[Deutsch](ISSUE_7_STATUS_REFRESH.de.md) | [English](ISSUE_7_STATUS_REFRESH.md)

Stand: 30.10.2026. Modellprüfung: GPT-6.1 Sol – hoch, vom Eigentümer bestätigt.

## Befund und Korrektur

Der Eigentümer meldet bei eingeschaltetem Gerät und geschlossenen, unbenutzten Fächern eine Aktualitätssperre in v0.1.0b3. Der Screenshot zeigt einen Abbruch vor jeder Sendebestätigung; es wurde kein ankommender Befehl beobachtet. Der Fehlertext umfasst sowohl ältere als auch fehlende/uneinheitliche Berichte; allein aus dem Screenshot lässt sich das genaue Alter nicht bestimmen. Der Code forderte keine Statusaktualisierung an und akzeptierte nur Berichte bis 15 Sekunden Alter. Die Bedienung hing damit vom regulären Pollingzeitpunkt ab.

Die Vorbereitung in v0.1.0b4 liest zuerst Modell, Adapterversion und Gerätezuordnung. Anschließend wählt sie einen geladenen, aktivierten Sensor desselben Airfryer-Control-Config-Entry und Geräts aus. Der öffentliche Dienst `homeassistant.update_entity` fordert mit dem serverseitigen Admin-Kontext genau einmal einen neuen Bericht an. Im geprüften Upstream f43a9bf8 erben die Sensoren von `CoordinatorEntity`; ihr Update ist eine lesende Koordinator-Abfrage. Keine privaten Steuermethoden, Button- oder Zahlenentitäten und keine zusätzlichen Cloud-Zugangsdaten werden verwendet.

Ein unveränderter alter Bericht wird auch dann abgelehnt, wenn er noch innerhalb von 15 Sekunden liegt: Seine Zeit muss nach Beginn der Abfrage liegen und neuer als die vorherige Meldung sein. Danach müssen öffentliche Fähigkeitsantwort und Laufzeit weiter übereinstimmen. Es werden keine Meldezeiten erfunden oder altersmäßig zurückgesetzt. Nach 20 Sekunden oder bei einem Fehler wird ohne automatische Wiederholung abgebrochen. Fehlender aktiver Sensor und erfolglose Aktualisierung haben eigene übersetzte Hinweise. Fehlertexte des Upstream werden nicht ausgegeben.

Die Gerätesperre umfasst jetzt auch die Vorbereitung. Parallele Anfragen werden nicht vorgemerkt. Eine neue Vorbereitung verwirft ältere Tokens desselben Benutzers auch dann, wenn die neue Abfrage scheitert. Beim finalen Bestätigen wird weiterhin ausschließlich erneut gelesen; dabei gibt es keine zweite Aktualisierung. Alle bisherigen Modell-, Fach-, Rechte-, Zustands-, Einmal- und Unklarheitssperren bleiben bestehen. Testvorschau, Rezeptdaten und feste Testwerte bleiben unverändert.

## Prüfung

Lokal bestanden: 108 Python-Tests, 21 Frontend-Tests, Python-Kompilierung und `git diff --check`. Neue Fälle prüfen erfolgreiche Erneuerung eines 90 Sekunden alten Berichts, unveränderten Cache trotz erfolgreicher Service-Rückkehr, Zeitüberschreitung, Auswahl nur geeigneter Sensoren, unveränderte Bestätigung ohne Refresh, gleichzeitige Vorbereitungen, Tokenentwertung nach fehlgeschlagener Vorbereitung und den sichtbaren Lade-/Sperrzustand. Die Tests benutzen ausschließlich simulierte Services; Vorbereitung löst keinen `programm_senden`-Aufruf aus. Die bestehende Speicherfehler-Ausgabe ist ein erwarteter Negativtest.

Am Paketende wird einmal die vollständige PR-Abnahme mit Python 3.12/3.14, Frontend, HACS und Hassfest angefordert. Keine zusätzlichen Zwischenläufe. Native HA-Laufzeit, Debouncing und echtes Polling bleiben lokal zu prüfen; eine von HA zeitversetzt vorgemerkte Abfrage kann ohne unmittelbar neuen Bericht weiterhin sicher gesperrt werden. Bei Bedarf manuell erneut vorbereiten, nicht automatisch wiederholen.

## Lokaler Test

1. v0.1.0b4 installieren, HA neu starten und die App vollständig neu öffnen. Exakt Airfryer Control 1.0.2-beta.1 beibehalten. Backup vorher erstellen.
2. Beide Fächer am Gerät bereit/aus, geschlossen und ohne Programm halten; Celsius, SYNC/MATCH aus. Am leeren Gerät bleiben, nicht Start drücken.
3. Als Admin Gerät und Fach 1 wählen und „Echten Gerätetest vorbereiten“ drücken. Erwartet: sichtbare Statusaktualisierung; bei erfolgreichem neuen Bericht erscheint die Einmalbestätigung. Während dieser Vorbereitung darf sich am Gerät nichts ändern.
4. Bei „kein aktivierter Sensor“ einen Statussensor in Airfryer Control prüfen/aktivieren. Bei „kein neuer erfolgreicher Bericht“ die Verbindung dort prüfen und den genauen Hinweis melden; nichts umgehen.
5. Nur bei richtiger Bestätigung (Fach 1, Airfry, 170 °C, eine Minute) einmalig senden und am Gerät Werte, unverändertes anderes Fach und ausbleibenden Heizstart prüfen. Nicht auf Start drücken. Bei Abweichungen oder unklarem Ausgang abbrechen. Anschließend das vorbereitete Programm am Gerät abbrechen; danach kann Fach 2 separat geprüft werden.

Rückmeldung getrennt erfassen: Vorbereitung nach Statusaktualisierung **BESTANDEN/FEHLGESCHLAGEN/NICHT GETESTET**; echte Übertragung je Fach ebenso. Der bisherige gesperrte Versuch bestätigt keine funktionierende Übertragung. Keine Rohdiagnosen, Zugangsdaten oder Kennungen teilen. Geräteabnahme der Korrektur: **NICHT GETESTET**.
