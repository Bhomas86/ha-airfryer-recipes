# Airfryer Recipes for Home Assistant

[English](README.md) | [Deutsch](README.de.md)

A Home Assistant custom integration for managing reusable air fryer recipes and sending their settings to supported air fryers through existing Home Assistant integrations.

> **Project status: Test beta 0.1.0b4 (as of 2026-10-30).** Recipe management, local storage, authenticated API and read-only device preview are implemented. Phone acceptance of the 0.1.0b2 preview passed on 2026-10-25. Version 0.1.0b4 adds a separate supervised initial test with real settings transmission; its appliance acceptance is pending. Normal device control, the dashboard card and SYNC/MATCH remain pending.

**New test beta 0.1.0b4:** Separate supervised appliance test with fixed values for CAF-DC111S-AEU and exactly Airfryer Control 1.0.2-beta.1. A single transmission requires explicit confirmation; normal device control remains blocked. [Installation and test](docs/releases/0.1.0b4.md).

Test preparation now requests a new status report itself. [Freshness blocking correction](docs/releases/0.1.0b4.md).

## Goals

- **Recipe library:** Create, edit, duplicate and delete named recipes.
- **Reusable settings:** Save cooking mode, temperature and duration for each recipe.
- **Device selection:** Choose a compatible air fryer.
- **Cooking zone selection:** Use the same recipe in different baskets/zones where supported.
- **Dashboard card:** Select a device, zone and recipe from dropdowns, review the settings and send them with one action.
- **Local storage:** Keep recipes in Home Assistant rather than in a cloud database.
- **Multilingual interface:** English and German are supported.

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

## Development status

- [x] Home Assistant setup and HACS metadata
- [x] Versioned local recipe storage and authenticated API
- [x] Administrator recipe management with categories, search, favorites and JSON import/export
- [x] Read-only device/zone discovery and server-enforced dry-run preview
- [x] English and German interface
- [x] HACS prerelease 0.1.0b2 and documented phone acceptance
- [ ] Verified model limits and safe live transmission
- [ ] Lovelace dashboard card and card editor
- [ ] SYNC/MATCH and stable release

Last documented results: 78 Python offline tests and 15 frontend tests passed; HACS, Hassfest and Python 3.12/3.14 passed in PR #19. See the [acceptance report](docs/reports/ISSUE_7_DRY_RUN_UI.md).

## Installation

**Prerelease, not a stable release.** Create a Home Assistant backup first. Add this repository as a custom HACS integration repository, show prereleases and select `v0.1.0b4` using “Redownload”. Restart Home Assistant and fully reopen the Companion app.

Recipe management works without Airfryer Control and requires no cloud credentials. Install Airfryer Control `1.0.2-beta.1` or newer for the extended device preview. It executes no control commands. For CAF-DC111S-AEU, the six reported programs and limits remain estimated/unverified; `proof` is missing from the upstream contract. Normal transmission remains blocked; the separate supervised beta test requires exactly Airfryer Control 1.0.2-beta.1.

Details: [release notes](docs/releases/0.1.0b4.md), [local test checklist](docs/LOCAL_TEST_CHECKLIST.md) and [roadmap](docs/ROADMAP.md).

## Safety and privacy

- Sending settings must not silently start a heating cycle.
- A device's own safety restrictions and required manual start confirmation must be respected.
- Do not commit VeSync credentials, access tokens, device identifiers or personal configuration data.
- Stored recipes are intended to remain local to the user's Home Assistant instance.

## Contributing

Feedback, bug reports and tested device compatibility details are welcome via [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues).

This project is independent of Cosori, VeSync and the Airfryer Control developers.
