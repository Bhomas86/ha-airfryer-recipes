import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/panel.js", import.meta.url), "utf8");

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
    customElements: { define(name, type) { assert.equal(name, "airfryer-recipes-panel"); Panel = type; } },
    confirm: confirmDialog,
    prompt: () => "Copy",
    setTimeout,
    URL,
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
  vm.runInNewContext(source, context);
  const panel = new Panel();
  panel._hass = { language: "de", user: { is_admin: admin }, callWS: api };
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
  assert.match(panel.shadowRoot.innerHTML, /170 °C, 1 minute/);
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
  assert.equal(calls.length, 0);
});

test("unsupported program rejection remains visible and enables no confirmation", async () => {
  const panel = betaPanel(async () => { throw { code: "beta_test_blocked", message: "program_unsupported" }; });
  await panel.prepareSelectedBeta({ values: { program: "proof", temperature_c: "35", duration_minutes: "7" } });
  assert.equal(panel.betaTest, null);
  assert.match(panel.betaMessage, /Programm wurde nicht ersetzt/);
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
  assert.match(panel.shadowRoot.innerHTML, /Heißluft-Frittieren · geschätzt · Senden ungeprüft/);
  assert.match(panel.shadowRoot.innerHTML, /Backen · bestätigt · Senden bestätigt/);
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
  assert.match(panel.shadowRoot.innerHTML, /Air Fry · estimated · sending unverified/);
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
