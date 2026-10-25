# Issue #7 – Dry-run preview and required send contract

[Deutsch](ISSUE_7_COMMAND_CONTRACT.de.md) | [English](ISSUE_7_COMMAND_CONTRACT.md)

## Outcome

PR #17 is merged. This follow-up adds `airfryer_recipes/prepare_send` as a server-enforced dry-run preview for administrators only. It validates a desired program, Celsius temperature and minutes against device-independent recipe bounds, rereads the target through read-only discovery and returns values and blocking reasons. It has no control calls, queue or live-mode switch. This is an initial coordinator stage; Issue #7 is not yet fully implemented.

Model check: GPT-6 Sol – High was recommended before this follow-up, work paused and the owner then resumed it. This tier remains suitable for the adapter/async review.

## Additional upstream finding

The reviewed revision remains [5a3c530](https://github.com/misterm2310/airfryer-control/tree/5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee). In `core/api.py`, `bypass_v2()` uses `_with_relogin()`, which logs in again and repeats the same request following an authentication error. Even `async_send(..., only=...)` with a fixed variant therefore does not guarantee a single transmission. Private `_post` methods and upstream credentials are not used as a workaround.

Together with the [earlier findings](ISSUE_7_DISCOVERY.md), this means that neither existing public actions nor the direct API call meet the required send contract. No recipe-persistence defect was found. No third-party repositories were changed and no upstream issues or messages were published.

## Required contract before live operation

These requirements propose a supported upstream interface; they are not existing functionality:

1. An explicit **prepare without heater start** call with exact model, zone, program, Celsius temperature and minutes. No arbitrary method, raw payload, shared zone 0 fallback or experimental start variant.
2. At most one control transport attempt per deliberate confirmation. Any required login may complete before that attempt; after it begins there must be no variant fallback, authentication replay or automatic retry. A timeout/disconnect after submission means “outcome unknown,” rather than “definitely failed.”
3. Successful observation time and revision per device/zone, explicit online/error status and actually reported zones. An error does not make cached data fresh again. Reconnection, a new device session and capability changes must invalidate existing confirmations. A global coordinator or HA entity timestamp is insufficient.
4. Model/zone/program limits with traceable provenance. Global TwinFry constants must not enable unconfirmed CAF-DC111S-AEU functionality. No silent clamping or substitution.
5. Independent device safety verification of preparation without heating and zone isolation; by default no changes to cooking, paused, preheating, open or unknown zones. Future running changes additionally need explicit device support, administrator opt-in and reconfirmation.
6. Results distinguish rejection, adapter acceptance, device confirmation and unknown outcome. A successful HA call alone must not count as device confirmation.

The future coordinator must additionally enforce authenticated user/device permissions, a bounded number of short-lived single-use confirmations binding user, target, exact values, policy and state revision, revalidation immediately before transmission and serialization per physical device. Concurrent requests must not form a queue; busy devices are rejected. Local locks cannot prevent state changes from physical buttons or another app; device safeguards must remain effective. These live features are explicitly not implemented in this package.

## Implemented API

Authenticated administrator, integration loaded:

```json
{"id":1,"type":"airfryer_recipes/prepare_send","device_id":"HA-DEVICE-ID","zone_id":1,"settings":{"program":"airfry","temperature_c":170,"duration_minutes":8}}
```

The response contains `mode=dry_run`, `live_send_enabled=false`, `transmitted=false`, `accepted_by_adapter=false`, `confirmed_on_device=false`, validated desired settings and `blocking_reasons`. Unverified contract, freshness and program limits always remain blocking reasons. Additional reasons cover offline/unknown connectivity and non-ready zones. Even reported idle state cannot authorize sending. Desired settings are not verified device payloads and are neither adapted to supported values nor persisted.

Extra fields such as `dry_run=false`, `live_send_enabled=true`, raw device commands or forged `is_admin` are rejected. Regular and unauthenticated users cannot request previews; regular-user control with device permissions follows later. A missing device or unreported zone returns `target_not_found`; after unload, `not_configured`. There is still no `confirm_send` command or confirmation token capable of enabling transmission. The API has no new phone UI yet.

## Verification and local acceptance

75 Python offline tests and 10 frontend tests passed, as did compilation and `git diff --check`. Additional tests cover both zones, unchanged settings, missing targets, rereading on every request, active/offline/unknown states, invalid values and extra fields, claimed live capabilities, authorization, unload and zero service calls. An intentionally triggered storage error in an existing test still produces an expected traceback. Tests of future live races, single-use confirmations and adapter control do not exist yet because these features are absent. PR Actions check HACS, Hassfest and Python 3.12/3.14.

Local HA and appliance: **NOT TESTED**. After a backup and installation of the entire integration directory, restart HA. As an administrator, first read `devices`, then send the request above using an actually reported HA device ID and zone ID through an authenticated HA WebSocket connection. Expect only dry-run mode, unchanged desired settings and blocking reasons; the appliance must remain unchanged. Verify `unauthorized` as a regular user and continue checking recipe management. Without the adapter there is no valid target. As agreed, manual API acceptance may wait until the UI exists.

## Decision on next steps

Live transmission remains blocked until a verifiable upstream contract and model-specific safety evidence exist. The next useful step is deciding whether to coordinate the contract above with the Airfryer Control project. Contact or changes to the third-party repository are not authorized and were not performed. A read-only test UI can be prepared independently; it must not imply verified programs or transmission permission. Model for further adapter/coordinator work: GPT-6 Sol – High. Pause before a new package as agreed.
