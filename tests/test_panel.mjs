import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/panel.js", import.meta.url), "utf8");

function fakeConnection() {
  const listeners = new Set();
  return { connected: true, listeners,
    addEventListener(type, callback) { if (type === "disconnected") listeners.add(callback); },
    removeEventListener(type, callback) { if (type === "disconnected") listeners.delete(callback); },
    disconnect() { this.connected = false; for (const callback of [...listeners]) callback(); },
  };
}

function panelWith(api, admin = true, confirmDialog = () => true) {
  let Panel;
  const events = [];
  const createdElements = [];
  const context = {
    HTMLElement: class {
      attachShadow() {
        this.shadowRoot = { addEventListener() {}, innerHTML: "", getElementById() {} };
        return this.shadowRoot;
      }
      dispatchEvent(event) { events.push(event); }
    },
    Event,
    customElements: { get(name) { return name === "airfryer-recipes-panel" ? Panel : undefined; }, define(name, type) { assert.equal(name, "airfryer-recipes-panel"); Panel = type; } },
    confirm: confirmDialog,
    prompt: () => "Copy",
    setTimeout,
    URL: class extends URL {
      static createObjectURL() { return "blob:diagnostic-preview"; }
      static revokeObjectURL() {}
    },
    Blob,
    document: { createElement: () => {
      const element = { clicked: false, click() { this.clicked = true; } };
      createdElements.push(element);
      return element;
    } },
    structuredClone,
    FormData: class {
      constructor(form) { this.values = form.values; }
      get(name) { return this.values[name] ?? null; }
      has(name) { return Object.hasOwn(this.values, name); }
    },
  };
  vm.runInNewContext(source.replace(/^export /m, ""), context);
  const panel = new Panel();
  Object.defineProperty(panel, "betaFeatures", { value: true, writable: true, configurable: true });
  panel._hass = { language: "de", user: { id: "u1", is_admin: admin }, connection: fakeConnection(), callWS: api };
  panel.watchConnection(panel._hass.connection);
  panel.events = events;
  panel.createdElements = createdElements;
  return panel;
}

function betaPanel(api, admin = true, dialog) {
  const panel = panelWith(api, admin, dialog);
  panel.deviceState = { status: "adapter_beta", devices: [{
    device_id: "ha-device", name: "Kitchen", model: "CAF-DC111S-AEU",
    zones: [{ zone_id: 1, status: "idle" }, { zone_id: 2, status: "idle" }],
  }] };
  panel.selectedDeviceId = "ha-device";
  panel.selectedZoneId = "1";
  return panel;
}

const betaPrepared = { token: "single-use", device_name: "Kitchen <unsafe>", zone_id: 1,
  settings: { program: "airfry", temperature_c: 170, duration_minutes: 1 } };

test("beta preparation never confirms automatically and displays the exact fixed test", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => { calls.push(request); return betaPrepared; });
  await panel.prepareBetaTest();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_prepare");
  assert.equal(calls[0].acknowledge_unverified, true);
  assert.equal(Object.hasOwn(calls[0], "settings"), false);
  assert.match(panel.shadowRoot.innerHTML, /Kitchen &lt;unsafe&gt;/);
  assert.match(panel.shadowRoot.innerHTML, /170 °C · 1 min/);
  assert.match(panel.shadowRoot.innerHTML, /Einmalig ans Gerät senden/);
});

test("beta send consumes the token and reports adapter acceptance without device confirmation", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => { calls.push(request); return { outcome: "accepted" }; });
  panel.betaTest = betaPrepared;
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_confirm");
  assert.equal(calls[0].token, "single-use");
  assert.equal(Object.hasOwn(calls[0], "device_id"), false);
  assert.match(panel.betaMessage, /keine Gerätebestätigung/);
  await panel.confirmBetaTest();
  assert.equal(calls.length, 1);
});

test("lost beta response does not retry or retain a token", async () => {
  let calls = 0;
  const panel = betaPanel(async () => { calls++; throw new Error("private transport data"); });
  panel.betaTest = betaPrepared;
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.match(panel.betaMessage, /Ergebnis unklar/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /private transport/);
  await panel.confirmBetaTest();
  assert.equal(calls, 1);
});

test("beta controls require administrator permission and explicit dialog acceptance", async () => {
  let calls = 0;
  const panel = betaPanel(async () => { calls++; }, false);
  panel.betaTest = betaPrepared;
  await panel.prepareBetaTest();
  await panel.confirmBetaTest();
  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /id="beta-device-test"/);
  const declined = betaPanel(async () => { calls++; }, true, () => false);
  declined.betaTest = betaPrepared;
  await declined.prepareBetaTest();
  await declined.confirmBetaTest();
  assert.equal(calls, 0);
});

test("changing beta target discards the visible confirmation and English messages exist", () => {
  const panel = betaPanel(async () => ({}));
  panel.betaTest = betaPrepared;
  panel.onChange({ target: { id: "preview-zone", value: "2" } });
  assert.equal(panel.betaTest, null);
  panel._hass.language = "en";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Supervised beta device test/);
  assert.match(panel.shadowRoot.innerHTML, /Both prepare buttons use the selected recipe or manual settings/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /fixed Air Fry test/);
});

test("beta preparation shows read-only refresh progress and a failed refresh never enables send", async () => {
  let reject;
  const calls = [];
  const panel = betaPanel((request) => {
    calls.push(request.type);
    return new Promise((resolve, fail) => { reject = fail; });
  });
  const task = panel.prepareBetaTest();
  assert.equal(panel.busy, true);
  assert.match(panel.shadowRoot.innerHTML, /Aktueller Gerätestatus wird angefordert/);
  assert.match(panel.shadowRoot.innerHTML, /keine Einstellungen gesendet/);
  reject({ code: "beta_test_blocked", message: "refresh_failed" });
  await task;
  assert.equal(panel.betaTest, null);
  assert.equal(panel.busy, false);
  assert.match(panel.betaMessage, /keinen neuen erfolgreichen Gerätebericht/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-action="beta-confirm"/);
  assert.deepEqual(calls, ["airfryer_recipes/beta_prepare"]);
});

test("selected recipe preparation sends only its ID and uses server-resolved confirmation values", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => {
    calls.push(request);
    return { ...betaPrepared, recipe_name: "Rolls", settings: { program: "airfry", temperature_c: 190, duration_minutes: 8 } };
  });
  await panel.onSubmit({ preventDefault() {}, submitter: { dataset: { betaSelection: "true" } },
    target: { id: "device-preview-form", values: { recipe_id: "saved", program: "forged", temperature_c: "999", duration_minutes: "999" } } });
  assert.equal(calls[0].source.recipe_id, "saved");
  assert.equal(Object.hasOwn(calls[0].source, "settings"), false);
  assert.equal(panel.betaTest.settings.temperature_c, 190);
  assert.match(panel.shadowRoot.innerHTML, /190 °C · 8 min/);
});

