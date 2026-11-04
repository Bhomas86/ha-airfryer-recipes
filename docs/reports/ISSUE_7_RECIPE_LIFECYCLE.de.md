# Rezeptübertragung und unterbrochene Bestätigung

[Deutsch](ISSUE_7_RECIPE_LIFECYCLE.de.md) | [English](ISSUE_7_RECIPE_LIFECYCLE.md)

Beta 0.1.0b11 setzt die Rezept-/manuelle Abnahme fort; Gären und erweiterte Temperaturunterstützung bleiben zurückgestellt. Bestehender Vertrag mit sechs Programmen, Temperatur-Schnittmenge, reine Administratorfreigabe, 15-Sekunden-Ablaufzeit, strenge Einmalübertragung und Rezeptspeicherung bleiben unverändert. Die bisherige [Zwölf-Schritte-Geräteabnahme](ISSUE_7_LOCAL_ACCEPTANCE.de.md) bleibt Nachweis für ihre Beispielwerte; R1/R2 sind nun als bestanden gemeldet; R3–R7 bleiben offen.

## Änderungen und Zusicherungen

Zwei Lücken wurden gefunden: Einzelbestätigungen waren an den Benutzer, aber nicht an die ursprüngliche WebSocket-Verbindung gebunden. Eine verspätete Vorbereitungsantwort konnte nach Eingabeänderungen oder Verlassen der Seite eine alte Bestätigung wieder anzeigen. Die Testfolge war bereits an die Verbindung gebunden; verspätete Listen-/Leseantworten benötigten zusätzliche Frontend-Prüfungen.

Jede `beta_prepare`-Route erzeugt jetzt vor asynchronen Rezept-/Statusarbeiten ein servereigenes `SendPermit`. Ein öffentlicher HA-Verbindungsbereinigungs-Callback schließt es bei WebSocket-Abbruch. Der Token speichert diese Freigabe; `beta_confirm` verlangt dieselbe Verbindungsidentität und prüft die Freigabe nach der letzten asynchronen Validierung erneut. Ein Abbruch während der Vorbereitung verhindert verspätete Tokens; ein Abbruch vor Übergabe an die Gerätesteuerung sperrt diesen Aufruf. Clients können weder Freigabe noch Verbindung vorgeben.

Das neue adminpflichtige `beta_cancel` akzeptiert nur den Token. Es verwirft eigene wartende Arbeit oder eine laufende Validierung. Es steuert kein Gerät und kann einen übermittelten Aufruf nicht zurückholen. Die gerätebezogene Sperre bleibt bis zum tatsächlichen Ende eines laufenden Aufrufs erhalten, auch nach Verwerfen. Unklare Ergebnisse behalten die bestehende Unsicherheitssperre bis zur physischen Kontrolle und ausdrücklichen frischen Wiederfreigabe. `transmitted:false` in einer Verwerfantwort beschreibt diesen Verwerfaufruf, nicht das mögliche Ankommen einer vorherigen Anfrage.

Bereinigung erfolgt bei Verbrauch, ausdrücklichem Verwerfen, Ersetzen, Ablaufprüfung, Entladen der Integration und Verbindungsabbruch. Kein Timer wiederholt oder setzt Arbeit fort. Fremde Verbindungen/Benutzer können eine Freigabe weder verwerfen noch bestätigen. Abgelaufene oder fehlgeschlagene Bestätigungen bleiben einmalig.

Das Panel überwacht das öffentliche HA-WebSocket-Ereignis `disconnected` und prüft vor Beta-/Testfolgen-Anfragen die Eigenschaft `connected`. Ein Wechsel von Verbindung, Seite, Benutzer, Rechten oder Einheit verwirft alte Bedienelemente. Änderungen von Eingaben, Rezept oder Ziel verwerfen den sichtbaren Token; verspätete Vorbereitungsantworten werden verworfen und abgemeldet, statt alte Werte erneut bestätigbar zu machen. Verlassen während einer Validierung fordert das Verwerfen an, sofern die Verbindung noch nutzbar ist. Verspätete Testlisten, Schritte und Wiederfreigabe-Antworten überschreiben keinen neueren Abbruchzustand. Manuelle Werte und Rezepte bleiben erhalten; Anfragen werden nicht automatisch nachgeholt.

