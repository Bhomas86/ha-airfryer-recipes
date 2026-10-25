# Entwurf: Unterstützte Schnittstelle für einmaliges, sicheres Bereitstellen

[Deutsch](UPSTREAM_SAFE_SEND_PROPOSAL.de.md) | [English](UPSTREAM_SAFE_SEND_PROPOSAL.md)

**Status: nicht veröffentlicht.** Vorgeschlagener Issue-Titel: `Sichere einmalige Bereitstellung und Statusaktualität / Safe single-attempt preparation and telemetry freshness`.

Hallo, wir entwickeln mit Airfryer Recipes eine geräteunabhängige Rezeptverwaltung, die Airfryer Control optional als Geräteadapter verwenden soll. Zielgerät ist zunächst eine Cosori Turbo Tower Pro Smart CAF-DC111S-AEU. Es geht ausschließlich um Bereitstellen mit anschließendem manuellem Start am Gerät.

Bei der Quellcodeprüfung von Revision `5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee` sind für unsere Anbindung folgende Fragen entstanden:

- `programm_senden` verwendet `async_send`, das bei Ablehnungen mehrere Varianten versucht. `bypass_v2` verwendet außerdem `_with_relogin`, das eine Anfrage nach Authentifizierungsfehler wiederholt. Gibt es eine unterstützte Möglichkeit für höchstens einen Steuer-Transportversuch ohne Varianten-Fallback und ohne Replay nach Versandbeginn? Wir möchten weder private Methoden aufrufen noch eigene VeSync-Anmeldung implementieren.
- Gibt es erfolgreiche Erfassungszeitpunkte und Statusrevisionen pro Gerät/Fach oder wäre eine solche Schnittstelle möglich? Ein globaler Refresh und der Ersatzwert „bereit“ für ein nicht gemeldetes Fach reichen für unsere Sicherheitsprüfung nicht aus.
- Welche Programme, Grenzen und Fachzuordnungen sind für CAF-DC111S-AEU bestätigt? Die globalen TwinFry-Konstanten möchten wir nicht ungeprüft übertragen.
- Könnte eine unterstützte Schnittstelle diese Daten sowie eine feste Bereitstellen-Funktion anbieten, die niemals die Heizung startet und keine Rohmethoden oder Startvarianten annimmt? Bei Timeout nach Versand sollte das Ergebnis als unbekannt zurückgegeben werden; ein neuer Versuch wäre nur nach erneuter Benutzerentscheidung zulässig.

Unsere echte Übertragung bleibt bis zur Klärung deaktiviert. Bislang gibt es nur lesende Erkennung und eine serverseitige Testvorschau ohne Steueraufrufe. Wir haben keine echten Geräte aus der Cloud angesprochen und keine Änderungen an diesem Repository vorgenommen. Es handelt sich um eine Anfrage zur Interoperabilität, nicht um die Behauptung einer bestätigten Sicherheitslücke.

Die vollständigen technischen Vertragsanforderungen und Grenzen stehen im [Prüfbericht](ISSUE_7_COMMAND_CONTRACT.de.md). Dieser Entwurf ist noch keine Kommunikationsfreigabe.
