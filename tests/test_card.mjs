import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const panelSource = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/panel.js", import.meta.url), "utf8");
const cardSource = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/card.js", import.meta.url), "utf8");
const phase = { program: "airfry", temperature_c: 180, duration_minutes: 7 };
const other = { program: "roast", temperature_c: 190, duration_minutes: 10 };
const prepared = { token: "once", device_name: "Kitchen", zone_id: 1, settings: phase };
const record = (settings, recipe_id = null) => ({ settings: { ...settings }, recipe_id, sent_at: "2026-11-02T08:00:00+00:00" });
const device = (device_id = "appliance") => ({ device_id, name: "Kitchen", connectivity: "reported_online",
  zones: [{ zone_id: 1, status: "idle" }, { zone_id: 2, status: "idle" }],
  programs: [{ id: "airfry", limits_status: "estimated" }, { id: "roast", limits_status: "estimated" }],
});
const validForm = { reportValidity: () => true };
const plain = (value) => JSON.parse(JSON.stringify(value));

function makeCard(api = async () => ({}), dialog = () => true) {
  const elements = new Map();
  const events = [];
  const context = {
    HTMLElement: class {
      attachShadow() {
        this.shadowRoot = { innerHTML: "", listeners: new Map(), addEventListener(type, callback) { this.listeners.set(type, callback); }, getElementById(id) { return id === "card-form" ? validForm : undefined; } };
      }
      dispatchEvent(event) { events.push(event); }
    },
    customElements: { define: (name, type) => elements.set(name, type), get: (name) => elements.get(name) },
    window: new EventTarget(), confirm: dialog, Event, CustomEvent: class extends Event { constructor(type, options) { super(type, options); this.detail = options?.detail; } },
    setTimeout, URL, Blob, structuredClone,
    document: { createElement: (name) => new (elements.get(name))() },
  };
  vm.runInNewContext(panelSource.replace(/^export /m, ""), context);
  vm.runInNewContext(cardSource.replace(/^import .*;$/m, ""), context);
  const card = new (elements.get("airfryer-recipes-card"))();
  const listeners = new Set();
  const connection = { connected: true, addEventListener: (_, callback) => listeners.add(callback),
    removeEventListener: (_, callback) => listeners.delete(callback),
    disconnect() { this.connected = false; for (const callback of [...listeners]) callback(); },
  };
  card._hass = { language: "de", user: { id: "admin", is_admin: true }, connection, callWS: api };
  card.watchConnection(connection);
  card.deviceState = { status: "adapter_beta", devices: [device(), device("other-appliance")] };
  card.selectedDeviceId = "appliance";
  card.selectedZoneId = "1";
  card.manualPreviewDurationMinutes = 7;
  card.historyAvailable = true;
  card.historyDevice = "appliance";
  card.render();
  return { card, elements, events, context };
}
function click(card, action, extra = {}) {
  return card.onClick({ target: { closest: () => ({ disabled: false, dataset: { action, ...extra } }) } });
}

test("zone switches restore separate settings and history without transmission", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); });
  card.history = { "1": record(phase), "2": record(other) };
  card.restoreDraft();
  await click(card, "zone", { zone: "2" });
  assert.deepEqual(plain(card.phase()), other);
  assert.match(card.shadowRoot.innerHTML, /Zuletzt gesendet · Fach 2/);
  assert.match(card.shadowRoot.innerHTML, /190 °C · 10 min/);
  card.onInput({ target: { id: "card-temperature", value: "195" } });
  await click(card, "zone", { zone: "1" });
  assert.deepEqual(plain(card.phase()), phase);
  await click(card, "zone", { zone: "2" });
  assert.equal(card.phase().temperature_c, 195);
  assert.equal(card.history["2"].settings.temperature_c, 190);
  assert.equal(calls.length, 0);
});

test("drafts stay separate for appliances as well as zones", async () => {
  const { card } = makeCard(async (r) => ({ available: true, zones: { "1": record(other) } }));
  card.onInput({ target: { id: "card-temperature", value: "185" } });
  await card.selectTarget("other-appliance", "1");
  assert.deepEqual(plain(card.phase()), other);
  card.onInput({ target: { id: "card-duration", value: "12" } });
  await card.selectTarget("appliance", "1");
  assert.equal(card.phase().temperature_c, 185);
  assert.equal(card.phase().duration_minutes, 7);
  await card.selectTarget("other-appliance", "1");
  assert.equal(card.phase().duration_minutes, 12);
});

test("restored snapshots use manual values if a recipe was edited or deleted", () => {
  const { card } = makeCard();
  card.history = { "1": record(phase, "recipe") };
  card.recipes = [{ id: "recipe", name: "Changed recipe", phases: [other] }];
  card.restoreDraft();
  assert.equal(card.previewRecipeId, "");
  assert.deepEqual(plain(card.phase()), phase);
  card.recipes = [];
  card.restoreDraft();
  assert.deepEqual(plain(card.phase()), phase);
  card.recipes = [{ id: "recipe", name: "Original recipe", phases: [phase] }];
  card.restoreDraft();
  assert.equal(card.previewRecipeId, "recipe");
});

