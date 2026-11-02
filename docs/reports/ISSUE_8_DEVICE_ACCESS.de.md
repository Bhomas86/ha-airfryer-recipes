# Ganze Geräte für normale HA-Benutzer freigeben

[Deutsch](ISSUE_8_DEVICE_ACCESS.de.md) | [English](ISSUE_8_DEVICE_ACCESS.md)

Beta 0.1.0b16 setzt Anforderung 17 nach der grundlegenden Card-Abnahme des Eigentümers um: Senden an beide Fächer, erneute Verwendung nach physischem Zurücksetzen, korrekte zuletzt gesendete Werte je Fach und Erhalt über HA-Neustart. Der frühere Versuch mit Grillen bei 200 °C wurde wegen des geprüften Adapterbereichs gesperrt; er belegt keinen Berechtigungsfehler von Fach 2. Daraus wird keine neue Grill-Grenze oder erweiterte Temperaturabnahme abgeleitet.

Der Eigentümer bestätigt auch die automatische Aktualisierung der bestehenden Dashboard-Ressourcen-URL; Anlegen auf einer frischen HA-Instanz bleibt ungeprüft.

**Umfangskorrektur des Eigentümers:** Ein ganzes Gerät für einen Benutzer freigeben, einschließlich aller Fächer und verfügbaren Programme. Keine einzelnen Fach-, Programm- oder Menüfreigaben. Bestehende Modell-/Programm-/Bereichs-, Bereitschafts- und beaufsichtigte Bestätigungsprüfungen gelten weiter; Gären und erweiterte Temperaturen bleiben zurückgestellt.

## Verhalten und Speicherung

Administratoren öffnen in der Rezeptbibliothek **Geräteberechtigungen → Gerätefreigaben verwalten**, wählen einen aktiven normalen HA-Benutzer und ein erkanntes Gerät und geben es ausdrücklich frei. Vorhandene Freigaben haben einen Entziehen-Button. Administratoren behalten grundsätzlich alle Geräte und verwalten allein Rezepte, Import/Export, Berechtigungen und geführte Testwerkzeuge. Normale Benutzer haben standardmäßig keinen Gerätezugriff. Nach Freigabe/Entzug aktualisieren sie ihre Card und dürfen Rezepte oder manuelle Werte für beide Fächer eines freigegebenen Geräts wählen. Sie sehen die gemeinsam gespeicherten zuletzt gesendeten Werte dieses Geräts. Rezeptdaten bleiben geräteunabhängig und unverändert.

Freigaben liegen im getrennten HA Store `airfryer_recipes.device_access`, Schema 1: Benutzer-IDs mit Geräte-IDs. Ein gesundes Repository samt Sperre wird über Integrationsneuladen weiterverwendet; normale Sendebestätigungen sind flüchtig und werden nie wiederhergestellt. Fehlende Freigaben sperren; beschädigte/neuere Daten bleiben unangetastet und sperren Benutzerfreigaben/Schreiben, während Admin-Bedienung und Rezeptverwaltung nutzbar bleiben. Fehlgeschlagene Speicherung erhält die bisherigen Freigaben. Berechtigungsverwaltung sendet keinen Gerätebefehl; Erkennung verwendet ausschließlich den vorhandenen lesenden Fähigkeitsdienst.

Diese Berechtigungen gelten für **Airfryer Recipes**. Sie beschränken nicht die eigenständige Integration Airfryer Control, andere HA-Aktionen oder Hersteller-Apps.

## Durchsetzung im Backend

Der neue authentifizierte Endpunkt `control` akzeptiert ausschließlich die freigegebenen Operationen Erkennung, Historie, Testvorschau, Vorbereitung gewählter Rezept-/manueller Werte, Bestätigung, Verwerfen und lesende Wiederfreigabe. Felder je Operation sind exakt festgelegt; Benutzeridentität stammt immer aus der angemeldeten Verbindung. Kein Client-Feld darf einen anderen Akteur wählen oder Admin-Werkzeuge aktivieren. `access_list` und `access_set` sind adminpflichtig und prüfen den aktuellen aktiven Administrator nach asynchroner Erkennung erneut. Inaktive/Systemkonten erhalten/nutzen keine normalen Freigaben. Entziehen funktioniert auch für gelöschte Benutzer oder nicht verfügbare Geräte.

Normale Erkennung filtert Geräte-IDs **vor** Fähigkeitsdienst-Aufrufen und vor der Rückgabe erneut. Historie und Vorschau prüfen das gewählte Gerät vor und nach dem Lesen; Vorschau bleibt serverseitig ohne Steueraufrufe. Ohne jede Freigabe liefert die Erkennung keine Geräte, ohne den Adapter abzufragen. Die bisherigen Admin-Endpunkte bleiben adminpflichtig.

