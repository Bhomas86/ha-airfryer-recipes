# Geprüfte Controller-Beta, Gären und Temperaturgrenzen-Testlauf

[Deutsch](ISSUE_7_CONTROLLER_BETA3.de.md) | [English](ISSUE_7_CONTROLLER_BETA3.md)

**Aktuelle Abnahme/Prüfung (b22, 04.11.2026):** Eigentümer bestätigt Kartenverhalten, Abschluss aller 44 Rückmeldeschritte und anschließenden Gären-Rezepttest. Historische offene Angaben unten beschreiben den damaligen Veröffentlichungsstand. Aktueller nativer b22-Neustart und offizielle Metadatenprüfungen bleiben offen. [Exakte Nachweise, Korrekturen und Release-Entscheidung](FINAL_REVIEW.de.md).

Der Eigentümer bestätigt beide b20-Gerätebildvarianten und wünscht B im Editor zuerst/als Standard, ohne eigene Veröffentlichung. Diese Präferenz wird mit den Controller-Änderungen in b21 gebündelt. Bestehende ausdrückliche A/B-Auswahlen bleiben erhalten. Am 04.11.2026 meldet der Eigentümer die Temperatur-/Proof-Umsetzung des Upstream-Entwicklers und beauftragt Prüfung, Integration und Abdeckung im großen beaufsichtigten Lauf. Dies autorisiert Vorbereitung und Umsetzung; die Geräteabnahme erfolgt weiterhin durch den Eigentümer.

## Geprüfter Quellstand und erhaltener Transport