test("default test mode only calls the server-enforced preview", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r); return { mode: "dry_run", transmitted: false, settings: r.settings, blocking_reasons: ["program_limits_unverified"] };
  }, () => { throw new Error("No live dialog in test mode"); });
  await card.sendSettings(validForm);
  assert.deepEqual(calls.map((r) => r.type), ["airfryer_recipes/prepare_send"]);
  assert.deepEqual(plain(calls[0].settings), phase);
  assert.match(card.shadowRoot.innerHTML, /kein Gerätebefehl gesendet/);
  assert.match(card.shadowRoot.innerHTML, /180 °C · 7 min/);
  assert.deepEqual(plain(card.history), {});
});

test("live send shows one exact confirmation, consumes token and reads server history", async () => {
  const calls = [], dialogs = [];
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("beta_prepare")) return prepared;
    if (r.type.endsWith("beta_confirm")) return { outcome: "accepted", history_saved: true };
    if (r.type.endsWith("sent_settings")) return { available: true, zones: { "1": record(phase) } };
  }, (message) => { dialogs.push(message); return true; });
  card.setConfig({ dry_run: false });
  await card.sendSettings(validForm);
  assert.equal(dialogs.length, 1);
  assert.match(dialogs[0], /Kitchen · Fach 1/);
  assert.match(dialogs[0], /180 °C · 7 min/);
  assert.deepEqual(calls.map((r) => r.type), ["airfryer_recipes/beta_prepare", "airfryer_recipes/beta_confirm", "airfryer_recipes/sent_settings"]);
  assert.deepEqual(plain(calls[0].source), { settings: phase });
  assert.equal(calls[1].token, "once");
  assert.equal(Object.hasOwn(calls[1], "device_id"), false);
  assert.equal(card.betaTest, null);
  assert.equal(card.betaSubmittingToken, null);
  assert.match(card.shadowRoot.innerHTML, /keine Gerätebestätigung/);
  assert.deepEqual(plain(card.history["1"].settings), phase);
});

test("recipe sends bind to the recipe ID and do not write recipes", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r); return r.type.endsWith("beta_prepare") ? prepared : { available: true, zones: {}, outcome: "accepted" };
  });
  card.setConfig({ dry_run: false });
  card.recipes = [{ id: "picco", name: "Piccolinies", phases: [phase] }];
  card.previewRecipeId = "picco";
  card.sourceMode = "recipe";
  await card.sendSettings(validForm);
  assert.deepEqual(plain(calls[0].source), { recipe_id: "picco" });
  assert.deepEqual(plain(card.recipes[0].phases[0]), phase);
  assert.equal(calls.some((r) => /update|create/.test(r.type)), false);
});

test("declining confirmation revokes preparation without sending or changing history", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); return prepared; }, () => false);
  card.setConfig({ dry_run: false });
  card.history = { "1": record(other) };
  await card.sendSettings(validForm);
  assert.deepEqual(calls.map((r) => r.type), ["airfryer_recipes/beta_prepare", "airfryer_recipes/beta_cancel"]);
  assert.deepEqual(plain(card.history["1"].settings), other);
});

test("double click during preparation cannot produce a second send", async () => {
  const calls = [];
  let resolve;
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("beta_prepare")) return new Promise((done) => { resolve = done; });
    return { outcome: "accepted", available: true, zones: {} };
  });
  card.setConfig({ dry_run: false });
  const running = card.sendSettings(validForm);
  await card.sendSettings(validForm);
  resolve(prepared);
  await running;
  assert.equal(calls.filter((r) => r.type.endsWith("beta_prepare")).length, 1);
  assert.equal(calls.filter((r) => r.type.endsWith("beta_confirm")).length, 1);
});

test("detaching while preparing revokes late token and never confirms on reconnect", async () => {
  const calls = [];
  let resolve;
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("beta_prepare")) return new Promise((done) => { resolve = done; });
  });
  card.setConfig({ dry_run: false });
  const running = card.sendSettings(validForm);
  card.disconnectedCallback();
  resolve(prepared);
  await running;
  card.connectedCallback();
  assert.equal(calls.some((r) => r.type.endsWith("beta_confirm")), false);
  assert.equal(calls.at(-1).type, "airfryer_recipes/beta_cancel");
  assert.equal(card.betaTest, null);
});

test("connection loss during preparation never replays a command", async () => {
  const calls = [];
  let resolve;
  const { card } = makeCard(async (r) => { calls.push(r); return new Promise((done) => { resolve = done; }); });
  card.setConfig({ dry_run: false });
  const running = card.sendSettings(validForm);
  card._hass.connection.disconnect();
  resolve(prepared);
  await running;
  card._hass.connection.connected = true;
  card.render();
  assert.equal(calls.length, 1);
  assert.equal(card.betaTest, null);
});

test("unknown result never updates stored display or retries and offers recovery", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("beta_prepare")) return prepared;
    throw new Error("private transport details");
  });
  card.setConfig({ dry_run: false });
  card.history = { "1": record(other) };
  await card.sendSettings(validForm);
  assert.equal(calls.length, 2);
  assert.equal(card.needsRecovery, true);
  assert.match(card.shadowRoot.innerHTML, /Ergebnis unklar/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /private transport/);
  assert.deepEqual(plain(card.history["1"].settings), other);
});

test("storage failure is shown as accepted transmission without retry", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r); return r.type.endsWith("beta_prepare") ? prepared : r.type.endsWith("beta_confirm")
      ? { outcome: "accepted", history_saved: false } : { available: false, zones: {} };
  });
  card.setConfig({ dry_run: false });
  await card.sendSettings(validForm);
  assert.match(card.shadowRoot.innerHTML, /nicht erneut senden/);
  assert.equal(calls.filter((r) => r.type.endsWith("beta_confirm")).length, 1);
});