Der einmalige Sender prüft aktives Konto/Gerätefreigabe während der Vorbereitung, nach frischer Validierung und unmittelbar vor der Übertragung erneut. Bestätigungen binden Benutzer, Verbindung, exakte Werte, Rezeptstand, Gerät und Fach. Jede Freigabeänderung erhöht **vor** dem Speichern eine Laufzeitrevision und sperrt normale Übertragungen während des Schreibens. Vorsorglich werden durch jede Änderung sämtliche zuvor vorbereiteten Bestätigungen normaler Benutzer ungültig, auch nach Entziehen/Wiederfreigeben oder Schreibfehler. Die Bestätigung ihres rechtmäßigen Eigentümers wird vor asynchroner Autorisierung verbraucht und kann nach einem Fehler nicht wiederholt werden. Ein aktiver Eigentümer darf auch nach Entzug verwerfen. Ein bereits übergebener Transport kann nicht zurückgerufen werden; Entzug verhindert neue Übergaben und löst keine Wiederholung aus.

Die Card verwendet für normale Benutzer den begrenzten Gerätezugriff, zeigt nur zurückgegebene Geräte und behält voreingestellten Testmodus sowie eine Bestätigung der exakten Werte. Konto-/Rollenwechsel leeren zwischengespeicherte Freigaben/Entwürfe/Historie; Offline-/Seitenwechselsperren und Verwerfen bleiben aktiv. Der grafische Karteneditor kann keine Rechte erteilen. Normale Wiederfreigabe benötigt bestätigtes physisches Zurücksetzen, liest frischen Ruhezustand und kann keinen Admin-Testlauf unterbrechen. Kein Garstart, Puffer, Wiederholen, Ändern laufender Fächer, Rohbefehl, SYNC oder MATCH kommt hinzu. Adapterbindung `1.0.2-beta.1` und geprüfter Vertrag für CAF-DC111S-AEU bleiben bestehen.

## Lokale Abnahme ohne neue Geräteübertragungen

1. v0.1.0b16 über HACS installieren, HA neu starten und beide Sitzungen vollständig neu laden. Card-/Ressourcenkonfiguration bleibt erhalten; die Ressourcen-URL wird auf b16 aktualisiert.
2. Ein vorhandenes separates **normales HA-Konto** verwenden, nicht die Admin-Sitzung. Ohne Gerätefreigabe muss dessen Card keinen Gerätezugriff zeigen. Die Rezeptverwaltung bleibt adminpflichtig.
3. Als Admin: Rezeptbibliothek → Geräteberechtigungen → Gerätefreigaben verwalten → Benutzer/Gerät wählen → Gerät freigeben. Es darf keine Fach-/Programmauswahl für die Freigabe geben.
4. Card des normalen Benutzers aktualisieren. Beide Fächer und gemeldete Programme dieses Geräts müssen verfügbar sein. `dry_run: true` beibehalten; Rezept-/manuelle Testvorschau auf jedem Fach prüfen. Keine Einstellungen werden übertragen, die Historie bleibt unverändert.
5. Als Admin entziehen, normale Card aktualisieren: Gerät muss verschwinden. Erneut freigeben, HA neu starten und erhaltene Freigabe prüfen. Andere Benutzer/Geräte bleiben ohne Freigabe. Vorhandene Rechte lassen sich auch bei offline gemeldetem Gerät entziehen.

Backend-Tests simulieren außerdem Entzug zwischen Vorbereitung und Bestätigung sowie während der abschließenden Validierung; dafür sind keine echten Geräteübertragungen nötig. Native Zwei-Konten-Abnahme in HA/Companion dieses neuen Pakets bleibt offen. Daraus folgt keine Abnahme sämtlicher Programmgrenzen oder Unterbrechungsfälle am Gerät.

## Prüfung

Lokal bestanden: **203 Python- und 93 Frontend-Tests** (62 Panel, 27 Card, 4 Modulladen), Kompilierung, Dokulinks/Sprachpaare und Diff-Formatprüfung. Neu abgedeckt: Standardsperre, Ganzgerät-/Benutzertrennung, Neustart, beschädigter/neuerer/fehlerhafter Speicher, paralleles Schreiben, inaktive/Systemkonten, gefälschte Felder/Akteure, gefilterte Erkennung, Historie, Testvorschau, exakte Rezeptübertragungen beider Fächer durch echte Routen/Repository/Sender, Entziehen/Wiederfreigeben, Entzug während Schreibvorgängen, Aufräumen und adminpflichtige Änderungen/Werkzeuge. Native neue Rechteoberfläche/Zwei-Konten-HA, HACS/Hassfest und Python 3.14 wurden nicht ausgeführt. Keine GitHub Actions. Nur die aktuell geprüfte Beta bleibt veröffentlicht; ältere werden zu Entwürfen, Tags/Code/Assets bleiben erhalten.
