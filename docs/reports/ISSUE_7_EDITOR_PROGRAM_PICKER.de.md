# Rezept-Programmauswahl und ausdrückliche Kennungskorrektur

[Deutsch](ISSUE_7_EDITOR_PROGRAM_PICKER.de.md) | [English](ISSUE_7_EDITOR_PROGRAM_PICKER.md)

Der Eigentümer konnte die gespeicherte Rezeptabnahme nicht durchführen, weil der Editor eine freie Programmeingabe verlangte. Der Vorschau-Screenshot zeigt Piccolinies mit 180 °C / 7 Minuten und `Airfry` als nicht gemeldet. Der geprüfte Adapter meldet die davon abweichende Kennung `airfry`. Rezeptschema v1 erhält bewusst die Groß-/Kleinschreibung von Kennungen und bindet kein Gerät ans Rezept. Dies ist eine Lücke in der Rezepterstellung, kein Nachweis einer fehlgeschlagenen Geräteübertragung.

Beta 0.1.0b12 bietet im Rezepteditor eine native Auswahlliste aus `selectedDevice().programs`. Sie verwendet dieselben übersetzten Programmnamen und Herkunftskennzeichnungen wie die Vorschau. Die Auswahlwerte sind die exakten gemeldeten IDs. Ein neues Rezept beginnt mit einer leeren Pflichtauswahl, nicht mit einem implizit gewählten Programm. Der beschreibende Gären-Eintrag im Modellprofil ergänzt kein auswählbares Adapterprogramm.

Eine bestehende nicht gemeldete Kennung bleibt als gewählte Option erhalten und wird als fehlend gekennzeichnet. Die Vorschau führt direkt zur Bearbeitung dieses Rezepts und scrollt den Editor ins Bild. Der Eigentümer wählt das gemeldete Programm und speichert dieselbe Rezept-ID; andere Datensätze werden nicht verändert. Kein Umwandeln der Schreibweise, Alias-Abgleich, Migration, automatisches Ersetzen oder Programm-Mapping beim Senden. Nur Bearbeiten/Anzeigen führt weder Speicherung noch Gerätesteuerung aus.

Ein separater Umschalter ermöglicht freie Programmeingabe trotz vorhandener Adapterauswahl. Ohne gemeldete Programme bleibt das Textfeld verfügbar. Gespeichert wird nur die Programm-ID, nie Geräte-/Fach-/Profilmetadaten. Ein Programmwechsel begrenzt Temperatur/Zeit nicht und ersetzt keine Eigentümerwerte. Bestehende Backend-Prüfungen für Rechte, Herkunft, Programm, Grenzen und frischen Zustand gelten weiter vor jeder beaufsichtigten Übertragung. Gären, erweiterte Temperaturen und die exakte Adapter-Versionsbindung bleiben unverändert.

Vor erneutem Aufbau des Editor-DOM wird der aktuelle Entwurf erfasst: Name, Beschreibung, rohe Tags, gemeinsamer Favorit, Kategorie-/neuer Kategorietext, Programm und Werte. Dadurch setzen Programm-/Eingabemoduswechsel, Fähigkeitsaktualisierung oder andere Render-Vorgänge keine ungespeicherten Felder zurück. Bei einem Wechsel der HA-Einheit wird ein bestehendes Temperaturfeld anhand seiner zuletzt angezeigten Einheit interpretiert. Neue Editorinstanzen setzen temporären Modus-/Kategoriestatus zurück. Mehrphasige Bearbeitung bleibt deaktiviert; ein beim Verlust der Adminrechte offener Editor wird ausgeblendet und kann nicht speichern. Rezept-Speichern verwirft alte sichtbare Testbestätigungen/-vorschauen.

## Prüfung

Lokal bestanden: **164 Python-Tests, 59 Frontend-Tests**, Kompilierung, lokale Dokulinks und git diff --check. Frontend-Prüfungen betreffen übersetzte gemeldete Auswahlwerte, leere Pflichtauswahl, Ausschluss reiner Profilprogramme, Erhalt von `Airfry` bis zum ausdrücklichen Speichern, Korrektur derselben ID mit unveränderten Werten, keine Geräte-/Fachspeicherung, freie Eingabe/fehlenden Adapter, Erhalt von Entwurf/Kategorie/Tags/Favorit, Fähigkeitsaktualisierung, Einheitenumrechnung und Rechteverlust. Ein integrierter API-/Repository-/Sender-Test lehnt die alte Schreibweise ohne Geräteabfrage oder Senden ab und akzeptiert das ausdrücklich aktualisierte Rezept danach auf Fach 1 und 2 mit simuliertem Gerätetransport.

Frontend-Tests verwenden VM-/DOM-Attrappen. Eine separate Chromium-/native-FormData-Prüfseite wurde vorbereitet; Chromium beendete sich jedoch vor ihrer Ausführung, weil die Cloud-Umgebung eine Socket-Operation sperrte (`setsockopt: Operation not permitted`); kein Browser-Erfolg wird behauptet. Reale HA-/Companion-Oberfläche, neue physische Gerätetests, HACS/Hassfest und Python 3.14 wurden nicht ausgeführt. Keine GitHub Actions.

## Gezielte Eigentümerprüfung

v0.1.0b12 installieren und HA neu starten; App vollständig neu öffnen. Dieselbe Airfryer-Control-Version wie bei der vorherigen Beta beibehalten. Bei Bedarf Geräte aktualisieren und den Airfryer in der Geräte-Testvorschau auswählen.

1. Piccolinies wählen. „Rezeptprogramm bearbeiten“ oder den normalen Bearbeiten-Button nutzen. „Heißluft-Frittieren“ aus der Programmliste wählen, 180 °C und 7 Minuten beibehalten und speichern. Die Vorschau muss nun das gemeldete Programm statt der alten fehlenden Option `Airfry` anzeigen.
2. Ein separates Testrezept über die Liste erstellen, ohne eine Programmkennung einzutippen. Programm, Temperatur und Dauer auswählen und speichern. Beim erneuten Öffnen müssen Auswahl und Werte erhalten bleiben.
3. [R1/R2 und die Abbruchabnahme](ISSUE_7_RECIPE_LIFECYCLE.de.md) mit dem korrigierten gespeicherten Rezept fortsetzen. Am Gerät bleiben, nicht Start drücken und Vorbereitungen zwischen Übertragungen abbrechen.

Eigentümernachtrag vom 01.11.2026: **Rezeptübertragung auf Fach 1 und 2 BESTANDEN**, nach der Editor-Korrektur gemeldet. [Genauer Nachweisumfang](ISSUE_7_LOCAL_ACCEPTANCE.de.md). Dies bestätigt R1/R2 in diesem Kontext; restliche Editorvarianten und R3–R7 sind nicht unabhängig abgenommen. Die frühere Folge mit zwölf Programm-/Facheinstellungen bleibt für ihre dokumentierten Beispielwerte abgenommen; daraus wird keine allgemeine Fähigkeitsfreigabe abgeleitet.