test("a server-side uncertain latch offers recovery even after changing zones", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); throw { code: "beta_test_blocked", message: "outcome_unknown" }; });
  card.setConfig({ dry_run: false });
  await card.selectTarget("appliance", "2");
  await card.sendSettings(validForm);
  assert.equal(card.needsRecovery, true);
  assert.match(card.shadowRoot.innerHTML, /data-action="recover"/);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_prepare");
});

test("non-admin, offline, unknown, cooking and invalid forms make no send requests", async () => {
  let calls = 0;
  const { card } = makeCard(async () => { calls++; });
  card._hass.user.is_admin = false;
  card.render();
  assert.match(card.shadowRoot.innerHTML, /Administrator/);
  await card.sendSettings(validForm);
  card._hass.user.is_admin = true;
  for (const connectivity of ["offline", "unknown"]) {
    card.selectedDevice().connectivity = connectivity;
    await card.sendSettings(validForm);
  }
  card.selectedDevice().connectivity = "reported_online";
  card.selectedZone().status = "cooking";
  await card.sendSettings(validForm);
  card.selectedZone().status = "idle";
  await card.sendSettings({ reportValidity: () => false });
  card._hass.connection.connected = false;
  await card.sendSettings(validForm);
  assert.equal(calls, 0);
});

test("initial load restores server history and a missing configured device stays missing", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("/list")) return { recipes: [] };
    if (r.type.endsWith("/devices")) return { devices: [device()] };
    return { available: true, zones: { "2": record(other) } };
  });
  card.drafts.clear();
  card.selectedDeviceId = "";
  card.selectedZoneId = "";
  await card.load();
  await card.selectTarget("appliance", "2");
  assert.deepEqual(plain(card.phase()), other);
  assert.equal(calls.some((r) => /beta_|prepare_send/.test(r.type)), false);
  card.setConfig({ device_id: "missing" });
  await card.load();
  assert.equal(card.selectedDeviceId, "missing");
  assert.equal(card.selectedDevice(), null);
  assert.equal(card.canSend(), false);
});

test("refresh preserves unsent zone drafts and edited recipes fall back to snapshots", async () => {
  const { card } = makeCard(async (r) => r.type.endsWith("/list") ? { recipes: [{ id: "r", phases: [other] }] }
    : r.type.endsWith("/devices") ? { devices: [device()] } : { available: true, zones: { "1": record(other) } });
  card.onInput({ target: { id: "card-temperature", value: "185" } });
  await card.load();
  assert.equal(card.phase().temperature_c, 185);
  assert.equal(card.history["1"].settings.temperature_c, 190);
});

test("Fahrenheit input keeps canonical Celsius and a zone change shows converted history", async () => {
  const { card } = makeCard();
  card._hass.config = { unit_system: { temperature: "°F" } };
  card.history = { "2": record(phase) };
  card.onInput({ target: { id: "card-temperature", value: "356" } });
  assert.equal(card.phase().temperature_c, 180);
  await card.selectTarget("appliance", "2");
  assert.match(card.shadowRoot.innerHTML, /356 °F · 7 min/);
});

test("card/editor registration, English fallback and escaping use no copied image assets", () => {
  const { card, elements, context } = makeCard();
  card._hass.language = "fr";
  card.setConfig({ title: '<img src=x onerror="oops">' });
  card.historyAvailable = true;
  card.render();
  assert.match(card.shadowRoot.innerHTML, /Last sent/);
  assert.match(card.shadowRoot.innerHTML, /<option value="airfry" selected>Air Fry<\/option>/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /<option[^>]*>[^<]*(sending unverified|limits unverified|owner-reported)/);
  assert.match(card.shadowRoot.innerHTML, /&lt;img/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /<img/);
  assert.equal(context.window.customCards[0].type, "airfryer-recipes-card");
  assert.equal(card.constructor.getStubConfig().dry_run, true);
  assert.equal(card.constructor.getConfigElement() instanceof elements.get("airfryer-recipes-card-editor"), true);
  assert.match(cardSource, /\.\/panel\.js\?v=0\.1\.0/);
});

test("visual editor uses safe defaults and emits dashboard configuration only", () => {
  const { elements, events } = makeCard();
  const editor = new (elements.get("airfryer-recipes-card-editor"))();
  editor.setConfig({ type: "custom:airfryer-recipes-card" });
  editor.hass = { language: "de" };
  assert.equal(editor.config.dry_run, true);
  assert.match(editor.shadowRoot.innerHTML, /Testmodus/);
  assert.match(editor.shadowRoot.innerHTML, /Home-Assistant-Geräte-ID/);
  editor.shadowRoot.listeners.get("change")({ target: { name: "dry_run", checked: false } });
  assert.equal(events[0].type, "config-changed");
  assert.equal(events[0].detail.config.dry_run, false);
  assert.equal(events[0].bubbles, true);
  assert.equal(events[0].composed, true);
});

test("changing configuration during preparation cancels the old target", async () => {
  const calls = [];
  let resolve;
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("beta_prepare")) return new Promise((done) => { resolve = done; });
    return {};
  });
  card.setConfig({ dry_run: false });
  const running = card.sendSettings(validForm);
  card.setConfig({ dry_run: false, device_id: "other-appliance" });
  resolve(prepared);
  await running;
  assert.equal(calls.some((r) => r.type.endsWith("beta_confirm")), false);
  assert.equal(card.selectedDeviceId, "other-appliance");
});

