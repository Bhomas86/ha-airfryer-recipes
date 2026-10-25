# Issue #7 – Handy-Oberfläche für Geräte-Testvorschau

[Deutsch](ISSUE_7_DRY_RUN_UI.de.md) | [English](ISSUE_7_DRY_RUN_UI.md)

## Umsetzung

Dieses Teilpaket baut auf der in PR #18 gemergten, serverseitig erzwungenen Testvorschau auf. Die Administrator-Rezeptverwaltung zeigt nun einen eigenen Abschnitt „Geräte-Testvorschau“. Er liest ausschließlich die authentifizierten Befehle `airfryer_recipes/devices` und `airfryer_recipes/prepare_send`.

Administratoren können einen gemeldeten Airfryer und ein tatsächlich gemeldetes Fach wählen. Ab Airfryer Control `1.0.2-beta.1` ruft das Backend zusätzlich den öffentlichen, rein lesenden Dienst `airfryer_control.faehigkeiten` auf. Nur erlaubte Programme, Bereiche, Vorschläge, Herkunftsstatus, Verbindung, Meldezeit und Revision gelangen in die Antwort. Kontodaten, Cloud-Gerätekennung, Rohdaten und unbekannte Felder werden verworfen. Tatsächlich gemeldete Fächer stammen weiterhin aus dem Laufzeitzustand und werden nicht aus der Fähigkeitsliste erfunden.

Als Wertequelle dient ein vorhandenes einphasiges Rezept oder eine manuelle Eingabe für Programm, Temperatur und Minuten. Gemeldete Programme erscheinen als Dropdown und kennzeichnen Grenzen als bestätigt beziehungsweise geschätzt sowie den Sendestatus als bestätigt beziehungsweise ungeprüft. Ein gespeichertes Rezept mit einem nicht gemeldeten Programm bleibt unverändert und wird ausdrücklich als nicht gemeldet angezeigt; es wird nicht still ersetzt. Fehlt der neue lesende Dienst, bleibt die freie Programmeingabe als kompatibler Rückfall erhalten. Die Temperatur wird entsprechend der HA-Einheit dargestellt und vor der Anfrage wieder in Celsius umgerechnet. Die Antwort zeigt die unveränderten Wunschwerte, den Fachzustand und verständlich übersetzte Sperrgründe.

Die Oberfläche enthält bewusst keine Senden- oder Bestätigungsaktion. Sie weist vor und nach der Vorschau darauf hin, dass kein Gerätebefehl ausgeführt wurde. Der Client übermittelt nur HA-Geräte-ID, Fach-ID und die drei Wunschwerte; keine Live-, Admin-, Rohbefehls- oder Adapterparameter. Das Backend bleibt die maßgebliche Sperre und liefert immer `live_send_enabled=false` und `transmitted=false`.

Gerätefehler sind von der Rezeptverwaltung getrennt. Fehlendes, veraltetes oder inkompatibles Airfryer Control sowie ein fehlgeschlagener Fähigkeitsaufruf verhindern weder Rezeptliste noch Favoriten. Ein normaler Benutzer sieht das Admin-Panel und damit auch diesen Abschnitt nicht; die Backend-Berechtigungsprüfung aus PR #17/#18 bleibt zusätzlich bestehen.

Modellprüfung: Für dieses abgegrenzte Frontend- und Testpaket wurde GPT-5.6 Sol – High empfohlen. Der Eigentümer hat den Modellwechsel vor Beginn bestätigt.

## Automatische Prüfungen

78 Python-Offline-Tests und 15 Frontend-Tests bestanden. Die fünf gerätebezogenen Frontend-Tests prüfen:

