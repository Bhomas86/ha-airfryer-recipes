# Lokale Abnahme – beide Fächer

[Deutsch](ISSUE_7_LOCAL_ACCEPTANCE.de.md) | [English](ISSUE_7_LOCAL_ACCEPTANCE.md)

30.10.2026. Vom Eigentümer im Chat bestätigt; keine Gerätetests durch Cloud Codex.
Testkontext: Airfryer Recipes 0.1.0b4, vereinbarte Upstream-Version Airfryer Control 1.0.2-beta.1.

| Prüfung | Fach 1 | Fach 2 |
| --- | --- | --- |
| Einstellungen am ausgewählten Fach angekommen | BESTANDEN | BESTANDEN |
| Airfry, 170 °C, eine Minute | BESTANDEN | BESTANDEN |
| Kein Heizstart | BESTANDEN | BESTANDEN |
| Jeweils anderes Fach unverändert | BESTANDEN | BESTANDEN |

Die Statusaktualisierung ermöglichte den erneuten Test. Die nach dem Senden stehenbleibende Adapterannahme ist das Endergebnis dieser Beta, keine laufende Prüfung. Für Fach 2 musste die Fachauswahl in der Geräte-Testvorschau ausdrücklich geändert werden; danach bestätigte der Eigentümer Zeit, Temperatur, Fach, ausbleibendes Heizen und unverändertes Fach 1.

Dies bestätigt ausschließlich die beaufsichtigte Einzelübertragung dieser Testwerte an beide Fächer. Andere Programme, Grenzwerte, freie Rezeptübertragung, aktive Fächer, SYNC/MATCH und automatische Gerätebestätigung sind NICHT GETESTET. Issue #7 bleibt offen.

Nächstes Umsetzungspaket: Rezept oder manuelle Werte im bestehenden Admin-Panel für die Übertragung auswählen; den bereits getesteten Sendeweg und Einmalbestätigungen weiterverwenden. Programme und Grenzen nur mit nachvollziehbarer Prüfung freigeben. Die bestehende Vorschau bleibt ohne Steuerbefehle. Anschließend lokale Beta-Abnahme; Dashboard folgt separat.

Nur Dokumentation geändert. Deutsche/englische Fassung abgeglichen, git diff --check bestanden. Keine neuen Geräteaufrufe, keine GitHub Actions und keine neue Beta für diesen Bericht. Für folgende Updates gilt bis zu einer neuen Anweisung: nur lokale Prüfungen, keine GitHub Actions.
