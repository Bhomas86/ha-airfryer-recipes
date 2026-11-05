# Diagnose und Fertigmeldungen — Issue #10

[English](ISSUE_10_SUPPORT.md) | [Deutsch](ISSUE_10_SUPPORT.de.md)

Im b24-Entwicklungszweig umgesetzt. Die native Abnahme steht aus; dies ist kein stabiler Release und keine Behauptung, dass mobile Zustellung in Home Assistant getestet wurde.

## Administratorwerkzeuge

Rezeptbibliothek → **Diagnose und Fertigmeldungen** öffnen. Diagnose anzeigen, das vollständige JSON prüfen und anschließend ausdrücklich herunterladen. Der Download verwendet genau die angezeigte Vorschau; nichts wird hochgeladen oder an GitHub gesendet. Das Backend erstellt eine Positivliste aus Integrations-/Schemaversion, Lade-/Verfügbarkeitsangaben und Anzahl der Benachrichtigungsregeln. Ausgeschlossen sind rohe Adapterdaten, Ausnahmetexte, Netzwerkadressen, Konto-/Geräte-/Benutzer-/Entitätskennungen, Dienstnamen, Rezeptdaten und Bilder. Kein automatisches Teilen. Sowohl WebSocket-Befehl als auch aktuelle Prüfung des authentifizierten Benutzers verlangen Administratorrechte.

Fertigmeldungen sind standardmäßig aus. Einstellungen laden und einen geladenen Fach-Statussensor von Airfryer Control sowie einen `notify.mobile_app_*`-Dienst aus den Listen wählen. Gewünschte Fächer separat aktivieren; ein Ziel pro Fach. Ein Administrator kann jede Regel deaktivieren. Dies sind Benachrichtigungseinstellungen, keine Steuerberechtigungen: Normale HA-Benutzer behalten ganze Gerätefreigaben ohne fachbezogene Steuereinschränkungen. Nur Administratoren konfigurieren Ziele. Die Zielauswahl erlaubt ausdrücklich die spätere Zustellung von Fertigmeldungen an dieses Companion-Gerät. Beim Konfigurieren wird kein Test-Push gesendet.

## Abschlussvertrag und Datenschutz

Geprüfter Controller: Airfryer Control **1.0.3-beta.3**, Commit `a9fc49e37c3d2698d21bfb361192717ff790eb6e`, `sensor.py`, `entity.py` und `core/parser.py`. Nur aktivierte, geladene Fach-1/2-Statusentitäten des Controllers mit ihrer Registry-Identität werden akzeptiert. Andere Controller-Versionen bieten keine auswählbaren Quellen. Regeln binden Entität, eindeutige Kennung, Konfigurationseintrag und Gerät; eine neu zugeordnete Entität übernimmt keine Benachrichtigungen.

HA-Zustandsereignisse werden ohne Polling oder Gerätedienstaufrufe beobachtet. Einer frischen, ausdrücklich gemeldeten Probe `gart` muss `fertig` folgen, mit steigender Meldezeit und Revision und höchstens 90 Sekunden Abstand. Jede Probe darf höchstens 90 Sekunden alt und nicht zukünftig datiert sein, mit `gemeldet: true` und `verbindung: ok`. Nicht verfügbare, fehlerhafte, veraltete, bereite, abgebrochene, pausierte, schubladenoffene und unbekannte Zustände verwerfen die Vormerkung. Identische wiederholte Garberichte erhalten sie; doppelte oder rückwärts laufende Fertigberichte senden nie erneut. Kein Ableiten aus Restzeit oder prognostizierter Fertigzeit. Die konservative Erkennung kann einen echten Abschluss nach Unterbrechung oder Pause verpassen; es wird keine Ersatzmeldung erfunden.

