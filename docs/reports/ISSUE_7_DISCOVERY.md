# Issue #7 – Read-only discovery and send-contract review

[Deutsch](ISSUE_7_DISCOVERY.de.md) | [English](ISSUE_7_DISCOVERY.md)

## Outcome and scope

PR #16 promoted storage, the API and manually accepted recipe management to `main` (`2ab457f`). This first part of Issue #7 adds only read-only discovery through `airfryer_recipes/devices`. Issue #7 remains open. The coordinator, dry-run preview, live transmission and program selection remain unimplemented.

Model check: GPT-6 Sol – High for the multi-module adapter/safety review; work paused after the recommendation and the owner resumed it after switching models. A higher model tier is not currently necessary.

## Safety-related upstream findings

Reviewed source: [Airfryer Control, commit 5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee](https://github.com/misterm2310/airfryer-control/tree/5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee), manifest version 1.0.1. Only source code from GitHub was read; no upstream function was imported or executed.

1. `services.py::_program` invokes `senden.py::async_send`, which tries multiple command variants after rejection, including a variant with `workChamber=0`. A single HA service call therefore does not guarantee a single device-control call. This conflicts with the project's no-auto-retry rule. This service is not connected.
2. `FryerData` has no successful-report timestamp per device/zone. A globally successful coordinator refresh can hide individual device failures; error paths can retain old states. HA entity timestamps therefore do not prove fresh device telemetry.
3. `sensor.py::ZONE_SENSORS` substitutes “bereit” (idle) for an unreported zone. That value must not authorize sending. Our discovery uses only zone reports actually present in runtime data.
4. `const.py` contains global TwinFry programs and limits, rather than a verified list for every model. These are not adopted as confirmed CAF-DC111S-AEU capabilities.

Upstream documents `readyStart=true` as preparation and `false` as immediate start on a TwinFry. That source-code statement does not replace local safety verification for all models. SYNC/MATCH, raw commands and experimental send functions remain outside this package.

## Implementation

- Join HA device-registry entries to matching configuration entries and loaded Airfryer Control runtime data; no VeSync query or forced refresh.
- Only explicitly reported zones; unknown states remain unknown. Offline or erroneous data is not represented as safely ready.
- Response: HA device ID, name, model, reported connectivity, zone states, `freshness=unverified`, `reported_at=null`, an empty program list and disabled control capabilities. “Reported online” does not mean a verified current connection.
- Cloud identifiers, credentials, raw data and error text are excluded. The authenticated API is not a diagnostic export.
- Discovery is administrator-only for now. Regular users are denied, including with a forged `is_admin`. Device-specific permissions for later regular-user control remain to be implemented.
- Requests are rejected when the recipe integration is unloaded. Missing or incompatible optional adapters do not prevent recipe management. No new storage files or migrations.
- No send API or device-control calls. This does not yet implement the planned server-side dry-run mode.

## Verification actually performed

68 Python offline tests and 10 frontend tests passed. New tests cover both zones, absent zone reports, unknown models/states, offline/error data, ambiguous ownership, disabled devices, incompatible runtime data, data minimization and API authorization including unload. The existing storage-error traceback is an expected negative test. Python compilation and `git diff --check` are checked before publication; HACS, Hassfest and Python 3.12/3.14 through PR Actions.

Local Home Assistant: **NOT TESTED** for this new API. Earlier recipe-management acceptance still applies only to the reviewed Issue #6 revision.

## Local acceptance and next decision

After a backup, install the entire integration directory from this feature branch and restart HA. Reopen recipe management without Airfryer Control. An administrator can read `{"id":1,"type":"airfryer_recipes/devices"}` through an authenticated HA WebSocket connection; without the adapter an empty list is expected. With the adapter, compare model/zones against its display. When the appliance is off, even an old reported state must never grant send permission. A regular user must receive `unauthorized`. This API has no new phone UI yet; acceptance can wait until that UI is implemented. Do not execute device commands for this package.

Before live transmission, a verifiable adapter contract is needed: exactly one control call without variant fallback, reliable successful-report timestamps per device/zone, confirmed model-specific programs/limits and proven preparation without heater start. Then implement the coordinator, user/device permissions, bound single-use confirmations, race-condition tests and server-side dry run. Recommended model for that follow-up: GPT-6 Sol – High; pause beforehand as agreed.
