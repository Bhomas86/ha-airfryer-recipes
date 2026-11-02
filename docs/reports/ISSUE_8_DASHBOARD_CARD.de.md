# Dashboard-Card 1A — beaufsichtigte Beta

[Deutsch](ISSUE_8_DASHBOARD_CARD.de.md) | [English](ISSUE_8_DASHBOARD_CARD.md)

In 0.1.0b13 nach dem vom Eigentümer freigegebenen neutralen Entwurf mit Gerätefokus umgesetzt. Dies ist das erste Dashboard-Paket zu Issue #8; Geräteberechtigungen für normale Benutzer, Bild-Uploads, Personalisierung und allgemeine Freigabe der Gerätesteuerung bleiben offen.

## Verhalten

Die mitgelieferte `custom:airfryer-recipes-card` enthält eine eigene CSS-Grafik mit zwei senkrecht gestapelten antippbaren Schubladen, getrennte Fachwahl/-zustände, Rezept-/Manuell-Auswahl, gemeldete Programme, Temperatur-/Zeitfelder und einen ausdrücklichen Sende-Button. Neutrale Schiefergrau-Akzente berücksichtigen die HA-Theme-Farben. Herstellerlogo, Produktfoto und fremde Grafik werden nicht verwendet. Dies beschreibt die Herkunft der Grafik, keine rechtliche Freigabe eines anderen Entwurfs.

Unter der Fachwahl stehen **Zuletzt gesendet · Fach X**, Programm, Temperatur und Dauer. Gemeint ist die letzte vom Adapter exakt angenommene Übertragung, **kein aktueller Gerätezustand und keine Gerätebestätigung**. Fachwechsel ändern nur die Auswahl und laden den zugehörigen Entwurf oder gespeicherten Stand. Formulareingaben, Vorschau, Abbruch, Ablehnung und unklare Ergebnisse überschreiben den angenommenen Stand nicht. Aktualisierung liest nur. Verbindung und Fachzustände sind gemeldete Momentaufnahmen; zum erneuten Lesen Aktualisieren verwenden. Es gibt keinen erfundenen Countdown oder Anspruch auf einen laufend aktuellen Gerätezustand.

Ungesendete Entwürfe bleiben während der Lebensdauer der Card je Gerät/Fach getrennt. Angenommene Stände überstehen Neuladen/Neustart im getrennten HA Store `airfryer_recipes.sent_settings` (Schema 1, höchstens 256 Geräte, Fächer 1/2). Rezepte bleiben geräteunabhängig und unverändert. Ein passender unveränderter Rezeptverweis wird als Rezept geladen; bei geändertem/gelöschtem Rezept werden die exakten historischen Werte im manuellen Modus geladen. Historie ist keine aktuelle Sendeberechtigung; jede Übertragung durchläuft die bestehenden Backend-Prüfungen.

Nur exakt angenommene Antworten des vorhandenen Senders schreiben die Historie, auch bei beaufsichtigten Panel-/Testfolgenübertragungen nach diesem Update. Frühere Übertragungen können nicht rekonstruiert werden. Asynchrone Schreibvorgänge werden serialisiert; Fehler erhalten den vorherigen Stand und das angenommene Übertragungsergebnis. Die Card warnt davor, nur wegen der Speicherung erneut zu senden. Beschädigte/neuere Speicher bleiben unangetastet, Historienschreiben wird gesperrt; Rezeptverwaltung bleibt nutzbar. Neuladen verwendet ein gesundes Historienobjekt samt Sperre weiter, damit ein noch laufender angenommener Schreibvorgang nicht mit einer neuen Speicherinstanz konkurriert. Keine Historienoperation sendet oder puffert Befehle.

## Sicherheit und Rechte

Die Card verwendet das vorhandene Backend für **beaufsichtigte Beta-Tests ausschließlich für Administratoren**. Der neue Historien-Endpunkt ist ebenfalls nur für Administratoren und liest ausschließlich; gefälschte Schreibzugriffe/Zusatzfelder werden abgewiesen. Normale Benutzer benötigen noch Backend-Geräte-/Fachrechte. Dashboard-Konfiguration gewährt mit dieser Version keine erweiterten Rechte.

