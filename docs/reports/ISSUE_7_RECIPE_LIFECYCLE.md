# Recipe transmission and interrupted confirmation

[Deutsch](ISSUE_7_RECIPE_LIFECYCLE.de.md) | [English](ISSUE_7_RECIPE_LIFECYCLE.md)

Beta 0.1.0b11 continues recipe/manual acceptance while Proof and wider temperature support remain deferred. The existing six-program contract, temperature intersection, administrator-only access, 15-second expiry, strict single transmission and recipe storage are unchanged. The earlier [twelve-step appliance acceptance](ISSUE_7_LOCAL_ACCEPTANCE.md) remains evidence for its nominal settings; new real acceptance below is pending.

## Changes and guarantees

Two gaps were found: individual confirmations were bound to the user but not the originating websocket, and a late preparation response could restore an old confirmation after input edits or leaving the page. Batch owner binding already existed, but late list/read responses also needed frontend lifetime checks.

Each `beta_prepare` route now creates a server-owned `SendPermit` before awaiting recipe/status work. A public HA connection cleanup callback closes it on websocket disconnect. The token stores this permit; `beta_confirm` requires the same connection identity and rechecks the permit after final asynchronous validation. Disconnect during preparation cannot mint a late token; disconnect before control submission blocks that call. Clients cannot supply the permit or owner.

New administrator-only `beta_cancel` accepts only the token. It revokes owned pending work or an in-progress validation. It performs no device control and cannot recall a submitted call. The sender retains its per-device lock until an in-flight call actually finishes, even after cancellation. Unknown outcomes keep the existing uncertainty latch until physical inspection and explicit fresh re-arming. `transmitted:false` in cancellation responses describes the cancellation operation, not whether an earlier request reached the appliance.

Cleanup runs on consumption, explicit discard, replacement, expiry validation, integration unload and disconnect. There is no timer that retries or resumes work. Wrong connections/users cannot cancel or confirm another permit. Expired or failed confirmations remain single-use.

The panel watches the public HA websocket `disconnected` event and checks its `connected` property before beta/batch requests. A connection/page/user/permission/unit change discards old controls. Input/recipe/target changes revoke the visible token; late preparation results are discarded and canceled instead of enabling a confirmation for old values. Leaving during validation requests cancellation where the connection is still usable. Late batch preparation, steps and re-arming results cannot overwrite a newer disconnected state. Manual inputs and recipes are retained; requests are never replayed automatically.

Reviewed public [HA JS connection implementation](https://github.com/home-assistant/home-assistant-js-websocket/blob/40bd9924299a9ef02e8ae7969aee0eeca05aaecc/lib/connection.ts): `connected`, `addEventListener` and `removeEventListener` support these guards. The library can queue requests during suspend/reconnect; the panel checks connection state before entering `callWS` for beta/batch operations. No private queue fields are accessed. Reviewing this source does not establish acceptance of the owner's installed frontend version.

## Local verification

Passed: **163 Python tests and 50 frontend tests**, compilation, documentation links and git diff --check. A complete mocked integration check sends saved recipes for all six programs on both zones through the actual WebSocket routes, repository and sender, with only device reads/service transport mocked. All twelve exact payloads are checked and the recipe export remains unchanged. An API recipe edit invalidates its earlier confirmation without overwriting the edit.

Additional checks cover cross-connection rejection, disconnect during preparation/validation, owner-only cancellation, cleanup, expiry, device locks while a submitted call remains pending, double taps, stale input responses, page return, offline request suppression, permission loss and interrupted batch/re-arming responses. Existing mocked offline, active/unknown-zone, freshness, recipe deletion/reload, uncertainty and dry-run protections remain covered. Frontend tests use VM/DOM/connection stubs; backend HA APIs are simulated. Native HA/Companion, real new appliance checks, Python 3.14, HACS/Hassfest and GitHub Actions were not run.

## Focused owner acceptance

Follow-up: the owner was blocked at recipe authoring because the editor required program text, and the screenshot showed the unreported identifier `Airfry`. Beta 0.1.0b12 adds a reported-program dropdown and an explicit correction path. [Editor correction and repeat procedure](ISSUE_7_EDITOR_PROGRAM_PICKER.md). R1/R2 remain pending until the corrected saved recipe is tested.

Back up, install v0.1.0b11, restart HA and fully reopen the app. Retain exactly Airfryer Control 1.0.2-beta.1 for this package. Cancel old appliance preparations, wait for both zones idle/off and re-arm if required. Remain beside the appliance; do not press Start. Create a separate single-phase test recipe using the previously accepted Air Fry / 180 °C / 7 minutes; do not overwrite a personal recipe.

| ID | Check | Expected result | Status |
| --- | --- | --- | --- |
| R1 | Select the saved test recipe and zone 1; prepare, check exact values and send once | Values on zone 1 match; zone 2 unchanged; no heat; recipe unchanged | NOT TESTED |
| R2 | Physically cancel R1, wait idle, then send the same recipe to zone 2 | Values on zone 2 match; zone 1 unchanged; no heat | NOT TESTED |
| R3 | Physically cancel R2, prepare again and choose Discard test | No settings transmitted by discard; no usable old confirmation | NOT TESTED |
| R4 | Prepare without sending, leave the panel and return | Old confirmation gone; no automatic transmission | NOT TESTED |
| R5 | Prepare manual settings, then edit temperature/time before confirming | Old confirmation unusable; prepare again to see the new values | NOT TESTED |
| R6 | Prepare without sending, disconnect the phone's connection to HA and reconnect | Old confirmation gone; no replay or resumed sequence | NOT TESTED |
| R7 | Prepare the saved recipe, edit it in another session, then try its old confirmation | Blocked; no device call and the edited recipe remains unchanged | NOT TESTED |

Cancel final prepared settings at the appliance. If a send was already submitted before leaving/disconnect, inspect it physically: cancellation does not prove that it never arrived. Record ID, displayed guidance, selected zone and physical result; no raw diagnostics or identifiers are needed.

After focused acceptance, the next implementation package is the normal dashboard workflow with backend user permissions. This release does not enable a dashboard, ordinary-user sends, Proof or wider model temperatures.
