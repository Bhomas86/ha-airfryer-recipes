# Guided test run with one confirmation

[Deutsch](ISSUE_7_GUIDED_BATCH.de.md) | [English](ISSUE_7_GUIDED_BATCH.md)

## Controls in 0.1.0b6

The owner confirms that the 0.1.0b5 selection button works but requests less interaction and one confirmation for a sequence. The new guided test section appears above the previous preview. Select device, **“Show test sequence”**, inspect the list and click **“Confirm displayed sequence and start”** once. No per-step dialogs. Initially both zones must be closed, idle/off and without prepared programs; Celsius, SYNC/MATCH off, empty appliance supervised. Do not press Start.

The normal sequence addresses zones 1 and 2 for each program: Air Fry 180 °C/7 minutes, Roast 190/10, Bake 180/6, Grill 205/1, Reheat 70/5 and Dry 55/10. At most twelve commands, not automatic cooking. Missing programs or unsuitable sample values are explicitly listed as skipped. Boundary and recipe tests remain separate individual attempts; extreme temperatures and long durations are not automatically selected.

Progress and matching reports appear during execution. “Stop remaining steps” works during pending requests. A submitted command cannot be recalled. If heating starts or the wrong zone changes, stop at the appliance and end testing. Inspect both zones physically afterward and cancel prepared programs at the appliance. This version has not passed real appliance acceptance.

## Guards

The complete list is generated server-side and bound to administrator, device, adapter instance and current WebSocket connection. Showing it only reads state; starting authorizes the list once. The plan lasts 60 seconds; a started run lasts at most ten minutes. Every step requires a fresh single-use server nonce. No background queue or replay after a lost response. Connection changes or unload prevent continuation; HA subscription cleanup stops the run when its WebSocket closes. Leaving the panel requests a stop.

Before each control call, permissions, contract bounds and new device reports are checked. Another read-only refresh afterward waits for a new report (up to 20 seconds for potentially deferred HA polling). Both zones must be inactive. A zone prepared by this same run can be reused only if reported program, set temperature and duration exactly match its last step and its state is waiting for Start. Other prepared states, mismatches, offline/unknown state and heating/cooking stop execution. Independent sends are blocked during the run.

No automatic reset, start, raw, SYNC or MATCH action. Shared transport remains only `programm_senden`, fixed `multi_app` variant, once, strict and without upstream auto-confirmation. Unknown outcomes or absent readback after sending block more attempts until HA restarts. Manual interruption during a pending transmission receives the same conservative treatment. Restarting does not prove the previous command never arrived.

## Validation and local acceptance

Passed locally: 132 Python tests, 29 frontend tests, compilation and git diff --check. New cases cover twelve distinct steps, missing programs, nonce replay, connection changes, stopping before/during sending, unknown responses, absent readback, device locking, adapter changes, expiry, WebSocket cleanup, own prepared-zone values and deferred read-only refresh. Chromium browser validation could not run successfully in this environment; no real Companion/HA runtime acceptance exists. No GitHub Actions, HACS/Hassfest or Python 3.14 runs for this update.

After installing v0.1.0b6, restart HA and fully reopen the app. Airfryer Control remains exactly 1.0.2-beta.1. First inspect the list without sending, then start once under supervision. Expect sequential steps without more confirmations, matching reports after each command, no heating and immediate stopping on discrepancies. Firmware support for overwriting this run's own prepared program is part of the new acceptance. If rejected, stop; no automatic workaround. Report last step, zone and guidance, without raw diagnostics or identifiers. Appliance acceptance: NOT TESTED.
