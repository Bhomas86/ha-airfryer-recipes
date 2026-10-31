# Geführter Testlauf mit einer Bestätigung

[Deutsch](ISSUE_7_GUIDED_BATCH.de.md) | [English](ISSUE_7_GUIDED_BATCH.md)

## Bedienung in 0.1.0b6

Der Eigentümer bestätigt, dass der Auswahlbutton von 0.1.0b5 funktioniert, fordert aber weniger Bedienaufwand und eine einzige Bestätigung für eine Folge. Der neue Bereich „Geführter Gerätetest“ steht über der bisherigen Vorschau. Gerät wählen, **„Testfolge anzeigen“**, Liste prüfen und einmal **„Angezeigte Testfolge bestätigen und starten“** drücken. Keine zusätzlichen Dialoge pro Schritt. Vor dem ersten Start müssen beide Fächer geschlossen, bereit/aus und ohne Programm sein; Celsius, SYNC/MATCH aus, Gerät leer und beaufsichtigt. Nicht auf Start drücken.

Die normale Folge umfasst jeweils Fach 1 und 2: Airfry 180 °C/7 Minuten, Roast 190/10, Bake 180/6, Grill 205/1, Reheat 70/5 und Dry 55/10. Das sind maximal zwölf Befehle, keine automatische Garfolge. Fehlende Programme oder nicht passende Beispielwerte werden ausdrücklich als ausgelassen angezeigt. Grenzwert- und Rezepttests aus der großen Liste bleiben separate Einzelversuche; insbesondere werden Maximaltemperaturen und lange Laufzeiten nicht automatisch angefahren.

Während des Laufs werden Fortschritt und passende Rückmeldungen angezeigt. „Restliche Schritte abbrechen“ ist auch während einer offenen Anfrage nutzbar. Bereits abgesendete Befehle können nicht zurückgeholt werden. Bei Heizstart oder falschem Fach am Gerät stoppen und Test beenden. Am Ende beide Fächer physisch prüfen und die vorbereiteten Programme am Gerät abbrechen. Diese Version wurde noch nicht am Gerät abgenommen.

## Absicherung

Die vollständige Liste wird serverseitig erzeugt und an Administrator, Gerät, Adapterinstanz und aktuelle WebSocket-Verbindung gebunden. Anzeige bereitet nur lesend vor; Start autorisiert die Liste einmal. Anzeige gilt 60 Sekunden, ein gestarteter Lauf höchstens zehn Minuten. Jeder Schritt benötigt einen neuen, einmaligen serverseitigen Folgetoken. Keine Hintergrund-Warteschlange und keine Wiederholung bei verlorener Antwort. Verbindungswechsel oder Entladen verhindert Fortsetzung; beim WebSocket-Schließen greift HA-Subscription-Cleanup. Verlassen des Panels fordert Abbruch an.

Vor jedem Steuerbefehl werden Rechte, Vertragsgrenzen und neue Gerätemeldungen geprüft. Danach wird erneut ausschließlich lesend aktualisiert, bis ein neuer Bericht vorliegt (maximal 20 Sekunden für eine möglicherweise verzögerte HA-Abfrage). Beide Fächer müssen nicht aktiv sein; ein bereits vom selben Lauf vorbereitetes Fach darf nur weiterverwendet werden, wenn Programm, Solltemperatur und Zeit exakt dem zuletzt gesendeten Schritt entsprechen und „wartet auf Start“ gemeldet wird. Andere vorbereitete Zustände, Abweichungen, Offline-/Unbekannt-Zustände und Heiz-/Garaktivität stoppen. Fremde Einzelübertragungen sind während des Laufs gesperrt.

Kein automatisches Zurücksetzen und kein Start-, Raw-, SYNC- oder MATCH-Aufruf. Der gemeinsame Transport bleibt ausschließlich `programm_senden`, feste Variante `multi_app`, einmal, streng und ohne Upstream-Autobestätigung. Ein unklarer Ausgang oder fehlende Rückmeldung nach dem Senden sperrt weitere Versuche bis zum HA-Neustart. Bei manueller Unterbrechung während einer offenen Übertragung gilt derselbe vorsichtige Umgang. Ein Neustart belegt nicht, dass der vorige Befehl nicht angekommen ist.

## Prüfung und lokale Abnahme

Lokal bestanden: 132 Python-Tests, 29 Frontend-Tests, Kompilierung und git diff --check. Neue Fälle prüfen zwölf eindeutige Schritte, fehlende Programme, Nonce-Replay, Verbindungswechsel, Abbruch vor/während des Sendens, unklare Antworten, fehlende Rückmeldung, Gerätesperre, Adapterwechsel, Ablauf, WebSocket-Cleanup, eigene vorbereitete Fachwerte und verzögertes lesendes Refresh. Die Browserprüfung mit Chromium war in dieser Umgebung nicht erfolgreich ausführbar; es liegt keine echte Companion-/HA-Laufzeitprüfung vor. Keine GitHub Actions, HACS/Hassfest oder Python-3.14-Läufe für dieses Update.

Nach Installation v0.1.0b6 HA neu starten und App vollständig neu öffnen. Airfryer Control bleibt exakt 1.0.2-beta.1. Zuerst die angezeigte Liste ohne Senden prüfen; dann beaufsichtigt einmal starten. Erwartet: Schrittfolge ohne weitere Bestätigung, nach jedem Befehl passende gemeldete Werte, kein Heizen und Stopp bei Abweichung. Ob die Firmware das Überschreiben des eigenen vorbereiteten Programms erlaubt, ist Teil dieser neuen Abnahme. Bei Ablehnung keine weiteren Versuche und keine automatische Fehlerumgehung. Rückmeldung mit letztem Schrittnamen, Fach und Meldung; keine Rohdiagnosen oder Kennungen. Geräteabnahme: NICHT GETESTET.
