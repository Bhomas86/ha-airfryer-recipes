# SYNC / MATCH — geprüfter Vertrag und sichere Vorschau

[English](ISSUE_1_SYNC_MATCH.md) | [Deutsch](ISSUE_1_SYNC_MATCH.de.md)

Issue #1 bleibt **für echte Übertragung blockiert**. Die b25-Entwicklung implementiert nur getrennte, lesende Dashboard-Vorschauen und Backend-Validierung. PR #47 wurde mit Eigentümerfreigabe zusammengeführt; dessen native Diagnose-/Push-Abnahme wird weiterhin nicht behauptet. Diese Arbeit veröffentlicht keine neue Beta.

## Aktuelles Dashboard-Verhalten

Werte in Fach 1 und für SYNC auch in Fach 2 derselben Karte einstellen. Die Vorschau verwendet diese ausdrücklichen Kartenentwürfe; ein fehlender zweiter Entwurf wird nicht aus Historie oder Controller-Standardwerten ergänzt. Rezeptkennungen werden gegen die aktuelle Serverbibliothek aufgelöst, ohne Rezepte zu ändern.

- **SYNC-Vorschau:** Erhält Programm, Temperatur und Dauer jedes Fachs und zeigt die geplante Wartezeit `längste Dauer − Dauer dieses Fachs`. Es wird kein Timer geplant und kein Gerätebefehl gesendet.
- **MATCH-Vorschau:** Verwendet ausdrücklich die Werte von **Fach 1** für beide Fächer, auch wenn Fach 2 ausgewählt ist. Beide resultierenden Fachwerte werden angezeigt.

Nur Geräte mit zwei Fächern zeigen die Vorschautasten. Offline sind sie deaktiviert. Das authentifizierte Backend prüft die aktuelle ganze Gerätefreigabe vor dem Lesen und nach allen asynchronen Lesevorgängen. Keine fachbezogenen Steuerfreigaben. Strikte Parameterprüfung weist zusätzliche/Live-Parameter zurück. Beide Phasen müssen zu geprüften Modell-/Programmgrenzen sowie tatsächlich gemeldeten Programmen/Bereichen des Geräts passen. Ungültige Werte werden abgewiesen, nie ersetzt oder begrenzt. Laufende/unbekannte Fächer, Verbindung, Modell und ungeprüfte Frische bleiben maschinenlesbare Sperrgründe; `live_send_enabled` und `transmitted` sind immer falsch. Eine Vorschau beschreibt nur und erlaubt keine spätere Übertragung. Getrenntes Senden pro Fach bleibt unverändert.

## Nachweise aus dem Controller

Geprüftes Airfryer Control:

- **1.0.3-beta.3**, Commit `a9fc49e37c3d2698d21bfb361192717ff790eb6e`.
- Aktuelle **1.0.3-beta.4**, Commit `4c73bf0b126bbc910bdd52a9a90ed9564fef7b30`: `services.py`, `senden.py`, `core/api.py`; dieselben Blocker bestehen fort.

Öffentliche Aktionen sind `airfryer_control.sync_senden` und `airfryer_control.match_senden`, nur mit Argument `geraet`. `services.py` registriert sie über `STOP_SCHEMA`, ohne strukturierten Antwortvertrag. Ihr Handler delegiert an `senden.async_send_sync`.

Diese Routine liest veränderliche `coordinator.plans`, einschließlich Standardwerten, und begrenzt Werte still. Sie akzeptiert nicht die exakten Werte unserer Karte. Ihr Vorbereitungsschritt aktualisiert Daten und kann vorbereitete Fächer mit `endCook` beenden. Ist ein Fach beschäftigt, kehrt lediglich dieser Helfer zurück; die äußere Routine sendet anschließend trotzdem `startMultiCook`. Ein Aufruf nach clientseitiger Bereitschaftsprüfung erfüllt daher unseren serverseitigen Sicherheitsvertrag nicht.

