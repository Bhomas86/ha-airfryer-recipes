# Targeted zone ending before program changes

[Deutsch](ISSUE_7_ZONE_RESET.de.md) | [English](ISSUE_7_ZONE_RESET.md)

The owner reported a successful Roast display after manual clearing and identified existing global and per-zone HA controls for ending. Reviewed upstream f43a9bf8 confirms ZoneSwitch.async_turn_off calls async_end with that zone; turning on would send settings. Beta uses only switch.turn_off, never toggle/turn_on or the global button.

Resolve both switches from device/entity registries: selected device, loaded upstream config entry, unique reviewed ZoneSwitch identifier, zone 1 or 2, enabled and available. No personal entity names/IDs are hardcoded or published. Missing or ambiguous controls prevent offering a sequence requiring resets.

Before each program change, verify fresh own prepared values and unchanged identity. End zone 1 once through the public HA service; only after a new idle report with zone 2 unchanged, end zone 2. Both must then report freshly idle/off before the next setting. Active, unknown, changed or foreign prepared states stop execution. Errors, timeouts or absent readback prevent subsequent reset/settings calls. Public reset calls have a 20-second timeout; Airfryer Recipes does not retry them.

The once-confirmed list displays resets alongside twelve ordinary settings. Six programs produce five changes with ten turn_off calls. Final prepared settings remain for physical inspection and owner cancellation at the appliance. Started runs now last at most twenty minutes to accommodate extra reads. Stop, connection binding, single-use nonces and explicit re-arming without HA restart remain.

Public upstream async_end uses its normal API authentication and may internally retry authentication failures. The settings service's single wire-level attempt guarantee therefore does not apply to these owner-identified reset controls. Our integration calls each zone service once, bypasses no private APIs and checks reported state afterward. Physical buttons or other apps can change state after validation; the owner remains beside the appliance for explicitly supervised acceptance. No heating start is requested.

Passed locally: 145 Python tests, 32 frontend tests, compilation and git diff --check. New checks cover the complete sequence with exactly ten targeted turn_off calls, no retry on reset failure, no second reset/settings after mismatched readback or stop, no plan with missing controls, unique registry ownership and visible reset consent. No GitHub Actions, HACS/Hassfest, Python 3.14 or real HA/appliance tests.

## Repeat acceptance

Back up, install v0.1.0b8, restart HA and fully reopen the app. Retain exactly Airfryer Control 1.0.2-beta.1. Cancel prepared programs physically and use the device re-arm check if still blocked. Both zones closed and idle/off, Celsius, SYNC/MATCH off. Confirm the list including ending actions once. Remain beside the empty appliance; do not press Start. Observe especially the transition after step 2: both own Air Fry preparations must be ended before Roast is sent to zone 1. Stop on errors/heating/wrong zones and report last step/guidance. Real automatic-reset acceptance: NOT TESTED.
