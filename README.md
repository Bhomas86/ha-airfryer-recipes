# Airfryer Recipes for Home Assistant

[English](README.md) | [Deutsch](README.de.md)

A planned Home Assistant custom integration for managing reusable air fryer recipes and sending their settings to supported air fryers through existing Home Assistant integrations.

> **Project status: Early development / planning.** Recipe management, dashboard controls and HACS installation are **not implemented yet**. This repository currently contains the project documentation.

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

- [ ] Custom integration skeleton and configuration flow
- [ ] Persistent, validated recipe storage
- [ ] Recipe management interface
- [ ] Lovelace dashboard card
- [ ] Adapter for Airfryer Control
- [ ] Device/zone compatibility and error handling
- [ ] Automated tests, HACS metadata and release packaging
- [ ] English and German translations

## Installation

**Not available yet.** Do not add this repository to HACS until the first installable release is published. Once implemented, installation instructions will be provided here.

## Safety and privacy

- Sending settings must not silently start a heating cycle.
- A device's own safety restrictions and required manual start confirmation must be respected.
- Do not commit VeSync credentials, access tokens, device identifiers or personal configuration data.
- Stored recipes are intended to remain local to the user's Home Assistant instance.

## Contributing

Feedback, bug reports and tested device compatibility details are welcome via [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues).

This project is independent of Cosori, VeSync and the Airfryer Control developers.
