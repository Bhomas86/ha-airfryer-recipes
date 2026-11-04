# Wiederanlauf ohne Home-Assistant-Neustart

[Deutsch](ISSUE_7_MANUAL_RECOVERY.de.md) | [English](ISSUE_7_MANUAL_RECOVERY.md)

## Befund und Umfang

Der Eigentümer meldet für v0.1.0b6 einen Stopp nach zwei bestätigten Schritten, vermutlich beim Wechsel von Airfry zu Roast auf Fach 1. Ein erforderliches Zurücksetzen der vorbereiteten Programme ist plausibel, aber aus der bisherigen generischen Meldung nicht belegt. Der Screenshot bestätigt zwei Rückmeldungen; er bestätigt keine vollständige Folge. Der Eigentümer verlangt ausdrücklich einen manuellen neuen Versuch ohne HA-Neustart, bleibt am Gerät und kann eingreifen.

v0.1.0b7 ergänzt **„Gerät geprüft – neuen Test freigeben“**. Zuerst alle vorbereiteten Programme am Gerät abbrechen und beide Fächer auf bereit/aus bringen. Danach diesen Knopf und den Hinweis bestätigen. Es wird nur ein neuer Status gelesen, kein Reset-, Stop-, Start- oder Einstellungsbefehl gesendet. Nach einer passenden frischen Meldung werden alte Einmalbestätigungen verworfen und die lokale Testsperre für dieses Gerät aufgehoben. Anschließend eine neue Liste anzeigen und einmal starten. Keine Wiederholung eines alten Schritts, keine Fortsetzung alter Tokens.

Die Wiederfreigabe prüft aktuelle Adminrechte, unveränderte Adapter-/Gerätezuordnung, beide ruhenden Fächer, Celsius und SYNC/MATCH aus. Laufende Anfragen oder ein aktiver Lauf sperren. Alte Listen werden zuerst gestoppt; bereits laufende Übertragung kann nicht zurückgeholt werden, und solange sie noch läuft wird nicht freigegeben. Bei fehlender, veralteter, aktiver oder noch vorbereiteter Fachmeldung bleibt die Sperre erhalten. Die neue Freigabe ersetzt für beaufsichtigte neue Versuche die frühere HA-Neustartpflicht. Sie beweist nicht, dass ein zuvor unklarer Befehl nie angekommen ist; der Eigentümer klärt den Zustand am Gerät.

## Abbruchgrund

Eine ausdrücklich als abgelehnt gemeldete Adapterantwort erscheint getrennt von einem unklaren Transportergebnis. Nur ein numerischer Fehlercode wird übernommen; Rohdaten, Kontokennungen und freie Fehlermeldungen werden verworfen. Im Testlauf stehen Schrittnummer, Programm, Fach und gegebenenfalls Code. Auch bei anderen Abbrüchen zeigt die Oberfläche den betroffenen Schritt. Nach einer Ablehnung wird kein nächster Befehl gesendet. Ob ein Geräte-Reset zwischen Programmen erforderlich ist, bleibt lokal zu klären; diese Version führt ihn nicht automatisch aus.

## Prüfung und erneuter Gerätetest

138 Python-Tests und 31 Frontend-Tests bestanden lokal, ebenso Kompilierung und git diff --check. Neue Tests prüfen Freigabe ohne Steueraufruf, alte Tokens, fehlende Zustimmung, aktuelle Rechte, noch laufende Anfragen, aktive Läufe, fehlgeschlagene Zustandsprüfung und genaue Ablehnung in Schritt 3. Keine GitHub Actions, HACS/Hassfest, Python 3.14 oder echte HA-/Gerätetests für diese Änderung.

Nach Backup v0.1.0b7 installieren, HA für das Update einmal neu starten und die Companion-App vollständig neu öffnen. Airfryer Control bleibt exakt 1.0.2-beta.1. Für spätere Wiederholungen ist kein weiterer HA-Neustart nötig: Programme am Gerät abbrechen, Gerät prüfen/freigeben, neue Liste anzeigen und einmal starten. Am leeren Gerät bleiben und nicht Start drücken. Bei erneutem Stopp bitte vollständige angezeigte Schrittmeldung und Code nennen. Bei Heizstart oder falschem Fach am Gerät unterbrechen. Abnahme der Wiederfreigabe und Ursache des dritten Schritts: NICHT GETESTET / UNGEKLÄRT.