test("Enter and ordinary recipe/manual selection never transmit", () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); });
  let prevented = false;
  card.recipes = [{ id: "r", name: "Rolls", phases: [phase] }];
  click(card, "mode", { mode: "recipe" });
  card.onChange({ target: { id: "card-recipe", value: "r" } });
  click(card, "mode", { mode: "manual" });
  card.onChange({ target: { id: "card-program", value: "roast" } });
  card.onSubmit({ preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(calls.length, 0);
  assert.equal(card.previewRecipeId, "");
  assert.equal(card.manualPreviewProgram, "roast");
  const mounted = card.shadowRoot.innerHTML;
  card.onChange({ target: { id: "card-temperature", value: "190" } });
  assert.equal(card.shadowRoot.innerHTML, mounted); // Blur must not replace Send before its click.
  assert.equal(card.manualPreviewTemperatureC, 190);
});

test("ordinary card loads permitted devices and history through scoped control API", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.type.endsWith("/list")) return { recipes: [] };
    if (r.action === "devices") return { devices: [device()] };
    if (r.action === "sent_settings") return { available: true, zones: { "2": record(other) } };
    throw Error("Unexpected route");
  });
  card._hass.user = { id: "ordinary", is_admin: false };
  card.selectedDeviceId = "";
  card.selectedZoneId = "";
  await card.load();
  assert.equal(card.hasDeviceAccess, true);
  await card.selectTarget("appliance", "2");
  assert.deepEqual(plain(card.phase()), other);
  assert.match(card.shadowRoot.innerHTML, /Zuletzt gesendet · Fach 2/);
  assert.equal(calls.some((r) => /beta_|create|update|access_/.test(r.type)), false);
  assert.deepEqual(calls.filter((r) => r.type.endsWith("/control")).map((r) => r.action), ["devices", "sent_settings", "appearance_get"]);
});

test("ordinary granted user can send either zone with one exact confirmation", async () => {
  const calls = [], dialogs = [];
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.action === "beta_prepare") return { ...prepared, zone_id: r.parameters.zone_id };
    if (r.action === "beta_confirm") return { outcome: "accepted", history_saved: true };
    if (r.action === "sent_settings") return { available: true, zones: {} };
  }, (message) => { dialogs.push(message); return true; });
  card.setConfig({ dry_run: false });
  card._hass.user = { id: "ordinary", is_admin: false };
  card.accessUserId = "ordinary";
  for (const zone of ["1", "2"]) {
    await card.selectTarget("appliance", zone);
    await card.sendSettings(validForm);
  }
  assert.equal(dialogs.length, 2);
  assert.match(dialogs[1], /Fach 2/);
  assert.deepEqual(calls.filter((r) => r.action === "beta_prepare").map((r) => r.parameters.zone_id), [1, 2]);
  assert.equal(calls.filter((r) => r.action === "beta_confirm").length, 2);
  assert.ok(calls.every((r) => r.type === "airfryer_recipes/control"));
  assert.ok(calls.every((r) => !Object.hasOwn(r.parameters, "user_id")));
});

test("ordinary test mode never requests a live preparation", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); return { settings: r.parameters.settings, blocking_reasons: [], transmitted: false }; });
  card._hass.user = { id: "ordinary", is_admin: false };
  card.accessUserId = "ordinary";
  await card.sendSettings(validForm);
  assert.deepEqual(calls.map((r) => r.action), ["prepare_send"]);
  assert.match(card.shadowRoot.innerHTML, /kein Gerätebefehl/);
});

test("ungranted user can refresh after an administrator grants access", async () => {
  let granted = false;
  const { card } = makeCard(async (r) => r.action === "devices" ? { devices: granted ? [device()] : [] }
    : r.action === "sent_settings" ? { available: true, zones: {} } : { recipes: [] });
  card._hass.user = { id: "ordinary", is_admin: false };
  await card.load();
  assert.equal(Boolean(card.canSend()), false);
  assert.match(card.shadowRoot.innerHTML, /Kein freigegebenes Gerät/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /data-action="refresh"[^>]*disabled/);
  granted = true;
  await card.load();
  assert.equal(Boolean(card.canSend()), true);
});

test("normal-user disconnect cancels a late token without a confirm or replay", async () => {
  const calls = [];
  let resolve;
  const { card } = makeCard(async (r) => {
    calls.push(r);
    if (r.action === "beta_prepare") return new Promise((done) => { resolve = done; });
    return {};
  });
  card.setConfig({ dry_run: false });
  card._hass.user = { id: "ordinary", is_admin: false };
  card.accessUserId = "ordinary";
  const task = card.sendSettings(validForm);
  card.disconnectedCallback();
  resolve(prepared);
  await task;
  assert.deepEqual(calls.map((r) => r.action), ["beta_prepare", "beta_cancel"]);
  assert.equal(card.betaTest, null);
});

test("ordinary user recovery retains explicit read-only acknowledgement", async () => {
  const calls = [];
  const { card } = makeCard(async (r) => { calls.push(r); return { rearmed: true, transmitted: false }; });
  card._hass.user = { id: "ordinary", is_admin: false };
  card.accessUserId = "ordinary";
  await card.recoverBeta();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].action, "beta_recover");
  assert.equal(calls[0].parameters.acknowledge_physical_reset, true);
});

