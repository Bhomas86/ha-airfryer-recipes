// Bundled locally; share the panel's transport, localization and token lifecycle.
import { AirfryerRecipesPanel } from "./panel.js?v=0.1.0b20";

const CARD_TEXT = {
  en: {
    title: "Kitchen air fryer", zone: "Zone", last: "Last sent", empty: "No settings sent yet",
    recipe: "Recipe", manual: "Manual", choose: "Choose a recipe", program: "Program",
    temperature: "Temperature", duration: "Duration", send: "Send settings", start: "Start at appliance",
    online: "Online", offline: "Offline", unknown: "Unknown", refresh: "Refresh status and recipes",
    reported: "Reported connection and zone status; refresh to update. Sending checks fresh state again.",
    admin: "No permitted device available. Ask an administrator to share the device, then refresh.",
    test: "Test mode · no transmission", preview: "Check test preview", previewDone: "Test preview checked. No device command was sent.",
    beta: "Supervised beta · settings only", historyError: "Last sent settings are unavailable.",
    saveError: "Transmission accepted, but last settings could not be saved. Do not resend just to save them.",
    accepted: "Settings accepted by adapter; not confirmed on the appliance. Check the appliance.",
    historyInfo: "Last accepted transmission, not the current appliance settings.",
    confirm: "Send these exact settings once as a supervised beta test? Check both zones are idle. Cooking starts at the appliance only.",
    configTitle: "Title", configDevice: "Home Assistant device ID (optional)", configTest: "Test mode (no device commands)",
    configHelp: "Leave the device ID empty to initially select an available appliance. Administrators grant ordinary users an entire device in the recipe library. Live transmission remains a supervised beta test.",
    size: "Card size", graphicSize: "Device graphic size", compact: "Compact", normal: "Normal", large: "Large", small: "Small", showStatus: "Show status", showHistory: "Show last sent settings",
    zoneStyle: "Zone selection on the image", zoneOutline: "A – Subtle outline", zoneInvisible: "B – Invisible touch areas",
    zoneStyleHelp: "A marks the selected zone with a thin outline and small numbers. B keeps the photo clear; its configured zones remain tappable. Set their size and position in Customize Airfryer, where the boxes stay visible. Choose zones on the image or beside it.",
    invalidConfig: "Invalid Airfryer Recipes card configuration",
  },
  de: {
    title: "Airfryer Küche", zone: "Fach", last: "Zuletzt gesendet", empty: "Noch keine Einstellungen gesendet",
    recipe: "Rezept", manual: "Manuell", choose: "Rezept auswählen", program: "Programm",
    temperature: "Temperatur", duration: "Dauer", send: "Einstellungen senden", start: "Start am Gerät",
    online: "Online", offline: "Offline", unknown: "Unbekannt", refresh: "Status und Rezepte aktualisieren",
    reported: "Gemeldete Verbindung und Fachzustände; zum Aktualisieren neu laden. Senden prüft den Zustand erneut frisch.",
    admin: "Kein freigegebenes Gerät verfügbar. Ein Administrator muss das Gerät freigeben; anschließend aktualisieren.",
    test: "Testmodus · keine Übertragung", preview: "Testvorschau prüfen", previewDone: "Testvorschau geprüft. Es wurde kein Gerätebefehl gesendet.",
    beta: "Beaufsichtigte Beta · nur Einstellungen", historyError: "Zuletzt gesendete Einstellungen sind nicht verfügbar.",
    saveError: "Übertragung angenommen, letzte Einstellungen konnten aber nicht gespeichert werden. Dafür nicht erneut senden.",
    accepted: "Einstellungen vom Adapter angenommen; keine Gerätebestätigung. Am Gerät kontrollieren.",
    historyInfo: "Letzte angenommene Übertragung, nicht die aktuellen Geräteeinstellungen.",
    confirm: "Diese Einstellungen einmalig als beaufsichtigten Beta-Test senden? Beide Fächer müssen ruhen. Garstart nur am Gerät.",
    configTitle: "Titel", configDevice: "Home-Assistant-Geräte-ID (optional)", configTest: "Testmodus (keine Gerätebefehle)",
    configHelp: "Ohne Geräte-ID wird anfangs ein verfügbares Gerät ausgewählt. Administratoren geben normalen Benutzern in der Rezeptbibliothek ein ganzes Gerät frei. Echtes Senden bleibt ein beaufsichtigter Beta-Test.",
    size: "Kartengröße", graphicSize: "Größe der Gerätegrafik", compact: "Kompakt", normal: "Normal", large: "Groß", small: "Klein", showStatus: "Status anzeigen", showHistory: "Zuletzt gesendete Einstellungen anzeigen",
    zoneStyle: "Fachauswahl auf dem Bild", zoneOutline: "A – Dezente Markierung", zoneInvisible: "B – Unsichtbare Touchbereiche",
    zoneStyleHelp: "A markiert das ausgewählte Fach mit einer dünnen Kontur und kleinen Nummern. B lässt das Foto frei; die eingerichteten Fachbereiche bleiben antippbar. Größe und Position unter Airfryer individualisieren einstellen; dort bleiben die Rechtecke sichtbar. Fach auf dem Bild oder daneben auswählen.",
    invalidConfig: "Ungültige Konfiguration der Airfryer-Recipes-Card",
  },
};
const html = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));
const textFor = (hass) => CARD_TEXT[hass?.language?.toLowerCase().startsWith("de") ? "de" : "en"];
const displayConfig = (config) => ({ size: "normal", graphic_size: "normal", show_status: true, show_last_sent: true, ...config, zone_style: config.zone_style ?? "outline" });
const validDisplay = (config) => [undefined, "compact", "normal", "large"].includes(config.size) &&
  [undefined, "small", "normal", "large"].includes(config.graphic_size) &&
  [undefined, "outline", "invisible"].includes(config.zone_style) &&
  ["show_status", "show_last_sent"].every((key) => config[key] === undefined || typeof config[key] === "boolean");
