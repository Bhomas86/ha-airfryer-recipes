# Issue #7 – Beta send contract re-review

[Deutsch](ISSUE_7_BETA_REVIEW.de.md) | [English](ISSUE_7_BETA_REVIEW.md)

As of 2026-10-30. Model check: GPT-6.1 Sol – High, confirmed by the owner; adapter/async and safety review. Source review only, with no device calls or upstream changes.

## Outcome

**Live transmission is not approved.** Airfryer Control `beta` remains at [`f43a9bf8`](https://github.com/misterm2310/airfryer-control/tree/f43a9bf8ddb7cc65e27897dd92158cc06840bc08) (`1.0.2-beta.1`), with `main` at `5a3c530d`. The contract is unchanged since the previous review. Our preview remains server-blocked; the presence of a beta service does not grant send permission.

## Source findings

- `services.py::_program` exposes `variante`, `einmal`, `streng` and `bestaetigen`. The regular program service passes `allow_start=False`. Explicitly select a variant verified for the model/zone; `einmal=true` alone otherwise just selects the first or remembered variant. The existing zone-0 variant is not approved for our adapter.
- `senden.py::async_send(once=True)` limits execution to one variant attempt and passes `retry=False`. `core/api.py::bypass_v2` then uses `_once` instead of `_with_relogin`. Login can occur before transport; this path does not replay the same control command after authentication failure. Connection failures produce an unknown outcome. This is source evidence, not a device or transport test.
- `streng=true` prevents silent clamping but checks generic program limits. `faehigkeiten.py` recognizes only TwinFry prefixes CAF-TF101S/CAF-TF102S; only TwinFry `airfry` is recorded as send-confirmed. Programs and limits remain estimated/unverified for CAF-DC111S-AEU. `proof` remains outside this contract.
- `coordinator.py` updates `last_report` after successful device queries and `revision` when raw data changes or the device goes offline. These are per-device values, not independent zone freshness evidence. Equal revisions prove neither a new successful query nor unchanged sessions or capabilities. Error/connection state and actually reported zones require additional checks.
- After `async_refresh()`, `services.py::_confirm` checks only `fryer.online`, matching values and readiness **or activity**. It requires neither an advanced report timestamp nor `connection == ok` or a successful new zone report. Matching cached values retained after a failed query can therefore produce `bestaetigt=true`. This field alone proves neither fresh device confirmation nor absence of heating under our requirements.
- The program service lacks sufficient running/unknown-zone blocking, single-use confirmations and serialization for our application. Our future coordinator must provide these. The `readyStart=true` payload does not replace local verification on CAF-DC111S-AEU.

## Next bounded package

1. First establish model/zone-specific programs, limits and a safe preparation variant for CAF-DC111S-AEU; explicitly resolve `proof`. Add no live controls before that evidence exists.
2. Establish freshness and session identity; require a new successful report, an actually reported zone, matching values and a non-heating state for confirmation. Do not trust upstream `bestaetigt` alone. A supported interface or independently verifiable read-only states may satisfy these requirements; private API/cloud access is not a workaround.
3. Only then implement user/device permissions, short-lived bound single-use confirmations, revalidation immediately before sending and per-device locking without queues. Block offline, unknown, stale or active zones; never automatically retry.
4. Run simulated failure, race and zero-control-call tests locally; comprehensive CI once at the section boundary. Real acceptance belongs exclusively to the owner after a separate implemented test procedure exists.

## Verification and limitations

Reviewed the named files at the fixed beta commit and compared them with our `command_preview.py`. No new feature implemented; no appliance or Home Assistant contacted. Local appliance acceptance and transport behavior: **NOT TESTED**. Existing 0.1.0b2 phone acceptance remains valid for preview, not live sending. This report does not retroactively rewrite historical model recommendations; AGENTS.md defines the current GPT-6.1 Sol policy.

## Actions budget and local validation of this package

The new budget policy is recorded in both languages in AGENTS, requirements and roadmap. Automatic PR tests use Python 3.12 only; the full 3.12/3.14 matrix is available manually with `full_suite=true`. Frontend tests run once. Automatic HACS/Hassfest checks are limited to relevant metadata/workflow changes and remain available manually. Documentation-only changes and the subsequent merge trigger no code checks. Superseded runs are canceled and jobs have ten-minute timeouts.

Passed locally on Python 3.12.14: 78 Python tests, the frontend command `node --test tests/test_panel.mjs`, YAML parsing and checks of workflow triggers, path filters, timeouts and concurrency, and `git diff --check`. The storage-error traceback is from an expected negative test. No local Python 3.14, Hassfest or HACS validation was run; GitHub execution of the new workflow logic is pending before PR publication. This completed package receives one regular PR validation run, with no additionally dispatched full matrix run.
