# Große Geräteabnahme – Beta 0.1.0b5

[Deutsch](BETA_0_1_0B5_TEST_PLAN.de.md) | [English](BETA_0_1_0B5_TEST_PLAN.md)

**Noch nicht am Gerät abgenommen.** Die frühere Abnahme bestätigt ausschließlich Airfry 170 °C/eine Minute an beiden Fächern. Der Eigentümer hat jetzt die beaufsichtigte Prüfung aller gemeldeten Programme beauftragt. Keine automatische Testfolge, kein Heiztest und keine GitHub Actions.

## Vorbereitung und Bedienung

1. HA-Backup erstellen; Airfryer Control exakt 1.0.2-beta.1 behalten. Airfryer Recipes v0.1.0b5 installieren, HA neu starten und die App vollständig neu öffnen.
2. Als Admin die Rezeptbibliothek öffnen. Gerät und Fach im oberen Bereich „Geräte-Testvorschau“ wählen. Beide Fächer müssen geschlossen, bereit/aus, ohne vorbereitetes Programm sein; Celsius am Gerät, SYNC/MATCH aus.
3. Unter „Quelle der Werte“ manuelle Werte oder ein einphasiges Rezept auswählen. Gewünschtes gemeldetes Programm, Temperatur und Minuten einstellen. Für echte Versuche den neuen Knopf **„Gewählte Werte für beaufsichtigtes Senden vorbereiten“** benutzen. „Testvorschau prüfen“ bleibt ohne Steuerbefehle. Der Knopf weiter unten bereitet weiterhin nur den alten festen 170-°C-/1-Minuten-Test vor.
4. Statusabfrage abwarten, dann die Bestätigung im Bereich „Beaufsichtigter Beta-Gerätetest“ prüfen: Gerät, Fach, Programm, Temperatur und Zeit müssen exakt stimmen. Innerhalb von 15 Sekunden „Einmalig ans Gerät senden“ und den Dialog bestätigen.
5. Direkt am Gerät Werte kontrollieren, anderes Fach unverändert und Heizung aus bestätigen. **Nicht Start drücken, auch nicht bei langen Zeitwerten.** Das ist eine Prüfung der Einstellungsübertragung, kein Garvorgang. Danach das vorbereitete Programm am Gerät abbrechen und beide Fächer wieder bereit/aus melden lassen.
6. Bei Heizstart, falschem Fach oder unklarem Ergebnis sofort am Gerät stoppen und keine weiteren Versuche ausführen. Bei einer normalen Sperre nichts umgehen; Test-ID und Wortlaut notieren. Unklarheitssperren bleiben bis zum HA-Neustart bestehen; ein Neustart beweist nicht, dass ein vorheriger Befehl nicht ankam.

## Reihenfolge und Ausfüllliste

Die [CSV-Ausfüllliste](BETA_0_1_0B5_RESULTS.csv) enthält 60 Versuche. In Excel/LibreOffice öffnen; pro Zeile BESTANDEN, FEHLGESCHLAGEN oder NICHT GETESTET, anderes Fach unverändert, Heizung aus und gegebenenfalls Meldung eintragen. Ein Fehler beendet mindestens den betroffenen Programmblock; Heizstart, falsches Fach oder unbekannter Ausgang beenden die ganze Abnahme. Erst nach Korrektur bewusst neu testen.

- **A – 12 Versuche:** Alle sechs gemeldeten Programme mit normalen manuellen Werten, jeweils Fach 1 und 2.
- **B – 12 Versuche:** Nur nach bestandenem A: dieselben Werte als eigene Testrezepte speichern und über Rezeptauswahl senden. Vorhandene persönliche Rezepte nicht überschreiben.
- **C1/C2/C3 – 36 Versuche:** Nur nach bestandenem A/B für das jeweilige Programm: untere Temperatur mit einer Minute, obere Temperatur mit einer Minute und normale Temperatur mit maximaler Beta-Garzeit. Die eingetragene Zeit wird nur bereitgestellt, niemals abgewartet oder gestartet.

| Programm | Normalwert °C / min | Prüfbereich °C | Beta-Maximum min |
| --- | --- | --- | --- |
| Airfry | 180 / 7 | 120–205 | 60 |
| Roast | 190 / 10 | 120–205 | 240 |
| Bake | 180 / 6 | 80–205 | 240 |
| Grill | 205 / 1 | 205–240 | 30 |
| Reheat | 70 / 5 | 40–205 | 60 |
| Dry | 55 / 10 | 34–95 | 1440 |

Diese Bereiche stammen aus dem geprüften Upstream-Vertrag und sind **keine bestätigten Modellgrenzen**. Zusätzlich prüft das Backend die aktuell gemeldeten Grenzen; bei engeren Adapterwerten den Versuch als gesperrt notieren. Fehlende Programme auslassen und melden. `proof` bleibt gesperrt. Dry bleibt wegen des bestehenden Rezeptformats auf 1440 Minuten begrenzt, obwohl der Upstream bis 2880 meldet.

## Ergänzende Prüfungen ohne beabsichtigte Übertragung

- Pro Programm einmal einen Temperaturwert knapp außerhalb des obigen Bereichs vorbereiten: Sperre, keine stillschweigende Begrenzung und keine Geräteänderung erwarten.
- Bestätigung verwerfen oder länger als 15 Sekunden warten: kein Senden. Für einen neuen Versuch neu vorbereiten.
- Ein Testrezept nach der Vorbereitung in einer zweiten Sitzung bearbeiten oder löschen: die alte Bestätigung muss gesperrt werden.
- Gerät vor der Vorbereitung ausschalten: Statusabfrage oder Zustandsprüfung muss sperren. Wieder einschalten darf keinen Befehl nachholen.
- Ein Fach vor der Vorbereitung öffnen: kein Senden. Laufende/pausierte Fächer nur dann prüfen, wenn das Gerät ohnehin regulär benutzt wird; andernfalls NICHT GETESTET eintragen.
- Normales Benutzerkonto: kein Admin-Testbereich. Deutsch/Englisch und eine Fahrenheit-Benutzereinstellung prüfen, wobei das Gerät selbst auf Celsius bleibt; beispielsweise 356 °F müssen als 180 °C ankommen.
- Nach den Tests Rezeptverwaltung und JSON-Export prüfen. Ein abgelehntes Rezept muss unverändert bleiben.

Keine Zugangsdaten, Gerätekennungen oder Rohdiagnosen teilen. Rückmeldungen mit Test-ID und sichtbarem Ergebnis reichen für die erste Fehleranalyse.