const samePhase = (a, b) => a && b && ["program", "temperature_c", "duration_minutes"].every((key) => a[key] === b[key]);

class AirfryerRecipesCard extends AirfryerRecipesPanel {
  constructor() {
    super();
    this.config = { dry_run: true };
    this.drafts = new Map();
    this.history = {};
    this.historyAvailable = null;
    this.historyDevice = "";
    this.historyRevision = 0;
    this.sourceMode = "manual";
    this.loadRevision = 0;
    this.needsRecovery = false;
    this.previewMessage = "";
    this.reloadRequested = false;
    this.accessUserId = "";
    this.appearance = null;
    this.appearanceRevision = 0;
    this.appearanceRefreshPending = false;
    this.appearanceChanged = (event) => {
      if (event.detail?.device_id === this.selectedDeviceId) this.refreshAppearance();
    };
  }

  connectedCallback() {
    super.connectedCallback();
    window.addEventListener("airfryer-recipes-appearance-saved", this.appearanceChanged);
    // HA can detach the dashboard card while its editor is open.
    if (this.appearanceConnectedOnce) this.refreshAppearance();
    this.appearanceConnectedOnce = true;
  }

  disconnectedCallback() {
    window.removeEventListener("airfryer-recipes-appearance-saved", this.appearanceChanged);
    super.disconnectedCallback();
  }

  setConfig(config) {
    if (!config || !validDisplay(config) || (config.device_id !== undefined && typeof config.device_id !== "string") ||
        (config.title !== undefined && typeof config.title !== "string") ||
        (config.dry_run !== undefined && typeof config.dry_run !== "boolean")) throw new Error(this.cardWords.invalidConfig);
    this.saveDraft();
    this.invalidateControls();
    this.config = displayConfig({ ...config, dry_run: config.dry_run !== false });
    if (config.device_id) this.selectedDeviceId = config.device_id;
    this.clearFeedback();
    if (this.started) this.scheduleReload();
    else this.render();
  }

  scheduleReload() {
    this.reloadRequested = this.busy;
    if (!this.busy) this.load();
  }
  finishWork() {
    this.busy = false;
    this.render();
    if (this.reloadRequested) { this.reloadRequested = false; this.load(); }
    else if (this.appearanceRefreshPending) this.refreshAppearance();
  }

  set hass(value) {
    if (this._hass && (this._hass.user?.id !== value?.user?.id || this._hass.user?.is_admin !== value?.user?.is_admin)) {
      this.drafts.clear();
      this.appearance=null;this.appearanceDevice="";
      this.accessUserId = "";
      this.history = {};
      this.historyAvailable = null;
      this.historyDevice = "";
      this.recipes = [];
      this.deviceState = { status: "adapter_missing", devices: [] };
      this.selectedDeviceId = this.config.device_id || "";
      this.selectedZoneId = "";
      this.previewRecipeId = "";
      this.sourceMode = "manual";
      this.manualPreviewProgram = "airfry";
      this.manualPreviewTemperatureC = 180;
      this.manualPreviewDurationMinutes = 7;
      this.started = false;
      this.reloadRequested = this.busy;
    }
    super.hass = value;
  }

  get cardWords() { return textFor(this._hass); }
  get hasDeviceAccess() { return this.admin || Boolean(this.accessUserId && this.accessUserId === this._hass?.user?.id && this.selectedDevice()); }

  async request(name, fields = {}) {
    const controlled = ["appearance_get", "devices", "sent_settings", "prepare_send", "beta_prepare", "beta_confirm", "beta_cancel", "beta_recover"];
    if (!this.admin && controlled.includes(name)) {
      if (this._hass?.connection?.connected === false || (!this.panelActive && name !== "beta_cancel")) throw { code: "beta_test_blocked", message: "connection_changed" };
      return super.request("control", { action: name, parameters: fields });
    }
    return super.request(name, fields);
  }

