# Airfryer Recipes für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

**Version 0.2.0** verwaltet geräteunabhängige Heißluftfritteusen-Rezepte lokal in Home Assistant und stellt Einstellungen über [Airfryer Control](https://github.com/misterm2310/airfryer-control) an einem unterstützten Gerät bereit. Der Garstart erfolgt physisch am Gerät.

- Rezeptbibliothek mit Admin-Bearbeitung, Kategorien/Tags, Suche, Favoriten und geprüftem JSON-Import/-Export.
- Dashboard-Karte mit unabhängigen Rezept-/manuellen Werten pro Fach, dauerhaft zuletzt gesendeten Einstellungen und grafischem Editor.
- Private Gerätebilder, einstellbare Touchbereiche und dezente Markierungen oder unsichtbare Touchbereiche.
- Ausdrückliche ganze Gerätefreigaben für normale HA-Benutzer, im Backend geprüft. Rezept-/Sicherheitsverwaltung bleibt Administratoren vorbehalten.
- Getrenntes SYNC-/MATCH-Bereitstellen mit genauer Bestätigung, frischer Prüfung inaktiver Fächer, einem Schreibversuch und ohne automatische Wiederholung oder implizites Rücksetzen.
- Diagnosevorschau mit Positivliste und benanntem Download sowie optionale Companion-Fertigmeldungen (standardmäßig aus).
- Vollständige deutsche/englische Oberfläche; Rezepte, Freigaben, Favoriten, Bilder und Historie bleiben lokal gespeichert.

## Installation und Einrichtung

1. `https://github.com/Bhomas86/ha-airfryer-recipes` in HACS als benutzerdefiniertes **Integrationsrepository** hinzufügen.
2. **v0.2.0** installieren, Home Assistant neu starten und Browser/Companion-App vollständig neu öffnen.
3. **Airfryer Recipes** unter Einstellungen → Geräte & Dienste hinzufügen. Rezeptverwaltung benötigt weder Gerät noch Cloud-Zugangsdaten.
4. Dashboard → Bearbeiten → Karte hinzufügen → **Airfryer Recipes**. Kein Dashboard wird automatisch angelegt oder verändert. Stabile Versionen blenden Geräte-/Entwicklertests und den Karten-Testmodus aus. Karten verwenden normales bestätigtes Bereitstellen; Beta-Versionen zeigen die Testwerkzeuge wieder.
5. Für normale Benutzer das gesamte Gerät ausdrücklich in der Admin-Rezeptbibliothek freigeben und die Karte aktualisieren.
6. Pro Fach Rezept/manuelle Werte wählen. Senden verlangt einen bewussten Klick und die Bestätigung der genauen Werte. Garstart erfolgt am Gerät.

## Unterstütztes Gerät und Controller

| Funktion | Geprüfter Umfang |
| --- | --- |
| Gerätevorbereitung | Cosori Turbo Tower Pro Smart **CAF-DC111S-AEU** |
| Einzelnes Fach senden und Fertigmeldungen | Airfryer Control **1.0.3-beta.3**, **1.0.3**, **1.0.4-beta.1** |
| SYNC-/MATCH-Bereitstellen | Airfryer Control **1.0.3** oder **1.0.4-beta.1** |
| Home-Assistant-Basis | **2026.10.0** oder neuer, mit geprüftem Controller-Vertrag |
| Andere Geräte/Controller-Releases | Rezeptverwaltung bleibt verfügbar; keine ungeprüfte Übertragung wird aktiviert |

Airfryer Control ist für die Rezeptverwaltung optional und verwaltet seine bestehende VeSync-Verbindung. Airfryer Recipes speichert keine zusätzlichen Cloud-Zugangsdaten. Kombiniertes Bereitstellen nutzt unseren eigenen abgesicherten Adapter zum geprüften internen Transport; keine Controller-Änderung erforderlich. Andere Controller-Versionen bleiben bis zur Prüfung ausdrücklich gesperrt.

## Alltag und Sicherheit

Beide Fachentwürfe unabhängig einstellen. **SYNC** bereitet unterschiedliche Zeiten für einen gemeinsamen Abschluss vor; **MATCH** verwendet ausdrücklich Fach 1 für beide Fächer. Beide Fächer müssen frisch bereit/aus melden; vorbereitete Programme und kombinierten Modus vor einer neuen kombinierten Vorbereitung am Gerät freimachen. Kein Heizstart, Software-Zeitsteuerungsersatz, automatisches Wiederholen oder Nachholen alter Befehle wird angefordert.

Eine angenommene Antwort bedeutet Annahme durch den Adapter, keine unabhängige Bestätigung am Gerät. Gerät kontrollieren. Nach unklarem Ergebnis nicht erneut senden: Beide Fächer physisch prüfen/freimachen und anschließend ausdrücklich lesend neu freigeben. Geräteschutz und physischer manueller Start bleiben erhalten.

Administratoren können Fertigmeldungen pro Fach und Companion-Ziel einrichten. Nur ein beobachteter frischer Übergang gart→fertig löst eine Nachricht aus; unklare/unterbrochene Folgen dürfen bewusst ohne Meldung bleiben. [Einrichtung und Verhalten](docs/reports/ISSUE_10_SUPPORT.de.md).

Diagnoseexport verwendet ausschließlich freigegebene technische Felder mit Vorschau vor Download. Persönliche/Gerätekennungen, Namen, Netzwerkadressen, Zugangsdaten, Rezepte und Bilder sind ausgeschlossen. Der benannte HTTP-Download erhält genau die Vorschau und verlangt aktuelle Administratorrechte. [Abnahme und Downloadverhalten](docs/reports/B26_ACCEPTANCE_AND_DOWNLOAD.de.md).

## Release und Prüfung

[Release Notes 0.2.0](docs/releases/0.2.0.de.md) · [Abschließende Releasefreigabe](docs/reports/RELEASE_0_1_0.de.md) · [SYNC-/MATCH-Entwurf und Abnahme](docs/reports/ISSUE_1_OWN_GUARD.de.md) · [Anforderungen](docs/REQUIREMENTS.de.md) · [Roadmap](docs/ROADMAP.de.md).

Der Eigentümer bestätigt Gerätevorbereitung, SYNC/MATCH, Abbrechen ohne Senden, keinen automatischen Heizstart, Speicherung, Berechtigungen und eine echte Fertigmeldung. Die Diagnose-Dateinamenkorrektur wurde ohne erneuten Handytest akzeptiert; diese Unterscheidung ist dokumentiert. Automatisierte Tests verwenden Simulationen statt echter Geräte. Frühere Beta-Notizen/-Berichte bleiben unter `docs/releases` und `docs/reports` als historische Nachweise erhalten.

Fehler und bestätigte Gerätekompatibilität über [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues) melden. Dieses Projekt ist unabhängig von Cosori, VeSync und den Entwicklern von Airfryer Control.
