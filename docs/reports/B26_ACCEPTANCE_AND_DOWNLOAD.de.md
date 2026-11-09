# b26-Abnahme und Dateiname des Diagnosedownloads

[English](B26_ACCEPTANCE_AND_DOWNLOAD.md) | [Deutsch](B26_ACCEPTANCE_AND_DOWNLOAD.de.md)

## Eigentümerabnahme, 2026-11-09

Der Eigentümer meldet den vorherigen b26-Abnahmeplan als bestanden: SYNC-/MATCH-Vorschau, Bestätigung abbrechen, SYNC bereitstellen, MATCH bereitstellen und kein automatischer Heizstart. Diagnoseexport funktionierte; der Dateiname war kryptisch. Regeln blieben nach Neustart erhalten. Eine Rückfrage bestätigt ausdrücklich genau eine Fertigmeldung auf dem Handy nach einem tatsächlich beendeten Garvorgang. Dies sind Eigentümerberichte, keine unabhängigen Cloud-Gerätemessungen; genaue Controller-Version/Werte wurden nicht nochmals einzeln genannt.

Das übermittelte JSON nennt b26 und enthält nur die neun vorgesehenen freigegebenen technischen Felder (Schema-/Integrationsversion, Lade-/Verfügbarkeitsangaben und Regelanzahl), ohne persönliche/Gerätekennungen, Namen, Rezepte, Zugangsdaten oder Netzwerkadressen. Der Anhang selbst wurde nicht ins Repository übernommen.

Die vorherige Eigentümerfreigabe erlaubt die PR-#48-Freigabe nach erfolgreichen Tests. Nach dieser Abnahme wurde PR #48 mit `ba44ba5e9fb2f9ae53aceb3016a19f6c709f2dc3` nach main zusammengeführt. Die Dateinamenkorrektur liegt separat im Folgezweig; keine Controller- oder Sendeverhaltensänderung. Die gezielte native Bereitstellungsabnahme zu #1 ist abgeschlossen. Zu #10 verbleiben nur diese Exportverbesserung/-prüfung und die abschließende Releasevalidierung als relevante Folgearbeit.

## Begrenzte Korrektur (b27-Entwicklung)

Der alte Download nutzte eine Blob-URL und das HTML-Downloadattribut. Android/Companion kann solche Downloads nach ihrer Blob-UUID benennen. Das passt zum hochgeladenen Dateinamen; native WebView-Interna wurden nicht aufgezeichnet.

Der neue Download verwendet einen authentifizierten HTTP-Anhang mit demselben lesbaren Namen sowohl im URL-Dateinamen als auch in `Content-Disposition`: **`airfryer-recipes-diagnostics.json`**. Keine Blob-URL mehr. Das Backend hält genau das angezeigte Vorschau-JSON zehn Minuten in einem begrenzten, benutzergebundenen reinen Arbeitsspeicher. Ein separater Administratorbefehl signiert nach Eigentumsprüfung einen 30 Sekunden gültigen Downloadlink. Der HTTP-Handler prüft aktive Administratorrechte, Eigentümer, Ablauf und geladene Integration erneut. Er liefert No-Store-/Nosniff-Header. Neue Vorschauen ersetzen die vorherige desselben Benutzers; maximal 128 aktive Benutzer; abgelaufene Einträge werden bereinigt, Entladen leert den Cache. Kein beliebiges Client-JSON oder eigener Dateiname wird akzeptiert. Eine passende Ablaufmeldung bittet um erneutes Anzeigen der Vorschau.

Diagnoseinhalt/Positivliste, Gerätesteuerung und Benachrichtigungsverhalten bleiben unverändert. Deutsche/englische Rückmeldungen und Dokumentation zusammen gepflegt. Dieser PR veröffentlicht keine neue Beta und führt die Dateinamenkorrektur nicht automatisch zusammen.

## Prüfung und verbleibender Schritt

Lokal bestanden: **291 Python-Tests unter 3.12.14 und 136 Frontend-Tests**, Kompilierung und `git diff --check`. Neue Regressionen prüfen tatsächlichen Antwortdateinamen/Header, unveränderten Vorschauinhalt, aktuelle Admin-/Eigentümerrechte, Ablauf/Ersetzen, Cachegrenzen, signierte URL und exakte Vorschaukennung sowie passende UI-Ablaufmeldung. Python 3.14 fehlt in der aktuellen Laufzeit; keine neuen Actions oder echten HA-/Companion-Aufrufe.

Nach Installation der Korrektur App vollständig neu öffnen, neue Diagnosevorschau anzeigen und herunterladen. Name `airfryer-recipes-diagnostics.json` sowie Übereinstimmung mit der Vorschau prüfen. **Für diese reine Downloadkorrektur sind keine erneuten SYNC-/MATCH-Gerätetests nötig.** Aktuelle Python-Matrix-/HACS-/Hassfest-Nachweise und stabile Versions-/Releasemetadaten bleiben vor Stable getrennt erforderlich; aus der Abnahme wird keine zusätzliche Actions-Freigabe abgeleitet.