  async recoverBeta() {
    if (this.admin) return super.recoverBeta();
    if (!this.hasDeviceAccess || this.busy || !this.controlCurrent(this.controlRevision) || !confirm(this.words.betaRecoverConfirm)) return;
    const revision = this.controlRevision;
    this.forgetBeta();
    this.busy = true;
    this.render();
    try {
      await this.request("beta_recover", { device_id: this.selectedDeviceId, acknowledge_physical_reset: true });
      if (this.controlCurrent(revision)) { this.needsRecovery = false; this.betaMessage = this.words.betaRecovered; }
    } catch (error) { if (this.controlCurrent(revision)) this.betaMessage = this.betaError(error); }
    finally { this.finishWork(); }
  }
  getCardSize() { return { compact: 11, normal: 14, large: 17 }[this.config.size || "normal"]; }
  static getStubConfig() { return { dry_run: true }; }
  static getConfigElement() { return document.createElement("airfryer-recipes-card-editor"); }
  key() { return JSON.stringify([this.selectedDeviceId, this.selectedZoneId]); }
  phase() {
    return this.selectedPreviewRecipe()?.phases[0] || { program: this.manualPreviewProgram,
      temperature_c: this.manualPreviewTemperatureC, duration_minutes: this.manualPreviewDurationMinutes };
  }
  saveDraft() {
    if (this.selectedDeviceId && this.selectedZoneId) this.drafts.set(this.key(), {
      recipe_id: this.previewRecipeId || null, settings: { ...this.phase() },
    });
  }
  restoreDraft() {
    const saved = this.drafts.get(this.key()) || (this.historyDevice === this.selectedDeviceId ? this.history[this.selectedZoneId] : null);
    const fallback = this.recipes.find((r) => r.phases?.length === 1);
    const phase = saved?.settings || fallback?.phases[0] || { program: "airfry", temperature_c: 180, duration_minutes: 7 };
    const recipe = saved ? this.recipes.find((r) => r.id === saved.recipe_id && r.phases?.length === 1 && samePhase(r.phases[0], phase)) : fallback;
    this.previewRecipeId = recipe?.id || "";
    this.sourceMode = recipe ? "recipe" : "manual";
    this.manualPreviewProgram = phase.program;
    this.manualPreviewTemperatureC = phase.temperature_c;
    this.manualPreviewDurationMinutes = phase.duration_minutes;
  }
  clearFeedback() {
    this.previewMessage = "";
    this.betaMessage = "";
    this.batchMessage = "";
    this.deviceError = "";
    this.sendPreview = null;
    this.needsRecovery = false;
  }

  async load() {
    if (!this._hass || !this.panelActive || this.busy) return;
    if (!this._hass.user) { this.render(); return; }
    this.saveDraft();
    this.forgetBeta();
    const revision = this.controlRevision;
    const loading = ++this.loadRevision;
    this.busy = true;
    this.render();
    try {
      const [list, devices] = await Promise.all([this.request("list"), this.request("devices")]);
      if (!this.controlCurrent(revision) || loading !== this.loadRevision) return;
      this.recipes = list.recipes;
      this.deviceState = { status: devices.status, devices: devices.devices || [] };
      this.accessUserId = this._hass.user.id;
      // An explicit or previously selected missing target must never fall back to another appliance.
      this.selectedDeviceId = this.config.device_id || this.selectedDeviceId || this.deviceState.devices[0]?.device_id || "";
      if (!this.selectedZone()) this.selectedZoneId = String(this.selectedDevice()?.zones?.[0]?.zone_id || "");
      await this.loadHistory();
      await this.loadAppearance();
      if (!this.controlCurrent(revision) || loading !== this.loadRevision) return;
      this.restoreDraft();
      this.error = "";
    } catch (error) {
      if (this.controlCurrent(revision)) this.showError(error);
    } finally { this.finishWork(); }
  }

  async loadAppearance() {
    const device_id=this.selectedDeviceId, revision=this.controlRevision;
    const loading = ++this.appearanceRevision;
    const current = () => this.controlCurrent(revision) && loading === this.appearanceRevision && device_id === this.selectedDeviceId;
    this.appearanceRefreshPending = false;
    this.appearance=null;
    this.appearanceDevice="";
    if (!device_id || !this.hasDeviceAccess) return false;
    try { const value=await this.request("appearance_get",{device_id});
      if(current()){this.appearance=value;this.appearanceDevice=device_id;}
    } catch { /* Retain the original neutral graphic on read failure. */ }
    return current();
  }

  async refreshAppearance() {
    if (!this.panelActive || !this._hass || this._hass.connection?.connected === false || !this.hasDeviceAccess) return;
    if (this.busy) { this.appearanceRefreshPending = true; return; }
    if (await this.loadAppearance()) this.render();
  }

