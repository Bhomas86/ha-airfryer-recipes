# AGENTS.md – Airfryer Recipes (deutsche Fassung)

[Deutsch](AGENTS.de.md) | [English](AGENTS.md)

Diese Datei erläutert die verbindlichen Entwicklungsregeln für Codex und andere Agenten.
**Für Agenten ist die englische [AGENTS.md](AGENTS.md) maßgeblich.** Beide Fassungen müssen inhaltlich gleich bleiben. Vor jeder Aufgabe sind auch die [Anforderungen](docs/REQUIREMENTS.de.md) zu beachten.

## Zweisprachige Berichte und Dokumentation – verpflichtend

**Deutsch ist die Arbeitssprache des Projektverantwortlichen; Englisch dient der internationalen Community.**

- Jeder neue oder geänderte Projektbericht und jedes nicht programmatische Projektdokument wird **vollständig auf Deutsch und Englisch** bereitgestellt: `*.md` (Englisch) und `*.de.md` (Deutsch). Beide verlinken aufeinander.
- Das betrifft Anforderungen, Roadmap, Architekturentscheidungen, Testberichte, Testchecklisten, Issues, PR-Beschreibungen, Release Notes und Benutzerdokumentation.
- Bei Issues und Pull Requests steht **Deutsch zuerst**, danach die vollständig verständliche englische Fassung.
- Kommunikation mit dem Projektverantwortlichen vorzugsweise auf Deutsch. Technische Bezeichner und Quellcode-Kommentare dürfen Englisch sein. UI-Texte werden mit `en` und `de` bereitgestellt; **Englisch ist Standard/Fallback**.
- Änderungen an Dokumentation und Übersetzungen erfolgen immer gemeinsam im selben PR. Die inhaltliche Übereinstimmung ist Teil der Prüfung.
- Für kleine Übersetzungen und Berichte GPT-6.1 Sol – niedrig nutzen; bei entsprechender Schwierigkeit oder entsprechendem Risiko gemäß der folgenden Richtlinie mittel oder hoch wählen.

## Modellrichtlinie – ausschließlich GPT-6.1 Sol

Ab 29.10.2026 schreibt der Projektverantwortliche **ausschließlich GPT-6.1 Sol** vor. Unterschieden wird nur der Denkaufwand: **niedrig, mittel oder hoch** (englisch: **Low, Medium, High**). Diese Regel ersetzt die bisherige Modellrichtlinie.

| Modellkonfiguration | Einsatzzweck |
| --- | --- |
| **GPT-6.1 Sol – niedrig** | Kleine Dokumentationsänderungen, Übersetzungen, Formatierung und einfache Wartung mit geringem Risiko |
| **GPT-6.1 Sol – mittel** | **STANDARD für normale Entwicklung**. Abgegrenzte Funktionen, Python, normale Fehlerkorrekturen, Unit-Tests und Code Reviews |
| **GPT-6.1 Sol – hoch** | Komplexe Architektur über mehrere Module, Home-Assistant-Async/Lifecycle, Migrationen, schwierige Fehlersuche, Sicherheit und Nebenläufigkeit |

Die Modellnamen stammen aus der Auswahl des Projektverantwortlichen. Ein Agent darf nicht behaupten, dass er das aktuell ausgewählte Modell automatisch sehen oder ändern kann.

### Pflichtprüfung vor jedem Aufgabenpaket

1. Umfang, Schwierigkeit, Sicherheitsrisiken und Unsicherheiten bewerten.
2. Kurz **Modellprüfung** ausgeben: empfohlene Stufe, Begründung und tatsächlich ausgewähltes Modell **nur, wenn zuverlässig bekannt**.
3. Wenn das aktuelle Modell nicht sichtbar ist, vor substanziellen Codeänderungen eine Bestätigung einholen.
4. Passt das gewählte Modell nicht, **vor Bearbeitung stoppen** und die kostengünstigste passende Stufe vorschlagen. Nicht stillschweigend umstellen oder weiterarbeiten.
5. Für jede Aufgabe **GPT-6.1 Sol** verwenden. Für einfache Aufgaben niedrig, für normale Entwicklung mittel und für komplexe oder sicherheitskritische Arbeiten hoch empfehlen.
6. Die empfohlene Stufe kurz begründen. Hoch ist eine zugelassene Aufwandsstufe und keine Ausnahme, die ein anderes Modell erfordert. Nie behaupten, die ausgewählte Stufe automatisch umzustellen.
7. Wenn sich der Aufgabenumfang oder das Risiko wesentlich ändert, erneut prüfen und nötigenfalls anhalten.

Beispiel:

