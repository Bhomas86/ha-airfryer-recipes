// Evaluate the shipped ES modules together, including browser-like duplicate
// element checks. The interaction tests separately exercise DOM/HA behavior.
import assert from "node:assert/strict";
import { cpSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import test from "node:test";

for (const mode of ["fresh", "panel-first", "legacy-panel-first", "multiple-query-versions"]) {
  await test(`shipped module graph registers the picker entry: ${mode}`, async () => {
    const directory = mkdtempSync(join(tmpdir(), "airfryer-module-test-"));
    const globals = ["HTMLElement", "window", "customElements"];
    const descriptors = globals.map((key) => Object.getOwnPropertyDescriptor(globalThis, key));
    try {
      for (const name of ["panel.js", "card.js", "personalization.js"]) cpSync(new URL(`../custom_components/airfryer_recipes/frontend/${name}`, import.meta.url), join(directory, name));
      writeFileSync(join(directory, "package.json"), JSON.stringify({ type: "module" }));
      const base = pathToFileURL(`${directory}/`).href;
      const elements = new Map();
      globalThis.HTMLElement = class {};
      globalThis.window = {};
      globalThis.customElements = {
        get: (name) => elements.get(name),
        define(name, constructor) {
          if (elements.has(name) || [...elements.values()].includes(constructor)) throw new Error("Already defined: " + name);
          elements.set(name, constructor);
        },
      };
      let existingPanel;
      if (mode === "legacy-panel-first") {
        existingPanel = class LegacyPanel extends HTMLElement {};
        customElements.define("airfryer-recipes-panel", existingPanel);
      } else if (mode !== "fresh") {
        const query = mode === "panel-first" ? "0.1.0b20" : "previous";
        await import(new URL("panel.js?v=" + query, base));
        existingPanel = customElements.get("airfryer-recipes-panel");
      }
      await import(new URL("card.js?v=0.1.0b20", base));
      const { AirfryerRecipesPanel } = await import(new URL("panel.js?v=0.1.0b20", base));
      await import(new URL("personalization.js?v=0.1.0b20", base));
      assert.ok(customElements.get("airfryer-device-designer"));
      const Card = customElements.get("airfryer-recipes-card");
      assert.ok(Card);
      assert.ok(customElements.get("airfryer-recipes-card-editor"));
      assert.equal(Object.getPrototypeOf(Card.prototype), AirfryerRecipesPanel.prototype);
      if (existingPanel) assert.equal(customElements.get("airfryer-recipes-panel"), existingPanel);
      assert.equal(window.customCards.length, 1);
      assert.equal(window.customCards[0].type, "airfryer-recipes-card");
      assert.equal(window.customCards[0].name, "Airfryer Recipes");
      if (mode === "multiple-query-versions") {
        await import(new URL("card.js?v=manual-resource", base));
        await import(new URL("panel.js?v=another-panel-resource", base));
        assert.equal(customElements.get("airfryer-recipes-card"), Card);
        assert.equal(window.customCards.length, 1);
      }
    } finally {
      globals.forEach((key, index) => {
        if (descriptors[index]) Object.defineProperty(globalThis, key, descriptors[index]);
        else delete globalThis[key];
      });
      rmSync(directory, { recursive: true, force: true });
    }
  });
}
