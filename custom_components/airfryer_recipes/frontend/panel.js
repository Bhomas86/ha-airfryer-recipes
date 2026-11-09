// Local Home Assistant custom panel. All mutations go through the authenticated API.
const SUPPORT_TEXT = {
  en: { expired: "The diagnostic preview expired. Show a new preview and download again.", title: "Diagnostics and completion notices", preview: "Preview diagnostics", warning: "Passwords, tokens, cookies, network addresses, personal and device IDs, names, recipes and images are excluded. Review the preview before sharing. Downloading sends nothing to GitHub.", download: "Download reviewed diagnostics", notifications: "Load completion notice settings", info: "Off by default. Choose a reported zone status sensor and a Companion mobile notification service. Only a fresh cooking → finished report triggers one notice. No notice after restart, offline gaps, cancellation or an uncertain state; no retry. Requires reviewed Airfryer Control 1.0.3-beta.3, 1.0.3 or 1.0.4-beta.1. Each zone is configured separately.", source: "Zone status sensor", target: "Mobile notification service", save: "Enable for selected zone", remove: "Disable", empty: "No completion notices enabled.", saved: "Settings saved", unavailable: "Notification settings unavailable; existing data preserved." },
  de: { expired: "Die Diagnosevorschau ist abgelaufen. Zeige eine neue Vorschau an und lade sie erneut herunter.", title: "Diagnose und Fertigmeldungen", preview: "Diagnosevorschau anzeigen", warning: "Passwörter, Tokens, Cookies, Netzwerkadressen, persönliche und Gerätekennungen, Namen, Rezepte und Bilder sind ausgeschlossen. Prüfe die Vorschau vor dem Teilen. Der Download sendet nichts an GitHub.", download: "Geprüfte Diagnose herunterladen", notifications: "Einstellungen für Fertigmeldungen laden", info: "Standardmäßig aus. Wähle einen gemeldeten Fach-Statussensor und einen mobilen Benachrichtigungsdienst der Companion-App. Nur eine frische Meldung gart → fertig löst eine Nachricht aus. Keine Nachricht nach Neustart, Offline-Lücken, Abbruch oder unklarem Zustand; keine Wiederholung. Benötigt geprüftes Airfryer Control 1.0.3-beta.3, 1.0.3 oder 1.0.4-beta.1. Jedes Fach wird separat eingestellt.", source: "Fach-Statussensor", target: "Mobiler Benachrichtigungsdienst", save: "Für gewähltes Fach aktivieren", remove: "Deaktivieren", empty: "Keine Fertigmeldungen aktiviert.", saved: "Einstellungen gespeichert", unavailable: "Benachrichtigungseinstellungen nicht verfügbar; bestehende Daten bleiben erhalten." },
};
const WORDS = {
  en: {
    chooseProgram: "Choose a program…", customProgram: "Enter a custom program", reportedPrograms: "Use reported programs",
    recipeProgramsFrom: "Program choices from", recipeProgramsInfo: "Only the program identifier is saved. The recipe remains independent of any appliance. Limits and availability are checked again before sending.",
    recipeProgramMissing: "This saved identifier is not reported by the selected appliance. Choose a reported program and save to correct it; no automatic replacement is made.",
    recipeProgramsUnavailable: "No programs were reported. You can enter an identifier manually and keep editing recipes without an adapter.",
    fixRecipeProgram: "Edit recipe program",
    betaConnection: "Connection or page changed. Old confirmations were discarded. Prepare a new test; no command will be replayed. A request already submitted cannot be recalled.",
    betaSelectionChanged: "Selection changed. Prepare the selected settings again.",
    modelTemperatures: "Appliance temperature ranges", modelOwner: "Appliance (owner report)", modelAdapter: "Adapter report",
    modelMissing: "Not reported", modelStep: "step", modelTemperatureInfo: "Supervised sending uses the intersection of the appliance range, the reviewed adapter contract and the current adapter report. Programs missing from the adapter cannot be sent. Duration limits remain unverified.",
    batchReset: "Before changing settings: end this run's prepared settings in zones 1 and 2 and verify idle state.", resetUnavailable: "No uniquely assigned loaded zone switch is available for ending. Check the Airfryer Control entities.", resetFailed: "Ending a zone failed or has an unknown outcome. Check the appliance and use re-arming before another attempt.",

    betaRecover: "Device checked – enable a new test", betaRecoverInfo: "For a new attempt, cancel prepared programs at the appliance first. Both zones must report idle/off. This check sends no control command and requires no HA restart.", betaRecoverConfirm: "Have you canceled all prepared programs at the appliance, checked both zones and remained beside it? Request a fresh read-only check and enable a new test?", betaRecovered: "Fresh idle status confirmed. Old confirmations discarded. You can show and start a new sequence without restarting HA.", betaRejected: "The adapter rejected the request. Cancel prepared programs at the appliance and use the device check before a new attempt.",

    batchTitle: "Guided appliance test", batchInfo: "One confirmation for the displayed sequence: lower, nominal and upper temperatures of seven reported programs on both zones, including Proof and its 1 °C step (30/31 °C). Up to 44 settings, one command at a time. Remain beside the empty appliance; do not press Start. The run checks reported settings between commands and stops on errors. Own prepared settings are ended before each temperature or program change. Cancel the final prepared programs at the appliance after the run.",
    batchPrepare: "Show test sequence", batchStart: "Confirm displayed sequence and start", batchStop: "Stop remaining steps",
    batchConsent: "By starting, I confirm that I am supervising the appliance and authorize every setting and the displayed zone-ending steps in this list once. No cooking start is requested.",
    batchLoading: "Reading device status and preparing the list… No settings are being sent.", batchProgress: "Step", batchOf: "of", batchDone: "Sequence completed. Reported settings matched after each command. Check both zones physically and cancel the prepared programs. No compatibility approval is implied.",
    batchStopped: "Remaining steps stopped. A submitted command cannot be recalled; inspect the appliance.", batchFailed: "Sequence stopped. A command may have arrived. Inspect the appliance; do not repeat the run until the outcome is clear.", batchSkipped: "Not included because not reported or sample values outside bounds", batchConnection: "Connection changed; this run cannot resume.",

    betaSelection: "Prepare selected settings for a supervised send",
    betaSelectionInfo: "Supervised beta: all seven reviewed programs, only when reported by the adapter and within their program limits. Maximum duration: 1440 minutes. Estimated capabilities remain unverified until local acceptance. No recipe is changed.",
    betaProgram: "This program is not in the reviewed beta contract. The selected program was not substituted.",
    betaRange: "These values are outside the appliance temperature range or reviewed adapter bounds, or exceed the 1440-minute beta limit. Reported adapter limits also apply. Nothing was clamped.",
    betaRecipeChanged: "The recipe changed or was deleted. Select it again and prepare a new confirmation.",
    betaSource: "Select a single-phase recipe or valid manual values.",
    betaRefreshing: "Requesting a fresh device status… No settings are being sent.",
    betaRefreshUnavailable: "No loaded, enabled Airfryer Control sensor is available for this device. Enable a status sensor and check the integration.",
    betaRefreshFailed: "No new successful device report followed the status request. Check the device connection in Airfryer Control. No settings were sent.",
    betaTitle: "Supervised beta device test", betaIntro: "CAF-DC111S-AEU only, zone 1 or 2. Both prepare buttons use the selected recipe or manual settings from the form above. Check the exact settings shown in the confirmation before sending. This is a real settings transmission with unverified device compatibility. Both zones must be idle. No cooking start is requested.",
    betaWarning: "Remain beside the empty appliance. Do not press Start. Device compatibility is unverified. If heating starts or the other zone changes, stop at the appliance and end testing. Prepare this supervised test?",
    betaPrepare: "Prepare selected settings", betaConfirm: "Send once to the appliance", betaCancel: "Discard test",
    betaConfirmWarning: "Send these exact settings ONCE? Do not press Start. Observe the appliance and both zones.",
    betaPending: "Ready for one explicit test send (expires after 15 seconds)",
    betaAccepted: "The adapter accepted the request. This is not device confirmation. Check program, temperature, duration and both zones at the appliance. Do not press Start; no heating should occur.",
    betaUnknown: "Outcome unknown. Do not send again. Check the appliance and stop testing. Use the device check after physically canceling prepared programs to enable a new test.",
    betaNoSend: "Test blocked; no command was sent.", betaFreshness: "The refreshed report could not be verified. No settings were sent. Check Airfryer Control and prepare a new test. Reports must be at most 15 seconds old.",
    betaState: "The report or device state changed. Check both zones and prepare a new test.", betaZones: "Both reported zones must be idle/off, Celsius selected and SYNC/MATCH off. Cancel any prepared program at the appliance first.",
    betaAdapter: "This test requires reviewed Airfryer Control 1.0.3-beta.3, 1.0.3 or 1.0.4-beta.1.", betaModel: "This beta test supports only CAF-DC111S-AEU.",
    betaCaps: "The adapter did not supply suitable Air Fry test bounds.", betaBusy: "A test is already in progress. No command was queued.",
    betaExpired: "The test confirmation expired or was consumed. Check the appliance before preparing a new test.",
    title: "Recipe library", subtitle: "Manage recipes independently of any appliance.",
    openMenu: "Open menu", leave: "Leave",
    search: "Search recipes", all: "All categories", new: "New recipe", import: "Import JSON",
    export: "Export JSON", empty: "No recipes found.", loading: "Loading recipes…",
    edit: "Edit", copy: "Duplicate", remove: "Delete", name: "Name", description: "Description",
    category: "Category", noCategory: "No category", addCategory: "Add new category…",
    newCategory: "New category", tags: "Tags (comma-separated)", program: "Program",
    temperature: "Temperature", duration: "Duration (minutes)", save: "Save",
    cancel: "Cancel", deleteConfirm: "Delete this recipe? This cannot be undone.",
    copyName: "Name for the duplicate", preview: "Import preview", incoming: "Recipes in file",
    duplicateIds: "Matching IDs", duplicateNames: "Matching names", skip: "Import, skip conflicts",
    replace: "Import, replace matching IDs", replaceConfirm: "Replace recipes with matching IDs?",
    imported: "Recipes imported", saved: "Recipe saved", deleted: "Recipe deleted",
    noAdmin: "Only administrators can manage recipes.", multiPhase: "Editing multiple phases is not supported yet.",
    invalidFile: "Choose a JSON file up to 1 MB.", genericError: "The request failed. Please try again.",
    unauthorized: "Permission is missing or has been revoked.", conflict: "A recipe with that ID or name already exists.",
    invalid: "Check the recipe values and try again.", expired: "The preview expired. Select the file again.",
    storage: "Saving failed. Check the Home Assistant logs.", notConfigured: "The integration is not configured.",
    phases: "Cooking phase", refresh: "Refresh", devicesNote: "Normal device control is not available. The separate supervised beta test requires explicit confirmation.",
    sharedFavorite: "Shared favorite", myFavorite: "My favorite", allFavorites: "All recipes",
    onlyMine: "My favorites", onlyShared: "Shared favorites",
    sample: "Create sample recipe", sampleConfirm: "Create one sample recipe?",
    sampleName: "Frozen bread rolls", sampleDescription: "Example recipe; no appliance is connected.",
    devicePreview: "Device test preview", devicePreviewInfo: "Checks the selected settings on the server. No device command is executed.",
    device: "Air fryer", zone: "Zone", recipeChoice: "Settings source", manualValues: "Manual values",
    checkPreview: "Check test preview", refreshDevices: "Refresh devices", noDevices: "No supported air fryer was reported.",
    adapterMissing: "Airfryer Control is not loaded. Recipe management remains available.",
    adapterIncompatible: "Airfryer Control data could not be read safely.", reportedOnline: "Reported online",
    adapterOutdated: "Install Airfryer Control 1.0.2-beta.1 or newer to load device programs.",
    capabilitiesError: "Airfryer Control did not return usable device programs.",
    offline: "Offline", unknown: "Unknown", unverifiedFreshness: "Status freshness is not verified.",
    reportedFreshness: "Airfryer Control supplied a report time; freshness is not yet used for sending.",
    unknownProgram: "not reported by this device",
    dryRunResult: "Test preview result", noTransmission: "Nothing was transmitted to the appliance.",
    desiredSettings: "Requested settings", blockingReasons: "Live transmission remains blocked for these reasons",
    targetMissing: "The selected device or reported zone is no longer available. Refresh the device list.",
    reasonContract: "The upstream send contract is not verified.", reasonFreshness: "Status freshness is not verified.",
    reasonLimits: "Programs and limits are not verified for this model.",
    reasonProgramMissing: "This program was not reported for the selected appliance.", reasonOffline: "The appliance is offline.",
    reasonConnection: "The connection state is unknown.", reasonZone: "The zone is not safely idle.",
    statusIdle: "Idle", statusOff: "Off", statusReady: "Waiting for manual start", statusFinished: "Finished",
    statusCooking: "Cooking", statusPreheating: "Preheating", statusPaused: "Paused",
    statusDrawerOpen: "Drawer open", statusHolding: "Holding", statusKeepingWarm: "Keeping warm", statusPreheated: "Preheated",
  },
  de: {
    chooseProgram: "Programm auswählen…", customProgram: "Eigenes Programm eingeben", reportedPrograms: "Gemeldete Programme auswählen",
    recipeProgramsFrom: "Programmauswahl von", recipeProgramsInfo: "Gespeichert wird nur die Programmkennung. Das Rezept bleibt geräteunabhängig. Grenzen und Verfügbarkeit werden vor dem Senden erneut geprüft.",
    recipeProgramMissing: "Diese gespeicherte Kennung wird vom gewählten Gerät nicht gemeldet. Zum Korrigieren ein gemeldetes Programm wählen und speichern; es wird nichts automatisch ersetzt.",
    recipeProgramsUnavailable: "Es wurden keine Programme gemeldet. Du kannst eine Kennung frei eingeben und Rezepte auch ohne Adapter weiter bearbeiten.",
    fixRecipeProgram: "Rezeptprogramm bearbeiten",
    betaConnection: "Verbindung oder Seite gewechselt. Alte Bestätigungen wurden verworfen. Einen neuen Test vorbereiten; kein Befehl wird nachgeholt. Eine bereits übermittelte Anfrage kann nicht zurückgeholt werden.",
    betaSelectionChanged: "Auswahl geändert. Die gewählten Werte erneut vorbereiten.",
    modelTemperatures: "Temperaturbereiche des Geräts", modelOwner: "Gerät (Eigentümerangabe)", modelAdapter: "Adaptermeldung",
    modelMissing: "Nicht gemeldet", modelStep: "Schritt", modelTemperatureInfo: "Beaufsichtigtes Senden verwendet die Schnittmenge aus Gerätebereich, geprüftem Adaptervertrag und aktueller Adaptermeldung. Im Adapter fehlende Programme können nicht gesendet werden. Die Zeitgrenzen bleiben ungeprüft.",
    batchReset: "Vor Wertewechsel: eigene vorbereitete Einstellungen in Fach 1 und 2 gezielt beenden und Bereitschaft prüfen.", resetUnavailable: "Kein eindeutig zugeordneter, geladener Fach-Schalter zum Beenden verfügbar. Bitte die Entitäten in Airfryer Control prüfen.", resetFailed: "Das Beenden eines Fachs ist fehlgeschlagen oder unklar. Gerät prüfen und vor einem neuen Versuch die Wiederfreigabe verwenden.",

    betaRecover: "Gerät geprüft – neuen Test freigeben", betaRecoverInfo: "Für einen neuen Versuch zuerst vorbereitete Programme am Gerät abbrechen. Beide Fächer müssen bereit/aus gemeldet werden. Diese Prüfung sendet keinen Steuerbefehl und benötigt keinen HA-Neustart.", betaRecoverConfirm: "Hast du alle vorbereiteten Programme am Gerät abgebrochen, beide Fächer geprüft und bleibst daneben? Jetzt den Zustand frisch lesen und einen neuen Test freigeben?", betaRecovered: "Frischer Bereitschaftszustand bestätigt. Alte Bestätigungen verworfen. Du kannst die Testfolge ohne HA-Neustart neu anzeigen und starten.", betaRejected: "Der Adapter hat die Anfrage abgelehnt. Vorbereitete Programme am Gerät abbrechen und vor einem neuen Versuch die Geräteprüfung benutzen.",

    batchTitle: "Geführter Gerätetest", batchInfo: "Eine Bestätigung für die angezeigte Folge: untere, übliche und obere Temperaturen von sieben gemeldeten Programmen an beiden Fächern, einschließlich Gären und 1-°C-Schritt (30/31 °C). Bis zu 44 Einstellungen, jeweils ein Befehl. Am leeren Gerät bleiben; nicht Start drücken. Der Lauf prüft gemeldete Werte zwischen den Befehlen und stoppt bei Fehlern. Vor jedem Temperatur- oder Programmwechsel werden die eigenen vorbereiteten Einstellungen beendet. Nach dem Lauf die letzten vorbereiteten Programme am Gerät abbrechen.",
    batchPrepare: "Testfolge anzeigen", batchStart: "Angezeigte Testfolge bestätigen und starten", batchStop: "Restliche Schritte abbrechen",
    batchConsent: "Mit Start bestätige ich, dass ich das Gerät beaufsichtige, und erlaube jede Einstellung sowie die angezeigten Schritte zum Beenden der Fächer genau einmal. Es wird kein Garstart angefordert.",
    batchLoading: "Gerätestatus und Testliste werden gelesen … Es werden keine Einstellungen gesendet.", batchProgress: "Schritt", batchOf: "von", batchDone: "Testfolge abgeschlossen. Nach jedem Befehl wurden passende Werte gemeldet. Beide Fächer am Gerät kontrollieren und vorbereitete Programme abbrechen. Das ist keine allgemeine Kompatibilitätsfreigabe.",
    batchStopped: "Restliche Schritte abgebrochen. Ein bereits gesendeter Befehl kann nicht zurückgeholt werden; Gerät prüfen.", batchFailed: "Testfolge gestoppt. Ein Befehl kann angekommen sein. Gerät prüfen und den Lauf erst nach geklärtem Ergebnis wiederholen.", batchSkipped: "Nicht enthalten, weil nicht gemeldet oder Testwerte außerhalb der Grenzen", batchConnection: "Die Verbindung hat gewechselt; dieser Lauf wird nicht fortgesetzt.",

    betaSelection: "Gewählte Werte für beaufsichtigtes Senden vorbereiten",
    betaSelectionInfo: "Beaufsichtigte Beta: alle sieben geprüften Programmkennungen, nur wenn vom Adapter gemeldet und innerhalb der Programmgrenzen. Höchstens 1440 Minuten. Geschätzte Fähigkeiten bleiben bis zur lokalen Abnahme ungeprüft. Rezepte werden nicht verändert.",
    betaProgram: "Dieses Programm ist nicht im geprüften Beta-Vertrag enthalten. Das gewählte Programm wurde nicht ersetzt.",
    betaRange: "Diese Werte liegen außerhalb des Geräte-Temperaturbereichs oder der geprüften Adaptergrenzen oder über dem Beta-Limit von 1440 Minuten. Zusätzlich gelten die gemeldeten Adaptergrenzen. Es wurden keine Werte begrenzt.",
    betaRecipeChanged: "Das Rezept wurde geändert oder gelöscht. Erneut auswählen und eine neue Bestätigung vorbereiten.",
    betaSource: "Ein einphasiges Rezept oder gültige manuelle Werte auswählen.",
    betaRefreshing: "Aktueller Gerätestatus wird angefordert … Es werden keine Einstellungen gesendet.",
    betaRefreshUnavailable: "Für dieses Gerät ist kein geladener, aktivierter Airfryer-Control-Sensor verfügbar. Einen Statussensor aktivieren und die Integration prüfen.",
    betaRefreshFailed: "Die Statusabfrage hat keinen neuen erfolgreichen Gerätebericht geliefert. Die Geräteverbindung in Airfryer Control prüfen. Es wurden keine Einstellungen gesendet.",
    betaTitle: "Beaufsichtigter Beta-Gerätetest", betaIntro: "Nur CAF-DC111S-AEU, Fach 1 oder 2. Beide Vorbereiten-Buttons verwenden das gewählte Rezept oder die manuellen Werte aus dem Formular oben. Vor dem Senden die exakten Werte in der Bestätigung prüfen. Dies ist eine echte Einstellungsübertragung bei ungeprüfter Gerätekompatibilität. Beide Fächer müssen ruhen. Es wird kein Garstart angefordert.",
    betaWarning: "Am leeren Gerät bleiben. Nicht auf Start drücken. Die Gerätekompatibilität ist ungeprüft. Falls Heizen beginnt oder sich das andere Fach ändert, am Gerät stoppen und den Test beenden. Diesen beaufsichtigten Test vorbereiten?",
    betaPrepare: "Gewählte Werte vorbereiten", betaConfirm: "Einmalig ans Gerät senden", betaCancel: "Test verwerfen",
    betaConfirmWarning: "Diese exakten Einstellungen EINMAL senden? Nicht auf Start drücken. Gerät und beide Fächer beobachten.",
    betaPending: "Für einen ausdrücklich bestätigten Test bereit (nach 15 Sekunden abgelaufen)",
    betaAccepted: "Der Adapter hat die Anfrage angenommen. Das ist keine Gerätebestätigung. Programm, Temperatur, Zeit und beide Fächer am Gerät prüfen. Nicht auf Start drücken; es darf kein Heizen beginnen.",
    betaUnknown: "Ergebnis unklar. Nicht erneut senden. Gerät prüfen und Test beenden. Nach dem Abbrechen vorbereiteter Programme am Gerät die Geräteprüfung für einen neuen Test benutzen.",
    betaNoSend: "Test gesperrt; es wurde kein Befehl gesendet.", betaFreshness: "Der aktualisierte Bericht konnte nicht bestätigt werden. Es wurden keine Einstellungen gesendet. Airfryer Control prüfen und den Test neu vorbereiten. Meldungen dürfen höchstens 15 Sekunden alt sein.",
    betaState: "Meldung oder Gerätezustand hat sich geändert. Beide Fächer prüfen und einen neuen Test vorbereiten.", betaZones: "Beide gemeldeten Fächer müssen bereit/aus sein, Celsius gewählt und SYNC/MATCH aus. Vorbereitete Programme zuerst am Gerät abbrechen.",
    betaAdapter: "Dieser Test benötigt geprüftes Airfryer Control 1.0.3-beta.3, 1.0.3 oder 1.0.4-beta.1.", betaModel: "Dieser Beta-Test unterstützt nur CAF-DC111S-AEU.",
    betaCaps: "Der Adapter hat keine passenden Grenzen für den Airfry-Test geliefert.", betaBusy: "Ein Test läuft bereits. Es wurde kein Befehl vorgemerkt.",
    betaExpired: "Die Testbestätigung ist abgelaufen oder verbraucht. Vor einem neuen Test das Gerät prüfen.",
    title: "Rezeptbibliothek", subtitle: "Rezepte unabhängig von einem Gerät verwalten.",
    openMenu: "Menü öffnen", leave: "Verlassen",
    search: "Rezepte suchen", all: "Alle Kategorien", new: "Neues Rezept", import: "JSON importieren",
    export: "JSON exportieren", empty: "Keine Rezepte gefunden.", loading: "Rezepte werden geladen…",
    edit: "Bearbeiten", copy: "Kopieren", remove: "Löschen", name: "Name", description: "Beschreibung",
    category: "Kategorie", noCategory: "Keine Kategorie", addCategory: "Neue Kategorie hinzufügen…",
    newCategory: "Neue Kategorie", tags: "Tags (durch Komma getrennt)", program: "Programm",
    temperature: "Temperatur", duration: "Dauer (Minuten)", save: "Speichern",
    cancel: "Abbrechen", deleteConfirm: "Dieses Rezept löschen? Das kann nicht rückgängig gemacht werden.",
    copyName: "Name für die Kopie", preview: "Importvorschau", incoming: "Rezepte in der Datei",
    duplicateIds: "Gleiche IDs", duplicateNames: "Gleiche Namen", skip: "Importieren, Konflikte überspringen",
    replace: "Importieren, gleiche IDs ersetzen", replaceConfirm: "Rezepte mit gleicher ID ersetzen?",
    imported: "Rezepte importiert", saved: "Rezept gespeichert", deleted: "Rezept gelöscht",
    noAdmin: "Nur Administratoren dürfen Rezepte verwalten.", multiPhase: "Mehrere Garphasen können noch nicht bearbeitet werden.",
    invalidFile: "Bitte eine JSON-Datei mit höchstens 1 MB wählen.", genericError: "Die Anfrage ist fehlgeschlagen. Bitte erneut versuchen.",
    unauthorized: "Die Berechtigung fehlt oder wurde entzogen.", conflict: "Ein Rezept mit dieser ID oder diesem Namen existiert bereits.",
    invalid: "Bitte die Rezeptwerte prüfen.", expired: "Die Vorschau ist abgelaufen. Datei erneut auswählen.",
    storage: "Speichern fehlgeschlagen. Bitte die Home-Assistant-Protokolle prüfen.", notConfigured: "Die Integration ist nicht eingerichtet.",
    phases: "Garphase", refresh: "Aktualisieren", devicesNote: "Normale Gerätesteuerung ist nicht verfügbar. Der separate beaufsichtigte Beta-Test erfordert eine ausdrückliche Bestätigung.",
    sharedFavorite: "Gemeinsamer Favorit", myFavorite: "Mein Favorit", allFavorites: "Alle Rezepte",
    onlyMine: "Meine Favoriten", onlyShared: "Gemeinsame Favoriten",
    sample: "Beispielrezept anlegen", sampleConfirm: "Ein Beispielrezept anlegen?",
    sampleName: "Tiefkühlbrötchen", sampleDescription: "Beispielrezept; kein Gerät ist verbunden.",
    devicePreview: "Geräte-Testvorschau", devicePreviewInfo: "Prüft die gewählten Werte auf dem Server. Es wird kein Gerätebefehl ausgeführt.",
    device: "Airfryer", zone: "Fach", recipeChoice: "Quelle der Werte", manualValues: "Manuelle Werte",
    checkPreview: "Testvorschau prüfen", refreshDevices: "Geräte aktualisieren", noDevices: "Es wurde kein unterstützter Airfryer gemeldet.",
    adapterMissing: "Airfryer Control ist nicht geladen. Die Rezeptverwaltung bleibt verfügbar.",
    adapterIncompatible: "Die Daten von Airfryer Control konnten nicht sicher gelesen werden.", reportedOnline: "Als online gemeldet",
    adapterOutdated: "Zum Laden der Geräteprogramme wird Airfryer Control 1.0.2-beta.1 oder neuer benötigt.",
    capabilitiesError: "Airfryer Control hat keine verwendbaren Geräteprogramme geliefert.",
    offline: "Offline", unknown: "Unbekannt", unverifiedFreshness: "Die Aktualität des Zustands ist nicht bestätigt.",
    reportedFreshness: "Airfryer Control hat eine Meldezeit geliefert; sie wird noch nicht zum Senden verwendet.",
    unknownProgram: "von diesem Gerät nicht gemeldet",
    dryRunResult: "Ergebnis der Testvorschau", noTransmission: "Es wurde nichts an das Gerät übertragen.",
    desiredSettings: "Gewünschte Werte", blockingReasons: "Echte Übertragung bleibt aus diesen Gründen gesperrt",
    targetMissing: "Das gewählte Gerät oder das gemeldete Fach ist nicht mehr verfügbar. Bitte Geräteliste aktualisieren.",
    reasonContract: "Der Upstream-Sendevertrag ist nicht bestätigt.", reasonFreshness: "Die Aktualität des Zustands ist nicht bestätigt.",
    reasonLimits: "Programme und Grenzen sind für dieses Modell nicht bestätigt.",
    reasonProgramMissing: "Dieses Programm wurde für das gewählte Gerät nicht gemeldet.", reasonOffline: "Das Gerät ist offline.",
    reasonConnection: "Der Verbindungszustand ist unbekannt.", reasonZone: "Das Fach ist nicht sicher bereit.",
    statusIdle: "Bereit", statusOff: "Aus", statusReady: "Wartet auf manuellen Start", statusFinished: "Fertig",
    statusCooking: "Gart", statusPreheating: "Heizt vor", statusPaused: "Pausiert",
    statusDrawerOpen: "Fach offen", statusHolding: "Wartet", statusKeepingWarm: "Hält warm", statusPreheated: "Vorgeheizt",
  },
};

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

