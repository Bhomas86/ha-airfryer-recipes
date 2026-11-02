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
    window: {}, confirm: dialog, Event, CustomEvent: class { constructor(type, options) { this.type = type; Object.assign(this, options); } },
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
  assert.match(card.shadowRoot.innerHTML, /&lt;img/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /<img/);
  assert.equal(context.window.customCards[0].type, "airfryer-recipes-card");
  assert.equal(card.constructor.getStubConfig().dry_run, true);
  assert.equal(card.constructor.getConfigElement() instanceof elements.get("airfryer-recipes-card-editor"), true);
  assert.match(cardSource, /\.\/panel\.js\?v=0\.1\.0b15/);
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
