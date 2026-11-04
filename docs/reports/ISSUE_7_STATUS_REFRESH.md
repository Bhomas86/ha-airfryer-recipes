# Issue #7 – Freshness blocking during test preparation

[Deutsch](ISSUE_7_STATUS_REFRESH.de.md) | [English](ISSUE_7_STATUS_REFRESH.md)

As of 2026-10-30. Model check: GPT-6.1 Sol – High, confirmed by the owner.

## Finding and correction

The owner reports freshness blocking in v0.1.0b3 with the appliance powered on and drawers closed and unused. The screenshot shows rejection before any send confirmation; no arriving command was observed. The error covers old as well as missing/inconsistent reports, so the screenshot alone cannot establish the exact age. Code requested no refresh and accepted reports only up to 15 seconds old, making interaction dependent on regular polling timing.

Preparation in v0.1.0b4 first reads model, adapter version and device ownership. It then selects a loaded, enabled sensor from the same Airfryer Control config entry and device. The public `homeassistant.update_entity` service requests a new report exactly once with a server-owned administrator context. In reviewed upstream f43a9bf8, sensors inherit from `CoordinatorEntity`; their update performs a read-only coordinator query. No private control methods, button/number entities or additional cloud credentials are used.

An unchanged cached report is rejected even if still within 15 seconds: its timestamp must follow query initiation and advance beyond the previous report. Public capabilities and runtime must still agree afterward. No timestamps are fabricated or made artificially fresh. Queries time out after 20 seconds or fail without automatic retry. Missing active sensors and unsuccessful refreshes have distinct translated guidance. Upstream error strings are not exposed.

Per-device locking now covers preparation too. Parallel requests are rejected without a queue. New preparation invalidates older tokens for that user even if the new query fails. Final confirmation still only rereads state, without a second refresh. All previous model, zone, permission, state, single-use and unknown-outcome gates remain. Dry-run preview, recipe data and fixed test settings are unchanged.

## Validation

Passed locally: 108 Python tests, 21 frontend tests, Python compilation and `git diff --check`. New cases cover renewal of a 90-second-old report, unchanged cache despite successful service return, timeouts, selection of eligible sensors only, unchanged confirmation without refresh, parallel preparations, token invalidation after failed preparation and visible loading/blocking states. Tests use simulated services only; preparation never calls `programm_senden`. Existing storage-error output is an expected negative test.

One full package-end PR acceptance run is requested for Python 3.12/3.14, frontend, HACS and Hassfest. No intermediate extra runs. Native HA runtime, debouncing and real polling require local acceptance; an HA-deferred query can still safely block without an immediately new report. Prepare again manually if needed; never automatically retry.

## Local test

1. Install v0.1.0b4, restart HA and fully reopen the app. Retain exactly Airfryer Control 1.0.2-beta.1. Back up first.
2. Keep both zones idle/off, closed and without programs; select Celsius, disable SYNC/MATCH. Remain beside the empty appliance and do not press Start.
3. As an administrator, select the appliance and zone 1, then prepare the real test. Expect visible status refresh and, following a successful new report, the single-use confirmation. Preparation must not change the appliance.
4. For “no enabled sensor”, inspect/enable an Airfryer Control status sensor. For “no new successful report”, inspect its connection and report the exact guidance; bypass nothing.
5. Only with the correct confirmation (zone 1, Air Fry, 170 °C, one minute), send once and inspect settings, unchanged other zone and absence of heating. Do not press Start. Stop on discrepancies or unknown outcome. Cancel the prepared program at the appliance afterward; zone 2 can then be tested separately.

Report preparation after refresh separately as **PASS/FAIL/NOT TESTED**, and real transmission for each zone likewise. The previous blocked attempt proves no working transmission. Share no raw diagnostics, credentials or identifiers. Appliance acceptance of the correction: **NOT TESTED**.
