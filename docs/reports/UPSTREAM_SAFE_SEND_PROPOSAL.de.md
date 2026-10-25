# Entwurf: Unterstützte Schnittstelle für einmaliges, sicheres Bereitstellen

[Deutsch](UPSTREAM_SAFE_SEND_PROPOSAL.de.md) | [English](UPSTREAM_SAFE_SEND_PROPOSAL.md)

**Status: vom Eigentümer auf Deutsch veröffentlicht und vom Entwickler beantwortet.** Die englische Begleitdatei dient der internen zweisprachigen Projektdokumentation.

**Vorgeschlagener Titel:** Rezeptverwaltung für Airfryer Control – Anbindung und benötigte Schnittstellen

---

Hallo,

wir hatten ja bereits wegen zweier Issues Kontakt. Ich möchte dir kurz vorstellen, was ich gerade auf Basis deiner Integration plane und welche Schnittstellen dafür hilfreich wären.

Ich entwickle mit Unterstützung von Codex eine zusätzliche Home-Assistant-Integration namens [Airfryer Recipes](https://github.com/Bhomas86/ha-airfryer-recipes). Sie soll einfache Rezepte mit Programm, Temperatur und Garzeit lokal verwalten. Die Rezeptbibliothek mit Kategorien, persönlichen Favoriten und JSON-Import/-Export funktioniert bereits und wurde von mir in Home Assistant getestet.

Als Nächstes ist eine Dashboard-Karte geplant: Airfryer und Fach auswählen, ein Rezept laden oder Werte manuell einstellen und anschließend bewusst übertragen. Die Gerätekommunikation und VeSync-Anmeldung sollen weiterhin vollständig über **Airfryer Control** laufen. Die Rezeptverwaltung soll auch ohne angeschlossenes Gerät funktionieren.

Mein erstes Zielgerät ist die **Cosori Turbo Tower Pro Smart CAF-DC111S-AEU**. Der Start des Garvorgangs soll weiterhin manuell am Gerät erfolgen. SYNC und MATCH sind für später vorgesehen.

Bei der Prüfung deines Quellcodes, Stand `5a3c530` / Version 1.0.1, sind für diese Anbindung vier Punkte aufgefallen:

1. **Ein festgelegter Sendeversuch ohne automatische Wiederholung.** `programm_senden` probiert über `async_send` bei Ablehnungen mehrere Befehlsvarianten. Zusätzlich kann `bypass_v2` über `_with_relogin` dieselbe Anfrage nach erneuter Anmeldung wiederholen. Für unsere Bedienung möchten wir einen Modus, der genau die festgelegte Variante höchstens einmal sendet. Nach einem unklaren Ergebnis soll der Benutzer selbst über einen neuen Versuch entscheiden. Eine nötige Anmeldung vor dem eigentlichen Senden wäre selbstverständlich möglich.

2. **Verlässlich aktuelle Zustände je Gerät und Fach.** Dafür wären der Zeitpunkt der letzten erfolgreichen Gerätemeldung und ein eindeutiger Fehler-/Verbindungsstatus hilfreich. Ein nicht gemeldetes Fach müsste von einem tatsächlich als „bereit“ gemeldeten Fach unterscheidbar sein. Aktuell liefert der Fachsensor bei fehlender Fachmeldung ebenfalls „bereit“. Alte Daten oder ein insgesamt erfolgreicher Koordinator-Refresh sollen keine Sendeerlaubnis begründen. Eine Statusrevision würde zusätzlich helfen, Änderungen zwischen Vorschau und Bestätigung zu erkennen.

3. **Bestätigte Programme und Grenzen pro Modell und Fach.** Die Oberfläche soll nur tatsächlich unterstützte Programme und passende Temperatur-/Zeitbereiche anbieten. Welche davon sind für die CAF-DC111S-AEU bereits bestätigt? Die allgemeinen TwinFry-Werte möchten wir nicht ungeprüft für andere Modelle übernehmen. Werte sollen auch nicht unbemerkt beim Senden begrenzt werden.

4. **Eine unterstützte Schnittstelle zum Bereitstellen ohne Heizstart.** Ideal wäre eine klar definierte Aktion oder Python-Schnittstelle mit Gerät, Fach, Programm, Temperatur und Minuten. Unsere Integration soll weder private Methoden aufrufen noch eigene Cloud-Zugangsdaten verwalten. Bei der Rückmeldung wäre die Unterscheidung zwischen „Befehl angenommen“, „Werte am Gerät bestätigt“ und „Ergebnis unbekannt“ hilfreich, soweit sich das feststellen lässt.

Wären solche Ergänzungen für dich grundsätzlich denkbar, oder gibt es dafür bereits einen vorgesehenen Weg? Mir geht es vor allem darum, die Anbindung mit dir abzustimmen und nicht an deiner Integration vorbeizubauen.

Bis zur Klärung bleibt die echte Übertragung bei uns deaktiviert. Vorhanden sind eine lesende Geräteerkennung und eine Testvorschau ohne Steuerbefehle. Änderungen während eines laufenden Garvorgangs bleiben zunächst ebenfalls gesperrt. Das sind Anforderungen an unsere geplante Anbindung; damit möchte ich keinen bestätigten Sicherheitsfehler deiner Integration behaupten.

Danke dir für deine bisherige Unterstützung!

## Ergebnis vom 25.10.2026

Der Entwickler bestätigte alle vier Beobachtungen und stellte anschließend Airfryer Control `1.0.2-beta.1` im Branch `beta` bereit. Der Stand `f43a9bf8ddb7cc65e27897dd92158cc06840bc08` enthält:

- `variante` und `einmal: true` für genau eine sichere Schreibweise ohne automatische Wiederholung,
- `letzte_meldung`, `verbindung`, `revision` und das Fachattribut `gemeldet`,
- den öffentlichen lesenden Dienst `airfryer_control.faehigkeiten`,
- `streng: true` gegen stille Begrenzung,
- `ergebnis` mit `angenommen`, `abgelehnt` oder `unbekannt` sowie optional `bestaetigt`.

Für die CAF-DC111S-AEU bleiben alle Programme und Grenzen geschätzt/ungeprüft. Der Dienst liefert sechs Programme; das am Gerät sichtbare `proof` fehlt noch. Airfryer Recipes nutzt zunächst ausschließlich `faehigkeiten` für die Testvorschau. Eine echte Übertragung bleibt getrennt und gesperrt.