```text
Modellprüfung
Aufgabe: JSON-Validierung und Unit-Tests für Rezepte entwickeln.
Empfehlung: GPT-6.1 Sol – mittel (abgegrenzte Implementierung).
Ausgewählt: In dieser Umgebung nicht zuverlässig erkennbar.
Aktion: Modell vor der Implementierung bestätigen lassen.
```

## Architektur und Umfang

- Eigene Home-Assistant-Integration mit Domain `airfryer_recipes`.
- Rezepte sind **geräteunabhängig**; Gerät und Fach werden erst beim Senden gewählt.
- Lokale versionierte HA-Speicherung mit sicherer Migration.
- Rezeptvalidierung, Speicherung, Adapter/Gerätesteuerung und Frontend klar trennen.
- MVP mit einer Garphase, später erweiterbares Datenmodell.
- Geräte/Fähigkeiten möglichst automatisch erkennen; verifizierte Modellprofile als Fallback. Unbekannte Fähigkeiten nicht freischalten.
- Erster optionaler Adapter: **Airfryer Control**. Rezeptverwaltung muss ohne ihn funktionieren.
- SYNC/MATCH sind vorhandene Upstream-Aktionen; exakte Parameter und Geräteverhalten vor UI-Integration prüfen. Von normalen Fachbefehlen getrennt halten.
- Interaktives Gerätebild: Modellvorlagen, neutrales Fallback, eigenes Bild, Fächer über relative Koordinaten verschiebbar.
- Verwaltungsoberfläche für Admins getrennt von normaler Dashboard-Bedienung. **Berechtigungen serverseitig prüfen**.
- Englisch ist Standard/Fallback, Deutsch vollständig unterstützen, beide READMEs pflegen; benutzerdefinierte Rezeptnamen nicht automatisch übersetzen.
- Intern Celsius speichern, zur Anzeige umrechnen und gerätespezifische Grenzen vor Übertragung prüfen.

## Unverhandelbare Sicherheit

- **Nie einen Heizvorgang unbeabsichtigt aus der Ferne starten.** Geräteinterne Sperren und manuellen Start respektieren.
- Während aktiven Garens standardmäßig Änderungen sperren; eine Admin-Freigabe benötigt zusätzliche Bestätigung und Geräteunterstützung. Bei unbekanntem Status sperren.
- Keine Befehle nach Verbindungswiederherstellung nachholen oder automatisch erneut senden.
- Im Testmodus dürfen **serverseitig keinerlei reale Steuerbefehle** ausgeführt werden.
- Bei fehlendem/offline Adapter Rezeptbearbeitung erlauben, Gerätesteuerung deaktivieren und verständlich kennzeichnen.
- Keine Geheimnisse, Passwörter, Sessions, Kennungen oder Netzwerkadressen im öffentlichen Repository oder in Diagnosedaten. Diagnoseexport nur mit Positivliste und vorheriger Nutzerwarnung.

## Entwicklungsablauf

1. Neue Aufgaben auf Feature-Branches bearbeiten, PR erstellen; nicht direkt auf `main` schreiben.
2. Aufgaben begrenzen und zunächst die Modellprüfung ausgeben.
3. Tests parallel zur Implementierung schreiben, Geräteantworten simulieren; keine echten Gerätetests in GitHub-CI oder Cloud Codex.
4. Reale Tests ausschließlich lokal anhand der [Testcheckliste](docs/LOCAL_TEST_CHECKLIST.de.md). Cloud Codex arbeitet nur mit GitHub und erhält keinen Zugriff auf LAN, Proxmox oder VeSync-Geheimnisse.
5. Vor Abschluss Änderungen, **tatsächlich ausgeführte** Tests, nicht verfügbare Prüfungen, Risiken und lokale Testschritte berichten – vollständig Deutsch und Englisch.
6. Rezeptdaten und Wiederherstellbarkeit über Updates schützen.
7. Sämtliche Berichte, Issue-/PR-Texte, Release Notes, Dokumentation und sichtbaren UI-Funktionen zweisprachig pflegen.
8. Home-Assistant-Async-Regeln beachten; keine blockierenden Dateizugriffe im Event-Loop und keine Umgehung der Berechtigungen.
9. Entscheidungen unter `docs/REQUIREMENTS.md` / `docs/REQUIREMENTS.de.md` sowie Zeitplanung unter `docs/ROADMAP.md` / `docs/ROADMAP.de.md` festhalten. Geplante Funktionen nie als fertig bezeichnen.

## Referenzen

- Home-Assistant-Entwicklerdokumentation: https://developers.home-assistant.io/
- Airfryer Control: https://github.com/misterm2310/airfryer-control
