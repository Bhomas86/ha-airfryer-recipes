# Lokale Abnahme – beide Fächer

[Deutsch](ISSUE_7_LOCAL_ACCEPTANCE.de.md) | [English](ISSUE_7_LOCAL_ACCEPTANCE.md)

## Vollständige beaufsichtigte Folge — 01.11.2026

**Alle zwölf angezeigten Einstellungen BESTANDEN.** Der Eigentümer lieferte den Screenshot der abgeschlossenen Folge (`Screenshot_20261101_143711_Home Assistant.jpg`) und bestätigte: „Alle Prüfungen bestanden und Gerät ist wieder aus.“ Das Panel zeigt zwölf erfolgreiche Einträge und meldet nach jedem Befehl passende Werte. Testgerät: Cosori Turbo Tower Pro Smart CAF-DC111S-AEU. Dies ist eine lokal vom Eigentümer durchgeführte Abnahme; Cloud Codex hatte keinen Gerätezugriff.

| Programm | Temperatur | Dauer | Fach 1 | Fach 2 |
| --- | --- | --- | --- | --- |
| Air Fry | 180 °C | 7 min | BESTANDEN | BESTANDEN |
| Braten | 190 °C | 10 min | BESTANDEN | BESTANDEN |
| Backen | 180 °C | 6 min | BESTANDEN | BESTANDEN |
| Grillen | 205 °C | 1 min | BESTANDEN | BESTANDEN |
| Aufwärmen | 70 °C | 5 min | BESTANDEN | BESTANDEN |
| Dörren | 55 °C | 360 min | BESTANDEN | BESTANDEN |

Der vollständige Lauf hat die früheren Abbruchstellen beim Programmwechsel und Dörren passiert. Er durchlief die geführte Folge mit Beenden eigener vorbereiteter Fächer zwischen den Programmgruppen. Den abschließenden Aus-Zustand bestätigt der Eigentümer; der Panel-Screenshot selbst zeigt die abgeschlossene Folge, keine unabhängige Aus-Zustandsmeldung oder Protokollierung einzelner Rücksetzübertragungen.

Die gezeigte Liste entspricht der korrigierten Folge aus 0.1.0b9, die in 0.1.0b10 beibehalten wurde. Die exakt installierte Version ist im Screenshot nicht sichtbar und nicht unabhängig erfasst. Vereinbarter Adaptervertrag bleibt Airfryer Control 1.0.2-beta.1; seine Version wurde anhand dieses Screenshots nicht erneut bestimmt.

Die Abnahme gilt für diese beaufsichtigten Beispielwerte und die abgeschlossene Folge. Sie bestimmt nicht sämtliche Temperatur-/Zeitgrenzen, Gären-Unterstützung, jeden Einzeltest-UI-Weg, beliebige gespeicherte Rezepte, Änderungen aktiver Fächer, SYNC/MATCH, Wiederverbindungs-/Fehlerfälle oder allgemeine Kompatibilität. Die [Eigentümer-Modellbereiche und Adaptereinschränkungen](ISSUE_7_MODEL_TEMPERATURES.de.md) bleiben getrennt. Diese Dokumentation ändert weder Fähigkeitskennzeichen noch Senderechte.

Nächste Arbeit: Für vollständige Turbo-Tower-Temperaturbereiche und Gären ist eine modellabhängige Upstream-Adapteränderung mit anschließender Vertragsprüfung und gezielter beaufsichtigter Abnahme nötig. Weitere Fehler-/Grenzfälle stehen im [erweiterten Abnahmeplan](BETA_0_1_0B5_TEST_PLAN.de.md); zwölf Beispielprüfungen entsprechen nicht allen sechzig Fällen.

Nur Dokumentation: deutsche/englische Fassung, lokale Dokulinks und git diff --check geprüft. Keine erneuten Code-Tests für diesen Bericht, keine neuen Gerätebefehle, keine GitHub Actions und keine neue Beta-Veröffentlichung.

## Frühere Einzelabnahme — 30.10.2026

Der folgende Abschnitt dokumentiert Umfang und nächste Schritte zum damaligen Datum; die oben abgeschlossene Folge ersetzt die damals noch ungeprüften Beispielprogramme.

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