test("selected manual Fahrenheit values are converted and never mixed with preview API", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => { calls.push(request); return betaPrepared; });
  panel._hass.config = { unit_system: { temperature: "°F" } };
  await panel.prepareSelectedBeta({ values: { recipe_id: "", program: "airfry", temperature_c: "356", duration_minutes: "7" } });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_prepare");
  assert.equal(calls[0].source.settings.temperature_c, 180);
  assert.equal(calls[0].source.settings.duration_minutes, 7);
});

test("lower prepare button transfers Dry settings and zone 2 without a fixed-test fallback", async () => {
  const calls = [];
  let scrolled = 0;
  const panel = betaPanel(async (request) => {
    calls.push(request);
    return { ...betaPrepared, zone_id: request.zone_id, settings: request.source.settings };
  });
  panel.selectedZoneId = "2";
  panel.shadowRoot.getElementById = (id) => id === "device-preview-form"
    ? { values: { recipe_id: "", program: "dry", temperature_c: "55", duration_minutes: "360" } }
    : id === "beta-device-test" ? { scrollIntoView() { scrolled++; } } : undefined;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "beta-prepare" } }) } });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_prepare");
  assert.equal(calls[0].zone_id, 2);
  assert.deepEqual({ ...calls[0].source.settings }, { program: "dry", temperature_c: 55, duration_minutes: 360 });
  assert.match(panel.shadowRoot.innerHTML, /Fach 2 · Dörren · 55 °C · 360 min/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /170 °C · 1 min/);
  assert.equal(scrolled, 1);
});

test("lower prepare button uses the saved recipe ID and never mixes in manual fields", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => {
    calls.push(request);
    return { ...betaPrepared, recipe_name: "Dry recipe", settings: { program: "dry", temperature_c: 55, duration_minutes: 360 } };
  });
  panel.shadowRoot.getElementById = (id) => id === "device-preview-form"
    ? { values: { recipe_id: "dry-recipe", program: "airfry", temperature_c: "170", duration_minutes: "1" } } : undefined;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "beta-prepare" } }) } });
  assert.equal(calls.length, 1);
  assert.deepEqual({ ...calls[0].source }, { recipe_id: "dry-recipe" });
  assert.match(panel.shadowRoot.innerHTML, /Dörren · 55 °C · 360 min/);
});

test("invalid Dry temperature shows the backend error and discards the old Air Fry confirmation", async () => {
  const calls = [];
  let scrolled = 0;
  const panel = betaPanel(async (request) => {
    calls.push(request);
    throw { code: "beta_test_blocked", message: "test_range" };
  });
  panel.betaTest = betaPrepared;
  panel.shadowRoot.getElementById = (id) => id === "beta-device-test"
    ? { scrollIntoView() { scrolled++; } } : undefined;
  await panel.prepareSelectedBeta({ values: { program: "dry", temperature_c: "120", duration_minutes: "360" } });
  assert.deepEqual(calls.map(call => call.type), ["airfryer_recipes/beta_cancel", "airfryer_recipes/beta_prepare"]);
  assert.equal(calls[1].source.settings.temperature_c, 120);
  assert.equal(panel.betaTest, null);
  assert.match(panel.shadowRoot.innerHTML, /Werte liegen außerhalb/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-action="beta-confirm"/);
  assert.equal(scrolled, 1);
});

test("missing selection form blocks the lower button without preparing a fixed test", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => { calls.push(request); return betaPrepared; });
  panel.betaTest = betaPrepared;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "beta-prepare" } }) } });
  assert.deepEqual(calls.map(call => call.type), ["airfryer_recipes/beta_cancel"]);
  assert.equal(panel.betaTest, null);
  assert.match(panel.betaMessage, /gültige manuelle Werte auswählen/);
});

test("editing selected values invalidates a pending confirmation and preserves manual inputs", async () => {
  const calls = [];
  const panel = betaPanel(async (request) => { calls.push(request); return betaPrepared; });
  panel.betaTest = betaPrepared;
  panel.onInput({ target: { id: "preview-temperature", value: "190" } });
  assert.equal(panel.betaTest, null);
  panel.onInput({ target: { id: "preview-duration", value: "8" } });
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /id="preview-temperature"[^>]*value="190"/);
  assert.match(panel.shadowRoot.innerHTML, /id="preview-duration"[^>]*value="8"/);
  await panel.confirmBetaTest();
  assert.deepEqual(calls.map(call => call.type), ["airfryer_recipes/beta_cancel"]);
});

test("late preparation after an input edit is canceled and cannot restore old values", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => {
    calls.push(r);
    return r.type.endsWith("beta_prepare") ? new Promise(resolve => { finish = resolve; }) : Promise.resolve({ discarded: true });
  });
  const preparing = panel.prepareSelectedBeta({ values: { program: "airfry", temperature_c: "180", duration_minutes: "7" } });
  panel.onInput({ target: { id: "preview-temperature", value: "190" } });
  finish(betaPrepared);
  await preparing;
  assert.equal(panel.betaTest, null);
  assert.equal(panel.manualPreviewTemperatureC, 190);
  assert.match(panel.betaMessage, /Auswahl geändert/);
  await panel.confirmBetaTest();
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_prepare", "airfryer_recipes/beta_cancel"]);
});

test("leaving during preparation discards the late result without restoring a confirmation on return", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => {
    calls.push(r);
    return r.type.endsWith("beta_prepare") ? new Promise(resolve => { finish = resolve; }) : Promise.resolve({ discarded: true });
  });
  const preparing = panel.prepareBetaTest();
  panel.disconnectedCallback();
  finish(betaPrepared);
  await preparing;
  panel.connectedCallback();
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_prepare", "airfryer_recipes/beta_cancel"]);
});

test("websocket disconnect clears a token and makes no queued control request", async () => {
  const calls = [];
  const panel = betaPanel(async r => { calls.push(r); return betaPrepared; });
  panel.betaTest = betaPrepared;
  panel._hass.connection.disconnect();
  await panel.confirmBetaTest();
  await panel.prepareBetaTest();
  assert.equal(panel.betaTest, null);
  assert.match(panel.betaMessage, /kein Befehl wird nachgeholt/);
  assert.equal(calls.length, 0);
  panel._hass.connection.connected = true;
  await panel.confirmBetaTest();
  assert.equal(calls.length, 0);
});

test("replacing the HA connection cancels the old token before binding the new connection", async () => {
  const calls = [];
  const panel = betaPanel(async r => { calls.push(r); return {}; });
  const old = panel._hass.connection;
  panel.started = true;
  panel.betaTest = betaPrepared;
  const next = fakeConnection();
  panel.hass = { ...panel._hass, connection: next };
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.equal(old.listeners.size, 0);
  assert.equal(next.listeners.size, 1);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_cancel"]);
  panel.disconnectedCallback();
  assert.equal(next.listeners.size, 0);
});

test("discard button revokes the server token without a confirm or device request", async () => {
  const calls = [];
  const panel = betaPanel(async r => { calls.push(r); return { discarded: true }; });
  panel.betaTest = betaPrepared;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "beta-cancel" } }) } });
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_cancel"]);
});