Vormerkungen existieren nur im Arbeitsspeicher. Neustart/Entladen/Konfigurationsänderungen löschen sie; kein Abschluss wird nachgeholt. Der ursprünglich konfigurierende Administrator muss beim Zustellversuch weiterhin aktiv und Administrator sein. Quellenidentität, vorhandenes Ziel, aktueller Zustand und Frische werden vor dem Senden geprüft. Nachrichten enthalten nur „Fach 1/2 meldet: fertig.“ in der eingestellten Sprache Deutsch/Englisch sowie den festen Titel „Airfryer Recipes“; keine Geräte-/Rezeptnamen, Temperaturen oder Kennungen. Zustellfehler erhalten allgemeine Logmeldungen und keine automatische Wiederholung. Beim Herunterfahren von HA wird nicht zugestellt. Keine neuen Heiz-/Steuerbefehle.

Regeln verwenden einen separaten versionierten, verifiziert atomaren lokalen Speicher. Fehlgeschlagenes Speichern aktiviert keine neuen Einstellungen; beschädigte/neuere Daten bleiben erhalten, Benachrichtigungen bleiben aus. Rezepte und Gerätefreigaben sind unabhängig. API-Fehler geben allgemeine Meldungen zurück. Einstellungen und Diagnose sind nur für Administratoren zugänglich.

## Prüfung und native Abnahme

Offline-Tests prüfen Datenschutz-Positivliste, aktuelle Administratorrechte, strikte Befehlsparameter, unabhängige Fächer, doppelte/falsch sortierte Berichte, Neustart, veraltete/ungültige/zukünftige Zeitstempel, Offline/Unbekannt/Abbruch/Pause, entzogene Rechte, neu zugeordnete Quellen, standardmäßig aus, Zustellfehler ohne Wiederholung, Speicherfehler/beschädigte Daten, Deaktivieren und Listener-Abmeldung. Frontend-Tests prüfen ausdrückliche Vorschau, Admin-Sichtbarkeit, Maskierung und genaue Deaktivierungsanfragen. Kein echtes Gerät, mobiler Push oder LAN-Zugriff wurde verwendet.

Native Prüfungen nach Installation/Neustart:

1. Administrator öffnet Werkzeuge; JSON anzeigen/herunterladen und ausgeschlossene Daten prüfen. Normale Benutzer dürfen keine Werkzeuge sehen; direkte Befehle müssen abgewiesen werden.
2. Anfangs keine Regeln. Ein Fach aktivieren und vorgesehenes Companion-Ziel wählen; nach Aktualisierung/Neustart muss die Regel erhalten sein. Konfiguration darf keinen Push senden.
3. Bei einem gewöhnlichen beaufsichtigten Garvorgang, der physisch am Gerät gestartet wird, genau eine Meldung beim gemeldeten Abschluss dieses Fachs prüfen. Das andere Fach unabhängig prüfen. Kein leeres Gerät allein für diesen Test aufheizen.
4. Garvorgang abbrechen, Regel deaktivieren und Offline-/Wiederverbindungsfall prüfen: keine falsche Fertigmeldung. Neustart bei bereits fertigem Programm darf keine alte Meldung auslösen.
5. Regeln nach dem Test bei Bedarf deaktivieren. Rezept/Karte/Gerätefreigaben weiter prüfen. Tatsächliche Ergebnisse vor Schließen von #10 dokumentieren.

Der Teil zur Releasevorbereitung hat bereits erfolgreiche vollständige Python-/Frontend- sowie HACS-/Hassfest-Actions für b23 in PR #46. Diese Nachweise gelten nicht für die neuen Änderungen. Der Eigentümer hat Actions gezielt für #46 freigegeben; neue Arbeit wird unter der fortbestehenden CI-Pause lokal geprüft.

Lokales Ergebnis: **249 Python-Tests jeweils unter Python 3.12.14 und 3.14.8; 128 Frontend-Tests bestanden**. Kompilierung und `git diff --check` bestanden. Deutsche/englische Dokumentation und UI-Texte inhaltlich abgeglichen.
