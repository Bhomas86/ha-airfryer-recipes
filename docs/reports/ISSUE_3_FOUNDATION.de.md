# Entwicklungsbericht – Issue #3: Home-Assistant-Grundstruktur

[Deutsch](ISSUE_3_FOUNDATION.de.md) | [English](ISSUE_3_FOUNDATION.md)

**Stand: 24.10.2026.** Die folgende Implementierung befindet sich in einem Feature-Branch und ist noch nicht auf einem echten Home Assistant geprüft.

## Umgesetzt

- `custom_components/airfryer_recipes/manifest.json`: Domain, Version, Dokumentation, Codeowner, Einrichtung und Beschränkung auf einen Konfigurationseintrag.
- `config_flow.py`: bestätigungsbasierte Ersteinrichtung ohne Cloud-Zugangsdaten und ohne Geräteverbindung. Erweiterte Geräteauswahl und Beispielrezepte folgen später.
- `__init__.py`: asynchroner Setup-, Konfigurationseintrag-Setup- und Unload-Lebenszyklus ohne Netzwerk- oder Geräteaufrufe.
- `const.py`: gemeinsam verwendete Integrationskonstanten.
- `strings.json`, `translations/de.json`, `translations/en.json`: deutsch/englische UI-Texte des ersten Einrichtungsdialogs.
- `hacs.json` und `custom_components/airfryer_recipes/brand/icon.png`: HACS-Grundmetadaten und eigenes Integrationssymbol.
- `tests/test_integration_skeleton.py`: isolierte Tests für Setup/Unload, nachgestellten Config Flow, Manifest, Übersetzungen und Icon.
- READMEs in beiden Sprachen auf den tatsächlichen Entwicklungsstand aktualisiert.

## Noch notwendige GitHub-Einstellung

Der HACS-Validator verlangt mindestens ein GitHub-Repository-Topic. Diese Repository-Einstellung kann über die aktuelle GitHub-Verbindung nicht geändert werden. Der Verantwortliche öffnet [das Repository](https://github.com/Bhomas86/ha-airfryer-recipes), bearbeitet rechts unter **About** das Zahnrad-Symbol und fügt beispielsweise `home-assistant`, `hacs`, `airfryer` und `recipes` als Topics hinzu. **Keine HACS-Prüfung deaktivieren oder ignorieren.** Der Icon-Pfad innerhalb von `custom_components/airfryer_recipes/brand/icon.png` wurde korrigiert.

## Grenzen

**Kein produktiver Release.** Es fehlen weiterhin Rezeptpersistenz, Rezeptverwaltung, Dashboard, Gerätedetektion, Airfryer-Control-Adapter und sichere Gerätebefehle. Der Einrichtungsdialog ist bisher **kein vollständiger Assistent** aus Anforderung 27. Die vorbereitete HACS-Struktur allein beweist keine erfolgreiche HA-Installation.

Die Unit-Tests verwenden einen HA-Stub, **kein echtes Home Assistant**. Die Python-CI-Ergebnisse werden nach dem PR separat kontrolliert. Keine echten Geräte wurden angesprochen.

## Lokale Abnahme (noch auszuführen)

1. Nicht auf der produktiven HA-Instanz testen, sondern in einer separaten Testumgebung oder nach Backup.
2. Den Ordner `custom_components/airfryer_recipes` in die HA-Testkonfiguration kopieren; Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen → Airfryer Recipes** den Bestätigungsdialog öffnen.
4. Einrichten, dann Integration neu laden, Home Assistant neu starten und entfernen; Protokolle auf Import-/Async-Fehler prüfen.
5. Einrichtung ohne Airfryer Control verifizieren; ein zweiter Konfigurationseintrag muss verhindert werden.
6. Oberfläche in Deutsch und Englisch anzeigen lassen und die Textübersetzungen kontrollieren.
7. Testlauf und Versionen als BESTANDEN/FEHLGESCHLAGEN/NICHT GETESTET dokumentieren.

**Freigabezustand:** Branch/PR zur Prüfung; keine HACS-Beta veröffentlichen, bevor reale Setup-Tests bestanden wurden.

## Referenzen

- [Anforderung #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3)
- [Home-Assistant-Config-Flow-Dokumentation](https://contributors.home-assistant.io/core/integrations/config-flow/)
- [Home-Assistant-Manifest](https://contributors.home-assistant.io/core/integrations/manifest/)
- [HACS-Anforderungen](https://www.hacs.xyz/docs/publish/integration/)
