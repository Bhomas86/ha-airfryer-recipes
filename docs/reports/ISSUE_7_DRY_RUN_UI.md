# Issue #7 – Phone UI for device dry-run preview

[Deutsch](ISSUE_7_DRY_RUN_UI.de.md) | [English](ISSUE_7_DRY_RUN_UI.md)

## Implementation

This package builds on the server-enforced dry-run preview merged in PR #18. The administrator recipe panel now contains a dedicated “Device test preview” section. It reads only the authenticated `airfryer_recipes/devices` and `airfryer_recipes/prepare_send` commands.

Administrators can choose a reported air fryer and an actually reported zone. Starting with Airfryer Control `1.0.2-beta.1`, the backend additionally calls the public, read-only `airfryer_control.faehigkeiten` service. Only allowlisted programs, ranges, suggestions, provenance status, connection, report time and revision reach the response. Account data, cloud device identifiers, raw data and unknown fields are discarded. Actually reported zones still come from runtime state and are not invented from the capability list.

Settings come from an existing single-phase recipe or manual program, temperature and minute inputs. Reported programs appear in a dropdown that labels limits as confirmed or estimated and sending as confirmed or unverified. A saved recipe whose program is not reported remains unchanged and is explicitly marked as unreported; it is never silently replaced. If the new read-only service is absent, free-text program input remains as a compatibility fallback. Temperature follows the HA unit for display and is converted back to Celsius before the request. The response presents unchanged desired settings, zone state and clearly translated blocking reasons.

The UI deliberately contains no send or confirmation action. Before and after preview it states that no device command was executed. The client sends only the HA device ID, zone ID and three desired values; it sends no live, administrator, raw-command or adapter parameters. The backend remains authoritative and always returns `live_send_enabled=false` and `transmitted=false`.

Device errors remain separate from recipe management. Missing, outdated or incompatible Airfryer Control and a failed capability request prevent neither recipe listing nor favorites. A regular user cannot see the administrator panel or this section; the backend authorization from PR #17/#18 remains in force as well.

Model check: GPT-5.6 Sol – High was recommended for this bounded frontend and test package. The owner confirmed the model switch before work began.

## Automated verification

78 Python offline tests and 15 frontend tests passed. The five device-related frontend tests verify that:

- recipe management remains usable when device discovery fails,
- only actually reported zones and safely escaped device values are rendered,
- preview sends no live-control fields and displays “nothing transmitted”,
- an unreported program from a saved recipe remains unchanged and visibly marked,
- manual Fahrenheit values convert back to Celsius,
- a vanished target produces a clear message inside the device section,
- regular users trigger no device discovery and cannot see the section.

Python compilation and `git diff --check` passed as well. HACS, Hassfest and Python 3.12/3.14 then run in PR Actions. Cloud Codex and CI had no access to Home Assistant, VeSync or a real appliance.

## Local phone acceptance

After a backup, install the complete `custom_components/airfryer_recipes` directory from this branch, restart Home Assistant, fully close the Companion App and reopen it.

1. Without loaded Airfryer Control, “Airfryer Control is not loaded” must appear. Recipes, search, favorites, import and export must remain functional.
2. With Airfryer Control `1.0.2-beta.1` or newer, select “Refresh devices”. Compare displayed name, model and only actually reported zones with Airfryer Control. A report time may be shown but does not grant send permission.
3. Under “Manual values”, inspect the program dropdown. For CAF-DC111S-AEU, programs currently reported by Airfryer Control must be labeled as estimated and sending unverified. `proof` is currently absent from the upstream contract and must not be invented.
4. Select an existing recipe. Program, temperature and time must be copied and displayed read-only. If its program is unreported, it must remain marked as such and must not change to the first list entry.
5. Select “Check test preview”. Expect “Nothing was transmitted to the appliance”, unchanged values and blockers for freshness and unconfirmed model limits. Nothing may change on the appliance.
6. Check manual values; in a Fahrenheit user session, display and returned values must convert correctly.
7. If safely possible, make the appliance or zone disappear from the upstream display between selection and preview, then check again. Expect a vanished-target message, no retry and no device change.
8. Check German and English user languages. A regular user must remain unable to open the administrator page.

If anything changes on the air fryer, mark the test **FAILED**, stop further previews and preserve Home Assistant logs. Live transmission, active-zone changes, SYNC/MATCH and heater start are not tested. Local acceptance remains **NOT TESTED** until installation.

## Limits and next step

Airfryer Control still treats CAF-DC111S-AEU as an unknown model; all six supplied programs and limits are therefore estimated/unverified. The appliance's visible `proof` program is absent from the beta contract. Preview is not device compatibility confirmation. Live transmission stays blocked until local contract acceptance and sufficient model-specific evidence exist.