- Rezeptverwaltung bleibt bei fehlgeschlagener Geräteabfrage verwendbar,
- nur tatsächlich gemeldete Fächer und sicher escaped Gerätewerte werden dargestellt,
- die Vorschau enthält keine Live-Steuerfelder und zeigt „nichts übertragen“,
- ein nicht gemeldetes Programm aus einem gespeicherten Rezept bleibt unverändert und sichtbar gekennzeichnet,
- manuelle Fahrenheit-Werte werden nach Celsius umgerechnet,
- ein verschwundenes Ziel erzeugt eine verständliche Meldung im Geräteabschnitt,
- normale Benutzer lösen keine Geräteabfrage aus und sehen den Abschnitt nicht.

Python-Kompilierung und `git diff --check` bestanden ebenfalls. HACS, Hassfest und Python 3.12/3.14 laufen anschließend in den PR-Actions. Cloud Codex und CI hatten keinen Zugriff auf Home Assistant, VeSync oder ein reales Gerät.

## Lokale Abnahme auf dem Handy

Nach Backup den vollständigen Ordner `custom_components/airfryer_recipes` aus diesem Branch installieren, Home Assistant neu starten und die Companion-App vollständig schließen und erneut öffnen.

1. Ohne geladenes Airfryer Control muss „Airfryer Control ist nicht geladen“ erscheinen. Rezepte, Suche, Favoriten, Import und Export müssen weiter funktionieren.
2. Mit Airfryer Control `1.0.2-beta.1` oder neuer „Geräte aktualisieren“ wählen. Angezeigten Namen, Modell und ausschließlich tatsächlich gemeldete Fächer mit Airfryer Control vergleichen. Die Meldezeit wird angezeigt, erteilt aber keine Sendeerlaubnis.
3. Unter „Manuelle Werte“ das Programm-Dropdown prüfen. Bei der CAF-DC111S-AEU müssen die derzeit von Airfryer Control gemeldeten Programme als geschätzt und im Senden ungeprüft erscheinen. `proof` fehlt aktuell im Upstream-Vertrag und darf nicht erfunden werden.
4. Ein vorhandenes Rezept auswählen. Programm, Temperatur und Zeit müssen übernommen und schreibgeschützt dargestellt werden. Ist sein Programm nicht gemeldet, muss es entsprechend gekennzeichnet bleiben und darf nicht auf den ersten Listeneintrag wechseln.
5. „Testvorschau prüfen“ wählen. Erwartet: „Es wurde nichts an das Gerät übertragen“, unveränderte Werte und Sperrgründe für Aktualität sowie unbestätigte Modellgrenzen. Am Airfryer darf sich nichts ändern.
6. Manuelle Werte prüfen; in einer Fahrenheit-Benutzersitzung müssen Anzeige und Rückgabe korrekt umgerechnet werden.
7. Airfryer oder Fach zwischen Auswahl und Vorschau aus der Upstream-Anzeige verschwinden lassen, sofern gefahrlos möglich, anschließend erneut prüfen. Erwartet: Hinweis zum nicht mehr verfügbaren Ziel, keine Wiederholung und keine Geräteänderung.
8. Oberfläche mit deutscher und englischer Benutzersprache prüfen. Ein normaler Benutzer darf die Admin-Seite weiterhin nicht öffnen.

Bei irgendeiner Änderung am Airfryer gilt der Test als **FEHLGESCHLAGEN**; dann keine weiteren Vorschauen ausführen und Home-Assistant-Protokolle sichern. Echte Übertragung, laufende Fächer, SYNC/MATCH und Heizstart werden nicht getestet. Die lokale Abnahme ist bis zur Installation **NICHT GETESTET**.

## Grenzen und nächster Schritt

Die CAF-DC111S-AEU wird von Airfryer Control weiterhin als unbekanntes Modell geführt; alle sechs gelieferten Programme und Grenzen sind deshalb geschätzt/ungeprüft. Das am Gerät sichtbare Programm `proof` fehlt im Beta-Vertrag. Die Vorschau ist keine Gerätekompatibilitätsbestätigung. Echte Übertragung bleibt bis zur lokalen Abnahme des Vertrags und zu ausreichenden modellspezifischen Nachweisen gesperrt.
