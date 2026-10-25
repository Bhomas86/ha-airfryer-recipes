# Issue #7 – Handy-Oberfläche für Geräte-Testvorschau

[Deutsch](ISSUE_7_DRY_RUN_UI.de.md) | [English](ISSUE_7_DRY_RUN_UI.md)

## Umsetzung

Dieses Teilpaket baut auf der in PR #18 gemergten, serverseitig erzwungenen Testvorschau auf. Die Administrator-Rezeptverwaltung zeigt nun einen eigenen Abschnitt „Geräte-Testvorschau“. Er liest ausschließlich die authentifizierten Befehle `airfryer_recipes/devices` und `airfryer_recipes/prepare_send`.

Administratoren können einen gemeldeten Airfryer und ein tatsächlich gemeldetes Fach wählen. Als Wertequelle dient ein vorhandenes einphasiges Rezept oder eine manuelle Eingabe für Programm, Temperatur und Minuten. Die Temperatur wird entsprechend der HA-Einheit dargestellt und vor der Anfrage wieder in Celsius umgerechnet. Die Antwort zeigt die unveränderten Wunschwerte, den Fachzustand und verständlich übersetzte Sperrgründe.

Die Oberfläche enthält bewusst keine Senden- oder Bestätigungsaktion. Sie weist vor und nach der Vorschau darauf hin, dass kein Gerätebefehl ausgeführt wurde. Der Client übermittelt nur HA-Geräte-ID, Fach-ID und die drei Wunschwerte; keine Live-, Admin-, Rohbefehls- oder Adapterparameter. Das Backend bleibt die maßgebliche Sperre und liefert immer `live_send_enabled=false` und `transmitted=false`.

Gerätefehler sind von der Rezeptverwaltung getrennt. Fehlendes Airfryer Control, inkompatible Laufzeitdaten oder ein fehlgeschlagener Discovery-Aufruf verhindern weder Rezeptliste noch Favoriten. Ein normaler Benutzer sieht das Admin-Panel und damit auch diesen Abschnitt nicht; die Backend-Berechtigungsprüfung aus PR #17/#18 bleibt zusätzlich bestehen.

Modellprüfung: Für dieses abgegrenzte Frontend- und Testpaket wurde GPT-5.6 Sol – High empfohlen. Der Eigentümer hat den Modellwechsel vor Beginn bestätigt.

## Automatische Prüfungen

75 Python-Offline-Tests und 14 Frontend-Tests bestanden. Die vier neuen Frontend-Tests prüfen:

- Rezeptverwaltung bleibt bei fehlgeschlagener Geräteabfrage verwendbar,
- nur tatsächlich gemeldete Fächer und sicher escaped Gerätewerte werden dargestellt,
- die Vorschau enthält keine Live-Steuerfelder und zeigt „nichts übertragen“,
- manuelle Fahrenheit-Werte werden nach Celsius umgerechnet,
- ein verschwundenes Ziel erzeugt eine verständliche Meldung im Geräteabschnitt,
- normale Benutzer lösen keine Geräteabfrage aus und sehen den Abschnitt nicht.

Python-Kompilierung und `git diff --check` werden vor Veröffentlichung geprüft. HACS, Hassfest und Python 3.12/3.14 laufen anschließend in den PR-Actions. Cloud Codex und CI hatten keinen Zugriff auf Home Assistant, VeSync oder ein reales Gerät.

## Lokale Abnahme auf dem Handy

Nach Backup den vollständigen Ordner `custom_components/airfryer_recipes` aus diesem Branch installieren, Home Assistant neu starten und die Companion-App vollständig schließen und erneut öffnen.

1. Ohne geladenes Airfryer Control muss „Airfryer Control ist nicht geladen“ erscheinen. Rezepte, Suche, Favoriten, Import und Export müssen weiter funktionieren.
2. Mit geladenem Airfryer Control „Geräte aktualisieren“ wählen. Angezeigten Namen, Modell und ausschließlich tatsächlich gemeldete Fächer mit Airfryer Control vergleichen. „Als online gemeldet“ ist ausdrücklich kein Frischenachweis.
3. Ein vorhandenes Rezept auswählen. Programm, Temperatur und Zeit müssen übernommen und schreibgeschützt dargestellt werden.
4. „Testvorschau prüfen“ wählen. Erwartet: „Es wurde nichts an das Gerät übertragen“, unveränderte Werte und mindestens die drei Sperrgründe für Upstream-Vertrag, Aktualität und Modellgrenzen. Am Airfryer darf sich nichts ändern.
5. „Manuelle Werte“ wählen und eigene Werte eingeben. Die Vorschau muss dieselben Wunschwerte zurückgeben; in einer Fahrenheit-Benutzersitzung müssen Anzeige und Rückgabe korrekt umgerechnet werden.
6. Airfryer oder Fach zwischen Auswahl und Vorschau aus der Upstream-Anzeige verschwinden lassen, sofern gefahrlos möglich, anschließend erneut prüfen. Erwartet: Hinweis zum nicht mehr verfügbaren Ziel, keine Wiederholung und keine Geräteänderung.
7. Oberfläche mit deutscher und englischer Benutzersprache prüfen. Ein normaler Benutzer darf die Admin-Seite weiterhin nicht öffnen.

Bei irgendeiner Änderung am Airfryer gilt der Test als **FEHLGESCHLAGEN**; dann keine weiteren Vorschauen ausführen und Home-Assistant-Protokolle sichern. Echte Übertragung, laufende Fächer, SYNC/MATCH und Heizstart werden nicht getestet. Die lokale Abnahme ist bis zur Installation **NICHT GETESTET**.

## Grenzen und nächster Schritt

Die freie Programmeingabe bleibt bestehen, weil noch keine verifizierten modellbezogenen Programme vorliegen. Die Vorschau ist keine Gerätekompatibilitätsbestätigung. Echte Übertragung bleibt bis zur Antwort beziehungsweise Anpassung des Airfryer-Control-Vertrags gesperrt. Ein Fork wäre technisch möglich, würde aber Wartung und Sicherheitsnachweis des Geräteadapters in dieses Projekt verlagern.