test("double tapping confirm creates exactly one request while its reply is pending", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => { calls.push(r); return new Promise(resolve => { finish = resolve; }); });
  panel.betaTest = betaPrepared;
  const sending = panel.confirmBetaTest();
  await panel.confirmBetaTest();
  assert.equal(calls.length, 1);
  finish({ outcome: "accepted" });
  await sending;
  assert.match(panel.betaMessage, /Adapter hat die Anfrage angenommen/);
});

test("leaving during confirmation asks to revoke validation and ignores its late response", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => {
    calls.push(r);
    return r.type.endsWith("beta_confirm") ? new Promise(resolve => { finish = resolve; }) : Promise.resolve({ discarded: true });
  });
  panel.betaTest = betaPrepared;
  const sending = panel.confirmBetaTest();
  panel.disconnectedCallback();
  finish({ outcome: "accepted" });
  await sending;
  panel.connectedCallback();
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.doesNotMatch(panel.betaMessage, /Adapter hat die Anfrage angenommen/);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_confirm", "airfryer_recipes/beta_cancel"]);
});

test("late batch preparation after disconnect cannot enable a start", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => { calls.push(r); return new Promise(resolve => { finish = resolve; }); });
  const preparing = panel.prepareBatch();
  panel._hass.connection.disconnect();
  finish(batchPlan);
  await preparing;
  panel._hass.connection.connected = true;
  await panel.startBatch();
  assert.equal(panel.batchPlan, null);
  assert.equal(calls.length, 1);
});

test("disconnect during a batch step ignores its late result and never requests the next nonce", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => {
    calls.push(r);
    if (r.type.endsWith("batch_start")) return Promise.resolve({ run_id: "batch", next_token: "one", total: 2 });
    if (r.type.endsWith("batch_next")) return new Promise(resolve => { finish = resolve; });
    return Promise.resolve({ stopped: true });
  });
  panel.batchPlan = batchPlan;
  const running = panel.startBatch();
  await Promise.resolve(); await Promise.resolve(); await Promise.resolve();
  panel._hass.connection.disconnect();
  finish({ ...batchPlan.steps[0], done: false, next_token: "two" });
  await running;
  assert.equal(panel.batchRunning, false);
  assert.equal(panel.batchPlan, null);
  assert.equal(panel.batchResults.length, 0);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/batch_start", "airfryer_recipes/batch_next"]);
});

test("admin permission loss discards the visible token and cannot submit it", async () => {
  const calls = [];
  const panel = betaPanel(async r => { calls.push(r); return {}; });
  panel.betaTest = betaPrepared;
  panel.started = true;
  panel.hass = { ...panel._hass, user: { id: "u1", is_admin: false } };
  await panel.confirmBetaTest();
  assert.equal(panel.betaTest, null);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-action="beta-confirm"/);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/beta_cancel"]);
});

test("changing the selected zone during list preparation discards the late list", async () => {
  let finish;
  const calls = [];
  const panel = betaPanel(r => { calls.push(r); return new Promise(resolve => { finish = resolve; }); });
  const preparing = panel.prepareBatch();
  panel.onChange({ target: { id: "preview-zone", value: "2" } });
  finish(batchPlan);
  await preparing;
  await panel.startBatch();
  assert.equal(panel.batchPlan, null);
  assert.match(panel.batchMessage, /Auswahl geändert/);
  assert.equal(calls.length, 1);
});

test("a late re-arm result cannot overwrite a disconnect message", async () => {
  let finish;
  const panel = betaPanel(() => new Promise(resolve => { finish = resolve; }));
  const recovering = panel.recoverBeta();
  panel._hass.connection.disconnect();
  finish({ rearmed: true, transmitted: false });
  await recovering;
  assert.match(panel.batchMessage, /kein Befehl wird nachgeholt/);
  assert.doesNotMatch(panel.batchMessage, /Frischer Bereitschaftszustand bestätigt/);
});

test("unsupported program rejection remains visible and enables no confirmation", async () => {
  const panel = betaPanel(async () => { throw { code: "beta_test_blocked", message: "program_unsupported" }; });
  await panel.prepareSelectedBeta({ values: { program: "proof", temperature_c: "35", duration_minutes: "7" } });
  assert.equal(panel.betaTest, null);
  assert.match(panel.betaMessage, /Programm wurde nicht ersetzt/);
});

test("model temperatures show owner ranges apart from adapter ranges without adding Proof to selection", () => {
  const panel = betaPanel(async () => ({}));
  const device = panel.selectedDevice();
  device.programs = [{ id: "airfry", temperature_c: { min: 120, max: 205 }, limits_status: "estimated" }];
  device.model_profile = { source: "owner_reported", programs: [
    { id: "airfry", temperature_c: { min: 120, max: 230 }, temperature_step_c: null },
    { id: "proof", temperature_c: { min: 30, max: 45 }, temperature_step_c: 1 },
  ] };
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /120–230 °C/);
  assert.match(panel.shadowRoot.innerHTML, /120–205 °C/);
  assert.match(panel.shadowRoot.innerHTML, /Gären<\/td><td>30–45 °C · 1 °C Schritt<\/td><td>Nicht gemeldet/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<option value="proof"/);
  assert.match(panel.shadowRoot.innerHTML, /Schnittmenge aus Gerätebereich/);
  panel._hass.language = "en";
  panel._hass.config = { unit_system: { temperature: "°F" } };
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Proof<\/td><td>86–113 °F · 1.8 °F step<\/td><td>Not reported/);
  assert.match(panel.shadowRoot.innerHTML, /Appliance \(owner report\)/);
  assert.match(panel.shadowRoot.innerHTML, /248–446 °F/);
});

test("absent or unsupported profile provenance shows no owner range table", () => {
  const panel = betaPanel(async () => ({}));
  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<details>/);
  panel.selectedDevice().model_profile = { source: "unknown", programs: [{ id: "proof" }] };
  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<details>/);
});

const batchPlan = { token: "batch", device_name: "Fixture", skipped: [],
  steps: [{ zone_id: 1, settings: { program: "airfry", temperature_c: 180, duration_minutes: 7 } },
          { zone_id: 2, settings: { program: "bake", temperature_c: 180, duration_minutes: 6 } }] };

test("guided test uses one start consent and sequences distinct nonces without browser dialogs", async () => {
  const calls = [];
  let dialogs = 0;
  const panel = betaPanel(async (r) => {
    calls.push(r);
    if (r.type.endsWith("batch_prepare")) return batchPlan;
    if (r.type.endsWith("batch_start")) return { run_id: "batch", next_token: "one", total: 2 };
    const i = r.next_token === "one" ? 0 : 1;
    return { ...batchPlan.steps[i], done: i === 1, next_token: i === 0 ? "two" : null };
  }, true, () => { dialogs++; return true; });
  await panel.prepareBatch();
  assert.equal(calls.length, 1); // Showing a list sends no commands.
  assert.match(panel.shadowRoot.innerHTML, /Angezeigte Testfolge bestätigen und starten/);
  await panel.startBatch();
  assert.equal(dialogs, 0);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/batch_prepare", "airfryer_recipes/batch_start",
    "airfryer_recipes/batch_next", "airfryer_recipes/batch_next"]);
  assert.equal(calls[1].acknowledge_supervised_batch, true);
  assert.deepEqual(calls.slice(2).map(r => r.next_token), ["one", "two"]);
  assert.equal(panel.batchResults.length, 2);
  assert.match(panel.batchMessage, /Testfolge abgeschlossen/);
});