  async loadHistory() {
    const device_id = this.selectedDeviceId;
    const revision = this.controlRevision;
    const loading = ++this.historyRevision;
    this.history = {};
    this.historyDevice = device_id;
    this.historyAvailable = null;
    if (!device_id || !this.hasDeviceAccess) return;
    try {
      const result = await this.request("sent_settings", { device_id });
      if (!this.controlCurrent(revision) || device_id !== this.selectedDeviceId || loading !== this.historyRevision) return;
      this.history = result.zones || {};
      this.historyAvailable = result.available === true;
    } catch {
      if (this.controlCurrent(revision) && device_id === this.selectedDeviceId && loading === this.historyRevision) this.historyAvailable = false;
    }
  }

  async selectTarget(device, zone) {
    if (this.busy) return;
    this.saveDraft();
    this.forgetBeta();
    const changedDevice = device !== this.selectedDeviceId;
    this.selectedDeviceId = device;
    this.selectedZoneId = String(zone);
    this.clearFeedback();
    if (changedDevice) {
      this.busy = true;
      this.render();
      await this.loadHistory();
      await this.loadAppearance();
    }
    this.restoreDraft();
    this.finishWork();
  }

  canSend() {
    const device = this.selectedDevice();
    return this.hasDeviceAccess && !this.error && !this.busy && !this.devicesBusy && this.controlCurrent(this.controlRevision) &&
      device?.connectivity === "reported_online" && this.selectedZone() &&
      ["idle", "off", "ready", "finished"].includes(this.selectedZone().status) &&
      (this.sourceMode !== "recipe" || this.selectedPreviewRecipe());
  }

  async sendSettings(form) {
    if (!this.canSend() || !form?.reportValidity?.()) return;
    this.saveDraft();
    this.forgetBeta();
    this.clearFeedback();
    const revision = this.controlRevision;
    const selection = this.selectionRevision;
    const current = () => this.controlCurrent(revision) && selection === this.selectionRevision;
    const device_id = this.selectedDeviceId;
    const zone_id = Number(this.selectedZoneId);
    const settings = { ...this.phase() };
    const source = this.previewRecipeId ? { recipe_id: this.previewRecipeId } : { settings };
    this.busy = true;
    this.render();
    let submitted = false;
    try {
      if (this.config.dry_run) {
        const result = await this.request("prepare_send", { device_id, zone_id, settings });
        if (current()) { this.sendPreview = result; this.previewMessage = this.cardWords.previewDone; }
        return;
      }
      const prepared = await this.request("beta_prepare", { device_id, zone_id, source, acknowledge_unverified: true });
      if (!current()) { this.cancelBetaToken(prepared.token); return; }
      this.betaTest = prepared;
      const exact = `${prepared.device_name} · ${this.cardWords.zone} ${prepared.zone_id}\n${this.programName(prepared.settings.program)} · ${this.toDisplay(prepared.settings.temperature_c)} ${this.unit} · ${prepared.settings.duration_minutes} min`;
      if (!confirm(`${exact}\n\n${this.cardWords.confirm}`) || !current()) {
        this.forgetBeta();
        return;
      }
      this.betaTest = null;
      this.betaSubmittingToken = prepared.token;
      submitted = true;
      const result = await this.request("beta_confirm", { token: prepared.token, acknowledge_supervised_test: true });
      if (!current()) return;
      this.betaMessage = result.outcome === "accepted" ? this.cardWords.accepted + (result.history_saved === false ? ` ${this.cardWords.saveError}` : "")
        : result.outcome === "rejected" ? this.words.betaRejected : this.words.betaUnknown;
      this.needsRecovery = result.outcome !== "accepted";
      await this.loadHistory();
    } catch (error) {
      if (current()) {
        this.betaMessage = submitted && error?.code !== "beta_test_blocked" ? this.words.betaUnknown : this.betaError(error);
        this.needsRecovery = submitted || error?.message === "outcome_unknown";
      }
    } finally {
      this.betaSubmittingToken = null;
      this.finishWork();
    }
  }

  onSubmit(event) { event.preventDefault(); } // Enter never transmits settings implicitly.
  onInput(event) {
    if (this.busy || !["card-temperature", "card-duration"].includes(event.target.id)) return;
    this.forgetBeta();
    const value = event.target.value === "" ? NaN : Number(event.target.value);
    if (event.target.id === "card-temperature") this.manualPreviewTemperatureC = this.fromDisplay(value);
    else this.manualPreviewDurationMinutes = value;
    this.sendPreview = null;
    this.previewMessage = "";
    this.shadowRoot.querySelector?.(".preview")?.remove();
    this.saveDraft();
  }
  onChange(event) {
    if (this.busy) return;
    const { id, value } = event.target;
    if (["card-temperature", "card-duration"].includes(id)) {
      this.onInput(event);
      // Keep the clicked Send button mounted when a numeric field loses focus.
      return;
    }
    if (id === "card-device") {
      const device = this.deviceState.devices.find((item) => item.device_id === value);
      return this.selectTarget(value, device?.zones?.[0]?.zone_id || "");
    }
    if (!["card-recipe", "card-program"].includes(id)) return;
    this.forgetBeta();
    if (id === "card-recipe") this.previewRecipeId = value;
    else this.manualPreviewProgram = value;
    this.clearFeedback();
    this.saveDraft();
    this.render();
  }
  onClick(event) {
    const button = event.target.closest?.("[data-action]");
    if (!button || button.disabled || this.busy) return;
    const action = button.dataset.action;
    if (action === "zone") return this.selectTarget(this.selectedDeviceId, button.dataset.zone);
    if (action === "refresh") return this.load();
    if (action === "send") return this.sendSettings(this.shadowRoot.getElementById("card-form"));
    if (action === "recover") return this.recoverBeta();
    if (action === "mode") {
      const phase = { ...this.phase() };
      this.forgetBeta();
      this.sourceMode = button.dataset.mode;
      this.previewRecipeId = this.sourceMode === "recipe" ? this.recipes.find((r) => r.phases?.length === 1)?.id || "" : "";
      this.manualPreviewProgram = phase.program;
      this.manualPreviewTemperatureC = phase.temperature_c;
      this.manualPreviewDurationMinutes = phase.duration_minutes;
      this.clearFeedback();
      this.saveDraft();
      this.render();
    }
  }