test("display defaults preserve the approved layout", () => {
  const {card}=makeCard(); card.setConfig({});
  assert.equal(card.config.size,"normal"); assert.equal(card.config.graphic_size,"normal");
  assert.equal(card.config.show_status,true); assert.equal(card.config.show_last_sent,true);
  assert.equal(card.getCardSize(),14);
});
test("display sizes and visibility are independent and do not enable offline sending", () => {
  const {card}=makeCard(); card.setConfig({size:"compact",graphic_size:"small",show_status:false,show_last_sent:false});
  assert.equal(card.getCardSize(),11); assert.match(card.shadowRoot.innerHTML,/max-width:130px/);
  assert.match(card.shadowRoot.innerHTML,/\.connection,\.zone small\{display:none\}/);
  assert.match(card.shadowRoot.innerHTML,/\.last\{display:none\}/);
  card.selectedDevice().connectivity="offline"; assert.equal(Boolean(card.canSend()),false);
  card.setConfig({size:"large",graphic_size:"large"}); assert.equal(card.getCardSize(),17);
  assert.match(card.shadowRoot.innerHTML,/max-width:205px/);
});
test("invalid display options cannot inject styles or weaken validation", () => {
  const {card}=makeCard();
  for(const config of [{size:"evil"},{graphic_size:"1px;"},{show_status:"false"},{show_last_sent:0}]) assert.throws(()=>card.setConfig(config));
});
test("appearance changes keep zone drafts and saved history without sending", async () => {
  const calls=[]; const {card}=makeCard(async r=>{calls.push(r);return {}});
  card.history={"1":record(phase),"2":record(other)};
  card.onInput({target:{id:"card-temperature",value:"185"}});
  card.setConfig({size:"compact",show_last_sent:false});
  await card.selectTarget("appliance","2"); await card.selectTarget("appliance","1");
  assert.equal(card.phase().temperature_c,185); assert.equal(card.history["1"].settings.temperature_c,180);
  assert.equal(calls.length,0);
});
test("visual editor emits booleans and size choices without resetting other settings", () => {
  const {elements,events}=makeCard(); const editor=new (elements.get("airfryer-recipes-card-editor"))();
  editor.setConfig({type:"custom:airfryer-recipes-card",dry_run:false,title:"Kitchen"});editor.hass={language:"de"};
  assert.match(editor.shadowRoot.innerHTML,/Kartengröße/);assert.match(editor.shadowRoot.innerHTML,/graphic_size/);
  for(const target of [{name:"size",value:"compact"},{name:"show_status",checked:false}]) editor.shadowRoot.listeners.get("change")({target});
  assert.equal(events.at(-1).detail.config.show_status,false);assert.equal(events.at(-1).detail.config.size,"compact");
  assert.equal(events.at(-1).detail.config.dry_run,false);assert.equal(events.at(-1).detail.config.title,"Kitchen");
});

test("saved relative artwork changes only the graphic and does not send settings",()=>{
 const calls=[];const {card}=makeCard(async r=>{calls.push(r)});
 card.appearanceDevice='appliance';card.appearance={preset:'side_by_side',image:null,zones:{'1':[4,15,43,75],'2':[53,15,43,75]}};card.render();
 assert.match(card.shadowRoot.innerHTML,/left:53%;top:15%;width:43%;height:75%/);
 assert.equal(calls.length,0);assert.equal(card.phase().temperature_c,180);
 card.selectedDevice().connectivity='offline';assert.equal(Boolean(card.canSend()),false);
});
test("appearance from another device never replaces the selected graphic",()=>{
 const {card}=makeCard();card.appearanceDevice='private-device';card.appearance={preset:'custom',image:'data:image/png;base64,AAAA',zones:{'1':[4,15,43,75],'2':[53,15,43,75]}};card.render();
 assert.doesNotMatch(card.shadowRoot.innerHTML,/<img src=/);
});

const artwork = {preset:'custom',image:'data:image/png;base64,AAAA',zones:{'1':[29,30,45,20],'2':[27,62,45,30]}};
const designerSource = readFileSync(new URL('../custom_components/airfryer_recipes/frontend/personalization.js', import.meta.url), 'utf8');
const settle = () => new Promise(resolve => setImmediate(resolve));
function notify(context, device_id='appliance') {
  context.window.dispatchEvent(new context.CustomEvent('airfryer-recipes-appearance-saved', {detail:{device_id}}));
}

test('saving in the designer updates the connected card without reloading or changing cooking settings', async () => {
  const calls=[];
  const {card,context,elements}=makeCard(async r=>{calls.push(r);return r.type.endsWith('appearance_get')?artwork:{saved:true};});
  card.connectedCallback();
  card.onInput({target:{id:'card-temperature',value:'185'}});
  card.history={'1':record(phase)};
  const revision=card.controlRevision;
  vm.runInNewContext(designerSource,context);
  const designer=new (elements.get('airfryer-device-designer'))();
  designer._hass=card._hass;designer.device='appliance';designer.draft=structuredClone(artwork);
  await designer.click({target:{closest:()=>({dataset:{action:'save'}})}});
  await settle();
  assert.deepEqual(calls.map(r=>r.type),['airfryer_recipes/appearance_set','airfryer_recipes/appearance_get']);
  assert.match(card.shadowRoot.innerHTML,/<img src="data:image\/png;base64,AAAA"/);
  assert.match(card.shadowRoot.innerHTML,/left:29%;top:30%;width:45%;height:20%/);
  assert.equal(card.phase().temperature_c,185);
  assert.equal(card.history['1'].settings.temperature_c,180);
  assert.equal(card.controlRevision,revision);
  assert.match(designer.shadowRoot.innerHTML,/Darstellung gespeichert/);
  card.disconnectedCallback();
});

