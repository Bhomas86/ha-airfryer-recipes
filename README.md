# Airfryer Recipes for Home Assistant

[English](README.md) | [Deutsch](README.de.md)

A planned Home Assistant custom integration for managing reusable air fryer recipes and sending their settings to supported air fryers through existing Home Assistant integrations.

> **Project status: Early development.** The integration shell from Issue #3 is merged. The recipe backend and WebSocket API are under review in PR #13 and PR #14. This branch adds an administrator recipe panel for Issue #6. Initial configuration succeeded on Home Assistant OS 2026.10.3; recipe operations, permissions and restart persistence still need local verification. The dashboard and device adapter are not implemented.

## Goals

- **Recipe library:** Create, edit, duplicate and delete named recipes.
- **Reusable settings:** Save cooking mode, temperature and duration for each recipe.
- **Device selection:** Choose a compatible air fryer.
- **Cooking zone selection:** Use the same recipe in different baskets/zones where supported.
- **Dashboard card:** Select a device, zone and recipe from dropdowns, review the settings and send them with one action.
- **Local storage:** Keep recipes in Home Assistant rather than in a cloud database.
- **Multilingual interface:** English and German are planned.

## Planned workflow

1. Create a recipe, e.g. **Frozen bread rolls**.
2. Assign a cooking mode, temperature and cooking time.
3. Open the dashboard card.
4. Choose the air fryer, cooking zone and saved recipe.
5. Review the settings and explicitly send them to the device.
6. Start cooking **at the appliance** if manual confirmation is required.

The recipe is independent of the cooking zone; a zone is selected when sending.

## Integration architecture

The project is intended to manage recipes separately from device communication. Initial development targets compatibility with the community integration [Airfryer Control](https://github.com/misterm2310/airfryer-control), which communicates with supported air fryers via VeSync.

The first target device is the **Cosori Turbo Tower Pro Smart (CAF-DC111S-AEU)**. Basic transmission of temperature and cooking time to its lower zone has been tested using **Airfryer Control**, **not this project**. Compatibility with other models, commands and cooking programs still requires verification.

## Planned milestones

- [x] Custom integration skeleton and configuration flow code ([Issue #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3); setup confirmed on HA 2026.10.3)
- [ ] Persistent, validated recipe storage ([Issue #4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4); a recipe and personal favorite survived a local restart, further acceptance pending)
- [ ] Recipe management interface (code in the Issue #6 branch; creation confirmed on a phone, further acceptance pending)
- [ ] Lovelace dashboard card
- [ ] Adapter for Airfryer Control
- [ ] Device/zone compatibility and error handling
- [ ] Automated tests, HACS metadata and release packaging
- [ ] English and German translations

## Installation

**No fully tested release is available yet.** Setup, recipe creation, and persistence of a recipe and personal favorite across a restart were confirmed on Home Assistant 2026.10.3. Other recipe workflows and permissions still require local testing. Do not assume stable use before the first verified release.

The setup flow requires no device, cloud credentials or network access. The administrator recipe panel is being tested in Issue #6; the full device onboarding wizard follows later.

## Safety and privacy

- Sending settings must not silently start a heating cycle.
- A device's own safety restrictions and required manual start confirmation must be respected.
- Do not commit VeSync credentials, access tokens, device identifiers or personal configuration data.
- Stored recipes are intended to remain local to the user's Home Assistant instance.

## Contributing

Feedback, bug reports and tested device compatibility details are welcome via [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues).

This project is independent of Cosori, VeSync and the Airfryer Control developers.