Der kombinierte Payload setzt `readyStart: true`, sein Erzeuger beschreibt die App-Form jedoch ausdrücklich als vermutet und nicht für dieses Modell mitgeschnitten. Der Schreibaufruf nutzt `bypass_v2` ohne `retry=False`; diese API verwendet standardmäßig automatische Neuanmeldung/Wiederholung. Die öffentlichen Aktionen bieten keinen Einmal-Schalter. Weder Rückkehr noch Verfügbarkeit beweisen native Modellabnahme. Private Controller-/Cloud-APIs, Änderungen an dessen Eingabespeicher oder zeitweises Überschreiben des Wiederholungsverhaltens wären kein sicherer öffentlicher Integrationsvertrag; nichts davon ist implementiert.

## Konkret benötigter öffentlicher Controller-Vertrag

1. Ausdrückliche unveränderliche Werte für Programm/Temperatur/Minuten **beider** Fächer akzeptieren oder eine eindeutig definierte MATCH-Quelle Fach 1; keine impliziten Eingabehelfer.
2. Strikter Modus weist unbekannte Programme, ungültige Wertebereiche und Temperaturschritte ohne Begrenzen/Ersetzen zurück.
3. Eine öffentliche Einmal-Option muss jeden Geräteschreibaufruf als `retry=False` erreichen, einschließlich etwaiger Rücksetzungen; keine Warteschlange oder Wiederholung alter Befehle.
4. Frischen Bericht und beide inaktiven Fächer unmittelbar vor dem Schreiben erneut prüfen. Unbekannt, offline, veraltet oder beschäftigt muss die gesamte Aktion abbrechen. Frühe Rückkehr des Vorbereitungshelfers darf kein Fortsetzen des äußeren Sendens erlauben.
5. Keine implizite Rücksetzung vorbereiteter Programme. Falls erforderlich, Rücksetzen separat mit exakt betroffenen Fächern und ausdrücklicher Benutzerfreigabe anbieten; anschließend Zustand neu prüfen.
6. Feste reine Vorbereitung (`readyStart: true`); kein Heizstart oder Software-Zeitsteuerungsersatz. Exakt unterstützte Modelle und Payload-Form dokumentieren.
7. Strukturierte Ergebnisse angenommen/abgelehnt/unbekannt sowie frische Revisions-/Rückmeldungsdaten ohne private Daten zurückgeben. Unbekannte Ergebnisse nie automatisch wiederholen.

Nach Veröffentlichung dieses Vertrags: prüfen/festschreiben, frische Einmalbestätigungen an beide Phasen, Ziel, Benutzer, Verbindung und Gerätefreigabe binden, vorhandene Gerätesperren teilen, serverseitigen Testmodus implementieren und beaufsichtigte native SYNC-/MATCH-Abnahme durchführen. #1 nicht aufgrund dieser Vorschau schließen.

## Prüfung

Offline-Tests prüfen getrennte SYNC-Werte/Wartezeit, MATCH-Richtung, serverseitige Rezeptauflösung, fehlerhafte/fehlende/unzulässige Werte, fehlende Fächer/Programme, Offline-/Laufend-/Unbekanntes-Modell-Sperren, entzogene Freigaben, strikte API-Wege und null Steueraufrufe. Kartentests prüfen ausdrückliche Entwürfe, keine stillen Ersatzwerte, normalen Benutzerzugriff sowie sichtbare/deaktivierte Tasten. Native kombinierte Gerätetests sind aus dieser Cloud-Umgebung nicht möglich und bleiben ausstehend.

Nativer reiner Vorschautest: Unterschiedliche Werte für beide Fächer wählen; SYNC muss sie samt Dauerdifferenz anzeigen. MATCH wählen; beide Ausgaben müssen Fach 1 entsprechen. Ganze Gerätefreigabe für normale Benutzer erteilen/entziehen und unabhängiges Senden weiter prüfen. Die Vorschau darf Gerät oder vorbereitete Programme nicht verändern. Diese Implementierung erlaubt keinen echten kombinierten Sendeversuch.

Lokal bestanden: **259 Python-Tests jeweils unter 3.12.14 und 3.14.8; 132 Frontend-Tests**, Kompilierung und `git diff --check`. Deutsche/englische Oberfläche und Dokumentation inhaltlich abgeglichen. Keine Actions unter der bestehenden CI-Pause gestartet.