const ACCESS_TEXT = {
  en: { title: "Device permissions", info: "Administrators can use all devices. Grant ordinary users an entire device, including all zones and available programs. Existing device safety checks still apply.", load: "Manage device access", user: "User", device: "Device", grant: "Grant device access", revoke: "Revoke", empty: "No devices shared with ordinary users.", unavailable: "Permissions storage unavailable; ordinary users remain blocked.", confirm: "Revoke access to this entire device? Pending confirmations will become invalid.", saved: "Device permissions saved.", choose: "Choose…" },
  de: { title: "Geräteberechtigungen", info: "Administratoren dürfen alle Geräte verwenden. Normale Benutzer erhalten ein ganzes Gerät einschließlich aller Fächer und verfügbaren Programme. Die bestehenden Geräteprüfungen gelten weiter.", load: "Gerätefreigaben verwalten", user: "Benutzer", device: "Gerät", grant: "Gerät freigeben", revoke: "Entziehen", empty: "Keine Geräte für normale Benutzer freigegeben.", unavailable: "Berechtigungsspeicher nicht verfügbar; normale Benutzer bleiben gesperrt.", confirm: "Die Freigabe für dieses ganze Gerät entziehen? Vorbereitete Bestätigungen werden ungültig.", saved: "Geräteberechtigungen gespeichert.", choose: "Auswählen…" },
};

