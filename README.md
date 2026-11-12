# Airfryer Recipes for Home Assistant

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5?logo=home-assistant)
![HACS](https://img.shields.io/badge/HACS-Compatible-41BDF5)
[![GitHub Downloads](https://img.shields.io/github/downloads/Bhomas86/ha-airfryer-recipes/total)](https://github.com/Bhomas86/ha-airfryer-recipes/releases)
[![GitHub License](https://img.shields.io/github/license/Bhomas86/ha-airfryer-recipes)](https://github.com/Bhomas86/ha-airfryer-recipes/blob/main/LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/Bhomas86/ha-airfryer-recipes)](https://github.com/Bhomas86/ha-airfryer-recipes/releases/latest)
[![GitHub Stars](https://img.shields.io/github/stars/Bhomas86/ha-airfryer-recipes)](https://github.com/Bhomas86/ha-airfryer-recipes/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Bhomas86/ha-airfryer-recipes)](https://github.com/Bhomas86/ha-airfryer-recipes/issues)
[![Sponsor Bhomas86](https://img.shields.io/badge/Sponsor-Bhomas86-EA4AAA?logo=githubsponsors)](https://github.com/sponsors/Bhomas86)

[English](README.md) | [Deutsch](README.de.md)

**Version 0.2.0** manages device-independent air fryer recipes locally in Home Assistant and prepares settings on a supported appliance through [Airfryer Control](https://github.com/misterm2310/airfryer-control). Cooking starts physically at the appliance.

- Recipe library with administrator editing, categories/tags, search, favorites and validated JSON import/export.
- Dashboard card with independent recipe/manual settings per zone, persistent last sent settings and a visual editor.
- Private device artwork, adjustable touch areas and a choice of subtle outlines or invisible touch areas.
- Explicit whole-device grants for ordinary HA users, enforced in the backend. Administrators retain recipe/security management.
- Separate SYNC/MATCH preparation with exact confirmation, fresh inactive-zone checks, one write attempt and no automatic retry or implicit reset.
- Allowlisted diagnostic preview and named download, plus optional Companion completion notices (off by default).
- Complete English/German UI; recipes, grants, favorites, artwork and history persist locally.

## Install and set up

1. Add `https://github.com/Bhomas86/ha-airfryer-recipes` to HACS as a custom **Integration** repository.
2. Install **v0.2.0**, restart Home Assistant and fully reopen the browser/Companion app.
3. Add **Airfryer Recipes** under Settings → Devices & services. Recipe management needs no appliance or cloud credentials.
4. Dashboard → Edit → Add card → **Airfryer Recipes**. No dashboard is created or changed automatically. Stable versions hide commissioning tests and the card test-mode option. Cards use normal confirmed preparation; beta versions expose the test tools again.
5. For ordinary users, explicitly share the entire appliance in the administrator recipe library, then refresh the card.
6. Select recipe/manual values per zone. Sending requires a deliberate click and confirmation of exact values. Start cooking at the appliance.

## Supported device and controller

| Feature | Reviewed scope |
| --- | --- |
| Device preparation | Cosori Turbo Tower Pro Smart **CAF-DC111S-AEU** |
| Single-zone sending and completion notices | Airfryer Control **1.0.3-beta.3**, **1.0.3**, **1.0.4-beta.1** |
| SYNC/MATCH preparation | Airfryer Control **1.0.3** or **1.0.4-beta.1** |
| Home Assistant baseline | **2026.10.0** or newer, with the reviewed controller contract |
| Other devices/controller releases | Recipe management remains available; no unreviewed transmission is enabled |

Airfryer Control is optional for recipe management and owns its existing VeSync connection. Airfryer Recipes stores no additional cloud credentials. Combined preparation uses our own guarded adapter to the reviewed transport internals; no controller modification is required. Other controller versions are deliberately blocked until reviewed.

## Daily use and safety

Set the two zone drafts independently. **SYNC** prepares different durations for a shared finish; **MATCH** explicitly uses zone 1 settings for both zones. Both zones must freshly report idle/off; physically clear prepared programs and combined mode before a new combined preparation. No heating start, software scheduling workaround, automatic command retry or offline replay is requested.

An accepted response means the adapter accepted settings, not that the appliance has independently confirmed them. Inspect the appliance. After an unknown outcome, do not resend: check/clear both zones physically, then explicitly request read-only re-arm. Device safeguards and physical manual start remain in force.

Administrators can configure completion notices per zone and Companion destination. Only an observed fresh cooking→finished report triggers one notice; uncertain/interrupted sequences may intentionally produce none. [Setup and behavior](docs/reports/ISSUE_10_SUPPORT.md).

Diagnostic export uses only allowlisted technical fields, with preview before download. It excludes personal/device IDs, names, network addresses, credentials, recipes and artwork. The named HTTP download retains the exact preview and requires current administrator access. [Acceptance and download behavior](docs/reports/B26_ACCEPTANCE_AND_DOWNLOAD.md).

## Release and validation

[0.2.0 release notes](docs/releases/0.2.0.md) · [Final release gate](docs/reports/RELEASE_0_1_0.md) · [SYNC/MATCH design and acceptance](docs/reports/ISSUE_1_OWN_GUARD.md) · [Requirements](docs/REQUIREMENTS.md) · [Roadmap](docs/ROADMAP.md).

The owner confirmed device preparation, SYNC/MATCH, cancellation without sending, no automatic heating start, persistence, permissions and a real completion notice. The owner accepted the diagnostic filename correction without another phone test; that distinction is documented. Automated tests use mocks, not real appliances. Historical beta notes/reports remain under `docs/releases` and `docs/reports` as historical evidence.

Report issues and verified device compatibility through [GitHub Issues](https://github.com/Bhomas86/ha-airfryer-recipes/issues). This project is independent of Cosori, VeSync and the Airfryer Control developers.

## Support

If you find this project useful, you can [sponsor its further development on GitHub](https://github.com/sponsors/Bhomas86).
