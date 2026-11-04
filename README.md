# Airfryer Recipes for Home Assistant

[English](README.md) | [Deutsch](README.de.md)

**[b23: Clear program names](docs/releases/0.1.0b23.md).** Remove the program-dropdown provenance/verification suffixes in the dashboard, recipe editor and preview. Missing programs remain marked. Owner confirms the b22 save/restart check.

**[b22: Final review and verified storage](docs/releases/0.1.0b22.md).** Fix favorite accumulation and false save acknowledgements after silent HA Store failures. Python 3.12/3.14 and frontend checks passed. [Review, acceptance and remaining checks](docs/reports/FINAL_REVIEW.md).

**[b21: Controller beta, full temperatures and Proof](docs/releases/0.1.0b21.md).** Requires exactly Airfryer Control 1.0.3-beta.3 for supervised sending. The large run now checks 44 settings, including all temperature bounds and Proof 30/31 °C. B is now first/default in the card editor; existing choices are preserved.

**[b20: Choose A or B](docs/releases/0.1.0b20.md).** Card editor → Zone selection on the image: subtle outline or invisible touch areas. In B, saved zones remain tappable on the photo; positioning rectangles stay visible in the device designer.

**[b19: Appearance updates immediately](docs/releases/0.1.0b19.md).** After Save appearance, cards in the same page reread the saved artwork without a page reload. Saving on b18 is owner-confirmed after reloading; new native refresh acceptance remains pending.

**[b18: Device artwork](docs/releases/0.1.0b18.md).** Admin card editor → Customize Airfryer: neutral gallery, private images and relative zone boxes.

**[b17: Display options](docs/releases/0.1.0b17.md).** Card size, graphic size and status/history visibility in the visual editor. Three local permission checks passed.

**[b16: Share an entire device](docs/reports/ISSUE_8_DEVICE_ACCESS.md).** Admins explicitly grant a whole device to an ordinary HA user, including all zones and available programs. No grants by default; recipe/security management stays admin-only. Only the current beta remains published.

A Home Assistant custom integration for managing reusable air fryer recipes and sending their settings to supported air fryers through existing Home Assistant integrations.

> **Project status: Test beta 0.1.0b23.** Basic card sends to both zones, physical-reset reuse, per-zone history and restart persistence are owner-confirmed. Whole-device user grants are implemented with backend enforcement; three local grant checks passed; both artwork styles are owner-confirmed; the 44-step reported-value sequence and Proof recipe workflow are owner-confirmed. New cards default to test mode; live transmission remains supervised beta. The focused b22 save/restart check is owner-confirmed; official HACS/Hassfest validation remains pending before a candidate.

**[Add the dashboard card](docs/reports/ISSUE_8_DASHBOARD_CARD.md):** Restart HA after the update, fully reopen the app, then Dashboard → Edit → Add card → Airfryer Recipes. No dashboard is changed automatically. Start with test mode enabled.

**[Local acceptance: six programs passed on both zones](docs/reports/ISSUE_7_LOCAL_ACCEPTANCE.md).** Evidence covers the documented nominal settings, not general approval of all limits.

**New test beta 0.1.0b5:** Separate supervised appliance test with selected recipe/manual values for CAF-DC111S-AEU and exactly Airfryer Control 1.0.2-beta.1. A single transmission requires explicit confirmation; normal device control remains blocked. [Installation and test](docs/releases/0.1.0b5.md).

Test preparation now requests a new status report itself. [Freshness blocking correction](docs/releases/0.1.0b5.md).

New: supervised selected recipe/manual settings for all six reported programs. [Extended test plan](docs/reports/BETA_0_1_0B5_TEST_PLAN.md). No GitHub Actions for this update.

**New: [Guided run with one confirmation](docs/releases/0.1.0b6.md).** 132 Python/29 frontend tests passed locally; no GitHub Actions.

**[New: Re-arm after physical reset](docs/releases/0.1.0b7.md).** 138 Python/31 frontend tests passed locally; no GitHub Actions.

**[New: End zone settings before program changes](docs/releases/0.1.0b8.md).** 145 Python/32 frontend tests passed locally; no GitHub Actions.

**[New: Transfer selected single-test settings and correct Dry sample](docs/releases/0.1.0b9.md).** 147 Python/36 frontend tests passed locally; no GitHub Actions.

**[New: Turbo Tower temperature profile and adapter comparison](docs/releases/0.1.0b10.md).** 150 Python/38 frontend tests passed locally; no GitHub Actions.

**[New: Recipe confirmation and connection changes](docs/releases/0.1.0b11.md).** 163 Python/50 frontend tests passed locally; no GitHub Actions. [Seven focused appliance checks](docs/reports/ISSUE_7_RECIPE_LIFECYCLE.md).

**[New: Program selection in the recipe editor](docs/releases/0.1.0b12.md).** 164 Python/59 frontend tests passed locally; no GitHub Actions. [Explicitly correct an existing recipe](docs/reports/ISSUE_7_EDITOR_PROGRAM_PICKER.md).

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
- [x] Initial Lovelace dashboard card and visual editor (supervised beta; ordinary users need whole-device grants)
- [ ] SYNC/MATCH and stable release

Current beta: 212 Python tests and 104 frontend tests passed locally. No GitHub Actions, HACS/Hassfest or Python 3.14 runs for this update. Basic card sends/history/restart passed local acceptance; new native permissions acceptance remains pending. [Dashboard behavior and checks](docs/reports/ISSUE_8_DASHBOARD_CARD.md). Whole-device permissions are implemented; personalization remains planned.

## Installation

**Prerelease, not a stable release.** Create a Home Assistant backup first. Add this repository as a custom HACS integration repository, show prereleases and select `v0.1.0b23` using “Redownload”. Restart Home Assistant and fully reopen the Companion app.

Recipe management works without Airfryer Control and requires no cloud credentials. Install Airfryer Control `1.0.2-beta.1` or newer for the extended device preview. It executes no control commands. For CAF-DC111S-AEU, the six reported programs and limits remain estimated/unverified; `proof` is missing from the upstream contract. Normal transmission remains blocked; the separate supervised beta test requires exactly Airfryer Control 1.0.2-beta.1.

Details: [release notes](docs/releases/0.1.0b23.md), [dashboard setup/checks](docs/reports/ISSUE_8_DASHBOARD_CARD.md), [local test checklist](docs/LOCAL_TEST_CHECKLIST.md) and [roadmap](docs/ROADMAP.md).

## Safety and privacy

- Sending settings must not silently start a heating cycle.
- A device's own safety restrictions and required manual start confirmation must be respected.
- Do not commit VeSync credentials, access tokens, device identifiers or personal configuration data.
- Stored recipes are intended to remain local to the user's Home Assistant instance.

## Contributing

Feedback, bug reports and tested device compatibility details are welcome via [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues).

This project is independent of Cosori, VeSync and the Airfryer Control developers.
