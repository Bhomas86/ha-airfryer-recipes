import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../custom_components/airfryer_recipes/frontend/panel.js", import.meta.url), "utf8");

function panelWith(api, admin = true) {
  let Panel;
  const context = {
    HTMLElement: class {
      attachShadow() {
        this.shadowRoot = { addEventListener() {}, innerHTML: "", getElementById() {} };
        return this.shadowRoot;
      }
    },
    customElements: { define(name, type) { assert.equal(name, "airfryer-recipes-panel"); Panel = type; } },
    confirm: () => true,
    prompt: () => "Copy",
    setTimeout,
    URL,
    Blob,
    document: { createElement: () => ({ click() {} }) },
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
  return panel;
}

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
      name: "Bread rolls", description: "", category: "Breakfast", tags: "quick, frozen",
      program: "airfry", temperature_c: "180", duration_minutes: "8", favorite: "on",
    } },
  });
  assert.equal(calls[0].type, "airfryer_recipes/create");
  assert.equal(calls[0].recipe.favorite, true);
  assert.deepEqual([...calls[0].recipe.tags], ["quick", "frozen"]);
  assert.equal(calls[0].recipe.phases[0].temperature_c, 180);
  assert.equal(calls[0].recipe.device_id, undefined);
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
