# Turbo-Tower-Temperaturprofil

[Deutsch](ISSUE_7_MODEL_TEMPERATURES.de.md) | [English](ISSUE_7_MODEL_TEMPERATURES.md)

Am 01.11.2026 nannte der Eigentümer Temperaturbereiche für CAF-DC111S-AEU. „Repeat“ wird als Reheat/Aufwärmen und „Proof“ als Gären verstanden. Der Dörrbereich wurde unmittelbar davor genannt. Nur für Gären wurden ausdrücklich 1-°C-Schritte angegeben; für andere Programme wird keine Schrittweite abgeleitet. Dies sind vom Eigentümer gemeldete Gerätegrenzen, getrennt von Nachweisen erfolgreicher Übertragungen und von Zeitgrenzen.

| Programm | Gerätebereich laut Eigentümer | Bereich des festgelegten Adapters | Beaufsichtigte Temperatur-Schnittmenge |
| --- | --- | --- | --- |
| Air Fry | 120–230 °C | 120–205 °C | 120–205 °C |
| Braten | 175–230 °C | 120–205 °C | 175–205 °C |
| Backen | 80–205 °C | 80–205 °C | 80–205 °C |
| Grillen | 160–230 °C | 205–240 °C | 205–230 °C |
| Aufwärmen | 40–205 °C | 40–205 °C | 40–205 °C |
| Dörren | 35–95 °C | 34–95 °C | 35–95 °C |
| Gären | 30–45 °C, 1-°C-Schritte | Fehlt | Gesperrt |

Die festgelegte Airfryer-Control-Version 1.0.2-beta.1, Stand [f43a9bf8](https://github.com/misterm2310/airfryer-control/tree/f43a9bf8ddb7cc65e27897dd92158cc06840bc08), wurde erneut gelesen: `const.py` enthält nur sechs Kennungen und TwinFry-Grenzen; `services.py` verlangt diese Kennungen und ruft mit `streng:true` vor dem Senden `outside_limits` auf. `senden.py` bildet diese Programme auf die vorbereitende `multi_app`-Nutzlast ab. Ohne strenge Prüfung würden Temperaturen stillschweigend begrenzt und Gären weiterhin nicht ergänzt. Der öffentliche sichere Dienst ermöglicht mit der geprüften Version deshalb nicht alle Eigentümerbereiche. Das Upstream-Repository wurde nicht geändert.

Beta b10 speichert alle sieben Gerätebereiche in einem Profil für das exakte Modell. Die Erkennung liefert dieses statische Profil unter `model_profile` getrennt von den Adapter-`programs`, ohne fehlende Programme zu ergänzen oder die Herkunft der Fähigkeiten umzubenennen. Unbekannte Modelle erhalten kein Profil. Die aufklappbare Temperaturtabelle im Panel zeigt Eigentümer- und Adapterbereiche getrennt, einschließlich fehlendem Gären und dessen 1-°C-Schritten. Die Anzeige folgt der HA-Einstellung °C/°F; gespeichert bleiben Celsiusgrenzen.

Die Backend-Prüfung erzwingt zusätzlich den Modelltemperaturbereich. Geprüfter Vertrag und aktuelle frische Adaptermeldung bleiben verpflichtend; nur die Schnittmenge lässt sich vorbereiten. Insbesondere werden Braten unter 175 °C und Grillen über 230 °C gesperrt. Am Modell gültige Werte außerhalb des festgelegten Vertrags bleiben ebenfalls gesperrt. Kein Begrenzen, automatischer Ausweichweg, Rohbefehl, Start, Wiederholen oder Gären unter anderer Kennung wird eingeführt. Rezept- und manuelle Quellen teilen dieselbe Prüfung; gespeicherte Rezepte und die unabhängige Testvorschau-API bleiben unverändert.

Die geführte Liste mit zwölf Schritten bleibt unverändert: Ihre Beispielwerte passen bereits zur Schnittmenge, einschließlich Dörren mit 55 °C / 360 Minuten auf beiden Fächern. Daraus folgt keine Abnahme der Grenzwerte. Programmzeitgrenzen und Temperaturschritte außerhalb von Gären bleiben ungeprüft.

Lokal bestanden: 150 Python-Tests, 38 Frontend-Tests, Kompilierung, Dokulinks und git diff --check. Geprüft werden Ablehnung vor Geräteabfragen/-steuerung bei modell- und adapterwidrigen Werten, alle gemeinsamen Temperaturgrenzen, gesperrtes Gären, fehlende Profile für unbekannte Modelle, unveränderte Adapterprogramme/-herkunft und übersetzte °C-/°F-Anzeige. Frontend-Tests nutzen VM-/DOM-Attrappen. Keine GitHub Actions, HACS/Hassfest, Python 3.14, native HA-/Companion-Oberfläche oder neuen Geräte-Grenzwerttests.

Lokale Prüfung: b10 installieren, HA neu starten und die App vollständig neu öffnen. In der Geräte-Testvorschau „Temperaturbereiche des Geräts“ aufklappen und mit dem Gerät vergleichen. Die geführte Liste enthält weiter sechs vom Adapter gemeldete Programme. Vor echten Übertragungen alte Vorbereitungen physisch abbrechen und bei Bedarf wieder freigeben; am Gerät bleiben und nicht Start drücken. Keine Zeitgrenzen ableiten oder Gären unter einem anderen Programm versuchen. Vollständige Bereiche und Gären benötigen eine modellabhängige Upstream-Adapteränderung mit anschließender Vertragsprüfung und ausdrücklicher beaufsichtigter Abnahme.
