# Lokale Abnahmecheckliste

[Deutsch](LOCAL_TEST_CHECKLIST.de.md) | [English](LOCAL_TEST_CHECKLIST.md)

Aktuell: **b22**, für beaufsichtigte Einstellungen an CAF-DC111S-AEU exakt **Airfryer Control 1.0.3-beta.3**. Dashboard, Rezeptverwaltung, Ganzgerätefreigaben, private Gerätebilder und beaufsichtigter Sendeweg sind umgesetzt. [Aktuelle Prüfung und Nachweise](reports/FINAL_REVIEW.de.md). Reale HA-/Gerätetests führt nur der Eigentümer aus; Cloud Codex und Actions haben keinen LAN-/Gerätezugriff.

## Gezielter b22-Speicher-/Neustarttest

Dieser Test prüft den korrigierten Speicherweg und benötigt keine Geräteübertragung. Karte, Ganzgerätefreigaben, abgeschlossene 44-Schritt-Rückmeldungsfolge und Gären-Rezepttest sind vom Eigentümer bestätigt; wegen dieser Speicherkorrekturen nicht automatisch alle Geräteeinstellungen wiederholen.

1. b22 installieren, HA neu starten und App neu öffnen. Karte im Testmodus lassen.
2. Harmlose Rezeptänderung (etwa Beschreibung) speichern, einen persönlichen Favoriten ändern und erfolgreiche Speicherung prüfen. Falls ein entbehrliches Rezept vorhanden ist: als Favorit markieren, als Admin löschen, dann einen anderen Favoriten ändern; ein alter gelöschter Verweis darf das Speichern nicht verhindern. Keine 501 Favoriten von Hand anlegen.
3. Aktuelles Gären-Rezept, Gerätefoto/Fachpositionen, gewählten A/B-Stil, Gerätefreigaben und getrennte zuletzt gesendete Werte beider Fächer notieren.
4. HA neu starten und App vollständig neu öffnen. Rezeptänderung/Favorit und notierte Einstellungen müssen erhalten sein; der freigegebene normale Benutzer sieht weiterhin das vorgesehene Gerät. Keine alte Bestätigung oder automatische Einstellungsübertragung darf fortgesetzt werden.
5. BESTANDEN / FEHLGESCHLAGEN / NICHT GETESTET mit installierten Versionen und konkreter Beobachtung melden. Dieser b22-Neustarttest bleibt bis zur ausdrücklichen Meldung offen.

## Berechtigungs- und Fehlerregression, wenn relevant

- [ ] Neuer normaler Benutzer sieht standardmäßig kein Gerät. Ganzgerätefreigabe gibt beide Fächer und alle gemeldeten Programme frei; Entzug sperrt nach Aktualisieren neue Lese-/Sendezugriffe. Keine Fach-/Programm-/Menüfreigaben.
- [ ] Normale Benutzer können Admin-Rezeptänderungen/Import/Export, Bildschreiben, Freigabeverwaltung und Testfolgen auch über direkte WebSocket-Aufrufe nicht nutzen. Persönliche Favoriten gehören nur zum authentifizierten Benutzer.
- [ ] Testmodus sendet keinen Steuerbefehl. Unbekannt/offline/gart sperren Einstellungen; Verbindungsabbruch/Wiederverbindung wiederholen keinen alten Befehl.
- [ ] Fehlendes/defektes Airfryer Control lässt die Rezeptverwaltung nutzbar. Eine andere Controller-Version besteht den gepinnten beaufsichtigten Vertrag nicht.
- [ ] Ungültiger Import/zukünftiges Schema verändern keine Originaldaten. Sicherungswiederherstellung nur an entbehrlicher Testkopie prüfen; für Schema 1 wird keine Migration behauptet.
- [ ] Bei natürlich auftretendem Speicherfehler darf die UI Speichern nicht fälschlich bestätigen. Eine angenommene Geräteübertragung bei Historienfehler muss angenommen bleiben und darf nicht nur zum Speichern wiederholt werden. Produktivspeicher nicht zur Fehlersimulation beschädigen; automatisierte Tests decken simulierte Fehler ab.

## Vorhandene Benutzerabläufe

- [ ] Rezept erstellen/bearbeiten/kopieren/nach Bestätigung löschen, Kategorien, Tags, Suche und gemeinsame/persönliche Favoriten; doppelte Namen/Großschreibung behandeln.
- [ ] Versionierter JSON-Import mit Vorschau und bewusster Konfliktwahl; authentifizierter benannter Export enthält keine Gerätebilder, Freigaben oder Kontodaten.
- [ ] Rezept-/Manuell-Quelle, fachbezogene Entwürfe/Historie, beide Fächer ohne Senden auswählbar, korrekt gemeldete Programme einschließlich Gären und ungeprüfter Herkunft.
- [ ] A zeigt dünne aktive Kontur/kleine Markierungen; B lässt eingerichtete Fotobereiche unsichtbar und antippbar. Bildeditor-Rechtecke bleiben sichtbar, skalieren mit dem Bild und bleiben nach Darstellung speichern erhalten. A/B-Kartenwahl nutzt den getrennten HA-Speichern-Knopf.
- [ ] Deutsche/englische UI und °C/°F-Anzeige; gespeicherte Temperaturen bleiben Celsius. Nicht ausdrücklich gemeldete native Tastatur-/Barrierefreiheits-/Mobilvarianten bleiben getrennte Prüfungen.

Für den großen beaufsichtigten Temperaturlauf die [exakte Tabelle/Anleitung](reports/ISSUE_7_CONTROLLER_BETA3.de.md) nutzen. Enthalten sind 44 Einstellungen beider Fächer, keine Gar-/Zeitgrenzenabnahme. Am leeren Gerät bleiben, nicht Start drücken und letzte Vorbereitungen am Gerät abbrechen.

## Release-Stand und spätere Arbeit

Vor Kandidat/stabiler Veröffentlichung gezieltes natives Neustartergebnis und offizielle HACS-/Hassfest-Validierung nachweisen. Lokale Simulationen/Metadatenprüfungen werden getrennt dokumentiert; ohne geänderte Eigentümeranweisung keine Actions starten. Diagnoseexport, geführte Ersteinrichtung, Benachrichtigungen, Änderungen aktiver Fächer und SYNC/MATCH sind getrennt geplant und dürfen hier nicht als umgesetzt erscheinen. Reale Prüfungen als BESTANDEN / FEHLGESCHLAGEN / NICHT GETESTET mit Version, Soll-/Ist-Ergebnis und ohne Zugangsdaten, Cloudkennungen oder rohe Diagnosedumps dokumentieren.