test("guided test stops on a lost response without replay or another step", async () => {
  const calls = [];
  const panel = betaPanel(async r => {
    calls.push(r);
    if (r.type.endsWith("batch_start")) return { run_id: "batch", next_token: "one", total: 2 };
    if (r.type.endsWith("batch_next")) throw new Error("private transport detail");
    return { stopped: true };
  });
  panel.batchPlan = batchPlan;
  await panel.startBatch();
  assert.equal(calls.filter(r => r.type.endsWith("batch_next")).length, 1);
  assert.match(panel.batchMessage, /Ein Befehl kann angekommen sein/);
  assert.doesNotMatch(panel.batchMessage, /private transport/);
  assert.equal(panel.batchRunning, false);
});

test("guided stop button works while a step is pending and prevents the next step", async () => {
  let resolve;
  const calls = [];
  const panel = betaPanel(async r => {
    calls.push(r);
    if (r.type.endsWith("batch_start")) return { run_id: "batch", next_token: "one", total: 2 };
    if (r.type.endsWith("batch_next")) return new Promise(done => { resolve = done; });
    return { stopped: true };
  });
  panel.batchPlan = batchPlan;
  const running = panel.startBatch();
  await Promise.resolve(); await Promise.resolve(); await Promise.resolve();
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "batch-stop" } }) } });
  resolve({ ...batchPlan.steps[0], done: false, next_token: "two" });
  await running;
  assert.equal(calls.filter(r => r.type.endsWith("batch_next")).length, 1);
  assert.match(panel.batchMessage, /Restliche Schritte abgebrochen/);
});

test("guided controls are admin-only and leaving the panel stops further requests", async () => {
  let calls = 0;
  const panel = betaPanel(async () => { calls++; }, false);
  panel.batchPlan = batchPlan;
  await panel.prepareBatch(); await panel.startBatch();
  panel.render();
  assert.equal(calls, 0);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /id="batch-test"/);
  panel.batchRunId = "batch";
  panel.disconnectedCallback();
  assert.equal(panel.batchStopRequested, true);
});

test("recovery sends only an explicit read-only re-arm and discards the old plan", async () => {
  const calls = [];
  const panel = betaPanel(async r => { calls.push(r); return { rearmed: true, transmitted: false }; });
  panel.batchPlan = batchPlan;
  panel.batchRunId = "old";
  await panel.recoverBeta();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/beta_recover");
  assert.equal(calls[0].acknowledge_physical_reset, true);
  assert.equal(panel.batchPlan, null);
  assert.equal(panel.batchRunId, null);
  assert.match(panel.batchMessage, /ohne HA-Neustart/);
});

test("adapter rejection identifies the failed batch step and does not claim unknown transport", async () => {
  const panel = betaPanel(async r => r.type.endsWith("batch_start")
    ? { run_id: "batch", next_token: "one", total: 2 }
    : { stopped: true, failed_step: 1, settings: { program: "airfry" }, zone_id: 1, error_code: 11912000 });
  panel.batchPlan = batchPlan;
  await panel.startBatch();
  assert.match(panel.batchMessage, /Schritt 1/);
  assert.match(panel.batchMessage, /Code 11912000/);
  assert.match(panel.batchMessage, /abgelehnt/);
  assert.equal(panel.batchResults.length, 0);
});

test("guided plan displays zone-ending actions before the single start consent", async () => {
  const panel = betaPanel(async () => ({ ...batchPlan, resets_between_programs: true }));
  await panel.prepareBatch();
  assert.match(panel.shadowRoot.innerHTML, /eigene vorbereitete Einstellungen in Fach 1 und 2 gezielt beenden/);
  assert.match(panel.shadowRoot.innerHTML, /sowie die angezeigten Schritte zum Beenden der Fächer/);
  assert.match(panel.shadowRoot.innerHTML, /<li value="2">/);
});

test("temperature batch lists resets before a same-program temperature change", async () => {
  const plan={...batchPlan,resets_between_programs:false,resets_between_settings:true,steps:[
    {zone_id:1,settings:{program:'proof',temperature_c:30,duration_minutes:60}},
    {zone_id:2,settings:{program:'proof',temperature_c:30,duration_minutes:60}},
    {zone_id:1,settings:{program:'proof',temperature_c:31,duration_minutes:60}},
    {zone_id:2,settings:{program:'proof',temperature_c:31,duration_minutes:60}},
  ]};
  const panel=betaPanel(async()=>plan);await panel.prepareBatch();
  assert.match(panel.shadowRoot.innerHTML,/class="muted">Vor Wertewechsel:[\s\S]*?<li value="3">/);
  assert.match(panel.shadowRoot.innerHTML,/Gären · 31 °C/);
  assert.match(panel.shadowRoot.innerHTML,/Bis zu 44 Einstellungen/);
  assert.equal(panel.batchNeedsReset(plan,1),false);assert.equal(panel.batchNeedsReset(plan,2),true);
});

test("program labels show names only without modifying capability metadata", () => {
  const panel=betaPanel();
  const program={id:'proof',limits_status:'owner_reported',send_status:'unverified',temperature_step_c:1};
  const before=JSON.stringify(program);
  assert.equal(panel.programOption(program),'Gären');
  panel._hass.language='en';
  assert.equal(panel.programOption(program),'Proof');
  assert.equal(JSON.stringify(program),before);
});

test("navigation remains available during loading and uses the HA sidebar event", async () => {
  const panel = panelWith(async () => ({ recipes: [] }));
  panel.busy = true;
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /data-action="menu" aria-label="Menü öffnen"/);
  assert.match(panel.shadowRoot.innerHTML, /<a href="\/">Verlassen<\/a>/);
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "menu" } }) } });
  assert.equal(panel.events.length, 1);
  assert.equal(panel.events[0].type, "hass-toggle-menu");
  assert.equal(panel.events[0].bubbles, true);
  assert.equal(panel.events[0].composed, true);
  panel._hass.language = "en";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /aria-label="Open menu"/);
  assert.match(panel.shadowRoot.innerHTML, /<a href="\/">Leave<\/a>/);
});

test("panel renders recipe names as escaped text and filters by tag", async () => {
  const panel = panelWith(async () => ({ recipes: [{
    id: "one", name: "<script>alert(1)</script>", description: "", category: "Dinner",
    tags: ["Schnell"], phases: [{ program: "airfry", temperature_c: 180, duration_minutes: 8 }],
  }] }));
  await panel.load();
  assert.match(panel.shadowRoot.innerHTML, /&lt;script&gt;/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<script>/);
  panel.query = "schnell";
  assert.equal(panel.filtered().length, 1);
  panel.query = "unknown";
  assert.equal(panel.filtered().length, 0);
});

