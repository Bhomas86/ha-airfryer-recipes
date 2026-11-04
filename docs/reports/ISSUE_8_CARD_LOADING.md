# Card missing from the picker — module registration correction

[Deutsch](ISSUE_8_CARD_LOADING.de.md) | [English](ISSUE_8_CARD_LOADING.md)

The owner reported that Airfryer Recipes was missing from the dashboard card picker and confirmed b13 was installed. The screenshot shows Airfryer Control's cards, which belong to the other integration. A duplicate-element loading failure was reproduced offline; the exact browser error on the owner's instance was not collected, and a post-update HA restart was not confirmed.

**Follow-up, 2026-11-02:** The owner subsequently reported the card was still absent on b14. Adding `/api/airfryer_recipes/card.js?v=0.1.0b14` under dashboard Resources as a JavaScript module made it work. The Companion screenshot confirms the card renders with the device graphic, zones, Online status, Piccolinies at 180 °C / 7 minutes and test mode. This accepts manual resource loading/display only, not automatic registration, zone switching, history persistence or a card-originated appliance send. No separate file package is needed. [Automatic dashboard resource correction](ISSUE_8_CARD_RESOURCES.md).

## Reproduced failure and correction

When the recipe panel element already exists, importing another query-versioned copy of `panel.js` throws on its unconditional `customElements.define`. The dependent card module then fails before registering its element or `window.customCards` entry. Earlier interaction tests removed the import and used a registry stub that allowed duplicate definitions, so they did not cover this module-loading failure.

Beta 0.1.0b14 guards the panel element definition and exports the current panel class. The card imports and extends that exported class directly. An existing panel remains registered, while the card uses its current bundled lifecycle rather than inheriting a potentially older registry constructor. Panel/card module URLs and the card's dependency use the same new version. No recipe/history storage, permission, preview or device-send behavior changes.

Four new tests load the **unmodified shipped ES modules together**, through their actual relative import, with a registry that rejects duplicate names/constructors: fresh page, current panel first, legacy panel first, and multiple query versions. They verify the picker entry, editor, current base class, preserved existing panel and absence of duplicate entries. Node imports are tested; browser rendering and HA HTTP delivery are not simulated by these tests.

## Installation and local checks

1. In HACS install **v0.1.0b14** for **Airfryer Recipes**, restart Home Assistant and fully reload/reopen the Companion app/browser. Updating Airfryer Control alone does not update this card.
2. Dashboard → Edit → Add card → search **Airfryer Recipes**. Check the card and recipe panel can both open, in either order. Leave test mode enabled; no appliance transmission is needed to verify visibility.
3. If it is still missing, check Settings → Dashboards → menu → Resources (enable Advanced mode in the user profile if needed). Add the following as a **JavaScript module**, or update an existing entry for this exact card instead of adding a duplicate:

   ```text
   /api/airfryer_recipes/card.js?v=0.1.0b14
   ```

   Reload the app and reopen Add card. This is a fallback for the integration's automatic module loading. Update/remove a manually pinned resource on later upgrades; do not leave older copies alongside the current one.
4. Manual card configuration, after its module is loaded:

   ```yaml
   type: custom:airfryer-recipes-card
   title: Airfryer Küche
   dry_run: true
   ```

If it remains unavailable, record the exact message from the manual card preview and any HA frontend log for `card.js`/`panel.js`. Do not send appliance settings for diagnosis. Native HA/Companion acceptance remains pending.

## Verification

Passed locally: **170 Python tests and 84 frontend tests** (59 panel, 21 card, 4 full-module loading), compilation, documentation links/language pairing and diff formatting. The initial b13 duplicate-element failure was reproduced before the fix. No GitHub Actions; no HACS/Hassfest, Python 3.14, native browser/HA/Companion or new appliance test was run. The existing workflow lists the added module tests only for a future explicitly authorized run.