export class AirfryerRecipesPanel extends HTMLElement {
  static get betaFeatures() { return /(?:b\d+|-beta(?:[.-]\d+)?)$/i.test("0.2.0"); }
  get betaFeatures() { return AirfryerRecipesPanel.betaFeatures; }
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.recipes = [];
    this.query = "";
    this.category = "";
    this.favoriteFilter = "";
    this.favorites = new Set();
    this.editor = null;
    this.renderedEditor = null;
    this.editorCustomProgram = false;
    this.editorCategoryNew = "";
    this.editorNewCategory = false;
    this.editorTagsText = null;
    this.editorRenderedUnit = "°C";
    this.renderedCategories = [];
    this.preview = null;
    this.deviceState = { status: "adapter_missing", devices: [], live_send_enabled: false };
    this.selectedDeviceId = "";
    this.selectedZoneId = "";
    this.previewRecipeId = "";
    this.manualPreviewProgram = "airfry";
    this.manualPreviewTemperatureC = 180;
    this.manualPreviewDurationMinutes = 10;
    this.sendPreview = null;
    this.batchPlan = null;
    this.batchRunning = false;
    this.batchRunId = null;
    this.batchStopRequested = false;
    this.batchMessage = "";
    this.batchResults = [];
    this.betaTest = null;
    this.betaSubmittingToken = null;
    this.selectionRevision = 0;
    this.controlRevision = 0;
    this.panelActive = true;
    this.watchedConnection = null;
    this.connectionLost = () => {
      this.invalidateControls();
      this.betaMessage = this.words.betaConnection;
      this.batchMessage = this.words.betaConnection;
      this.render();
    };
    this.betaMessage = "";
    this.deviceError = "";
    this.devicesBusy = false;
    this.busy = false;
    this.notice = "";
    this.error = "";
    this.started = false;
    this.accessData = null;
    this.accessMessage = "";
    this.shadowRoot.addEventListener("click", (event) => this.onClick(event));
    this.shadowRoot.addEventListener("submit", (event) => this.onSubmit(event));
    this.shadowRoot.addEventListener("input", (event) => this.onInput(event));
    this.shadowRoot.addEventListener("change", (event) => this.onChange(event));
  }

  set hass(value) {
    const oldLanguage = this._hass?.language;
    const oldAdmin = this._hass?.user?.is_admin;
    const oldUnit = this._hass?.config?.unit_system?.temperature;
    const oldConnection = this._hass?.connection;
    if (this._hass && (this._hass.user?.id !== value?.user?.id || oldAdmin !== value?.user?.is_admin)) {
      this.supportData = null;
      this.diagnosticPreview = null;
      this.diagnosticPreviewId = null;
      this.supportMessage = "";
      this.accessData = null;
      this.accessMessage = "";
    }
    const controlsChanged = this._hass && (oldConnection !== value?.connection ||
      this._hass.user?.id !== value?.user?.id || oldAdmin !== value?.user?.is_admin ||
      oldUnit !== value?.config?.unit_system?.temperature);
    if (controlsChanged) this.invalidateControls();
    this._hass = value;
    if (this.panelActive) this.watchConnection(value?.connection);
    if (!this.started && value) {
      this.started = true;
      this.load();
    } else if (oldLanguage !== value?.language || oldAdmin !== value?.user?.is_admin ||
        oldUnit !== value?.config?.unit_system?.temperature || controlsChanged) {
      this.render();
    }
  }

  get words() {
    return WORDS[this._hass?.language?.toLowerCase().startsWith("de") ? "de" : "en"];
  }

  get admin() {
    return Boolean(this._hass?.user?.is_admin);
  }

  get unit() {
    return this._hass?.config?.unit_system?.temperature === "°F" ? "°F" : "°C";
  }

  toDisplay(celsius) {
    return this.unit === "°F" ? Math.round(celsius * 9 / 5 + 32) : celsius;
  }

  fromDisplay(value) {
    return this.unit === "°F" ? Math.round((value - 32) * 5 / 9) : value;
  }

  async request(name, fields = {}) {
    if ((name.startsWith("beta_") || name.startsWith("batch_")) &&
        (this._hass?.connection?.connected === false ||
          (!this.panelActive && !["beta_cancel", "batch_stop"].includes(name)))) {
      throw { code: "beta_test_blocked", message: "connection_changed" };
    }
    return this._hass.callWS({ type: `airfryer_recipes/${name}`, ...fields });
  }

  watchConnection(connection) {
    if (connection === this.watchedConnection) return;
    this.watchedConnection?.removeEventListener?.("disconnected", this.connectionLost);
    this.watchedConnection = connection;
    connection?.addEventListener?.("disconnected", this.connectionLost);
  }

  cancelBetaToken(token) {
    if (token) this.request("beta_cancel", { token }).catch(() => {});
  }

  forgetBeta() {
    this.selectionRevision++;
    this.cancelBetaToken(this.betaTest?.token);
    this.cancelBetaToken(this.betaSubmittingToken);
    this.betaTest = null;
    this.betaMessage = this.betaSubmittingToken ? this.words.betaUnknown : "";
  }

  invalidateControls() {
    const run_id = this.batchRunId;
    this.controlRevision++;
    this.forgetBeta();
    this.batchStopRequested = true;
    this.batchPlan = null;
    this.batchRunId = null;
    if (run_id) this.request("batch_stop", { run_id }).catch(() => {});
  }

  controlCurrent(revision) {
    return this.panelActive && this.controlRevision === revision && this._hass?.connection?.connected !== false;
  }

  showError(error) {
    const code = error?.code;
    const key = {
      unauthorized: "unauthorized", recipe_conflict: "conflict", invalid_format: "invalid",
      preview_expired: "expired", storage_error: "storage", not_configured: "notConfigured",
    }[code] || "genericError";
    this.error = this.words[key];
    this.notice = "";
    this.render();
  }

  async load() {
    if (!this._hass) return;
    this.busy = true;
    this.render();
    try {
      const [list, favorites] = await Promise.all([this.request("list"), this.request("favorites")]);
      this.recipes = list.recipes;
      this.favorites = new Set(favorites.recipe_ids);
      this.error = "";
      await this.loadDevices();
    } catch (error) {
      this.showError(error);
    } finally {
      this.busy = false;
      this.render();
    }
  }

  selectedDevice() {
    return this.deviceState.devices.find((device) => device.device_id === this.selectedDeviceId) || null;
  }

  selectedZone() {
    const wanted = Number(this.selectedZoneId);
    return this.selectedDevice()?.zones?.find((zone) => zone.zone_id === wanted) || null;
  }

  selectedPreviewRecipe() {
    return this.recipes.find((recipe) => recipe.id === this.previewRecipeId && recipe.phases?.length === 1) || null;
  }

  programName(program) {
    const names = {
      airfry: { de: "Heißluft-Frittieren", en: "Air Fry" },
      roast: { de: "Braten", en: "Roast" }, bake: { de: "Backen", en: "Bake" },
      grill: { de: "Grillen", en: "Grill" }, reheat: { de: "Aufwärmen", en: "Reheat" },
      dry: { de: "Dörren", en: "Dry" }, proof: { de: "Gären", en: "Proof" },
    };
    const language = this._hass?.language?.toLowerCase().startsWith("de") ? "de" : "en";
    return names[program]?.[language] || program;
  }

  programOption(program) {
    return this.programName(program.id);
  }

  renderModelTemperatures(device) {
    const profile = device?.model_profile;
    if (profile?.source !== "owner_reported" || !Array.isArray(profile.programs)) return "";
    const t = this.words;
    const range = (value) => `${this.toDisplay(value.min)}–${this.toDisplay(value.max)} ${this.unit}`;
    return `<details><summary>${t.modelTemperatures}</summary><p>${t.modelTemperatureInfo}</p>
      <table><thead><tr><th>${t.program}</th><th>${t.modelOwner}</th><th>${t.modelAdapter}</th></tr></thead><tbody>
      ${profile.programs.map((program) => {
        const reported = device.programs?.find((item) => item.id === program.id);
        const step = program.temperature_step_c;
        return `<tr><td>${escapeHtml(this.programName(program.id))}</td><td>${escapeHtml(range(program.temperature_c))}${step ? ` · ${this.unit === "°F" ? step * 9 / 5 : step} ${this.unit} ${t.modelStep}` : ""}</td><td>${reported?.temperature_c ? escapeHtml(range(reported.temperature_c)) : t.modelMissing}</td></tr>`;
      }).join("")}</tbody></table></details>`;
  }

  async loadDevices() {
    if (!this.admin) return;
    this.forgetBeta();
    this.devicesBusy = true;
    this.deviceError = "";
    this.render();
    try {
      const result = await this.request("devices");
      this.deviceState = {
        status: result.status || "adapter_incompatible",
        devices: Array.isArray(result.devices) ? result.devices : [],
        live_send_enabled: false,
      };
      if (!this.deviceState.devices.some((device) => device.device_id === this.selectedDeviceId)) {
        this.selectedDeviceId = this.deviceState.devices[0]?.device_id || "";
      }
      const programs = this.selectedDevice()?.programs || [];
      if (!programs.some((program) => program.id === this.manualPreviewProgram)) {
        this.manualPreviewProgram = programs[0]?.id || "airfry";
      }
      const zones = this.selectedDevice()?.zones || [];
      if (!zones.some((zone) => String(zone.zone_id) === String(this.selectedZoneId))) {
        this.selectedZoneId = zones[0] ? String(zones[0].zone_id) : "";
      }
      this.sendPreview = null;
    } catch (error) {
      this.deviceState = { status: "adapter_incompatible", devices: [], live_send_enabled: false };
      this.deviceError = this.words.genericError;
    } finally {
      this.devicesBusy = false;
    }
  }

  statusLabel(status) {
    const key = {
      idle: "statusIdle", off: "statusOff", ready: "statusReady", finished: "statusFinished",
      cooking: "statusCooking", preheating: "statusPreheating", preheated: "statusPreheated",
      paused: "statusPaused", drawer_open: "statusDrawerOpen", holding: "statusHolding",
      keeping_warm: "statusKeepingWarm", offline: "offline",
    }[status] || "unknown";
    return this.words[key];
  }

  reasonLabel(reason) {
    const key = {
      upstream_contract_unverified: "reasonContract", freshness_unverified: "reasonFreshness",
      program_limits_unverified: "reasonLimits", program_not_reported: "reasonProgramMissing",
      device_offline: "reasonOffline",
      connection_unknown: "reasonConnection", zone_not_idle: "reasonZone",
    }[reason];
    return key ? this.words[key] : this.words.unknown;
  }

  async action(task, success) {
    if (this.busy || !this.admin) return;
    this.busy = true;
    this.error = "";
    this.render();
    try {
      const result = await task();
      this.notice = typeof success === "function" ? success(result) : success;
      this.editor = null;
      this.preview = null;
      const list = await this.request("list");
      this.recipes = list.recipes;
    } catch (error) {
      this.showError(error);
    } finally {
      this.busy = false;
      this.render();
    }
  }

  filtered() {
    const term = this.query.trim().toLocaleLowerCase();
    return this.recipes.filter((recipe) =>
      (!this.category || recipe.category === this.category) &&
      (!this.favoriteFilter || (this.favoriteFilter === "mine" && this.favorites.has(recipe.id)) ||
        (this.favoriteFilter === "shared" && recipe.favorite)) &&
      (!term || [recipe.name, recipe.description, recipe.category, ...(recipe.tags || [])]
        .some((part) => part.toLocaleLowerCase().includes(term))));
  }

  categories() {
    return [...new Set(this.recipes.map((recipe) => recipe.category).filter(Boolean))]
      .sort((left, right) => left.localeCompare(right));
  }

  captureEditorDraft() {
    if (!this.editor || this.editor !== this.renderedEditor || this.editor.phases?.length > 1) return;
    const element = this.shadowRoot.getElementById("editor");
    if (element?.id !== "editor") return;
    const form = new FormData(element);
    this.editor.name = String(form.get("name") || "");
    this.editor.description = String(form.get("description") || "");
    this.editor.favorite = form.has("favorite");
    this.editorTagsText = String(form.get("tags") || "");
    const category = String(form.get("category_choice") || "");
    this.editorNewCategory = category === "new";
    this.editorCategoryNew = String(form.get("category_new") || "");
    if (category.startsWith("existing-")) this.editor.category = this.renderedCategories[Number(category.slice(9))] || "";
    else if (!this.editorNewCategory) this.editor.category = "";
    const temperature = form.get("temperature_c");
    const minutes = form.get("duration_minutes");
    this.editor.phases = [{ program: String(form.get("program") || ""),
      temperature_c: temperature === null || temperature === "" ? undefined : this.editorRenderedUnit === "°F"
        ? Math.round((Number(temperature) - 32) * 5 / 9) : Number(temperature),
      duration_minutes: minutes === null || minutes === "" ? undefined : Number(minutes),
    }];
  }

  get supportWords() { return SUPPORT_TEXT[this._hass?.language?.toLowerCase().startsWith("de") ? "de" : "en"]; }

  renderSupport() {
    if (!this.admin) return "";
    const t = this.supportWords, data = this.supportData;
    return `<details class="support" ${this.supportOpen ? "open" : ""}><summary>${t.title}</summary><p>${t.warning}</p>
      <button data-action="diagnostics-preview">${t.preview}</button>
      ${this.diagnosticPreview ? `<pre style="white-space:pre-wrap;overflow-wrap:anywhere">${escapeHtml(JSON.stringify(this.diagnosticPreview, null, 2))}</pre><button data-action="diagnostics-download">${t.download}</button>` : ""}
      <p>${t.info}</p><button data-action="notifications-load">${t.notifications}</button>
      ${data ? (data.available ? `<p>${this.supportMessage ? escapeHtml(this.supportMessage) : ""}</p><form id="notifications-form"><label>${t.source}<select name="source" aria-label="${t.source}">${data.sources.map(x => `<option value="${escapeHtml(x)}">${escapeHtml(x)}</option>`).join("")}</select></label>
      <label>${t.target}<select name="target" aria-label="${t.target}">${data.targets.map(x => `<option value="${escapeHtml(x)}">${escapeHtml(x)}</option>`).join("")}</select></label><button type="button" data-action="notifications-save" ${!data.sources.length || !data.targets.length ? "disabled" : ""}>${t.save}</button></form>
      ${data.rules.length ? data.rules.map(r => `<p>${escapeHtml(r.entity_id)} → ${escapeHtml(r.target)} <button data-action="notifications-remove" data-id="${escapeHtml(r.entity_id)}">${t.remove}</button></p>`).join("") : `<p>${t.empty}</p>`}` : `<p>${t.unavailable}</p>`) : ""}</details>`;
  }

  async supportAction(type, button) {
    const revision = this.controlRevision;
    const userId = this._hass?.user?.id;
    const current = () => this.admin && this.controlRevision === revision && this._hass?.user?.id === userId;
    this.busy = true;
    try {
      if (type === "diagnostics-preview") {
        const result = await this.request("diagnostics_preview");
        if (current()) { this.diagnosticPreview = result.diagnostics; this.diagnosticPreviewId = result.preview_id; }
      } else if (type === "diagnostics-download" && this.diagnosticPreview) {
        const result = await this.request("diagnostics_download", { preview_id: this.diagnosticPreviewId });
        if (!current()) return;
        const link = document.createElement("a");
        link.href = result.url; link.download = result.filename; link.click();
      } else {
        if (type !== "notifications-load") {
          const form = new FormData(this.shadowRoot.getElementById("notifications-form"));
          await this.request("notification_set", { entity_id: type === "notifications-remove" ? button.dataset.id : String(form.get("source") || ""), target: type === "notifications-remove" ? "" : String(form.get("target") || ""), language: this._hass?.language?.toLowerCase().startsWith("de") ? "de" : "en" });
          if (!current()) return;
          this.supportMessage = this.supportWords.saved;
        }
        const data = await this.request("notification_settings");
        if (current()) this.supportData = data;
      }
    } catch (error) { if (current()) { if (error?.code === "preview_expired") this.error = this.supportWords.expired; else this.showError(error); } }
    finally { this.busy = false; this.render(); }
  }

  get accessWords() { return ACCESS_TEXT[this._hass?.language?.toLowerCase().startsWith("de") ? "de" : "en"]; }

  renderAccess() {
    if (!this.admin) return "";
    const t = this.accessWords, data = this.accessData;
    return `<section class="preview" id="device-access"><h2>${t.title}</h2><p>${t.info}</p>
      <button type="button" data-action="access-load" ${this.busy ? "disabled" : ""}>${t.load}</button>
      ${this.accessMessage ? `<p role="status">${escapeHtml(this.accessMessage)}</p>` : ""}
      ${data ? data.available ? `<form id="device-access-form"><div class="grid"><label>${t.user}<select name="user_id" required><option value="">${t.choose}</option>${data.users.map((u) => `<option value="${escapeHtml(u.id)}">${escapeHtml(u.name)}</option>`).join("")}</select></label>
        <label>${t.device}<select name="device_id" required><option value="">${t.choose}</option>${data.devices.map((d) => `<option value="${escapeHtml(d.id)}">${escapeHtml(d.name)}</option>`).join("")}</select></label></div><button type="button" data-action="access-grant" ${this.busy ? "disabled" : ""}>${t.grant}</button></form>
        ${data.grants.length ? `<ul>${data.grants.map((g) => `<li>${escapeHtml(data.users.find((u) => u.id === g.user_id)?.name || g.user_id)} · ${escapeHtml(data.devices.find((d) => d.id === g.device_id)?.name || g.device_id)} <button type="button" data-action="access-revoke" data-user="${escapeHtml(g.user_id)}" data-device="${escapeHtml(g.device_id)}" ${this.busy ? "disabled" : ""}>${t.revoke}</button></li>`).join("")}</ul>` : `<p>${t.empty}</p>`}` : `<p class="error">${t.unavailable}</p>` : ""}</section>`;
  }

  async manageAccess(change = null) {
    if (!this.admin || this.busy) return;
    const revision = this.controlRevision;
    this.busy = true;
    this.render();
    try {
      if (change) await this.request("access_set", change);
      const data = await this.request("access_list");
      if (this.controlCurrent(revision) && this.admin) {
        this.accessData = data;
        this.accessMessage = change ? this.accessWords.saved : "";
      }
    } catch (error) { if (this.controlCurrent(revision)) this.showError(error); }
    finally { this.busy = false; this.render(); }
  }

  render() {
    if (!this.shadowRoot) return;
    this.supportOpen = this.shadowRoot.querySelector?.("details.support")?.open ?? this.supportOpen;
    this.captureEditorDraft();
    if (this.editor !== this.renderedEditor) {
      this.editorCustomProgram = false;
      this.editorCategoryNew = "";
      this.editorNewCategory = false;
      this.editorTagsText = null;
    }
    const t = this.words;
    const categories = this.categories();
    const selected = this.editor;
    const phase = selected?.phases?.[0] || {};
    const multiple = selected?.phases?.length > 1;
    const device = this.selectedDevice();
    const zones = device?.zones || [];
    const previewRecipe = this.selectedPreviewRecipe();
    const previewPhase = previewRecipe?.phases?.[0] || {
      program: this.manualPreviewProgram, temperature_c: this.manualPreviewTemperatureC, duration_minutes: this.manualPreviewDurationMinutes,
    };
    const programs = device?.programs || [];
    const editorProgramReported = programs.some((program) => program.id === phase.program);
    const editorProgramOptions = [
      ...(!editorProgramReported && phase.program ? [{ id: phase.program, missing: true }] : []), ...programs,
    ];
    const programReported = programs.some((program) => program.id === previewPhase.program);
    const programOptions = programs.length ? [
      ...(!programReported && previewPhase.program ? [{ id: previewPhase.program, missing: true }] : []),
      ...programs,
    ] : [];
    const deviceMessage = this.deviceState.status === "adapter_missing" ? t.adapterMissing
      : this.deviceState.status === "adapter_incompatible" ? t.adapterIncompatible
      : this.deviceState.status === "adapter_outdated" ? t.adapterOutdated
      : this.deviceState.status === "adapter_capabilities_error" ? t.capabilitiesError
      : !this.deviceState.devices.length ? t.noDevices : "";
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;box-sizing:border-box;color:var(--primary-text-color);background:var(--primary-background-color);min-height:100%;font:inherit}
        *{box-sizing:border-box}main{max-width:1100px;margin:auto;padding:20px}h1{margin:0 0 6px;font-size:1.8rem}h2{font-size:1.25rem}
        header{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:10px;margin:-20px -20px 14px;padding:10px 20px;background:var(--primary-background-color);border-bottom:1px solid var(--divider-color)}
        header h1{flex:1;min-width:0;margin:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:1.25rem}
        header button{flex:none;padding:8px 12px}header a{flex:none;border:1px solid var(--divider-color);background:var(--card-background-color);color:var(--primary-text-color);border-radius:8px;padding:10px 14px;text-decoration:none;min-height:42px}
        .muted{color:var(--secondary-text-color)}.toolbar,.row,.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
        .toolbar{margin:22px 0}.toolbar input{flex:1 1 180px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,280px),1fr));gap:14px}
        article,.editor,.preview{background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:12px;padding:18px;overflow-wrap:anywhere}
        article h2{margin:0 0 6px}article p{margin:8px 0}.actions{margin-top:14px}button,input,select,textarea{font:inherit}
        button{border:1px solid var(--divider-color);background:var(--card-background-color);color:var(--primary-text-color);border-radius:8px;padding:10px 14px;cursor:pointer;min-height:42px}
        button.primary{background:var(--primary-color);color:var(--text-primary-color,#fff);border-color:var(--primary-color)}button:disabled{opacity:.5;cursor:default}
        input,select,textarea{width:100%;border:1px solid var(--divider-color);background:var(--card-background-color);color:var(--primary-text-color);border-radius:8px;padding:10px;min-height:42px}
        textarea{min-height:82px}label{display:block;margin:12px 0 5px;font-weight:600}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 14px}
        details{margin:12px 0}summary{cursor:pointer}table{width:100%;border-collapse:collapse;font-size:.9em}th,td{text-align:left;padding:7px 4px;border-bottom:1px solid var(--divider-color);vertical-align:top}
        .editor,.preview{margin:18px 0}.message{padding:12px;border-radius:8px;margin:12px 0;background:var(--secondary-background-color)}.error{color:var(--error-color)}
        .visually-hidden{position:absolute;clip:rect(0,0,0,0);width:1px;height:1px;overflow:hidden}
        @media(max-width:600px){main{padding:14px}header{margin:-14px -14px 14px;padding:10px 14px}.grid{grid-template-columns:1fr}.toolbar>*{flex:1 1 100%}.actions button{flex:1 1 auto}}
      </style>
      <main>
        <header><button type="button" data-action="menu" aria-label="${t.openMenu}" title="${t.openMenu}">☰</button><h1>${t.title}</h1><a href="/">${t.leave}</a></header>
        <p class="muted">${t.subtitle}</p>
        ${!this.admin ? `<p class="message error">${t.noAdmin}</p>` : ""}
        ${this.error ? `<p class="message error" role="alert">${this.error}</p>` : ""}
        ${this.notice ? `<p class="message" role="status">${escapeHtml(this.notice)}</p>` : ""}
        ${this.renderAccess()}
        ${this.renderSupport()}
        <div class="toolbar">
          <input id="search" type="search" aria-label="${t.search}" placeholder="${t.search}" value="${escapeHtml(this.query)}">
          <select id="category" aria-label="${t.category}"><option value="">${t.all}</option>${categories.map((name) => `<option value="${escapeHtml(name)}" ${this.category === name ? "selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>
          <select id="favorite-filter" aria-label="${t.myFavorite}"><option value="">${t.allFavorites}</option><option value="mine" ${this.favoriteFilter === "mine" ? "selected" : ""}>${t.onlyMine}</option><option value="shared" ${this.favoriteFilter === "shared" ? "selected" : ""}>${t.onlyShared}</option></select>
          <button data-action="refresh" ${this.busy ? "disabled" : ""}>${t.refresh}</button>
          ${this.admin ? `<button class="primary" data-action="new">${t.new}</button>${!this.recipes.length ? `<button data-action="sample">${t.sample}</button>` : ""}<button data-action="choose-import">${t.import}</button><button data-action="export">${t.export}</button>` : ""}
          <input class="visually-hidden" id="import-file" type="file" accept=".json,application/json">
        </div>
        ${this.admin && selected ? `<form id="editor" class="editor"><h2>${selected.id ? t.edit : t.new}</h2>
          ${multiple ? `<p class="message error">${t.multiPhase}</p>` : ""}
          <div class="grid"><div><label for="recipe-name">${t.name}</label><input id="recipe-name" name="name" maxlength="100" required value="${escapeHtml(selected.name)}"></div>
          <div><label for="recipe-category">${t.category}</label><select id="recipe-category" name="category_choice"><option value="" ${!this.editorNewCategory && !selected.category ? "selected" : ""}>${t.noCategory}</option>${categories.map((name, index) => `<option value="existing-${index}" ${!this.editorNewCategory && selected.category === name ? "selected" : ""}>${escapeHtml(name)}</option>`).join("")}<option value="new"${this.editorNewCategory ? " selected" : ""}>${t.addCategory}</option></select>
          <div id="new-category-field" ${this.editorNewCategory ? "" : "hidden"}><label for="recipe-category-new">${t.newCategory}</label><input id="recipe-category-new" name="category_new" maxlength="64" ${this.editorNewCategory ? "required" : ""} value="${escapeHtml(this.editorCategoryNew)}"></div></div></div>
          <label for="recipe-description">${t.description}</label><textarea id="recipe-description" name="description" maxlength="500">${escapeHtml(selected.description)}</textarea>
          <label for="recipe-tags">${t.tags}</label><input id="recipe-tags" name="tags" value="${escapeHtml(this.editorTagsText ?? (selected.tags || []).join(", "))}">
          <label><input type="checkbox" name="favorite" ${selected.favorite ? "checked" : ""} style="width:auto;min-height:auto"> ${t.sharedFavorite}</label>
          <h3>${t.phases}</h3><div class="grid">
          <div><label for="recipe-program">${t.program}</label>${programs.length && !this.editorCustomProgram
            ? `<select id="recipe-program" name="program" required><option value="" disabled ${!phase.program ? "selected" : ""}>${t.chooseProgram}</option>${editorProgramOptions.map((program) => `<option value="${escapeHtml(program.id)}" ${program.id === phase.program ? "selected" : ""}>${escapeHtml(program.missing ? `${program.id} · ${t.unknownProgram}` : this.programOption(program))}</option>`).join("")}</select>`
            : `<input id="recipe-program" name="program" maxlength="64" required value="${escapeHtml(phase.program)}">`}
          ${programs.length ? `<p class="muted">${t.recipeProgramsFrom}: ${escapeHtml(device.name)}. ${t.recipeProgramsInfo}</p><button type="button" data-action="editor-program-mode">${this.editorCustomProgram ? t.reportedPrograms : t.customProgram}</button>` : `<p class="muted">${t.recipeProgramsUnavailable}</p>`}
          ${phase.program && programs.length && !editorProgramReported ? `<p class="message">${t.recipeProgramMissing}</p>` : ""}</div>
          <div><label for="recipe-temperature">${t.temperature} (${this.unit})</label><input id="recipe-temperature" name="temperature_c" type="number" min="${this.unit === "°F" ? 32 : 0}" max="${this.unit === "°F" ? 752 : 400}" step="1" required value="${phase.temperature_c === undefined ? "" : escapeHtml(this.toDisplay(phase.temperature_c))}"></div>
          <div><label for="recipe-duration">${t.duration}</label><input id="recipe-duration" name="duration_minutes" type="number" min="1" max="1440" step="1" required value="${escapeHtml(phase.duration_minutes)}"></div></div>
          <div class="actions"><button class="primary" type="submit" ${this.busy || multiple ? "disabled" : ""}>${t.save}</button><button type="button" data-action="cancel">${t.cancel}</button></div></form>` : ""}
        ${this.preview ? `<section class="preview"><h2>${t.preview}</h2><p>${t.incoming}: ${this.preview.incoming_count}</p><p>${t.duplicateIds}: ${this.preview.duplicate_ids.length}${this.preview.duplicate_ids.length ? ` (${escapeHtml(this.preview.duplicate_ids.join(", "))})` : ""}</p><p>${t.duplicateNames}: ${this.preview.duplicate_names.length}${this.preview.duplicate_names.length ? ` (${escapeHtml(this.preview.duplicate_names.join(", "))})` : ""}</p>
          <div class="actions"><button class="primary" data-action="import-skip" ${this.busy ? "disabled" : ""}>${t.skip}</button><button data-action="import-replace" ${this.busy ? "disabled" : ""}>${t.replace}</button><button data-action="cancel-preview">${t.cancel}</button></div></section>` : ""}
        ${this.admin && this.betaFeatures ? `<section class="preview" id="batch-test"><h2>${t.batchTitle}</h2><p>${t.batchInfo}</p>
          <label for="batch-device">${t.device}</label><select id="batch-device" ${this.busy || this.batchRunning ? "disabled" : ""}>${this.deviceState.devices.map((item) => `<option value="${escapeHtml(item.device_id)}" ${item.device_id === this.selectedDeviceId ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}</select>
          <div class="actions"><button type="button" data-action="batch-prepare" ${this.busy || this.devicesBusy || this.batchRunning || !device ? "disabled" : ""}>${t.batchPrepare}</button>
          ${this.batchRunning ? `<button type="button" data-action="batch-stop">${t.batchStop}</button>` : `<button type="button" data-action="beta-recover" ${this.busy || !device ? "disabled" : ""}>${t.betaRecover}</button>`}</div><p class="muted">${t.betaRecoverInfo}</p>
          ${this.batchPlan ? `<p><strong>${escapeHtml(this.batchPlan.device_name)}</strong></p><ol>${this.batchPlan.steps.map((step, index) => `${this.batchNeedsReset(this.batchPlan, index) ? `<li style="list-style:none" class="muted">${t.batchReset}</li>` : ""}<li value="${index + 1}">${t.zone} ${step.zone_id} · ${escapeHtml(this.programName(step.settings.program))} · ${this.toDisplay(step.settings.temperature_c)} ${this.unit} · ${step.settings.duration_minutes} min</li>`).join("")}</ol>
          ${this.batchPlan.skipped?.length ? `<p>${t.batchSkipped}: ${escapeHtml(this.batchPlan.skipped.join(", "))}</p>` : ""}
          ${!this.batchRunning && !this.batchRunId ? `<p>${t.batchConsent}</p><button class="primary" type="button" data-action="batch-start" ${this.busy ? "disabled" : ""}>${t.batchStart}</button>` : ""}` : ""}
          ${this.batchMessage ? `<p class="message" role="status">${escapeHtml(this.batchMessage)}</p>` : ""}
          ${this.batchResults.length ? `<ol>${this.batchResults.map((item) => `<li>${t.zone} ${item.zone_id} · ${escapeHtml(this.programName(item.settings.program))} · ${item.settings.temperature_c} °C · ${item.settings.duration_minutes} min ✓</li>`).join("")}</ol>` : ""}
        </section>` : ""}
        ${this.admin && this.betaFeatures ? `<section class="preview" id="device-preview"><h2>${t.devicePreview}</h2>
          <p>${t.devicePreviewInfo}</p>
          ${this.deviceError ? `<p class="message error" role="alert">${escapeHtml(this.deviceError)}</p>` : ""}
          ${deviceMessage ? `<p class="message">${deviceMessage}</p>` : ""}
          <div class="actions"><button type="button" data-action="refresh-devices" ${this.devicesBusy || this.busy ? "disabled" : ""}>${t.refreshDevices}</button></div>
          ${device ? `<form id="device-preview-form">
            <div class="grid"><div><label for="preview-device">${t.device}</label><select id="preview-device" name="device_id">${this.deviceState.devices.map((item) => `<option value="${escapeHtml(item.device_id)}" ${item.device_id === this.selectedDeviceId ? "selected" : ""}>${escapeHtml(item.name)}${item.model ? ` · ${escapeHtml(item.model)}` : ""}</option>`).join("")}</select>
            <p class="muted">${device.connectivity === "reported_online" ? t.reportedOnline : device.connectivity === "offline" ? t.offline : t.unknown} · ${device.freshness === "reported" ? t.reportedFreshness : t.unverifiedFreshness}</p></div>
            <div><label for="preview-zone">${t.zone}</label><select id="preview-zone" name="zone_id" ${!zones.length ? "disabled" : ""}>${zones.map((item) => `<option value="${item.zone_id}" ${String(item.zone_id) === String(this.selectedZoneId) ? "selected" : ""}>${t.zone} ${item.zone_id} · ${escapeHtml(this.statusLabel(item.status))}</option>`).join("")}</select></div>
            <div><label for="preview-recipe">${t.recipeChoice}</label><select id="preview-recipe" name="recipe_id"><option value="">${t.manualValues}</option>${this.recipes.filter((item) => item.phases?.length === 1).map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === this.previewRecipeId ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}</select></div></div>
            <div class="grid"><div><label for="preview-program">${t.program}</label>${programOptions.length
              ? `<select id="preview-program" name="program" required ${previewRecipe ? "disabled" : ""}>${programOptions.map((program) => `<option value="${escapeHtml(program.id)}" ${program.id === previewPhase.program ? "selected" : ""}>${escapeHtml(program.missing ? `${this.programName(program.id)} · ${t.unknownProgram}` : this.programOption(program))}</option>`).join("")}</select>${previewRecipe ? `<input type="hidden" name="program" value="${escapeHtml(previewPhase.program)}">` : ""}`
              : `<input id="preview-program" name="program" maxlength="64" required ${previewRecipe ? "readonly" : ""} value="${escapeHtml(previewPhase.program)}">`}</div>
            <div><label for="preview-temperature">${t.temperature} (${this.unit})</label><input id="preview-temperature" name="temperature_c" type="number" min="${this.unit === "°F" ? 32 : 0}" max="${this.unit === "°F" ? 752 : 400}" step="1" required ${previewRecipe ? "readonly" : ""} value="${escapeHtml(this.toDisplay(previewPhase.temperature_c))}"></div>
            <div><label for="preview-duration">${t.duration}</label><input id="preview-duration" name="duration_minutes" type="number" min="1" max="1440" step="1" required ${previewRecipe ? "readonly" : ""} value="${escapeHtml(previewPhase.duration_minutes)}"></div></div>
            <div class="actions"><button class="primary" type="submit" ${this.busy || this.devicesBusy || !zones.length ? "disabled" : ""}>${t.checkPreview}</button>
            <button type="submit" data-beta-selection="true" ${this.busy || this.devicesBusy || !zones.length ? "disabled" : ""}>${t.betaSelection}</button></div>
            <p class="muted">${t.betaSelectionInfo}</p>
          </form>` : ""}
          ${previewRecipe && programs.length && !programReported ? `<p class="message">${t.recipeProgramMissing}</p><button type="button" data-action="edit" data-id="${escapeHtml(previewRecipe.id)}">${t.fixRecipeProgram}</button>` : ""}
          ${this.renderModelTemperatures(device)}
          ${this.sendPreview ? `<section class="message" role="status"><h3>${t.dryRunResult}</h3><p><strong>${t.noTransmission}</strong></p>
            <p>${t.desiredSettings}: ${escapeHtml(this.sendPreview.settings.program)} · ${escapeHtml(this.toDisplay(this.sendPreview.settings.temperature_c))} ${this.unit} · ${escapeHtml(this.sendPreview.settings.duration_minutes)} min</p>
            <p>${t.zone}: ${escapeHtml(this.sendPreview.zone_id)} · ${escapeHtml(this.statusLabel(this.sendPreview.zone_status))}</p>
            <p>${t.blockingReasons}:</p><ul>${this.sendPreview.blocking_reasons.map((reason) => `<li>${escapeHtml(this.reasonLabel(reason))}</li>`).join("")}</ul></section>` : ""}
        </section>` : ""}
        ${this.busy && !this.recipes.length ? `<p>${t.loading}</p>` : ""}
        ${this.admin && this.betaFeatures ? `<section class="preview" id="beta-device-test"><h2>${t.betaTitle}</h2><p>${t.betaIntro}</p>
          <p>${t.device}: ${escapeHtml(device?.name || "—")} · ${t.zone}: ${escapeHtml(this.selectedZoneId || "—")}</p>
          <button type="button" data-action="beta-prepare" ${this.busy || this.devicesBusy || !this.selectedZone() ? "disabled" : ""}>${t.betaPrepare}</button>
          ${this.betaTest ? `<div class="message"><p>${t.betaPending}</p>
            <p>${this.betaTest.recipe_name ? escapeHtml(this.betaTest.recipe_name) : t.manualValues}</p><p><strong>${escapeHtml(this.betaTest.device_name)} · ${t.zone} ${escapeHtml(this.betaTest.zone_id)} · ${escapeHtml(this.programName(this.betaTest.settings.program))} · ${escapeHtml(this.toDisplay(this.betaTest.settings.temperature_c))} ${this.unit} · ${escapeHtml(this.betaTest.settings.duration_minutes)} min</strong></p>
            <button type="button" data-action="beta-confirm" ${this.busy ? "disabled" : ""}>${t.betaConfirm}</button>
            <button type="button" data-action="beta-cancel" ${this.busy ? "disabled" : ""}>${t.betaCancel}</button></div>` : ""}
          ${this.betaMessage ? `<p class="message" role="status">${escapeHtml(this.betaMessage)}</p>` : ""}
        </section>` : ""}
        <section class="cards">${this.filtered().map((recipe) => `<article><h2>${escapeHtml(recipe.name)}</h2>
          ${recipe.description ? `<p>${escapeHtml(recipe.description)}</p>` : ""}
          <p class="muted">${escapeHtml(recipe.category)} ${recipe.tags?.length ? `· ${escapeHtml(recipe.tags.join(", "))}` : ""}</p>
          <p>${escapeHtml(recipe.phases[0]?.program || "")} · ${escapeHtml(this.toDisplay(recipe.phases[0]?.temperature_c || 0))} ${this.unit} · ${escapeHtml(recipe.phases[0]?.duration_minutes || 0)} min</p>
          ${recipe.favorite ? `<p>★ ${t.sharedFavorite}</p>` : ""}
          ${this.admin ? `<div class="actions"><button data-action="personal-favorite" data-id="${escapeHtml(recipe.id)}" aria-label="${t.myFavorite}: ${escapeHtml(recipe.name)}">${this.favorites.has(recipe.id) ? "★" : "☆"} ${t.myFavorite}</button><button data-action="edit" data-id="${escapeHtml(recipe.id)}">${t.edit}</button><button data-action="copy" data-id="${escapeHtml(recipe.id)}">${t.copy}</button><button data-action="delete" data-id="${escapeHtml(recipe.id)}">${t.remove}</button></div>` : ""}
        </article>`).join("")}</section>
        ${!this.busy && !this.filtered().length ? `<p>${t.empty}</p>` : ""}
        ${this.betaFeatures ? `<p class="muted">${t.devicesNote}</p>` : ""}
      </main>`;
    this.renderedEditor = this.editor;
    this.editorRenderedUnit = this.unit;
    this.renderedCategories = categories;
  }

  connectedCallback() {
    this.panelActive = true;
    this.watchConnection(this._hass?.connection);
  }

  disconnectedCallback() {
    this.invalidateControls();
    this.panelActive = false;
    this.watchConnection(null);
  }

  onInput(event) {
    if (this.batchRunning) return;
    if (["preview-temperature", "preview-duration"].includes(event.target.id)) {
      if (event.target.id === "preview-temperature") this.manualPreviewTemperatureC = this.fromDisplay(Number(event.target.value));
      else this.manualPreviewDurationMinutes = Number(event.target.value);
      this.forgetBeta();
      const confirmation = this.shadowRoot.querySelector?.('[data-action="beta-confirm"]');
      if (confirmation) confirmation.disabled = true;
      return;
    }
    if (event.target.id !== "search") return;
    const cursor = event.target.selectionStart;
    this.query = event.target.value;
    this.render();
    const search = this.shadowRoot.getElementById("search");
    search.focus();
    search.setSelectionRange(cursor, cursor);
  }

  onChange(event) {
    if (this.batchRunning) { this.render(); return; }
    if (event.target.id === "recipe-program") {
      this.render();
      return;
    }
    if (event.target.id === "batch-device") {
      this.selectedDeviceId = event.target.value;
      this.selectedZoneId = String(this.selectedDevice()?.zones?.[0]?.zone_id || "");
      this.batchPlan = null;
      this.batchRunId = null;
      this.forgetBeta();
      this.render();
      return;
    }
    if (event.target.id === "category") {
      this.category = event.target.value;
      this.render();
    } else if (event.target.id === "recipe-category") {
      const isNew = event.target.value === "new";
      this.shadowRoot.getElementById("new-category-field").hidden = !isNew;
      const input = this.shadowRoot.getElementById("recipe-category-new");
      input.required = isNew;
      if (isNew) input.focus();
    } else if (event.target.id === "favorite-filter") {
      this.favoriteFilter = event.target.value;
      this.render();
    } else if (event.target.id === "preview-device") {
      this.forgetBeta();
      this.selectedDeviceId = event.target.value;
      this.selectedZoneId = this.selectedDevice()?.zones?.[0]
        ? String(this.selectedDevice().zones[0].zone_id) : "";
      this.manualPreviewProgram = this.selectedDevice()?.programs?.[0]?.id || "airfry";
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-zone") {
      this.forgetBeta();
      this.selectedZoneId = event.target.value;
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-recipe") {
      this.forgetBeta();
      this.previewRecipeId = event.target.value;
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-program") {
      this.forgetBeta();
      this.manualPreviewProgram = event.target.value;
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "import-file") {
      this.previewFile(event.target.files?.[0]);
    }
  }

  async previewFile(file) {
    if (!this.admin || !file || file.size > 1_000_000) {
      this.error = this.words.invalidFile;
      this.render();
      return;
    }
    this.busy = true;
    this.render();
    try {
      this.preview = await this.request("import_preview", { payload: await file.text() });
      this.error = "";
    } catch (error) {
      this.showError(error);
    } finally {
      this.busy = false;
      this.render();
    }
  }

  async onClick(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const type = button.dataset.action;
    if (type === "menu") {
      this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }));
      return;
    }
    if (type === "batch-stop" && this.admin) return this.stopBatch();
    if (this.busy || this.devicesBusy || this.batchRunning) return;
    if (this.admin && type === "beta-recover") return this.recoverBeta();
    if (this.admin && type === "batch-prepare") return this.prepareBatch();
    if (this.admin && type === "batch-start") return this.startBatch();
    const recipe = this.recipes.find((item) => item.id === button.dataset.id);
    const t = this.words;
    if (type === "refresh") return this.load();
    if (!this.admin) return;
    if (type.startsWith("diagnostics-") || type.startsWith("notifications-")) return this.supportAction(type, button);
    if (type === "access-load") return this.manageAccess();
    if (type === "access-grant") {
      const element = this.shadowRoot.getElementById("device-access-form");
      if (!element?.reportValidity?.()) return;
      const form = new FormData(element);
      return this.manageAccess({ user_id: String(form.get("user_id") || ""), device_id: String(form.get("device_id") || ""), allowed: true });
    }
    if (type === "access-revoke" && confirm(this.accessWords.confirm)) return this.manageAccess({ user_id: button.dataset.user, device_id: button.dataset.device, allowed: false });
    if (type === "editor-program-mode" && this.editor) {
      this.captureEditorDraft();
      this.editorCustomProgram = !this.editorCustomProgram;
      this.render();
      return;
    }
    if (type === "beta-prepare") return this.prepareSelectedBeta(this.shadowRoot.getElementById("device-preview-form"));
    if (type === "beta-confirm") return this.confirmBetaTest();
    if (type === "beta-cancel") { this.forgetBeta(); this.render(); return; }
    if (type === "refresh-devices") {
      await this.loadDevices();
      this.render();
      return;
    }
    if (type === "new") this.editor = { name: "", description: "", category: "", tags: [], phases: [{}] };
    if (type === "sample" && !this.recipes.length && confirm(t.sampleConfirm)) {
      const recipe = {
        name: t.sampleName, description: t.sampleDescription, category: "", tags: [], favorite: false,
        phases: [{ program: "airfry", temperature_c: 180, duration_minutes: 10 }],
      };
      return this.action(() => this.request("create", { recipe }), t.saved);
    }
    if (type === "edit" && recipe) this.editor = structuredClone(recipe);
    if (type === "cancel") this.editor = null;
    if (type === "cancel-preview") this.preview = null;
    if (type === "choose-import") return this.shadowRoot.getElementById("import-file").click();
    if (type === "delete" && recipe && confirm(t.deleteConfirm)) {
      return this.action(() => this.request("delete", { recipe_id: recipe.id }), t.deleted);
    }
    if (type === "copy" && recipe) {
      const name = prompt(t.copyName, `${recipe.name} (${t.copy})`);
      if (name?.trim()) return this.action(() => this.request("duplicate", { recipe_id: recipe.id, name: name.trim() }), t.saved);
    }
    if (type === "personal-favorite" && recipe) {
      const favorite = !this.favorites.has(recipe.id);
      return this.action(async () => {
        await this.request("set_favorite", { recipe_id: recipe.id, favorite });
        if (favorite) this.favorites.add(recipe.id);
        else this.favorites.delete(recipe.id);
      }, t.myFavorite);
    }
    if (type === "export") {
      try {
        const result = await this.request("export");
        const link = document.createElement("a");
        link.href = result.url;
        link.download = result.filename;
        link.click();
      } catch (error) { this.showError(error); }
    }
    if (type.startsWith("import-") && this.preview) {
      const policy = type === "import-replace" ? "replace_ids" : "skip";
      if (policy === "replace_ids" && !confirm(t.replaceConfirm)) return;
      const token = this.preview.token;
      return this.action(
        () => this.request("import_confirm", { token, policy }),
        (result) => `${t.imported}: ${result.imported}`,
      );
    }
    this.render();
    if (["new", "edit"].includes(type)) this.shadowRoot.getElementById("editor")?.scrollIntoView?.({ block: "start", behavior: "smooth" });
  }

  onSubmit(event) {
    if (event.target.id === "notifications-form") { event.preventDefault(); return; }
    if (event.target.id === "device-access-form") { event.preventDefault(); return; }
    if (this.batchRunning) { event.preventDefault(); return; }
    if (event.target.id === "device-preview-form") {
      event.preventDefault();
      if (event.submitter?.dataset?.betaSelection === "true") return this.prepareSelectedBeta(event.target);
      return this.submitDevicePreview(event.target);
    }
    if (event.target.id !== "editor") return;
    event.preventDefault();
    if (!this.admin || this.editor?.phases?.length > 1) return;
    const form = new FormData(event.target);
    const categoryChoice = String(form.get("category_choice") || "");
    const categories = this.categories();
    const newCategory = String(form.get("category_new") || "").trim().replace(/\s+/g, " ");
    const category = categoryChoice === "new"
      ? categories.find((name) => name.toLocaleLowerCase() === newCategory.toLocaleLowerCase()) || newCategory
      : categoryChoice.startsWith("existing-") ? categories[Number(categoryChoice.slice(9))] || "" : "";
    const recipe = {
      name: String(form.get("name") || "").trim(),
      description: String(form.get("description") || "").trim(),
      category,
      tags: String(form.get("tags") || "").split(",").map((tag) => tag.trim()).filter(Boolean),
      favorite: form.has("favorite"),
      phases: [{
        program: String(form.get("program") || "").trim(),
        temperature_c: this.fromDisplay(Number(form.get("temperature_c"))),
        duration_minutes: Number(form.get("duration_minutes")),
      }],
    };
    if (this.editor.id) recipe.id = this.editor.id;
    const command = this.editor.id ? "update" : "create";
    this.forgetBeta();
    this.sendPreview = null;
    return this.action(() => this.request(command, { recipe }), this.words.saved);
  }

  betaError(error) {
    const key = {
      connection_changed: "betaConnection",
      reset_unavailable: "resetUnavailable", reset_failed: "resetFailed", source: "betaSource", program_unsupported: "betaProgram", test_range: "betaRange", recipe_changed: "betaRecipeChanged",
      freshness: "betaFreshness", refresh_unavailable: "betaRefreshUnavailable", refresh_failed: "betaRefreshFailed", state_changed: "betaState", zones: "betaZones",
      adapter_version: "betaAdapter", adapter_data: "adapterIncompatible", model: "betaModel", capabilities: "betaCaps",
      busy: "betaBusy", confirmation: "betaExpired", outcome_unknown: "betaUnknown",
      connection: "reasonConnection", target: "targetMissing", unauthorized: "unauthorized",
      not_configured: "notConfigured",
    }[error?.message];
    return `${this.words.betaNoSend} ${this.words[key || "genericError"]}`;
  }

  showBatch() {
    this.shadowRoot.getElementById("batch-test")?.scrollIntoView?.({ block: "start", behavior: "smooth" });
  }

  async recoverBeta() {
    if (!this.admin || this.busy || this.batchRunning || !this.controlCurrent(this.controlRevision) || !this.selectedDeviceId || !confirm(this.words.betaRecoverConfirm)) return;
    this.busy = true;
    const revision = this.controlRevision;
    this.batchPlan = null;
    this.forgetBeta();
    this.batchRunId = null;
    this.batchMessage = this.words.batchLoading;
    this.render();
    try {
      await this.request("beta_recover", { device_id: this.selectedDeviceId, acknowledge_physical_reset: true });
      if (this.controlCurrent(revision)) this.batchMessage = this.words.betaRecovered;
    } catch (error) { if (this.controlCurrent(revision)) this.batchMessage = this.betaError(error); }
    finally { this.busy = false; this.render(); if (this.controlCurrent(revision)) this.showBatch(); }
  }

  async prepareBatch() {
    if (!this.admin || this.busy || this.batchRunning || !this.controlCurrent(this.controlRevision) || !this.selectedDeviceId) return;
    this.busy = true;
    const revision = this.controlRevision;
    this.forgetBeta();
    const selection = this.selectionRevision;
    const device_id = this.selectedDeviceId;
    this.batchPlan = null;
    this.batchRunId = null;
    this.batchResults = [];
    this.batchMessage = this.words.batchLoading;
    this.render();
    try {
      const plan = await this.request("batch_prepare", { device_id });
      if (this.controlCurrent(revision) && this.selectionRevision === selection && this.selectedDeviceId === device_id) {
        this.batchPlan = plan;
        this.batchMessage = "";
      } else if (this.controlCurrent(revision)) {
        this.batchMessage = this.words.betaSelectionChanged;
      }
    } catch (error) { if (this.controlCurrent(revision)) this.batchMessage = this.betaError(error); }
    finally { this.busy = false; this.render(); if (this.controlCurrent(revision)) this.showBatch(); }
  }

  async stopBatch() {
    this.batchStopRequested = true;
    this.batchMessage = this.words.batchStopped;
    this.render();
    if (this.batchRunId) {
      try { await this.request("batch_stop", { run_id: this.batchRunId }); } catch (_) { /* never retry */ }
    }
  }

  batchNeedsReset(plan, index) {
    const current = plan.steps[index]?.settings, previous = plan.steps[index - 1]?.settings;
    return Boolean(current && previous && ((plan.resets_between_settings &&
      ["program", "temperature_c", "duration_minutes"].some(key => current[key] !== previous[key])) ||
      (plan.resets_between_programs && current.program !== previous.program)));
  }

  async startBatch() {
    if (!this.admin || this.busy || this.batchRunning || !this.controlCurrent(this.controlRevision) || !this.batchPlan || this.batchRunId) return;
    this.batchRunning = true;
    const revision = this.controlRevision;
    const plan = this.batchPlan;
    this.batchStopRequested = false;
    this.batchResults = [];
    this.batchRunId = plan.token;
    this.render();
    this.showBatch();
    try {
      const run = await this.request("batch_start", { token: plan.token, acknowledge_supervised_batch: true });
      let nonce = run.next_token;
      while (this.controlCurrent(revision) && !this.batchStopRequested && nonce) {
        const next = plan.steps[this.batchResults.length];
        this.batchMessage = `${this.words.batchProgress} ${this.batchResults.length + 1} ${this.words.batchOf} ${run.total}: ${this.programName(next.settings.program)} · ${this.words.zone} ${next.zone_id}`;
        if (this.batchNeedsReset(plan, this.batchResults.length)) this.batchMessage += ` · ${this.words.batchReset}`;
        this.render();
        const result = await this.request("batch_next", { run_id: run.run_id, next_token: nonce });
        if (!this.controlCurrent(revision)) return;
        if (result.stopped) {
          this.batchMessage = `${this.words.batchProgress} ${result.failed_step}: ${this.programName(result.settings.program)} · ${this.words.zone} ${result.zone_id}. ${this.words.betaRejected}${Number.isInteger(result.error_code) ? ` (Code ${result.error_code})` : ""}`;
          this.batchStopRequested = true;
          return;
        }
        this.batchResults.push(result);
        nonce = result.done ? null : result.next_token;
      }
      if (this.controlCurrent(revision)) this.batchMessage = this.batchStopRequested ? this.words.batchStopped : this.words.batchDone;
    } catch (error) {
      if (!this.controlCurrent(revision)) return;
      const reason = { reset_unavailable: "resetUnavailable", reset_failed: "resetFailed", zones: "betaZones", freshness: "betaFreshness", refresh_failed: "betaRefreshFailed",
        batch_connection: "batchConnection", state_changed: "betaState", unauthorized: "unauthorized" }[error?.message];
      const failed = plan.steps[this.batchResults.length];
      this.batchMessage = this.batchStopRequested ? this.words.batchStopped
        : `${this.words.batchProgress} ${this.batchResults.length + 1}: ${this.programName(failed.settings.program)} · ${this.words.zone} ${failed.zone_id}. ${this.words.batchFailed}${reason ? ` ${this.words[reason]}` : ""}`;
      this.batchStopRequested = true;
      try { await this.request("batch_stop", { run_id: this.batchRunId }); } catch (_) { /* no replay */ }
    } finally { this.batchRunning = false; this.render(); if (this.controlCurrent(revision)) this.showBatch(); }
  }

  async prepareSelectedBeta(formElement) {
    if (!this.admin || this.busy || this.devicesBusy || this.batchRunning || !this.controlCurrent(this.controlRevision)) return;
    if (!formElement) {
      this.forgetBeta();
      this.betaMessage = this.betaError({ message: "source" });
      this.render();
      this.showBeta();
      return;
    }
    const form = new FormData(formElement);
    const recipeId = String(form.get("recipe_id") || "");
    const source = recipeId ? { recipe_id: recipeId } : { settings: {
      program: String(form.get("program") || "").trim(),
      temperature_c: this.fromDisplay(Number(form.get("temperature_c"))),
      duration_minutes: Number(form.get("duration_minutes")),
    } };
    return this.prepareBetaTest(source);
  }

  async prepareBetaTest(source = null) {
    if (!this.admin || this.busy || this.devicesBusy || this.batchRunning || !this.controlCurrent(this.controlRevision) || !this.selectedZone() || !confirm(this.words.betaWarning)) return;
    const device_id = this.selectedDeviceId;
    const zone_id = Number(this.selectedZoneId);
    this.forgetBeta();
    const revision = this.controlRevision;
    const selection = this.selectionRevision;
    this.betaMessage = this.words.betaRefreshing;
    this.busy = true;
    this.render();
    try {
      const fields = { device_id, zone_id, acknowledge_unverified: true };
      if (source !== null) fields.source = source;
      const result = await this.request("beta_prepare", fields);
      if (this.controlCurrent(revision) && this.selectionRevision === selection &&
          this.selectedDeviceId === device_id && Number(this.selectedZoneId) === zone_id) {
        this.betaMessage = "";
        this.betaTest = result;
      } else {
        this.cancelBetaToken(result.token);
        if (this.controlCurrent(revision)) this.betaMessage = this.words.betaSelectionChanged;
      }
    } catch (error) {
      if (this.controlCurrent(revision)) this.betaMessage = this.betaError(error);
    } finally { this.busy = false; this.render(); if (this.controlCurrent(revision)) this.showBeta(); }
  }

  showBeta() {
    this.shadowRoot.getElementById("beta-device-test")?.scrollIntoView?.({ block: "start", behavior: "smooth" });
  }

  async confirmBetaTest() {
    if (!this.admin || this.busy || this.devicesBusy || !this.controlCurrent(this.controlRevision) || !this.betaTest) return;
    const prepared = this.betaTest;
    const exact = `${prepared.device_name} · ${this.words.zone} ${prepared.zone_id} · ${prepared.settings.program} · ${this.toDisplay(prepared.settings.temperature_c)} ${this.unit} · ${prepared.settings.duration_minutes} min`;
    if (!confirm(`${exact}\n${this.words.betaConfirmWarning}`)) return;
    const revision = this.controlRevision;
    const selection = this.selectionRevision;
    this.betaSubmittingToken = prepared.token;
    this.betaTest = null; // Never reuse a confirmation, including after a lost response.
    this.busy = true;
    this.betaMessage = "";
    this.render();
    try {
      const result = await this.request("beta_confirm", { token: prepared.token, acknowledge_supervised_test: true });
      if (this.controlCurrent(revision) && this.selectionRevision === selection) this.betaMessage = result.outcome === "accepted" ? this.words.betaAccepted : result.outcome === "rejected" ? `${this.words.betaRejected}${Number.isInteger(result.error_code) ? ` (Code ${result.error_code})` : ""}` : this.words.betaUnknown;
    } catch (error) {
      if (this.controlCurrent(revision) && this.selectionRevision === selection) this.betaMessage = error?.code === "beta_test_blocked" ? this.betaError(error) : this.words.betaUnknown;
    } finally { this.betaSubmittingToken = null; this.busy = false; this.render(); }
  }

  async submitDevicePreview(formElement) {
    if (!this.admin || this.busy || this.devicesBusy) return;
    const form = new FormData(formElement);
    const request = {
      device_id: String(form.get("device_id") || ""),
      zone_id: Number(form.get("zone_id")),
      settings: {
        program: String(form.get("program") || "").trim(),
        temperature_c: this.fromDisplay(Number(form.get("temperature_c"))),
        duration_minutes: Number(form.get("duration_minutes")),
      },
    };
    this.busy = true;
    this.deviceError = "";
    this.sendPreview = null;
    this.render();
    try {
      this.sendPreview = await this.request("prepare_send", request);
    } catch (error) {
      this.deviceError = error?.code === "target_not_found" ? this.words.targetMissing
        : error?.code === "unauthorized" ? this.words.unauthorized
        : error?.code === "invalid_format" ? this.words.invalid : this.words.genericError;
    } finally {
      this.busy = false;
      this.render();
    }
  }
}

// An older query-versioned module may already own the panel's element name.
// Still export this module's current base class for the dashboard card.
if (!customElements.get("airfryer-recipes-panel")) customElements.define("airfryer-recipes-panel", AirfryerRecipesPanel);