test("recipe editor lists saved categories before the new-category choice without resetting other inputs", () => {
  const panel = panelWith(async () => ({ recipes: [] }));
  panel.recipes = [
    { id: "one", name: "Rolls", category: "Aufbacken", phases: [{}] },
    { id: "two", name: "Cake", category: "Backen", phases: [{}] },
  ];
  panel.editor = { name: "Test", category: "Aufbacken", phases: [{}] };
  panel.render();
  const markup = panel.shadowRoot.innerHTML;
  assert.match(markup, /<option value="existing-0" selected>Aufbacken<\/option><option value="existing-1" >Backen<\/option><option value="new">Neue Kategorie hinzufügen…<\/option>/);
  const field = { hidden: true };
  const input = { required: false, focused: false, focus() { this.focused = true; } };
  panel.shadowRoot.getElementById = (id) => id === "new-category-field" ? field : input;
  panel.onChange({ target: { id: "recipe-category", value: "new" } });
  assert.equal(field.hidden, false);
  assert.equal(input.required, true);
  assert.equal(input.focused, true);
  assert.equal(panel.shadowRoot.innerHTML, markup);
  panel.onChange({ target: { id: "recipe-category", value: "existing-0" } });
  assert.equal(field.hidden, true);
  assert.equal(input.required, false);
});

function recipeEditorPanel(api = async () => ({ recipes: [] })) {
  const panel = betaPanel(api);
  panel.selectedDevice().programs = ["airfry", "roast", "bake", "grill", "reheat", "dry"].map(id =>
    ({ id, limits_status: "estimated", send_status: "unverified" }));
  panel.editor = { name: "", description: "", category: "", tags: [], phases: [{}] };
  panel.render();
  return panel;
}

test("new recipe uses reported program IDs in a localized dropdown without picking one automatically", () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => { calls.push(r); });
  panel.selectedDevice().model_profile = { programs: [{ id: "proof" }] };
  panel.render();
  const form = panel.shadowRoot.innerHTML.match(/<form id="editor"[\s\S]*?<\/form>/)[0];
  assert.match(form, /<select id="recipe-program" name="program" required>/);
  assert.match(form, /<option value="" disabled selected>Programm auswählen/);
  assert.match(form, /value="airfry" >Heißluft-Frittieren<\/option>/);
  assert.match(form, /value="roast" >Braten/);
  assert.match(form, /value="dry" >Dörren/);
  assert.doesNotMatch(form, /value="proof"|<input id="recipe-program"/);
  assert.equal(panel.editor.phases[0].program, undefined);
  assert.equal(calls.length, 0);
  panel._hass.language = "en";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Choose a program…/);
  assert.match(panel.shadowRoot.innerHTML, /Only the program identifier is saved/);
});

test("legacy Airfry spelling remains selected and can be opened for explicit correction", async () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => { calls.push(r); });
  const recipe = { id: "legacy", name: "Piccolinies", category: "", phases: [{
    program: "Airfry", temperature_c: 180, duration_minutes: 7 }] };
  panel.recipes = [recipe];
  panel.editor = null;
  panel.previewRecipeId = recipe.id;
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Rezeptprogramm bearbeiten/);
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "edit", id: recipe.id } }) } });
  const form = panel.shadowRoot.innerHTML.match(/<form id="editor"[\s\S]*?<\/form>/)[0];
  assert.match(form, /value="Airfry" selected>Airfry · von diesem Gerät nicht gemeldet/);
  assert.match(form, /value="airfry" >Heißluft-Frittieren/);
  assert.equal(panel.editor.phases[0].program, "Airfry");
  assert.equal(recipe.phases[0].program, "Airfry");
  assert.equal(calls.length, 0);
});

test("explicitly saving a reported program corrects the same recipe without storing a device or zone", async () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => {
    calls.push(r);
    return r.type.endsWith("/list") ? { recipes: [] } : { recipe: r.recipe };
  });
  panel.editor = { id: "legacy", name: "Piccolinies", phases: [{ program: "Airfry", temperature_c: 180, duration_minutes: 7 }] };
  await panel.onSubmit({ preventDefault() {}, target: { id: "editor", values: {
    name: "Piccolinies", program: "airfry", temperature_c: "180", duration_minutes: "7",
  } } });
  assert.equal(calls[0].type, "airfryer_recipes/update");
  assert.equal(calls[0].recipe.id, "legacy");
  assert.equal(calls[0].recipe.phases[0].program, "airfry");
  assert.equal(calls[0].recipe.phases[0].temperature_c, 180);
  assert.equal(calls[0].recipe.phases[0].duration_minutes, 7);
  assert.equal(Object.hasOwn(calls[0].recipe, "device_id"), false);
  assert.equal(Object.hasOwn(calls[0].recipe, "zone_id"), false);
  assert.equal(calls.some(r => r.type.includes("beta_") || r.type.endsWith("prepare_send")), false);
});

test("switching to custom input and back preserves all unsaved editor fields", async () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => { calls.push(r); });
  const form = { id: "editor", values: { name: "Unsaved <name>", description: "Keep description", tags: "one, two, ",
    category_choice: "new", category_new: "New category", favorite: "on", program: "airfry", temperature_c: "190", duration_minutes: "9" } };
  panel.shadowRoot.getElementById = id => id === "editor" ? form : undefined;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "editor-program-mode" } }) } });
  assert.match(panel.shadowRoot.innerHTML, /<input id="recipe-program" name="program"[^>]*value="airfry"/);
  assert.match(panel.shadowRoot.innerHTML, /value="Unsaved &lt;name&gt;"/);
  assert.match(panel.shadowRoot.innerHTML, /<option value="new" selected>/);
  assert.match(panel.shadowRoot.innerHTML, /id="recipe-category-new"[^>]*required[^>]*value="New category"/);
  assert.match(panel.shadowRoot.innerHTML, /value="one, two, "/);
  assert.match(panel.shadowRoot.innerHTML, /name="favorite" checked/);
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "editor-program-mode" } }) } });
  assert.match(panel.shadowRoot.innerHTML, /<select id="recipe-program" name="program" required>/);
  assert.match(panel.shadowRoot.innerHTML, /value="airfry" selected/);
  assert.equal(panel.editor.phases[0].temperature_c, 190);
  assert.equal(panel.editor.phases[0].duration_minutes, 9);
  assert.equal(calls.length, 0);
});

test("program selection rerender retains the native form draft and does not mutate a stored recipe", () => {
  const panel = recipeEditorPanel();
  const stored = { id: "one", name: "Original", phases: [{ program: "airfry", temperature_c: 180, duration_minutes: 7 }] };
  panel.recipes = [stored];
  panel.editor = structuredClone(stored);
  panel.render();
  const form = { id: "editor", values: { name: "Changed name", program: "roast", temperature_c: "190", duration_minutes: "10" } };
  panel.shadowRoot.getElementById = id => id === "editor" ? form : undefined;
  panel.onChange({ target: { id: "recipe-program", value: "roast" } });
  assert.match(panel.shadowRoot.innerHTML, /value="roast" selected/);
  assert.equal(panel.editor.name, "Changed name");
  assert.equal(panel.editor.phases[0].program, "roast");
  assert.equal(stored.name, "Original");
  assert.equal(stored.phases[0].program, "airfry");
});