  render() {
    if (!this.shadowRoot || !this.config) return;
    const t = this.cardWords;
    const device = this.selectedDevice();
    const zones = (device?.zones || []).filter((z) => [1, 2].includes(z.zone_id));
    const connection = this._hass?.connection?.connected === false ? "offline" : ({ reported_online: "online", offline: "offline" }[device?.connectivity] || "unknown");
    const phase = this.phase();
    const record = this.historyDevice === this.selectedDeviceId ? this.history[this.selectedZoneId] : null;
    const disabled = this.busy || !this.hasDeviceAccess;
    const recipes = this.recipes.filter((r) => r.phases?.length === 1);
    const programs = [...(device?.programs || [])];
    if (!programs.some((p) => p.id === phase.program)) programs.unshift({ id: phase.program, missing: true });
    const layout = displayConfig(this.config);
    const graphic = { small: [130, 66], normal: [178, 90], large: [205, 108] }[layout.graphic_size];
    const appearance=this.appearanceDevice===this.selectedDeviceId?this.appearance:null;
    const personalized=appearance?.zones && (appearance.preset!=="stacked" || JSON.stringify(appearance.zones)!==JSON.stringify({"1":[5,8,90,39],"2":[5,53,90,39]}));
    const artwork = personalized ? `<div class="appliance personalized ${appearance.preset === 'outline' ? 'outline' : ''}" role="group" aria-label="${html(device?.name || t.title)}">
      ${appearance.image?.startsWith('data:image/png;base64,') ? `<img src="${html(appearance.image)}" alt="">` : ''}
      ${zones.map(z => {
        const box = appearance.zones[String(z.zone_id)];
        return box ? `<button type="button" class="hotspot" data-action="zone" data-zone="${z.zone_id}" aria-label="${t.zone} ${z.zone_id}" aria-pressed="${String(z.zone_id) === this.selectedZoneId}" style="left:${Number(box[0])}%;top:${Number(box[1])}%;width:${Number(box[2])}%;height:${Number(box[3])}%" ${disabled ? 'disabled' : ''}>${layout.zone_style === 'outline' ? `<span class="zone-marker" aria-hidden="true">${z.zone_id}</span>` : ''}</button>` : '';
      }).join('')}</div>` : null;
    const zoneButton = (zone, graphic = false) => `<button type="button" data-action="zone" data-zone="${zone.zone_id}" class="${graphic ? "drawer" : "zone"} ${String(zone.zone_id) === this.selectedZoneId ? "selected" : ""}" aria-pressed="${String(zone.zone_id) === this.selectedZoneId}" aria-label="${t.zone} ${zone.zone_id}" ${disabled ? "disabled" : ""}>
      ${graphic ? `<b>${zone.zone_id}</b><i></i>` : `<span class="radio"></span><span>${t.zone} ${zone.zone_id}<small>${html(this.statusLabel(zone.status))}</small></span>`}</button>`;
    this.shadowRoot.innerHTML = `<style>
      :host{display:block;color:var(--primary-text-color,#edf0f4);font-family:var(--paper-font-body1_-_font-family,system-ui,sans-serif)}
      *{box-sizing:border-box}ha-card{display:block;overflow:hidden;background:var(--ha-card-background,var(--card-background-color,#111b25));border-radius:var(--ha-card-border-radius,16px);padding:20px;border:1px solid var(--divider-color,#34404e)}
      header{display:flex;align-items:center;gap:9px;margin-bottom:18px}h2{font-size:1.3rem;line-height:1.25;margin:0;flex:1;overflow-wrap:anywhere}.connection{font-size:.82rem;display:flex;align-items:center;gap:6px;white-space:nowrap}.dot{width:9px;height:9px;border-radius:50%;background:#84909d}.online .dot{background:#53b687}.refresh{background:none;border:0;min-width:38px;padding:5px;font-size:1.25rem}
      button,input,select{font:inherit;color:inherit}button{cursor:pointer}button:disabled{cursor:default;opacity:.5}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--primary-color,#9bb9d3);outline-offset:2px}button,input,select{border:1px solid var(--divider-color,#3c4957);border-radius:10px;background:var(--secondary-background-color,#17212c)}
      .overview{display:grid;grid-template-columns:minmax(105px,40%) minmax(0,1fr);gap:20px;align-items:center;margin-bottom:18px}.appliance{max-width:178px;width:100%;justify-self:center;border-radius:25px 25px 17px 17px;padding:17px 9px 13px;background:linear-gradient(110deg,#63717d,#1d2833 18%,#2f3c49 85%,#687580);box-shadow:inset 0 1px 2px #bec8d0,0 5px 9px #0005;position:relative}.appliance:after{content:"";position:absolute;bottom:-5px;left:15%;right:15%;height:5px;border-radius:0 0 4px 4px;background:#4b5660}
      .drawer{display:flex;flex-direction:column;align-items:center;justify-content:center;width:100%;min-height:90px;margin:4px 0;border:1px solid #677584;background:linear-gradient(120deg,#596876,#263442 65%,#1b2631);border-radius:15px;box-shadow:inset 0 1px 3px #b3bdc855;color:#eaf0f4}.drawer b{font-size:1.7rem;font-weight:600}.drawer i{height:8px;width:65%;margin-top:12px;border-radius:5px;background:linear-gradient(#a3adb5,#333d47);box-shadow:0 3px 4px #0009}.drawer.selected{border-color:#c1d0dc;box-shadow:inset 0 0 14px #9caebe55,0 0 0 2px #99aebe44}.offline .appliance{filter:grayscale(1);opacity:.55}
      .zone{width:100%;display:flex;align-items:center;gap:10px;text-align:start;background:none;border:0;padding:10px 4px}.radio{display:block;width:23px;height:23px;border:2px solid #84919e;border-radius:50%;flex-shrink:0}.selected .radio:after{content:"";display:block;border-radius:50%;margin:4px;width:11px;height:11px;background:#b7c8d5}.zone small{display:block;color:var(--secondary-text-color,#aebac5);margin-top:4px}.last{margin-top:9px;padding-top:12px;border-top:1px solid var(--divider-color,#34404e);font-size:.78rem;line-height:1.5;overflow-wrap:anywhere}.last strong{display:block;font-weight:500;color:var(--secondary-text-color,#aebac5)}.last p{margin:4px 0 0}
      label{display:block;font-size:.82rem;margin:10px 0 5px;color:var(--secondary-text-color,#b8c2cc)}input,select{width:100%;min-height:44px;padding:9px 11px;min-width:0}input:disabled,select:disabled{opacity:.7}.tabs{display:flex;border:1px solid var(--divider-color,#3c4957);border-radius:24px;margin:12px 0;overflow:hidden}.tabs button{border:0;border-radius:23px;flex:1;min-height:42px;background:none}.tabs button.active,.send{background:#a6b7c5;color:#15212b;font-weight:600}.values{display:grid;grid-template-columns:1fr 1fr;gap:12px}.send{width:100%;min-height:46px;margin-top:14px;border:0}.foot{border-top:1px solid var(--divider-color,#34404e);text-align:center;padding-top:13px;margin:14px 0 0;font-size:.8rem;color:var(--secondary-text-color,#aebac5)}.mode-note{font-size:.75rem;margin:8px 0 0;text-align:center;color:var(--secondary-text-color,#aebac5)}.message{font-size:.85rem;line-height:1.45;margin:12px 0 0;overflow-wrap:anywhere}.error{color:var(--error-color,#e49c95)}.preview{font-size:.8rem;margin-top:10px;overflow-wrap:anywhere}.preview p{margin:6px 0}.recover{min-height:44px;padding:9px;margin-top:10px}
      .appliance{max-width:${graphic[0]}px}.drawer{min-height:${graphic[1]}px}
      ${layout.size === "compact" ? "ha-card{padding:14px}header{margin-bottom:10px}label{margin-top:7px}.overview{gap:12px;margin-bottom:12px}.tabs{margin:8px 0}.foot{margin-top:10px}" : ""}
      ${layout.size === "large" ? "ha-card{padding:24px}h2{font-size:1.5rem}input,select{min-height:50px}.send{min-height:52px}.overview{gap:24px}" : ""}
      ${layout.show_status ? "" : ".connection,.zone small{display:none}"}
      ${layout.show_last_sent ? "" : ".last{display:none}"}
      .personalized{aspect-ratio:1;padding:0;position:relative;overflow:hidden}.personalized:after{display:none}.personalized img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;pointer-events:none}.personalized.outline{background:transparent;border:2px solid #9aa9b6}
      .personalized .hotspot{position:absolute;appearance:none;margin:0;padding:0;min-width:0;min-height:0;background:transparent;border:2px solid transparent;box-shadow:none;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
      .zone-style-outline .hotspot[aria-pressed=true]{border-color:#b7d1e5}.zone-marker{position:absolute;left:2px;top:50%;transform:translateY(-50%);display:grid;place-items:center;width:20px;height:20px;border-radius:50%;font-size:.7rem;font-weight:600;color:#f1f5f8;background:#435564;pointer-events:none}.hotspot[aria-pressed=true] .zone-marker{color:#15212b;background:#b7d1e5}
      .zone-style-invisible .hotspot{border:0;border-radius:0;background:transparent;box-shadow:none}.zone-style-invisible .zone{min-height:60px;margin:8px 0;padding:10px 12px;border:1px solid var(--divider-color,#3c4957)}.zone-style-invisible .zone.selected{border-color:#a6b7c5;background:#a6b7c533}.zone-style-invisible .radio{display:none}
      @media(max-width:340px){ha-card{padding:14px}.overview{gap:12px;grid-template-columns:minmax(90px,38%) minmax(0,1fr)}.drawer{min-height:${Math.min(graphic[1],78)}px}.connection{font-size:.75rem}h2{font-size:1.1rem}.last{font-size:.72rem}}
    </style><ha-card class="${html(connection)} zone-style-${layout.zone_style}"><header><h2>${html(this.config.title || t.title)}</h2><span class="connection" title="${t.reported}"><i class="dot"></i>${html(t[connection] || t.unknown)}</span><button class="refresh" type="button" data-action="refresh" aria-label="${t.refresh}" title="${t.refresh}" ${this.busy ? "disabled" : ""}>↻</button></header>
      ${!this.admin && (!this.accessUserId || !this.deviceState.devices.length) ? `<p class="message">${t.admin}</p>` : `
      ${!this.config.device_id && (this.deviceState.devices.length > 1 || (!device && this.deviceState.devices.length)) ? `<label for="card-device">${this.words.device}</label><select id="card-device" ${this.busy ? "disabled" : ""}>${!device ? `<option value="" selected disabled>${this.words.device}</option>` : ""}${this.deviceState.devices.map((d) => `<option value="${html(d.device_id)}" ${d.device_id === this.selectedDeviceId ? "selected" : ""}>${html(d.name)}</option>`).join("")}</select>` : ""}
      <div class="overview">${artwork || `<div class="appliance" role="group" aria-label="${html(device?.name || t.title)}">${zones.map((z) => zoneButton(z, true)).join("") || `<div class="drawer">—</div>`}</div>`}
      <div>${zones.map((z) => zoneButton(z)).join("")}<div class="last" title="${t.historyInfo}"><strong>${t.last} · ${t.zone} ${html(this.selectedZoneId || "—")}</strong>${this.historyAvailable === false ? `<p>${t.historyError}</p>` : record ? `<p>${html(this.programName(record.settings.program))}<br>${this.toDisplay(record.settings.temperature_c)} ${this.unit} · ${record.settings.duration_minutes} min</p>` : `<p>${this.historyAvailable === null ? this.words.loading : t.empty}</p>`}</div></div></div>
      ${!device ? `<p class="message">${this.words.targetMissing}</p>` : ""}
      <form id="card-form"><label for="card-recipe">${t.recipe}</label><select id="card-recipe" ${disabled || this.sourceMode !== "recipe" ? "disabled" : ""}><option value="">${t.choose}</option>${recipes.map((r) => `<option value="${html(r.id)}" ${r.id === this.previewRecipeId ? "selected" : ""}>${html(r.name)}</option>`).join("")}</select>
      <div class="tabs" role="group" aria-label="${t.recipe} / ${t.manual}">${["recipe", "manual"].map((mode) => `<button type="button" data-action="mode" data-mode="${mode}" class="${this.sourceMode === mode ? "active" : ""}" aria-pressed="${this.sourceMode === mode}" ${disabled ? "disabled" : ""}>${t[mode]}</button>`).join("")}</div>
      <label for="card-program">${t.program}</label><select id="card-program" ${disabled || this.sourceMode === "recipe" ? "disabled" : ""}>${programs.map((p) => `<option value="${html(p.id)}" ${p.id === phase.program ? "selected" : ""}>${html(p.missing ? `${this.programName(p.id)} · ${this.words.unknownProgram}` : this.programOption(p))}</option>`).join("")}</select>
      <div class="values"><div><label for="card-temperature">${t.temperature} (${this.unit})</label><input id="card-temperature" type="number" required step="1" min="${this.toDisplay(0)}" max="${this.toDisplay(400)}" value="${Number.isFinite(phase.temperature_c) ? this.toDisplay(phase.temperature_c) : ""}" ${disabled || this.sourceMode === "recipe" ? "disabled" : ""}></div><div><label for="card-duration">${t.duration} (min)</label><input id="card-duration" type="number" required step="1" min="1" max="1440" value="${Number.isFinite(phase.duration_minutes) ? phase.duration_minutes : ""}" ${disabled || this.sourceMode === "recipe" ? "disabled" : ""}></div></div>
      <button type="button" class="send" data-action="send" ${this.canSend() ? "" : "disabled"}>${this.config.dry_run ? t.preview : t.send}</button></form>
      <p class="mode-note">${this.config.dry_run ? t.test : t.beta}</p>
      ${this.sendPreview ? `<div class="preview"><p>${html(this.previewMessage)}</p><p>${html(this.programName(this.sendPreview.settings.program))} · ${this.toDisplay(this.sendPreview.settings.temperature_c)} ${this.unit} · ${this.sendPreview.settings.duration_minutes} min</p><p>${(this.sendPreview.blocking_reasons || []).map((r) => html(this.reasonLabel(r))).join(" · ")}</p></div>` : ""}
      ${[this.error, this.deviceError, this.betaMessage, this.batchMessage].filter(Boolean).map((m) => `<p class="message" role="status">${html(m)}</p>`).join("")}
      ${this.needsRecovery ? `<button type="button" data-action="recover" class="recover" ${disabled ? "disabled" : ""}>${this.words.betaRecover}</button><p class="message">${this.words.betaRecoverInfo}</p>` : ""}
      <p class="foot">ⓘ ${t.start}</p>`}
    </ha-card>`;
  }
}

class AirfryerRecipesCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.addEventListener("click", async (event) => {
      if(event.target.dataset?.customize!=="true"||!this._hass?.user?.is_admin)return;
      await import("./personalization.js?v=0.1.0b20");this.customize=true;this.render();
    });
    this.shadowRoot.addEventListener("change", (event) => {
      const target = event.target;
      if (!["title", "device_id", "dry_run", "size", "graphic_size", "zone_style", "show_status", "show_last_sent"].includes(target.name)) return;
      this.config = { ...this.config, [target.name]: ["dry_run", "show_status", "show_last_sent"].includes(target.name) ? target.checked : target.value.trim() };
      this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this.config }, bubbles: true, composed: true }));
    });
  }
  setConfig(config) { this.config = displayConfig({ ...config, dry_run: config.dry_run !== false }); this.render(); }
  set hass(value) { const language = this._hass?.language; this._hass = value; if (language !== value?.language) this.render(); const designer=this.shadowRoot.querySelector?.("airfryer-device-designer");if(designer)designer.hass=value; }
  render() {
    if (!this.config) return;
    const t = textFor(this._hass);
    this.shadowRoot.innerHTML = `<style>:host{display:block}label{display:block;margin:14px 0}input[type=text],select{display:block;box-sizing:border-box;width:100%;min-height:44px;margin-top:6px;padding:8px;font:inherit;color:var(--primary-text-color);background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:6px}p{font-size:.85rem;line-height:1.5}</style>
      <label>${t.configTitle}<input name="title" type="text" value="${html(this.config.title || "")}"></label>
      <label>${t.configDevice}<input name="device_id" type="text" value="${html(this.config.device_id || "")}"></label>
      ${[["size", t.size, ["compact", "normal", "large"]], ["graphic_size", t.graphicSize, ["small", "normal", "large"]]].map(([key, label, values]) => `<label>${label}<select name="${key}">${values.map((value) => `<option value="${value}" ${this.config[key] === value ? "selected" : ""}>${t[value]}</option>`).join("")}</select></label>`).join("")}
      <label>${t.zoneStyle}<select name="zone_style">${[["outline", t.zoneOutline], ["invisible", t.zoneInvisible]].map(([value, label]) => `<option value="${value}" ${this.config.zone_style === value ? "selected" : ""}>${label}</option>`).join("")}</select></label><p>${t.zoneStyleHelp}</p>
      ${[["show_status", t.showStatus], ["show_last_sent", t.showHistory]].map(([key, label]) => `<label><input name="${key}" type="checkbox" ${this.config[key] ? "checked" : ""}> ${label}</label>`).join("")}
      <label><input name="dry_run" type="checkbox" ${this.config.dry_run ? "checked" : ""}> ${t.configTest}</label><p>${t.configHelp}</p>${this._hass?.user?.is_admin ? `<button type="button" data-customize="true">${this._hass.language?.startsWith("de")?"Airfryer individualisieren":"Customize Airfryer"}</button>`:""}${this.customize?"<airfryer-device-designer></airfryer-device-designer>":""}`;
    const designer=this.shadowRoot.querySelector?.("airfryer-device-designer");if(designer){designer.preferredDevice=this.config.device_id||"";designer.hass=this._hass;}
  }
}

if (!customElements.get("airfryer-recipes-card")) customElements.define("airfryer-recipes-card", AirfryerRecipesCard);
if (!customElements.get("airfryer-recipes-card-editor")) customElements.define("airfryer-recipes-card-editor", AirfryerRecipesCardEditor);
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "airfryer-recipes-card")) window.customCards.push({
  type: "airfryer-recipes-card", name: "Airfryer Recipes", description: "Recipe and manual settings for two cooking zones / Rezepte und manuelle Werte für zwei Fächer", preview: true,
});
