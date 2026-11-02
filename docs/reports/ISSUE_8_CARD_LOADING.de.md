# Card fehlt im Katalog — Korrektur der Modulregistrierung

[Deutsch](ISSUE_8_CARD_LOADING.de.md) | [English](ISSUE_8_CARD_LOADING.md)

Der Eigentümer meldete die fehlende Airfryer-Recipes-Card im Dashboard-Kartenkatalog und bestätigte die installierte b13. Der Screenshot zeigt die Karten von Airfryer Control, die zur anderen Integration gehören. Ein Ladeabbruch durch doppelte Elementregistrierung wurde offline reproduziert; der genaue Browserfehler der Eigentümerinstanz wurde nicht erfasst, ein HA-Neustart nach dem Update nicht bestätigt.

## Reproduzierter Fehler und Korrektur

Existiert das Element der Rezeptansicht bereits, wirft der Import einer weiteren über den URL-Parameter versionierten Kopie von `panel.js` bei deren unbedingtem `customElements.define` einen Fehler. Das abhängige Card-Modul bricht ab, bevor es sein Element oder den Eintrag in `window.customCards` registriert. Die bisherigen Bedienungstests entfernten den Import und verwendeten eine Registry-Attrappe, die doppelte Definitionen erlaubte; diesen Ladefehler deckten sie daher nicht ab.

Beta 0.1.0b14 schützt die Panel-Elementdefinition und exportiert die aktuelle Panel-Klasse. Die Card importiert diese Klasse direkt und erbt davon. Eine vorhandene Rezeptansicht bleibt registriert; die Card verwendet ihren aktuellen mitgelieferten Ablauf statt eines möglicherweise älteren Konstruktors aus der Registry. Panel-/Card-Modul-URLs und die Card-Abhängigkeit verwenden dieselbe neue Version. Keine Änderung an Rezept-/Historienspeicher, Rechten, Vorschau oder Geräteübertragung.

Vier neue Tests laden die **unveränderten mitgelieferten ES-Module zusammen**, einschließlich ihres tatsächlichen relativen Imports, mit einer Registry, die doppelte Namen/Konstruktoren abweist: leere Seite, aktuelles Panel zuerst, älteres Panel zuerst und mehrere URL-Versionen. Geprüft werden Katalogeintrag, Editor, aktuelle Basisklasse, erhaltenes vorhandenes Panel und fehlende Doppeleinträge. Geprüft werden Node-Imports; Browserdarstellung und HA-HTTP-Auslieferung werden dabei nicht simuliert.

## Installation und lokale Prüfung

1. In HACS für **Airfryer Recipes** die **v0.1.0b14** installieren, Home Assistant neu starten und Companion-App/Browser vollständig neu laden/öffnen. Ein Update nur von Airfryer Control aktualisiert diese Card nicht.
2. Dashboard → Bearbeiten → Karte hinzufügen → **Airfryer Recipes** suchen. Card und Rezeptansicht in beiden Reihenfolgen öffnen. Testmodus aktiviert lassen; für die Sichtbarkeitsprüfung ist keine Geräteübertragung nötig.
3. Falls sie weiter fehlt: Einstellungen → Dashboards → Menü → Ressourcen prüfen (gegebenenfalls im Benutzerprofil den erweiterten Modus aktivieren). Folgende URL als **JavaScript-Modul** hinzufügen oder einen vorhandenen Eintrag genau dieser Card aktualisieren, statt ein Duplikat anzulegen:

   ```text
   /api/airfryer_recipes/card.js?v=0.1.0b14
   ```

   App neu laden und „Karte hinzufügen“ erneut öffnen. Dies ist eine Alternative zum automatischen Modulladen der Integration. Einen manuell festgelegten Ressourceneintrag bei späteren Updates anpassen/entfernen; keine älteren Kopien neben der aktuellen belassen.
4. Manuelle Kartenkonfiguration, nachdem ihr Modul geladen ist:

   ```yaml
   type: custom:airfryer-recipes-card
   title: Airfryer Küche
   dry_run: true
   ```

Falls sie weiter nicht verfügbar ist, den exakten Text aus der manuellen Kartenvorschau und vorhandene HA-Frontend-Meldungen zu `card.js`/`panel.js` festhalten. Zur Diagnose keine Geräteeinstellungen senden. Native HA-/Companion-Abnahme bleibt offen.

## Prüfung

Lokal bestanden: **170 Python- und 84 Frontend-Tests** (59 Panel, 21 Card, 4 vollständige Modulladetests), Kompilierung, Dokulinks/Sprachpaare und Diff-Formatprüfung. Der ursprüngliche b13-Fehler der doppelten Elementregistrierung wurde vor der Korrektur reproduziert. Keine GitHub Actions; HACS/Hassfest, Python 3.14, nativer Browser/HA/Companion und neue Geräteprüfung wurden nicht ausgeführt. Der vorhandene Workflow enthält die ergänzten Modultests nur für einen später ausdrücklich freigegebenen Lauf.