test("recipes remain freely editable without reported adapter programs", () => {
  const panel = recipeEditorPanel();
  panel.deviceState = { devices: [], status: "adapter_missing" };
  panel.editor = { name: "Portable", phases: [{ program: "my-program", temperature_c: 150, duration_minutes: 4 }] };
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /<input id="recipe-program" name="program"[^>]*value="my-program"/);
  assert.match(panel.shadowRoot.innerHTML, /Rezepte auch ohne Adapter weiter bearbeiten/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<select id="recipe-program"/);
});

test("device refresh preserves an unsaved program even when the new report no longer includes it", async () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => {
    calls.push(r);
    return { status: "adapter_beta", devices: [{ device_id: "ha-device", name: "Kitchen", zones: [{zone_id:1,status:"idle"}],
      programs: [{id:"airfry", limits_status:"estimated", send_status:"unverified"}] }] };
  });
  const form = { id: "editor", values: { name: "Keep draft", program: "roast", temperature_c: "190", duration_minutes: "10" } };
  panel.shadowRoot.getElementById = id => id === "editor" ? form : undefined;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "refresh-devices" } }) } });
  assert.equal(panel.editor.name, "Keep draft");
  assert.equal(panel.editor.phases[0].program, "roast");
  assert.match(panel.shadowRoot.innerHTML, /value="roast" selected>roast · von diesem Gerät nicht gemeldet/);
  assert.deepEqual(calls.map(r => r.type), ["airfryer_recipes/devices"]);
});

test("unsaved editor temperature keeps its meaning across a Fahrenheit-to-Celsius rerender", () => {
  const panel = recipeEditorPanel();
  panel._hass.config = { unit_system: { temperature: "°F" } };
  panel.render();
  const form = { id: "editor", values: { name: "Draft", program: "airfry", temperature_c: "356", duration_minutes: "7" } };
  panel.shadowRoot.getElementById = id => id === "editor" ? form : undefined;
  panel.started = true;
  panel.hass = { ...panel._hass, config: { unit_system: { temperature: "°C" } } };
  assert.match(panel.shadowRoot.innerHTML, /id="recipe-temperature"[^>]*value="180"/);
  assert.equal(panel.editor.phases[0].temperature_c, 180);
});

test("an editor left open when permissions change is hidden and cannot save", async () => {
  const calls = [];
  const panel = recipeEditorPanel(async r => { calls.push(r); });
  panel.started = true;
  panel.hass = { ...panel._hass, user: { id: "u1", is_admin: false } };
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /<form id="editor"/);
  await panel.onSubmit({ preventDefault() {}, target: { id: "editor", values: { program: "airfry" } } });
  assert.equal(calls.length, 0);
});

test("non-admin panel cannot invoke a mutation", async () => {
  const calls = [];
  const panel = panelWith(async (request) => { calls.push(request.type); return { recipes: [] }; }, false);
  await panel.action(() => panel.request("delete", { recipe_id: "one" }), "deleted");
  assert.deepEqual(calls, []);
  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-action="new"/);
});

test("import preview waits for explicit confirmation and uses selected policy", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    if (request.type.endsWith("import_preview")) return {
      token: "preview-token", incoming_count: 1, duplicate_ids: ["one"], duplicate_names: [],
    };
    if (request.type.endsWith("import_confirm")) return { imported: 1 };
    return { recipes: [] };
  });
  await panel.previewFile({ size: 20, text: async () => '{"schema_version":1,"recipes":[]}' });
  assert.equal(calls.length, 1);
  assert.match(panel.shadowRoot.innerHTML, /Gleiche IDs: 1/);
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "import-replace" } }) } });
  assert.equal(calls[1].type, "airfryer_recipes/import_confirm");
  assert.equal(calls[1].policy, "replace_ids");
  assert.equal(calls[1].token, "preview-token");
});

test("export opens the server-provided named download instead of a blob URL", async () => {
  const panel = panelWith(async (request) => {
    assert.equal(request.type, "airfryer_recipes/export");
    return {
      url: "/api/airfryer_recipes/export?authSig=signed",
      filename: "Airfryer-Rezepte-Home-Assistant.json",
    };
  });
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "export" } }) } });
  assert.equal(panel.createdElements.length, 1);
  assert.equal(panel.createdElements[0].href, "/api/airfryer_recipes/export?authSig=signed");
  assert.equal(panel.createdElements[0].download, "Airfryer-Rezepte-Home-Assistant.json");
  assert.equal(panel.createdElements[0].clicked, true);
});

test("form creates a device-independent recipe through the authenticated API", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    return request.type.endsWith("list") ? { recipes: [] } : { recipe: { id: "one" } };
  });
  panel.editor = { name: "", phases: [{}] };
  await panel.onSubmit({
    preventDefault() {},
    target: { id: "editor", values: {
      name: "Bread rolls", description: "", category_choice: "new", category_new: "Breakfast", tags: "quick, frozen",
      program: "airfry", temperature_c: "180", duration_minutes: "8", favorite: "on",
    } },
  });
  assert.equal(calls[0].type, "airfryer_recipes/create");
  assert.equal(calls[0].recipe.favorite, true);
  assert.equal(calls[0].recipe.category, "Breakfast");
  assert.deepEqual([...calls[0].recipe.tags], ["quick", "frozen"]);
  assert.equal(calls[0].recipe.phases[0].temperature_c, 180);
  assert.equal(calls[0].recipe.device_id, undefined);
});

test("new category with different case reuses the stored spelling", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    return request.type.endsWith("list") ? { recipes: [] } : { recipe: { id: "two" } };
  });
  panel.recipes = [{ id: "one", name: "Old rolls", category: "Aufbacken", phases: [{}] }];
  panel.editor = { name: "", phases: [{}] };
  await panel.onSubmit({ preventDefault() {}, target: { id: "editor", values: {
    name: "Rolls", category_choice: "new", category_new: "  aufBACKen  ",
    program: "airfry", temperature_c: "180", duration_minutes: "8",
  } } });
  assert.equal(calls[0].recipe.category, "Aufbacken");
});

test("selected existing category is saved unchanged", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    return request.type.endsWith("list") ? { recipes: [] } : { recipe: { id: "two" } };
  });
  panel.recipes = [{ id: "one", name: "Old rolls", category: "Aufbacken", phases: [{}] }];
  panel.editor = { name: "", phases: [{}] };
  await panel.onSubmit({ preventDefault() {}, target: { id: "editor", values: {
    name: "Rolls", category_choice: "existing-0", category_new: "Unused",
    program: "airfry", temperature_c: "180", duration_minutes: "8",
  } } });
  assert.equal(calls[0].recipe.category, "Aufbacken");
});

test("Fahrenheit display converts back to Celsius for storage", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    return request.type.endsWith("list") ? { recipes: [] } : { recipe: { id: "one" } };
  });
  panel._hass.config = { unit_system: { temperature: "°F" } };
  assert.equal(panel.toDisplay(180), 356);
  panel.editor = { name: "", phases: [{}] };
  await panel.onSubmit({ preventDefault() {}, target: { id: "editor", values: {
    name: "Rolls", program: "airfry", temperature_c: "356", duration_minutes: "8",
  } } });
  assert.equal(calls[0].recipe.phases[0].temperature_c, 180);
});

