// Local Home Assistant custom panel. All mutations go through the authenticated API.
const WORDS = {
  en: {
    title: "Recipe library", subtitle: "Manage recipes independently of any appliance.",
    search: "Search recipes", all: "All categories", new: "New recipe", import: "Import JSON",
    export: "Export JSON", empty: "No recipes found.", loading: "Loading recipes…",
    edit: "Edit", copy: "Duplicate", remove: "Delete", name: "Name", description: "Description",
    category: "Category", tags: "Tags (comma-separated)", program: "Program",
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
    phases: "Cooking phase", refresh: "Refresh", devicesNote: "Device controls are not available in this panel.",
    sharedFavorite: "Shared favorite", myFavorite: "My favorite", allFavorites: "All recipes",
    onlyMine: "My favorites", onlyShared: "Shared favorites",
    sample: "Create sample recipe", sampleConfirm: "Create one sample recipe?",
    sampleName: "Frozen bread rolls", sampleDescription: "Example recipe; no appliance is connected.",
  },
  de: {
    title: "Rezeptbibliothek", subtitle: "Rezepte unabhängig von einem Gerät verwalten.",
    search: "Rezepte suchen", all: "Alle Kategorien", new: "Neues Rezept", import: "JSON importieren",
    export: "JSON exportieren", empty: "Keine Rezepte gefunden.", loading: "Rezepte werden geladen…",
    edit: "Bearbeiten", copy: "Kopieren", remove: "Löschen", name: "Name", description: "Beschreibung",
    category: "Kategorie", tags: "Tags (durch Komma getrennt)", program: "Programm",
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
    phases: "Garphase", refresh: "Aktualisieren", devicesNote: "Gerätesteuerung ist in dieser Ansicht nicht verfügbar.",
    sharedFavorite: "Gemeinsamer Favorit", myFavorite: "Mein Favorit", allFavorites: "Alle Rezepte",
    onlyMine: "Meine Favoriten", onlyShared: "Gemeinsame Favoriten",
    sample: "Beispielrezept anlegen", sampleConfirm: "Ein Beispielrezept anlegen?",
    sampleName: "Tiefkühlbrötchen", sampleDescription: "Beispielrezept; kein Gerät ist verbunden.",
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
    } catch (error) {
      this.showError(error);
    } finally {
      this.busy = false;
      this.render();
    }
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

  render() {
    if (!this.shadowRoot) return;
    const t = this.words;
    const categories = [...new Set(this.recipes.map((recipe) => recipe.category).filter(Boolean))].sort();
    const selected = this.editor;
    const phase = selected?.phases?.[0] || {};
    const multiple = selected?.phases?.length > 1;
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;box-sizing:border-box;color:var(--primary-text-color);background:var(--primary-background-color);min-height:100%;font:inherit}
        *{box-sizing:border-box}main{max-width:1100px;margin:auto;padding:20px}h1{margin:0 0 6px;font-size:1.8rem}h2{font-size:1.25rem}
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
        @media(max-width:600px){main{padding:14px}.grid{grid-template-columns:1fr}.toolbar>*{flex:1 1 100%}.actions button{flex:1 1 auto}}
      </style>
      <main>
        <h1>${t.title}</h1><p class="muted">${t.subtitle}</p>
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
          <div><label for="recipe-category">${t.category}</label><input id="recipe-category" name="category" maxlength="64" value="${escapeHtml(selected.category)}"></div></div>
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
    } else if (event.target.id === "favorite-filter") {
      this.favoriteFilter = event.target.value;
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
    if (!button || this.busy) return;
    const type = button.dataset.action;
    const recipe = this.recipes.find((item) => item.id === button.dataset.id);
    const t = this.words;
    if (type === "refresh") return this.load();
    if (!this.admin) return;
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
        const url = URL.createObjectURL(new Blob([result.payload], { type: "application/json" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = "airfryer-recipes.json";
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
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
    if (event.target.id !== "editor") return;
    event.preventDefault();
    if (!this.admin || this.editor?.phases?.length > 1) return;
    const form = new FormData(event.target);
    const recipe = {
      name: String(form.get("name") || "").trim(),
      description: String(form.get("description") || "").trim(),
      category: String(form.get("category") || "").trim(),
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
}

customElements.define("airfryer-recipes-panel", AirfryerRecipesPanel);
