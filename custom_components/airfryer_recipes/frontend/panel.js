// Local Home Assistant custom panel. All mutations go through the authenticated API.
const WORDS = {
  en: {
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
    unauthorized: "Administrator permission is required.", conflict: "A recipe with that ID or name already exists.",
    invalid: "Check the recipe values and try again.", expired: "The preview expired. Select the file again.",
    storage: "Saving failed. Check the Home Assistant logs.", notConfigured: "The integration is not configured.",
    phases: "Cooking phase", refresh: "Refresh", devicesNote: "Live device transmission is not available.",
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
    estimatedProgram: "estimated", confirmedProgram: "confirmed", unknownProgram: "not reported by this device",
    sendUnverified: "sending unverified", sendConfirmed: "sending confirmed",
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
    unauthorized: "Administratorrechte sind erforderlich.", conflict: "Ein Rezept mit dieser ID oder diesem Namen existiert bereits.",
    invalid: "Bitte die Rezeptwerte prüfen.", expired: "Die Vorschau ist abgelaufen. Datei erneut auswählen.",
    storage: "Speichern fehlgeschlagen. Bitte die Home-Assistant-Protokolle prüfen.", notConfigured: "Die Integration ist nicht eingerichtet.",
    phases: "Garphase", refresh: "Aktualisieren", devicesNote: "Echte Geräteübertragung ist nicht verfügbar.",
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
    estimatedProgram: "geschätzt", confirmedProgram: "bestätigt", unknownProgram: "von diesem Gerät nicht gemeldet",
    sendUnverified: "Senden ungeprüft", sendConfirmed: "Senden bestätigt",
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

class AirfryerRecipesPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.recipes = [];
    this.query = "";
    this.category = "";
    this.favoriteFilter = "";
    this.favorites = new Set();
    this.editor = null;
    this.preview = null;
    this.deviceState = { status: "adapter_missing", devices: [], live_send_enabled: false };
    this.selectedDeviceId = "";
    this.selectedZoneId = "";
    this.previewRecipeId = "";
    this.manualPreviewProgram = "airfry";
    this.sendPreview = null;
    this.deviceError = "";
    this.devicesBusy = false;
    this.busy = false;
    this.notice = "";
    this.error = "";
    this.started = false;
    this.shadowRoot.addEventListener("click", (event) => this.onClick(event));
    this.shadowRoot.addEventListener("submit", (event) => this.onSubmit(event));
    this.shadowRoot.addEventListener("input", (event) => this.onInput(event));
    this.shadowRoot.addEventListener("change", (event) => this.onChange(event));
  }

  set hass(value) {
    const oldLanguage = this._hass?.language;
    const oldAdmin = this._hass?.user?.is_admin;
    const oldUnit = this._hass?.config?.unit_system?.temperature;
    this._hass = value;
    if (!this.started && value) {
      this.started = true;
      this.load();
    } else if (oldLanguage !== value?.language || oldAdmin !== value?.user?.is_admin ||
        oldUnit !== value?.config?.unit_system?.temperature) {
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
    return this._hass.callWS({ type: `airfryer_recipes/${name}`, ...fields });
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
    const limits = program.limits_status === "confirmed" ? this.words.confirmedProgram
      : program.limits_status === "estimated" ? this.words.estimatedProgram : this.words.unknown;
    const send = program.send_status === "confirmed" ? this.words.sendConfirmed : this.words.sendUnverified;
    return `${this.programName(program.id)} · ${limits} · ${send}`;
  }

  async loadDevices() {
    if (!this.admin) return;
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

  render() {
    if (!this.shadowRoot) return;
    const t = this.words;
    const categories = this.categories();
    const selected = this.editor;
    const phase = selected?.phases?.[0] || {};
    const multiple = selected?.phases?.length > 1;
    const device = this.selectedDevice();
    const zones = device?.zones || [];
    const previewRecipe = this.selectedPreviewRecipe();
    const previewPhase = previewRecipe?.phases?.[0] || {
      program: this.manualPreviewProgram, temperature_c: 180, duration_minutes: 10,
    };
    const programs = device?.programs || [];
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
        <div class="toolbar">
          <input id="search" type="search" aria-label="${t.search}" placeholder="${t.search}" value="${escapeHtml(this.query)}">
          <select id="category" aria-label="${t.category}"><option value="">${t.all}</option>${categories.map((name) => `<option value="${escapeHtml(name)}" ${this.category === name ? "selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>
          <select id="favorite-filter" aria-label="${t.myFavorite}"><option value="">${t.allFavorites}</option><option value="mine" ${this.favoriteFilter === "mine" ? "selected" : ""}>${t.onlyMine}</option><option value="shared" ${this.favoriteFilter === "shared" ? "selected" : ""}>${t.onlyShared}</option></select>
          <button data-action="refresh" ${this.busy ? "disabled" : ""}>${t.refresh}</button>
          ${this.admin ? `<button class="primary" data-action="new">${t.new}</button>${!this.recipes.length ? `<button data-action="sample">${t.sample}</button>` : ""}<button data-action="choose-import">${t.import}</button><button data-action="export">${t.export}</button>` : ""}
          <input class="visually-hidden" id="import-file" type="file" accept=".json,application/json">
        </div>
        ${selected ? `<form id="editor" class="editor"><h2>${selected.id ? t.edit : t.new}</h2>
          ${multiple ? `<p class="message error">${t.multiPhase}</p>` : ""}
          <div class="grid"><div><label for="recipe-name">${t.name}</label><input id="recipe-name" name="name" maxlength="100" required value="${escapeHtml(selected.name)}"></div>
          <div><label for="recipe-category">${t.category}</label><select id="recipe-category" name="category_choice"><option value="" ${!selected.category ? "selected" : ""}>${t.noCategory}</option>${categories.map((name, index) => `<option value="existing-${index}" ${selected.category === name ? "selected" : ""}>${escapeHtml(name)}</option>`).join("")}<option value="new">${t.addCategory}</option></select>
          <div id="new-category-field" hidden><label for="recipe-category-new">${t.newCategory}</label><input id="recipe-category-new" name="category_new" maxlength="64"></div></div></div>
          <label for="recipe-description">${t.description}</label><textarea id="recipe-description" name="description" maxlength="500">${escapeHtml(selected.description)}</textarea>
          <label for="recipe-tags">${t.tags}</label><input id="recipe-tags" name="tags" value="${escapeHtml((selected.tags || []).join(", "))}">
          <label><input type="checkbox" name="favorite" ${selected.favorite ? "checked" : ""} style="width:auto;min-height:auto"> ${t.sharedFavorite}</label>
          <h3>${t.phases}</h3><div class="grid">
          <div><label for="recipe-program">${t.program}</label><input id="recipe-program" name="program" maxlength="64" required value="${escapeHtml(phase.program)}"></div>
          <div><label for="recipe-temperature">${t.temperature} (${this.unit})</label><input id="recipe-temperature" name="temperature_c" type="number" min="${this.unit === "°F" ? 32 : 0}" max="${this.unit === "°F" ? 752 : 400}" step="1" required value="${phase.temperature_c === undefined ? "" : escapeHtml(this.toDisplay(phase.temperature_c))}"></div>
          <div><label for="recipe-duration">${t.duration}</label><input id="recipe-duration" name="duration_minutes" type="number" min="1" max="1440" step="1" required value="${escapeHtml(phase.duration_minutes)}"></div></div>
          <div class="actions"><button class="primary" type="submit" ${this.busy || multiple ? "disabled" : ""}>${t.save}</button><button type="button" data-action="cancel">${t.cancel}</button></div></form>` : ""}
        ${this.preview ? `<section class="preview"><h2>${t.preview}</h2><p>${t.incoming}: ${this.preview.incoming_count}</p><p>${t.duplicateIds}: ${this.preview.duplicate_ids.length}${this.preview.duplicate_ids.length ? ` (${escapeHtml(this.preview.duplicate_ids.join(", "))})` : ""}</p><p>${t.duplicateNames}: ${this.preview.duplicate_names.length}${this.preview.duplicate_names.length ? ` (${escapeHtml(this.preview.duplicate_names.join(", "))})` : ""}</p>
          <div class="actions"><button class="primary" data-action="import-skip" ${this.busy ? "disabled" : ""}>${t.skip}</button><button data-action="import-replace" ${this.busy ? "disabled" : ""}>${t.replace}</button><button data-action="cancel-preview">${t.cancel}</button></div></section>` : ""}
        ${this.admin ? `<section class="preview" id="device-preview"><h2>${t.devicePreview}</h2>
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
            <div class="actions"><button class="primary" type="submit" ${this.busy || this.devicesBusy || !zones.length ? "disabled" : ""}>${t.checkPreview}</button></div>
          </form>` : ""}
          ${this.sendPreview ? `<section class="message" role="status"><h3>${t.dryRunResult}</h3><p><strong>${t.noTransmission}</strong></p>
            <p>${t.desiredSettings}: ${escapeHtml(this.sendPreview.settings.program)} · ${escapeHtml(this.toDisplay(this.sendPreview.settings.temperature_c))} ${this.unit} · ${escapeHtml(this.sendPreview.settings.duration_minutes)} min</p>
            <p>${t.zone}: ${escapeHtml(this.sendPreview.zone_id)} · ${escapeHtml(this.statusLabel(this.sendPreview.zone_status))}</p>
            <p>${t.blockingReasons}:</p><ul>${this.sendPreview.blocking_reasons.map((reason) => `<li>${escapeHtml(this.reasonLabel(reason))}</li>`).join("")}</ul></section>` : ""}
        </section>` : ""}
        ${this.busy && !this.recipes.length ? `<p>${t.loading}</p>` : ""}
        <section class="cards">${this.filtered().map((recipe) => `<article><h2>${escapeHtml(recipe.name)}</h2>
          ${recipe.description ? `<p>${escapeHtml(recipe.description)}</p>` : ""}
          <p class="muted">${escapeHtml(recipe.category)} ${recipe.tags?.length ? `· ${escapeHtml(recipe.tags.join(", "))}` : ""}</p>
          <p>${escapeHtml(recipe.phases[0]?.program || "")} · ${escapeHtml(this.toDisplay(recipe.phases[0]?.temperature_c || 0))} ${this.unit} · ${escapeHtml(recipe.phases[0]?.duration_minutes || 0)} min</p>
          ${recipe.favorite ? `<p>★ ${t.sharedFavorite}</p>` : ""}
          ${this.admin ? `<div class="actions"><button data-action="personal-favorite" data-id="${escapeHtml(recipe.id)}" aria-label="${t.myFavorite}: ${escapeHtml(recipe.name)}">${this.favorites.has(recipe.id) ? "★" : "☆"} ${t.myFavorite}</button><button data-action="edit" data-id="${escapeHtml(recipe.id)}">${t.edit}</button><button data-action="copy" data-id="${escapeHtml(recipe.id)}">${t.copy}</button><button data-action="delete" data-id="${escapeHtml(recipe.id)}">${t.remove}</button></div>` : ""}
        </article>`).join("")}</section>
        ${!this.busy && !this.filtered().length ? `<p>${t.empty}</p>` : ""}
        <p class="muted">${t.devicesNote}</p>
      </main>`;
  }

  onInput(event) {
    if (event.target.id !== "search") return;
    const cursor = event.target.selectionStart;
    this.query = event.target.value;
    this.render();
    const search = this.shadowRoot.getElementById("search");
    search.focus();
    search.setSelectionRange(cursor, cursor);
  }

  onChange(event) {
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
      this.selectedDeviceId = event.target.value;
      this.selectedZoneId = this.selectedDevice()?.zones?.[0]
        ? String(this.selectedDevice().zones[0].zone_id) : "";
      this.manualPreviewProgram = this.selectedDevice()?.programs?.[0]?.id || "airfry";
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-zone") {
      this.selectedZoneId = event.target.value;
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-recipe") {
      this.previewRecipeId = event.target.value;
      this.sendPreview = null;
      this.render();
    } else if (event.target.id === "preview-program") {
      this.manualPreviewProgram = event.target.value;
      this.sendPreview = null;
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
    if (this.busy || this.devicesBusy) return;
    const recipe = this.recipes.find((item) => item.id === button.dataset.id);
    const t = this.words;
    if (type === "refresh") return this.load();
    if (!this.admin) return;
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
  }

  onSubmit(event) {
    if (event.target.id === "device-preview-form") {
      event.preventDefault();
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
    return this.action(() => this.request(command, { recipe }), this.words.saved);
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

customElements.define("airfryer-recipes-panel", AirfryerRecipesPanel);