test("device discovery failure does not break recipe management", async () => {
  const panel = panelWith(async (request) => {
    if (request.type.endsWith("/list")) return { recipes: [{
      id: "one", name: "Rolls", description: "", category: "", tags: [],
      phases: [{ program: "airfry", temperature_c: 180, duration_minutes: 8 }],
    }] };
    if (request.type.endsWith("/favorites")) return { recipe_ids: [] };
    if (request.type.endsWith("/devices")) throw { code: "storage_error" };
    throw new Error(request.type);
  });
  await panel.load();
  assert.equal(panel.recipes.length, 1);
  assert.match(panel.shadowRoot.innerHTML, /Rolls/);
  assert.match(panel.shadowRoot.innerHTML, /Die Anfrage ist fehlgeschlagen/);
  assert.match(panel.shadowRoot.innerHTML, /Daten von Airfryer Control konnten nicht sicher gelesen/);
});

test("dry-run UI uses only reported zones and sends no live-control fields", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    if (request.type.endsWith("prepare_send")) return {
      mode: "dry_run", live_send_enabled: false, transmitted: false,
      accepted_by_adapter: false, confirmed_on_device: false,
      device_id: "ha-device", zone_id: 2,
      settings: request.settings, zone_status: "cooking",
      blocking_reasons: ["upstream_contract_unverified", "freshness_unverified", "zone_not_idle"],
    };
    throw new Error(request.type);
  });
  panel.recipes = [{ id: "recipe-one", name: "Testbrötchen", phases: [{
    program: "airfry", temperature_c: 160, duration_minutes: 8,
  }] }];
  panel.deviceState = { status: "adapter_loaded", live_send_enabled: false, devices: [{
    device_id: "ha-device", name: "Küche <oben>", model: "CAF-DC111S-AEU",
    connectivity: "reported_online", freshness: "reported",
    zones: [{ zone_id: 2, status: "cooking" }],
    programs: [
      { id: "airfry", limits_status: "estimated", send_status: "unverified" },
      { id: "bake", limits_status: "confirmed", send_status: "confirmed" },
    ],
  }] };
  panel.selectedDeviceId = "ha-device";
  panel.selectedZoneId = "2";
  panel.previewRecipeId = "recipe-one";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Geräte-Testvorschau/);
  assert.match(panel.shadowRoot.innerHTML, /Küche &lt;oben&gt;/);
  assert.match(panel.shadowRoot.innerHTML, /Fach 2 · Gart/);
  assert.match(panel.shadowRoot.innerHTML, />Heißluft-Frittieren<\/option>/);
  assert.match(panel.shadowRoot.innerHTML, />Backen<\/option>/);
  assert.match(panel.shadowRoot.innerHTML, /Meldezeit geliefert/);
  assert.match(panel.shadowRoot.innerHTML, /Testvorschau prüfen/);
  assert.match(panel.shadowRoot.innerHTML, /Es wird kein Gerätebefehl ausgeführt/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /confirm_send|Einstellungen senden/);

  await panel.onSubmit({ preventDefault() {}, target: { id: "device-preview-form", values: {
    device_id: "ha-device", zone_id: "2", recipe_id: "recipe-one",
    program: "airfry", temperature_c: "160", duration_minutes: "8",
  } } });
  assert.equal(calls.length, 1);
  assert.deepEqual(Object.keys(calls[0]).sort(), ["device_id", "settings", "type", "zone_id"]);
  assert.equal(calls[0].type, "airfryer_recipes/prepare_send");
  assert.deepEqual({ ...calls[0].settings }, {
    program: "airfry", temperature_c: 160, duration_minutes: 8,
  });
  assert.match(panel.shadowRoot.innerHTML, /Es wurde nichts an das Gerät übertragen/);
  assert.match(panel.shadowRoot.innerHTML, /Das Fach ist nicht sicher bereit/);
  const germanKeys = Object.keys(panel.words).sort();
  panel._hass.language = "en";
  panel.render();
  assert.deepEqual(Object.keys(panel.words).sort(), germanKeys);
  assert.match(panel.shadowRoot.innerHTML, /Device test preview/);
  assert.match(panel.shadowRoot.innerHTML, /Nothing was transmitted to the appliance/);
  assert.match(panel.shadowRoot.innerHTML, /The upstream send contract is not verified/);
  assert.match(panel.shadowRoot.innerHTML, />Air Fry<\/option>/);
});

test("saved recipe program absent from adapter remains unchanged and is marked", async () => {
  const panel = panelWith(async () => ({ recipes: [] }));
  panel.recipes = [{ id: "proof-recipe", name: "Teig", phases: [{
    program: "proof", temperature_c: 35, duration_minutes: 60,
  }] }];
  panel.deviceState = { status: "adapter_beta", live_send_enabled: false, devices: [{
    device_id: "ha-device", name: "Kitchen", model: "CAF-DC111S-AEU",
    connectivity: "reported_online", freshness: "reported",
    zones: [{ zone_id: 1, status: "idle" }],
    programs: [{ id: "airfry", limits_status: "estimated", send_status: "unverified" }],
  }] };
  panel.selectedDeviceId = "ha-device";
  panel.selectedZoneId = "1";
  panel.previewRecipeId = "proof-recipe";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Gären · von diesem Gerät nicht gemeldet/);
  assert.match(panel.shadowRoot.innerHTML, /<input type="hidden" name="program" value="proof">/);
  assert.match(panel.shadowRoot.innerHTML, /<select id="preview-program" name="program" required disabled>/);
});

test("manual dry-run converts Fahrenheit and target errors stay in device section", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request);
    throw { code: "target_not_found" };
  });
  panel._hass.config = { unit_system: { temperature: "°F" } };
  panel.deviceState = { status: "adapter_loaded", live_send_enabled: false, devices: [{
    device_id: "ha-device", name: "Kitchen", model: null, connectivity: "unknown",
    zones: [{ zone_id: 1, status: "unknown" }],
  }] };
  panel.selectedDeviceId = "ha-device";
  panel.selectedZoneId = "1";
  await panel.onSubmit({ preventDefault() {}, target: { id: "device-preview-form", values: {
    device_id: "ha-device", zone_id: "1", program: " airfry ",
    temperature_c: "356", duration_minutes: "10",
  } } });
  assert.equal(calls[0].settings.program, "airfry");
  assert.equal(calls[0].settings.temperature_c, 180);
  assert.match(panel.shadowRoot.innerHTML, /nicht mehr verfügbar/);
  assert.equal(panel.error, "");
});

test("regular users see neither device preview nor device discovery requests", async () => {
  const calls = [];
  const panel = panelWith(async (request) => {
    calls.push(request.type);
    return request.type.endsWith("/list") ? { recipes: [] } : { recipe_ids: [] };
  }, false);
  await panel.load();
  assert.deepEqual(calls.sort(), ["airfryer_recipes/favorites", "airfryer_recipes/list"]);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /id="device-preview"/);
});