Geprüfte öffentliche [HA-JS-Verbindungsimplementierung](https://github.com/home-assistant/home-assistant-js-websocket/blob/40bd9924299a9ef02e8ae7969aee0eeca05aaecc/lib/connection.ts): `connected`, `addEventListener` und `removeEventListener` unterstützen diese Prüfungen. Die Bibliothek kann bei Suspend/Wiederverbindung Anfragen vormerken; das Panel prüft deshalb vor `callWS` den Verbindungszustand für Beta-/Testfolgenoperationen. Es greift auf keine privaten Warteschlangenfelder zu. Die Quellcodeprüfung ersetzt keine Abnahme der beim Eigentümer installierten Frontend-Version.

## Lokale Prüfung

Bestanden: **163 Python-Tests und 50 Frontend-Tests**, Kompilierung, Dokulinks und git diff --check. Ein vollständiger simulierter Integrationstest sendet gespeicherte Rezepte für alle sechs Programme auf beiden Fächern durch die tatsächlichen WebSocket-Routen, das Repository und den Sender; nur Geräteabfragen und Diensttransport sind simuliert. Alle zwölf exakten Nutzlasten werden geprüft; der Rezeptexport bleibt unverändert. Eine Rezeptänderung über die API macht die frühere Bestätigung ungültig, ohne die Änderung zu überschreiben.

Weitere Prüfungen betreffen fremde Verbindungen, Abbruch während Vorbereitung/Validierung, nur eigenes Verwerfen, Bereinigung, Ablauf, Gerätesperren bei noch laufendem übermitteltem Aufruf, Doppelklick, verspätete Eingabeantworten, Seitenrückkehr, unterdrückte Offline-Anfragen, Rechteverlust und unterbrochene Testfolgen-/Wiederfreigabe-Antworten. Bestehende simulierte Prüfungen für Offline, aktive/unbekannte Fächer, Frische, Rezeptlöschung/-Reload, Unsicherheit und Testvorschau bleiben enthalten. Frontend-Tests verwenden VM-/DOM-/Verbindungsattrappen; Backend-HA-APIs sind simuliert. Native HA-/Companion-Oberfläche, neue reale Geräteprüfungen, Python 3.14, HACS/Hassfest und GitHub Actions wurden nicht ausgeführt.

## Gezielte Eigentümerabnahme

Nachtrag: Der Eigentümer war bei der Rezepterstellung blockiert, weil der Editor Programmtext verlangte; der Screenshot zeigte die nicht gemeldete Kennung `Airfry`. Beta 0.1.0b12 ergänzt eine Liste gemeldeter Programme und einen ausdrücklichen Korrekturweg. [Editor-Korrektur und erneutes Vorgehen](ISSUE_7_EDITOR_PROGRAM_PICKER.de.md). Am 01.11.2026 bestätigte der Eigentümer anschließend, dass der Test für Fach 1 und 2 geklappt hat. R1/R2 werden nun für die Rezeptübertragung als bestanden erfasst; R3–R7 bleiben offen. [Nachweisumfang](ISSUE_7_LOCAL_ACCEPTANCE.de.md).

Backup erstellen, v0.1.0b11 installieren, HA neu starten und die App vollständig neu öffnen. Für dieses Paket exakt Airfryer Control 1.0.2-beta.1 beibehalten. Alte Vorbereitungen am Gerät abbrechen, auf beide Fächer bereit/aus warten und bei Bedarf wieder freigeben. Am Gerät bleiben; nicht Start drücken. Ein separates einphasiges Testrezept mit dem bereits abgenommenen Airfry / 180 °C / 7 Minuten erstellen; kein persönliches Rezept überschreiben.

| ID | Prüfung | Erwartetes Ergebnis | Status |
| --- | --- | --- | --- |
| R1 | Gespeichertes Testrezept und Fach 1 wählen; vorbereiten, exakte Werte prüfen und einmal senden | Werte auf Fach 1 passen; Fach 2 unverändert; keine Heizung; Rezept unverändert | BESTANDEN — Übertragung gemeldet |
| R2 | R1 physisch abbrechen, Bereitschaft abwarten, gleiches Rezept an Fach 2 senden | Werte auf Fach 2 passen; Fach 1 unverändert; keine Heizung | BESTANDEN — Übertragung gemeldet |
| R3 | R2 physisch abbrechen, erneut vorbereiten und Test verwerfen | Verwerfen sendet keine Einstellungen; keine nutzbare alte Bestätigung | NICHT GETESTET |
| R4 | Ohne Senden vorbereiten, Panel verlassen und zurückkehren | Alte Bestätigung verschwunden; keine automatische Übertragung | NICHT GETESTET |
| R5 | Manuelle Werte vorbereiten, danach Temperatur/Zeit vor dem Bestätigen ändern | Alte Bestätigung unbenutzbar; erneute Vorbereitung zeigt neue Werte | NICHT GETESTET |
| R6 | Ohne Senden vorbereiten, Verbindung des Telefons zu HA trennen und wiederherstellen | Alte Bestätigung verschwunden; kein Nachholen oder Fortsetzen einer Folge | NICHT GETESTET |
| R7 | Gespeichertes Rezept vorbereiten, in anderer Sitzung ändern, alte Bestätigung versuchen | Gesperrt; kein Geräteaufruf, geändertes Rezept bleibt unverändert | NICHT GETESTET |

Der Status von R1/R2 erfasst den vom Eigentümer gemeldeten Übertragungserfolg. Einzelbeobachtungen (anderes Fach, Heizung, gespeicherte Werte) wurden in diesem Nachtrag nicht separat wiederholt. Die Erwartungsspalte bleibt das vollständige Abnahmeziel.

Abschließend vorbereitete Einstellungen am Gerät abbrechen. Wurde vor Verlassen/Abbruch bereits ein Sendeaufruf übermittelt, physisch prüfen: Verwerfen beweist nicht, dass er nie angekommen ist. ID, angezeigten Hinweis, gewähltes Fach und physisches Ergebnis notieren; Rohdiagnosen oder Kennungen sind nicht nötig.

Nach gezielter Abnahme folgt als nächstes Umsetzungspaket die normale Dashboard-Bedienung samt Backend-Benutzerrechten. Dieser Release schaltet weder Dashboard, normale Benutzerübertragungen, Gären noch größere Modelltemperaturbereiche frei.
