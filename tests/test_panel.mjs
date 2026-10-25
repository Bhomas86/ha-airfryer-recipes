import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/panel.js", import.meta.url), "utf8");

function panelWith(api, admin = true) {
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
    confirm: () => true,
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
    connectivity: "reported_online", freshness: "unverified",
    zones: [{ zone_id: 2, status: "cooking" }],
  }] };
  panel.selectedDeviceId = "ha-device";
  panel.selectedZoneId = "2";
  panel.previewRecipeId = "recipe-one";
  panel.render();
  assert.match(panel.shadowRoot.innerHTML, /Geräte-Testvorschau/);
  assert.match(panel.shadowRoot.innerHTML, /Küche &lt;oben&gt;/);
  assert.match(panel.shadowRoot.innerHTML, /Fach 2 · Gart/);
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