Neue Cards beginnen mit `dry_run: true`. Dann ruft der Button ausschließlich die bestehende serverseitige `prepare_send`-Testvorschau auf, ohne Steueraufrufe oder Historienänderung. `dry_run: false` aktiviert die vorhandene Beta-Vorbereitung und eine Bestätigung mit den exakten serverseitig ermittelten Werten. Bestätigungen bleiben einmalig, kurzlebig und an die angemeldete Verbindung gebunden; verspätete Antworten, Seitenwechsel, Konfigurationswechsel, Verbindungsverlust und Doppeltippen dürfen keine neue Bestätigung still auslösen. Keine automatische Wiederholung oder Nachsendung nach Wiederverbindung. Nach unklarem/abgelehntem Ergebnis verlangt die Freigabe weiterhin bestätigtes physisches Zurücksetzen und eine frische reine Leseprüfung. Die Card sendet nur Einstellungen; Garstart erfolgt am Gerät.

Exakte Adapterbindung `1.0.2-beta.1`, Ziel CAF-DC111S-AEU, Backend-Zustands-/Bereichsprüfungen und der Vertrag mit sechs Programmen bleiben unverändert. Gären und erweiterte Temperaturen bleiben zurückgestellt. Fehlt ein konfiguriertes/zuvor gewähltes Gerät, wird niemals still ein anderes gewählt.

## Installation und lokale Abnahme

1. HA sichern, `v0.1.0b13` über HACS installieren, HA neu starten und Browser/Companion-App vollständig neu öffnen. Die Integration lädt das lokale Card-Modul automatisch; kein Dashboard wird automatisch geändert.
2. Dashboard → Bearbeiten → Karte hinzufügen → **Airfryer Recipes**. Der grafische Editor unterstützt Titel, optionale HA-Geräte-ID und Testmodus. Bei mehreren erkannten Geräten ohne konfigurierte ID wird das Gerät in der Card gewählt. Bei zwischengespeichertem Kartenkatalog die App vollständig neu laden; manuelles YAML funktioniert ebenfalls:

   ```yaml
   type: custom:airfryer-recipes-card
   title: Airfryer Küche
   dry_run: true
   ```

3. Ohne Geräteübertragung: neutrales Layout bei Handy-/Tabletbreite, beide Schubladen-/Fachbuttons, Rezept-/Manuell-Felder und Testvorschau prüfen. Fachwechsel, Bearbeiten und Aktualisieren dürfen nichts senden. Anfangs ist **Noch keine Einstellungen gesendet** korrekt; historische Daten werden nicht erfunden.
4. Optionale beaufsichtigte Sendeabnahme: als Administrator neben dem Gerät mit beiden Fächern in Ruhe den Testmodus deaktivieren und eine bereits getestete Nominaleinstellung senden. Exaktes Gerät/Fach/Werte einmal bestätigen, am Gerät kontrollieren und die Vorbereitung anschließend physisch abbrechen. Nicht Start drücken. Nur das gewählte Fach soll seine angenommene Historie zeigen. Bei Bedarf am anderen Fach zur Trennungsprüfung wiederholen; Zurückwechseln muss die Historie des ersten Faches zeigen. Keine vollständige Wiederholung der zwölfteiligen Testfolge für dieses Card-Paket nötig.
5. Neu öffnen/HA neu starten und erhaltene Historie ohne Übertragung prüfen. Formulareingaben ohne Senden dürfen die Historie nicht verändern. Offline-/Seitenwechselverhalten ohne Heizen prüfen. Normale Benutzer müssen den Beta-Rechtehinweis sehen und dürfen Historien-/Sende-Endpunkte nicht nutzen.

## Prüfung

Lokal bestanden: **170 Python-Tests**, **59 Panel-Frontend-Tests**, **21 Card-Frontend-Tests**, Python-Kompilierung und Diff-Formatprüfung. Abgedeckt sind Fach-/Gerätetrennung, dauerhafte Stände, parallele/fehlgeschlagene Schreibvorgänge, beschädigter/neuerer Speicher, Rechte-/Feldprüfungen, Rezeptverweise, reine Testvorschau, exakte Bestätigung, Abbruch, veraltete Bestätigungen, Verbindungsverlust, Doppeltippen, Einheiten und Konfiguration/Editor. Native Browser-/HA-/Companion-Darstellung und neue Geräteabnahme **nicht ausgeführt**. Eigenständiges Chromium konnte zuvor wegen der Socket-Beschränkungen dieser Umgebung nicht starten; kein nativer Browsererfolg wird behauptet. HACS/Hassfest und Python 3.14 wurden nicht ausgeführt. Keine GitHub Actions angefordert oder gestartet.