Neueste veröffentlichte Upstream-Vorabversion bei der Prüfung: [Airfryer Control v1.0.3-beta.3](https://github.com/misterm2310/airfryer-control/releases/tag/v1.0.3-beta.3). Tag und Manifest kennzeichnen Commit [a9fc49e37c3d2698d21bfb361192717ff790eb6e](https://github.com/misterm2310/airfryer-control/tree/a9fc49e37c3d2698d21bfb361192717ff790eb6e). Beaufsichtigtes Senden verlangt jetzt exakt Version 1.0.3-beta.3. Ältere Releases, frühere Betas und ungeprüfte künftige Versionen bestehen diese Sperre nicht. Rezeptverwaltung/lesende Erkennung bleiben unabhängig von der Sendefreigabe nutzbar.

Geprüfte Dateien: modelle.py (Turbo-Tower-Profil), faehigkeiten.py, services.py, senden.py, core/api.py, coordinator.py, core/parser.py, switch.py, sensor.py, __init__.py, const.py und manifest.json, alle aus diesem Commit. Der modellbezogene Dienst akzeptiert proof und die sieben gemeldeten Geräte-Temperaturbereiche. Die feste Variante multi_app bildet proof auf Proof ab, fordert startMultiCook mit readyStart: true an und übergibt bei once=True retry=False an bypass_v2. Dessen _once-Zweig meldet für diese Steueranfrage nicht erneut an und wiederholt sie nicht. streng=True weist Werte außerhalb der Grenzen zurück, statt sie zu begrenzen; bestaetigen=False verhindert, dass zwischengespeicherte Upstream-Bestätigung als eigener Nachweis gilt. Felder des Einstellungsaufrufs und Prüfung auf genau einen Versuch bleiben erhalten. Das fachbezogene switch.turn_off ordnet weiterhin das gewählte Fach endCook zu; es fordert keinen Garstart an.

Airfryer Recipes prüft zusätzlich exakt CAF-DC111S-AEU, Celsius, beide frisch gemeldeten Fächer inaktiv, SYNC/MATCH aus, passenden Zustand/Revision/Fähigkeiten und aktuelle Berechtigung. Gären verlangt den gemeldeten 1-°C-Schritt. Die Schrittweite wird Teil der Bestätigungs-/Laufbindung. Fehlende, beschädigte oder unbekannte Metadaten sperren weiterhin. Normale Benutzer benötigen unverändert eine aktuelle Ganzgerätefreigabe. Keine rohe API, Ersatzschreibweise, startfähige Aktion oder Wiederholung kommt hinzu.

## Grenzen und Herkunft

| Programm | Temperatur °C | Upstream-Zeitobergrenze, Minuten | Unsere Beta-Zeitobergrenze | Testtemperaturen °C | Testdauer, Minuten |
| --- | --- | --- | --- | --- | --- |
| Heißluft-Frittieren | 120–230 | 60 | 60 | 120, 180, 230 | 7 |
| Braten | 175–230 | 240 | 240 | 175, 190, 230 | 10 |
| Backen | 80–205 | 240 | 240 | 80, 180, 205 | 6 |
| Grillen | 160–230 | 30 | 30 | 160, 205, 230 | 1 |
| Aufwärmen | 40–205 | 60 | 60 | 40, 70, 205 | 5 |
| Dörren | 35–95 | 2880 | 1440 | 35, 55, 95 | 360 |
| Gären | 30–45, Schritt 1 | 720, geschätzt | 720 | 30, 31, 35, 45 | 60 |

Die Upstream-Herkunft besitzer wird zu owner_reported normalisiert, nicht bestätigt oder unbekannt. UI-Beschriftungen behalten ungeprüfte Grenzen/Übertragung ausdrücklich bei. Temperaturschritte werden nur als gewöhnliche begrenzte Ganzzahlen übernommen; Wahrheitswerte werden abgewiesen. Die zusammengefasste Upstream-Besitzerkennzeichnung belegt keine Zeitabnahme: Die Gären-Obergrenze ist ausdrücklich geschätzt, andere Zeitgrenzen bleiben an diesem Gerät ebenfalls ungeprüft, und unser Rezept-/Manuell-Schema begrenzt jede Dauer weiterhin auf 1440 Minuten. Der Lauf prüft Temperaturen, keine Zeitgrenzen oder tatsächliches Garen. Bereits angenommene übliche Übertragungen belegen weder die neuen Grenzwerte noch Gären.

## Großer Lauf und Abbruchverhalten

Die vollständige Folge enthält **44 Einstellungen**: 22 Temperatur-/Dauerkombinationen, jeweils für Fach 1, dann Fach 2. Enthalten sind untere/übliche/obere Temperaturen aller sieben Programme und die benachbarten Gären-Werte 30/31 °C. Die UI zeigt vor einer ausdrücklichen beaufsichtigten Bestätigung jede Einstellung und jeden Fach-Beenden-Übergang. Fehlende Programme oder eine Meldung, die deren gesamte Werte-Gruppe nicht abdeckt, führen dazu, dass das ganze Programm als übersprungen erscheint; niemals wird nur sein neuer Grenzwert still weggelassen. Eine vollständige Abnahme benötigt keine übersprungenen Programme.

Vor jedem anderen Temperatur-/Programmpaar beide von diesem Lauf vorbereiteten Fächer beenden und frisch prüfen, dann das nächste Paar bereitstellen. Das gilt auch für Temperaturwechsel innerhalb desselben Programms. Ein vollständiger Lauf enthält 42 Fach-Beenden-Aktionen zwischen den 22 Paaren; das letzte Paar bricht der Eigentümer am Gerät ab. Jeder Folgeschritt verbraucht einen neuen verbindungsgebundenen Einmalschlüssel und prüft Zustand, Fähigkeiten und Berechtigung erneut. Abbruch, Ablehnung, abweichende Rückmeldung, unklares Ergebnis, Ablauf, Rollen-/Verbindungswechsel oder fehlende Beenden-Entitäten verhindern weitere Schritte. Keine Warteschlange und kein automatisches Fortsetzen/Wiederholen. Die bestehende 20-Minuten-Laufgrenze bleibt; abgelaufene Läufe können ihre Schritte nicht wiederholen. Passend gemeldete Werte sind keine allgemeine Geräte-/Garfreigabe.

## Nachweise und lokales Vorgehen

Lokal geprüft: **220 Python- und 125 Frontend-Tests**, Kompilierung, Sprachpaar-/Linkprüfung und git-diff-Formatprüfung. Neue Abdeckung umfasst realistisch geformte gepinnte Fähigkeitsdaten, Besitzerherkunft/Schrittprüfung, Versionssperren, alle sieben Programme, Grenzwert-/Proof-Abfragen beider Fächer, vollständigen 44-Schritt-Lauf durch echte Sender-/read_target-Logik mit simulierten öffentlichen Diensten und frischem Zustand, 44 Rezeptübertragungen über WebSocket/Repository, Beenden innerhalb desselben Programms sowie fehlende/unvollständige Fähigkeitsgruppen. Testmodus mit Gären als Besitzerangabe führt weiterhin keinen Steueraufruf aus. Die Testdaten enthalten keine Benutzerfotos, Zugangsdaten oder Diagnosedaten.

Zusätzlich isolierte Funktionskörper aus dem gepinnten Upstream-Quellcode ausgeführt: 30 erfolgreiche Grenzwert-/Proof-Schritt-Fälle durch _program, async_send und build_variants sowie sieben strikte Ablehnungen unterhalb der Grenzen. Jeder Transport war simuliert; erfolgreiche Fälle forderten readyStart: true, multi_app und retry=False genau einmal an. Dies ist kein Upstream-HA-Integrationstest und kein Gerätenachweis. Kein Cloud-/LAN-/Gerätezugriff, keine GitHub Actions, HACS/Hassfest, Python 3.14 oder native HA-/Companion-Prüfung ausgeführt.

Airfryer Control auf **1.0.3-beta.3** und Airfryer Recipes auf **b21** aktualisieren, HA neu starten und App neu öffnen. Vorbereitete Programme am Gerät abbrechen, beide Fächer bereit/aus prüfen und am leeren Gerät bleiben; nicht Start drücken. Im Admin-Rezeptpanel die geführte Testfolge anzeigen. Erwartet werden **44 Schritte, sieben Programme, keine übersprungenen Programme**, Tabellenwerte und ausdrückliches Beenden zwischen Temperaturpaaren. Liste prüfen und einmal bestätigen. Beide Fächer beobachten: kein Heizen, keine Änderung des anderen Fachs außer dessen aufgeführtem Beenden/Senden, korrekte Programm-/Temperatur-/Zeitwerte jedes Schritts. Bei Heizen, unerwartetem Verhalten, Ablehnung oder Abbruch am Gerät abbrechen und exakten Schritt/Programm/Temperatur/Fach melden; keine verlorene Anfrage wiederholen. Abschließend die letzten Gären-Einstellungen am Gerät abbrechen. Diese Beobachtungen getrennt vom UI-Telemetrievergleich melden. Die neue Abnahme bleibt offen.