test('appearance notifications ignore other devices and read through normal-user permissions', async () => {
  const calls=[];
  const {card,context}=makeCard(async r=>{calls.push(r);return artwork;});
  card._hass.user={id:'ordinary',is_admin:false};card.accessUserId='ordinary';card.connectedCallback();
  notify(context,'other-appliance');await settle();assert.equal(calls.length,0);
  notify(context);await settle();
  assert.deepEqual(plain(calls),[{type:'airfryer_recipes/control',action:'appearance_get',parameters:{device_id:'appliance'}}]);
  card.disconnectedCallback();
});

test('appearance refresh waits for active work and coalesces repeated notifications', async () => {
  const calls=[];const {card,context}=makeCard(async r=>{calls.push(r);return artwork;});
  card.connectedCallback();card.busy=true;
  notify(context);notify(context);assert.equal(calls.length,0);
  card.finishWork();await settle();
  assert.equal(calls.length,1);assert.deepEqual(plain(card.appearance),artwork);
  card.disconnectedCallback();
});

test('a late appearance read cannot overwrite a newer saved appearance', async () => {
  const pending=[];const {card}=makeCard(()=>new Promise(resolve=>pending.push(resolve)));
  const old=card.refreshAppearance(),latest=card.refreshAppearance();
  pending[1](artwork);await latest;
  pending[0]({...artwork,preset:'outline',image:null});await old;
  assert.deepEqual(plain(card.appearance),artwork);
});

test('detached cards stop listening and reread saved appearance when reattached', async () => {
  const calls=[];const {card,context}=makeCard(async r=>{calls.push(r);return artwork;});
  card.connectedCallback();card.disconnectedCallback();
  notify(context);await settle();assert.equal(calls.length,0);
  card.connectedCallback();await settle();assert.equal(calls.length,1);
  assert.deepEqual(plain(card.appearance),artwork);
  card.disconnectedCallback();
});

test('appearance replies after a role change or disconnect are discarded', async () => {
  for(const change of ['role','disconnect']){
    let resolve;const {card}=makeCard(r=>r.type.endsWith('appearance_get')
      ?new Promise(done=>{resolve=done;}):Promise.resolve({recipes:[],devices:[]}));
    card.started=true;
    const task=card.refreshAppearance();
    if(change==='role')card.hass={...card._hass,user:{id:'ordinary',is_admin:false}};
    else card.disconnectedCallback();
    resolve(artwork);await task;
    assert.equal(card.appearance,null);
    assert.doesNotMatch(card.shadowRoot.innerHTML,/<img src=/);
  }
});

test('failed appearance refresh falls back without changing settings or resending', async () => {
  const calls=[];const {card}=makeCard(async r=>{calls.push(r);throw Error('denied');});
  card.appearance=artwork;card.appearanceDevice='appliance';
  await card.refreshAppearance();
  assert.equal(card.appearance,null);assert.equal(card.phase().temperature_c,180);
  assert.deepEqual(calls.map(r=>r.type),['airfryer_recipes/appearance_get']);
});

const hotspots = card => [...card.shadowRoot.innerHTML.matchAll(/<button[^>]*class="hotspot"[^>]*>[\s\S]*?<\/button>/g)].map(match => match[0]);
function setArtwork(card) {card.appearanceDevice='appliance';card.appearance=structuredClone(artwork);card.render();}

test('omitted zone styles default to B; unknown zone styles are rejected', () => {
  const {card}=makeCard();card.setConfig({});assert.equal(card.config.zone_style,'invisible');
  card.setConfig({zone_style:undefined});assert.equal(card.config.zone_style,'invisible');
  for(const zone_style of ['filled','outline;display:none',false,null,{}])assert.throws(()=>card.setConfig({zone_style}));
});

