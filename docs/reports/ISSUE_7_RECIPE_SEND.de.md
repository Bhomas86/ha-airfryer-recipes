# Rezept- und manuelle Beta-Übertragung

[Deutsch](ISSUE_7_RECIPE_SEND.de.md) | [English](ISSUE_7_RECIPE_SEND.md)

Stand 30.10.2026. GPT-6.1 Sol – hoch, vom Eigentümer bestätigt. Die Abnahme aller gemeldeten Programme wurde ausdrücklich beauftragt. Echte erweiterte Geräteabnahme: NICHT GETESTET.

Die optionale `source` in `beta_prepare` akzeptiert genau `recipe_id` oder `settings` mit Programm, Celsius und Minuten. Rezepte werden serverseitig geladen; nur eine Phase ist zulässig. Die unveränderliche Phase wird im benutzergebundenen Einmaltoken gespeichert. Bestätigung akzeptiert keine nachträglichen Ziel-/Wertfelder. Geänderte, gelöschte oder ausgetauschte Rezeptbibliotheken sowie laufende Schreibvorgänge sperren die Bestätigung. Rezepte werden nicht begrenzt, ersetzt oder verändert.

Die sechs geprüften Upstream-Kennungen airfry/roast/bake/grill/reheat/dry sind ausschließlich als beaufsichtigter Beta-Test zulässig, wenn aktuell gemeldet und innerhalb gemeldeter sowie geprüfter Vertragsgrenzen. Geschätzte Grenzen bleiben ungeprüft; unknown-Provenienz und nicht gemeldete Programme sperren. Dry endet am bestehenden Rezeptlimit 1440 Minuten. Die feste 170-°C-/1-Minuten-Probe und die steuerungsfreie Vorschau bleiben erhalten.

Statusaktualisierung, unveränderte frische Meldung, aktive Adminrechte, beide ruhenden Fächer, Celsius, SYNC/MATCH aus, 15-Sekunden-Token und genau eine Variante ohne Retry bleiben verpflichtend. Ein unklarer Ausgang sperrt weitere Versuche bis zum HA-Neustart. Adapterannahme ist weiterhin keine Gerätebestätigung.

Lokal bestanden: 119 Python-Tests (Python 3.12), 25 Frontend-Tests, Kompilierung und git diff --check. Neue Fälle prüfen zwölf simulierte Programm-/Fachübertragungen, programmabhängige Grenzen und Herkunft, Rezeptauflösung, Manipulation, Änderung/Löschung, laufende Speicherung, °F-Umrechnung und UI-Tokenentwertung. GitHub Actions, HACS/Hassfest und Python 3.14 wurden für diese Änderung nicht ausgeführt – auf ausdrückliche Vorgabe nur lokale Prüfungen. Native HA- und Geräteabnahme verbleiben beim Eigentümer.

[Große Testanleitung und Ergebnisliste](BETA_0_1_0B5_TEST_PLAN.de.md). Frühere bestandene Abnahme gilt nur für Airfry 170 °C/eine Minute auf beiden Fächern; keine generelle Freigabe und kein Heiztest.