test("admin device-access view contains whole-device grants and escapes names", async () => {
  const calls = [];
  const panel = panelWith(async (r) => { calls.push(r); return { available: true, users: [{ id: "u", name: "User <x>" }], devices: [{ id: "d", name: "Kitchen" }], grants: [{ user_id: "u", device_id: "d" }] }; });
  await panel.manageAccess();
  assert.equal(calls[0].type, "airfryer_recipes/access_list");
  assert.match(panel.shadowRoot.innerHTML, /Geräteberechtigungen/);
  assert.match(panel.shadowRoot.innerHTML, /User &lt;x&gt;/);
  assert.match(panel.shadowRoot.innerHTML, /einschließlich aller Fächer/);
  assert.match(panel.shadowRoot.innerHTML, /data-action="access-revoke"/);
  panel._hass.language = "en";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Device permissions/);
});

test("admin grants and revokes only a user/device pair after explicit clicks", async () => {
  const calls = [];
  const panel = panelWith(async (r) => { calls.push(r); return r.type.endsWith("access_list") ? { available: true, users: [], devices: [], grants: [] } : { saved: true }; });
  const form = { reportValidity: () => true, values: { user_id: "u", device_id: "d" } };
  panel.shadowRoot.getElementById = (id) => id === "device-access-form" ? form : undefined;
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "access-grant" } }) } });
  assert.deepEqual(JSON.parse(JSON.stringify(calls[0])), { type: "airfryer_recipes/access_set", user_id: "u", device_id: "d", allowed: true });
  await panel.onClick({ target: { closest: () => ({ dataset: { action: "access-revoke", user: "u", device: "d" } }) } });
  assert.equal(calls[2].allowed, false);
  let prevented = false;
  panel.onSubmit({ target: { id: "device-access-form" }, preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
});

test("ordinary panel cannot manage permissions and stale admin replies stay hidden", async () => {
  let calls = 0;
  const userPanel = panelWith(async () => { calls++; }, false);
  await userPanel.manageAccess();
  userPanel.render();
  assert.doesNotMatch(userPanel.shadowRoot.innerHTML, /id="device-access"/);
  assert.equal(calls, 0);
  let resolve;
  const adminPanel = panelWith(() => new Promise((done) => { resolve = done; }));
  const task = adminPanel.manageAccess();
  adminPanel.invalidateControls();
  adminPanel._hass.user.is_admin = false;
  resolve({ available: true, users: [{ id: "secret" }], devices: [], grants: [] });
  await task;
  assert.equal(adminPanel.accessData, null);
  assert.doesNotMatch(adminPanel.shadowRoot.innerHTML, /secret/);
});

test("support preview is explicit, private tools stay hidden from ordinary users", async () => {
  const calls = [];
  const panel = panelWith(async req => { calls.push(req); return { diagnostics: { schema_version: 1, library_loaded: true } }; });
  panel.render();
  assert.equal(calls.length, 0);
  assert.match(panel.shadowRoot.innerHTML, /Passwörter, Tokens/);
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /data-action="diagnostics-download"/);
  await panel.supportAction("diagnostics-preview", {});
  assert.equal(calls[0].type, "airfryer_recipes/diagnostics_preview");
  assert.match(panel.shadowRoot.innerHTML, /data-action="diagnostics-download"/);
  assert.match(panel.shadowRoot.innerHTML, /library_loaded/);
  panel._hass.user.is_admin = false;
  panel.render();
  assert.doesNotMatch(panel.shadowRoot.innerHTML, /library_loaded|diagnostics-preview|notifications-load/);
});

test("notification settings escape labels and disabling sends only the chosen sensor", async () => {
  const calls = [];
  const panel = panelWith(async req => { calls.push(req); return { available: true, sources: ['sensor.zone1'], targets: ['mobile_app_phone'], rules: [] }; });
  panel.supportData = { available: true, sources: ['<private>'], targets: ['mobile_app_phone'], rules: [] };
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /&lt;private&gt;/);
  panel.shadowRoot.getElementById = () => ({ values: {} });
  await panel.supportAction("notifications-remove", { dataset: { id: "sensor.zone1" } });
  assert.equal(calls[0].type, "airfryer_recipes/notification_set");
  assert.equal(calls[0].entity_id, "sensor.zone1");
  assert.equal(calls[0].target, "");
  assert.equal(calls[1].type, "airfryer_recipes/notification_settings");
});


test("diagnostic download requests only the reviewed preview and uses a real named URL", async () => {
  const calls = [];
  const panel = panelWith(async req => { calls.push(req); return { url:"/api/airfryer_recipes/diagnostics/token/airfryer-recipes-diagnostics.json?authSig=signed", filename:"airfryer-recipes-diagnostics.json" }; });
  panel.diagnosticPreview = { schema_version: 1, library_loaded: true };
  panel.diagnosticPreviewId = "reviewed-preview";
  await panel.supportAction("diagnostics-download", {});
  assert.equal(calls.length, 1);
  assert.equal(calls[0].type, "airfryer_recipes/diagnostics_download");
  assert.equal(calls[0].preview_id, "reviewed-preview");
  assert.equal(panel.createdElements[0].download, "airfryer-recipes-diagnostics.json");
  assert.match(panel.createdElements[0].href, /\/airfryer-recipes-diagnostics.json\?authSig=/);
  assert.equal(panel.createdElements[0].clicked, true);
});

test('expired diagnostic preview shows relevant feedback without starting a download', async () => {
  const panel = panelWith(async () => { throw { code:'preview_expired' }; });
  panel.diagnosticPreview = { schema_version:1 }; panel.diagnosticPreviewId='old';
  await panel.supportAction('diagnostics-download',{});
  assert.match(panel.error,/Diagnosevorschau ist abgelaufen/);
  assert.equal(panel.createdElements.length,0);
});


test('production recipe library hides all commissioning sections but retains recipes and settings', () => {
 const panel=panelWith(async()=>({}));panel.betaFeatures=false;panel.render();
 assert.doesNotMatch(panel.shadowRoot.innerHTML,/id="batch-test"|id="device-preview"|id="beta-device-test"/);
 assert.match(panel.shadowRoot.innerHTML,/data-action="new"/);
 assert.match(panel.shadowRoot.innerHTML,/notifications-load/);
 panel.betaFeatures=true;panel.render();
 assert.match(panel.shadowRoot.innerHTML,/id="batch-test"/);
});


test('shipped stable version disables beta features without an override', () => {
 const panel=panelWith(async()=>({}));
 delete panel.betaFeatures;
 assert.equal(panel.betaFeatures,false);
 panel.render();
 assert.doesNotMatch(panel.shadowRoot.innerHTML,/id="batch-test"|id="device-preview"|id="beta-device-test"/);
});

test('release channel shows tools only for beta versions', () => {
 for (const [version,expected] of [['0.2.0',false],['0.2.0b1',true],['0.2.0-beta.1',true]]) {
  let Panel;
  vm.runInNewContext(source.replace('"0.2.0"',JSON.stringify(version)).replace(/^export /m,''),{
   HTMLElement:class {},customElements:{get(){},define(name,type){Panel=type;}}
  });
  assert.equal(Panel.betaFeatures,expected);
 }
});