test('A shows small markers and the active outline using the stored relative areas', () => {
  const {card}=makeCard();card.setConfig({zone_style:'outline'});setArtwork(card);
  const buttons=hotspots(card);assert.equal(buttons.length,2);
  assert.match(card.shadowRoot.innerHTML,/<ha-card class="online zone-style-outline"/);
  assert.match(buttons[0],/aria-pressed="true"/);assert.match(buttons[1],/aria-pressed="false"/);
  assert.match(buttons[0],/left:29%;top:30%;width:45%;height:20%/);
  assert.match(buttons[0],/<span class="zone-marker" aria-hidden="true">1<\/span>/);
  assert.match(card.shadowRoot.innerHTML,/\.zone-style-outline \.hotspot\[aria-pressed=true\]\{border-color:/);
  assert.doesNotMatch(card.shadowRoot.innerHTML,/#667f9388|#869ead99/);
});

test('B retains empty labeled buttons over the photo and visible side selection', () => {
  const {card}=makeCard();card.setConfig({zone_style:'invisible'});setArtwork(card);
  const buttons=hotspots(card);assert.equal(buttons.length,2);
  assert.match(card.shadowRoot.innerHTML,/<ha-card class="online zone-style-invisible"/);
  for(const [index,button] of buttons.entries()){
    assert.match(button,new RegExp('aria-label="Fach '+(index+1)+'"'));
    assert.match(button,/><\/button>$/);
    assert.doesNotMatch(button,/disabled|tabindex="-1"|hidden|display:none/);
  }
  assert.match(buttons[1],/left:27%;top:62%;width:45%;height:30%/);
  assert.match(card.shadowRoot.innerHTML,/\.zone-style-invisible \.hotspot\{border:0;border-radius:0;background:transparent;box-shadow:none\}/);
  assert.match(card.shadowRoot.innerHTML,/\.zone-style-invisible \.zone.selected\{border-color:/);
  assert.match(card.shadowRoot.innerHTML,/button:focus-visible/);
});

test('both styles select either zone without transmitting and preserve independent drafts', async () => {
  for(const zone_style of ['outline','invisible']){
    const calls=[];const {card}=makeCard(async r=>{calls.push(r);});
    card.setConfig({zone_style});setArtwork(card);card.onInput({target:{id:'card-temperature',value:'185'}});
    await click(card,'zone',{zone:'2'});card.onInput({target:{id:'card-duration',value:'12'}});
    assert.match(hotspots(card)[1],/aria-pressed="true"/);
    assert.match(card.shadowRoot.innerHTML,/class="zone selected"[^>]*aria-pressed="true" aria-label="Fach 2"/);
    await click(card,'zone',{zone:'1'});assert.equal(card.phase().temperature_c,185);
    await click(card,'zone',{zone:'2'});assert.equal(card.phase().duration_minutes,12);
    assert.equal(calls.length,0);
    card.selectedDevice().connectivity='offline';assert.equal(Boolean(card.canSend()),false);
  }
});

test('zone style changes preserve the private image, saved boxes and cooking values', () => {
  const calls=[];const {card}=makeCard(async r=>{calls.push(r);});setArtwork(card);
  card.history={'1':record(phase)};card.onInput({target:{id:'card-temperature',value:'185'}});
  for(const zone_style of ['invisible','outline'])card.setConfig({zone_style});
  assert.deepEqual(plain(card.appearance),artwork);assert.equal(card.phase().temperature_c,185);
  assert.equal(card.history['1'].settings.temperature_c,180);assert.equal(calls.length,0);
});

test('invisible areas respect busy and ungranted states', () => {
  const {card}=makeCard();card.setConfig({zone_style:'invisible'});setArtwork(card);
  card.busy=true;card.render();assert.ok(hotspots(card).every(button=>button.includes(' disabled')));
  card.busy=false;card._hass.user={id:'ordinary',is_admin:false};card.accessUserId='';card.render();
  assert.equal(hotspots(card).length,0);assert.equal(Boolean(card.canSend()),false);
});

test('editor saves A/B as card configuration in both languages without changing device artwork', () => {
  const {card,elements,events}=makeCard();setArtwork(card);
  const Editor=elements.get('airfryer-recipes-card-editor');const editor=new Editor();
  editor.setConfig({type:'custom:airfryer-recipes-card',title:'Kitchen',dry_run:true,graphic_size:'large'});
  editor.hass={language:'de'};
  assert.match(editor.shadowRoot.innerHTML,/A – Dezente Markierung/);
  assert.match(editor.shadowRoot.innerHTML,/B – Unsichtbare Touchbereiche/);
  assert.match(editor.shadowRoot.innerHTML,/name="zone_style"/);
  assert.ok(editor.shadowRoot.innerHTML.indexOf('B – Unsichtbare Touchbereiche')<editor.shadowRoot.innerHTML.indexOf('A – Dezente Markierung'));
  assert.match(editor.shadowRoot.innerHTML,/value="invisible" selected/);
  editor.shadowRoot.listeners.get('change')({target:{name:'zone_style',value:'invisible'}});
  assert.equal(events.at(-1).type,'config-changed');assert.equal(events.at(-1).detail.config.zone_style,'invisible');
  assert.equal(events.at(-1).detail.config.graphic_size,'large');assert.equal(events.at(-1).detail.config.dry_run,true);
  editor.hass={language:'en'};assert.match(editor.shadowRoot.innerHTML,/B – Invisible touch areas/);
  assert.match(editor.shadowRoot.innerHTML,/value="invisible" selected/);
  const reopened=new Editor();reopened.setConfig(plain(events.at(-1).detail.config));
  assert.equal(reopened.config.zone_style,'invisible');assert.deepEqual(plain(card.appearance),artwork);
});

test('B keeps rectangles visible in the designer and applies resized invisible areas after saving', async () => {
  const calls=[];let saved=structuredClone(artwork);
  const {card,context,elements}=makeCard(async r=>{
    calls.push(r);
    if(r.type.endsWith('appearance_set')){saved=plain(r.appearance);return {saved:true};}
    return structuredClone(saved);
  });
  card.setConfig({zone_style:'invisible'});setArtwork(card);card.connectedCallback();
  vm.runInNewContext(designerSource,context);
  const designer=new (elements.get('airfryer-device-designer'))();
  designer._hass=card._hass;designer.device='appliance';designer.devices=[device()];
  designer.saved=structuredClone(artwork);designer.draft=structuredClone(artwork);designer.render();
  assert.match(designer.shadowRoot.innerHTML,/<button type="button" data-zone="1"[^>]*>Fach 1<\/button>/);
  assert.match(designer.shadowRoot.innerHTML,/Hier bleiben sie zum Ausrichten sichtbar/);
  await designer.change({target:{dataset:{zoneInput:'1',index:'2'},value:'50'}});
  assert.equal(designer.saved.zones['1'][2],45);
  await designer.click({target:{closest:()=>({dataset:{action:'save'}})}});await settle();
  assert.equal(saved.zones['1'][2],50);
  assert.match(hotspots(card)[0],/width:50%;height:20%/);
  assert.ok(hotspots(card).every(button=>/><\/button>$/.test(button)));
  assert.deepEqual(calls.map(r=>r.type),['airfryer_recipes/appearance_set','airfryer_recipes/appearance_get']);
  card.disconnectedCallback();
});

test("SYNC preview uses explicit drafts of both zones and never calls send", async () => {
  const calls = [];
  const { card } = makeCard(async r => { calls.push(r); return { zones: [{ zone_id: 1, settings: phase, planned_delay_minutes: 3 }, { zone_id: 2, settings: other, planned_delay_minutes: 0 }], transmitted: false }; });
  card.drafts.set(JSON.stringify(['appliance', '2']), { settings: other, recipe_id: null });
  await click(card, 'multi-sync');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, 'airfryer_recipes/multi_preview');
  assert.deepEqual(plain(calls[0].sources), { '1': { settings: phase }, '2': { settings: other } });
  assert.match(card.shadowRoot.innerHTML, /Nur Vorschau/);
  assert.match(card.shadowRoot.innerHTML, /Geplante Wartezeit: 3 min/);
});

test("MATCH explicitly uses zone one even when zone two is selected", async () => {
  const calls = [];
  const { card } = makeCard(async r => { calls.push(r); return { zones: [] }; });
  card.drafts.set(JSON.stringify(['appliance', '1']), { settings: phase, recipe_id: null });
  card.selectedZoneId = '2'; card.manualPreviewProgram = other.program;
  card.manualPreviewTemperatureC = other.temperature_c; card.manualPreviewDurationMinutes = other.duration_minutes;
  await click(card, 'multi-match');
  assert.equal(calls[0].mode, 'match');
  assert.deepEqual(plain(calls[0].sources), { '1': { settings: phase } });
});

test("missing zone drafts and unsupported/offline devices cannot silently send", async () => {
  const calls = [];
  const { card } = makeCard(async r => { calls.push(r); });
  await click(card, 'multi-sync');
  assert.equal(calls.length, 0);
  assert.match(card.shadowRoot.innerHTML, /Wähle zuerst die Werte/);
  card.selectedDevice().connectivity = 'offline'; card.render();
  assert.match(card.shadowRoot.innerHTML, /data-action="multi-sync" disabled/);
  card.selectedDevice().zones.pop(); card.render();
  assert.doesNotMatch(card.shadowRoot.innerHTML, /data-action="multi-sync"/);
});

test("ordinary user multi-preview uses whole-device backend route", async () => {
  const calls = [];
  const { card } = makeCard(async r => { calls.push(r); return { zones: [] }; });
  card._hass.user = { id: 'user', is_admin: false }; card.accessUserId = 'user';
  await click(card, 'multi-match');
  assert.equal(calls[0].type, 'airfryer_recipes/control');
  assert.equal(calls[0].action, 'multi_preview');
  assert.equal(calls[0].parameters.device_id, 'appliance');
});

test('multi preview explains the remaining state guard for the reviewed new controller', () => {
  const { card } = makeCard();
  card.multiPreview = { zones: [], controller_contract: { explicit_values: true, live_send_enabled: false } };
  card.render();
  assert.match(card.shadowRoot.innerHTML, /Controller unterstützt die neuen Optionen/);
  assert.match(card.shadowRoot.innerHTML, /fehlende oder unbekannte Fächer/);
  card._hass.language = 'en'; card.render();
  assert.match(card.shadowRoot.innerHTML, /missing or unknown zones/);
  card.multiPreview.controller_contract.explicit_values = false; card.render();
  assert.match(card.shadowRoot.innerHTML, /has not been reviewed/);
});

test('own multi-send asks confirmation with both exact phases before one confirm request', async () => {
  const calls = [], dialogs = [];
  const { card } = makeCard(async r => {
    calls.push(r);
    if (r.parameters?.token && r.action === 'multi_cancel') return {};
    if (r.action === 'multi_prepare') return { token:'multi-token', zones:[{zone_id:1,settings:phase},{zone_id:2,settings:other}] };
    if (r.action === 'multi_confirm') return { outcome:'accepted', history_saved:true };
    return { available:true,zones:{} };
  }, text => { dialogs.push(text); return true; });
  card.config.dry_run = false;
  card.drafts.set(JSON.stringify(['appliance','2']),{settings:other,recipe_id:null});
  await click(card,'multi-send-sync');
  assert.equal(dialogs.length,1);
  assert.match(dialogs[0],/Fach 1.*180/); assert.match(dialogs[0],/Fach 2.*190/);
  const controlled = calls.filter(r=>r.type==='airfryer_recipes/multi_action');
  assert.equal(controlled[0].action,'multi_prepare');
  assert.equal(controlled[0].parameters.dry_run,false);
  assert.equal(controlled.filter(r=>r.action==='multi_confirm').length,1);
});

test('own multi dry-run and rejected dialog never confirm a device command', async () => {
  for (const dry of [true,false]) {
    const calls=[];
    const { card } = makeCard(async r=>{calls.push(r);return {token:dry?undefined:'multi-token',zones:[{zone_id:1,settings:phase},{zone_id:2,settings:phase}]};},()=>false);
    card.config.dry_run=dry;
    await click(card,'multi-send-match');
    assert.equal(calls.filter(r=>r.action==='multi_confirm').length,0);
    assert.equal(calls[0].parameters.dry_run,dry);
  }
});
