# SYNC / MATCH — reviewed contract and safe preview

[English](ISSUE_1_SYNC_MATCH.md) | [Deutsch](ISSUE_1_SYNC_MATCH.de.md)

**Follow-up 2026-11-08:** Several blockers below are fixed in controller 1.0.3. A missing/unknown-zone write remains reproducible. [Current review](ISSUE_1_CONTROLLER_103.md). Earlier owner-reported successful SYNC/MATCH tests remain valid.

Issue #1 remains **blocked for live transmission**. b25 development implements only the separate read-only dashboard previews and backend validation. PR #47 was merged with the owner's authorization; its native diagnostic/push acceptance is still not claimed. No new beta is published by this work.

## Current dashboard behavior

Set the values in zone 1 and, for SYNC, zone 2 on the same card. A preview uses those explicit card drafts; it does not fill a missing second draft from stored history or controller defaults. Recipe IDs resolve against the current server library without changing a recipe.

- **SYNC preview:** preserves each zone's program, temperature and duration, and displays the planned delay `longest duration − this zone's duration`. It does not schedule a timer or send a device command.
- **MATCH preview:** explicitly uses **zone 1** settings for both zones, even if zone 2 is selected. Both effective zone settings are displayed.

Only two-zone targets expose the preview controls. Offline controls are disabled. The authenticated backend checks the current whole-device grant before reading and again after all awaited reads. No per-zone control grants are added. Strict envelopes reject extra/live parameters. Both phases must fit the reviewed model/program bounds and the programs/ranges actually reported by the selected device. Invalid values are rejected, never substituted or clamped. Active/unknown zones, connection, model and unverified freshness remain visible machine-readable blockers; `live_send_enabled` and `transmitted` are always false. A preview is descriptive, not a permit to send later. Separate per-zone sending continues unchanged.

## Upstream evidence

Reviewed Airfryer Control:

- **1.0.3-beta.3**, commit `a9fc49e37c3d2698d21bfb361192717ff790eb6e`.
- Current **1.0.3-beta.4**, commit `4c73bf0b126bbc910bdd52a9a90ed9564fef7b30`: `services.py`, `senden.py`, `core/api.py`; the same blockers remain.

Public actions are `airfryer_control.sync_senden` and `airfryer_control.match_senden`, with only the `geraet` argument. `services.py` registers them using `STOP_SCHEMA`, without a structured response contract. Their handler delegates to `senden.async_send_sync`.

This routine reads mutable `coordinator.plans`, including fallback defaults, and silently clamps values. It does not accept the exact values displayed by our card. Its preparation helper refreshes and can issue `endCook` for prepared zones. If a zone is busy, that helper merely returns; the outer routine still continues to `startMultiCook`. Thus calling this action after a client-side idle check does not enforce our server-side safety contract.

The combined payload requests `readyStart: true`, but its builder explicitly describes the app shape as presumed rather than captured for this model. The write calls `bypass_v2` without `retry=False`; that API defaults to automatic reauthentication/retry. The public actions do not expose a one-shot switch. Neither action return nor availability establishes native model acceptance. Calling private controller/cloud APIs, mutating its plans or temporarily monkey-patching retry behavior would not provide a safe public integration contract, so none is implemented.

## Concrete public contract needed from the controller

1. Accept explicit immutable program/temperature/minutes for **both** zones (or a clearly defined zone-1 MATCH source), not implicit input helpers.
2. Strict mode rejects unsupported programs, out-of-range values and invalid temperature steps without clamping/substitution.
3. A public one-shot option must reach every device write as `retry=False`, including any reset writes; no queued/replayed commands.
4. Revalidate a fresh report and both inactive zones immediately before writing. Unknown, offline, stale or busy must abort the entire action. A preparation helper returning early must not allow the outer send to continue.
5. No implicit reset of prepared programs. If reset is required, expose it separately with exact affected zones and explicit user authorization, then revalidate state.
6. Fixed prepare-only semantics (`readyStart: true`); no heating start or software timing workaround. Document exact supported models and payload shape.
7. Return structured accepted/rejected/unknown outcomes and fresh revision/readback metadata without private data. Unknown must never be retried automatically.

After that contract is published, review/pin it, connect fresh one-use confirmations bound to both phases, target, owner, connection and device grant, share existing per-device locks, implement server-enforced dry run, and perform a supervised native check of both SYNC and MATCH before claiming completion. Do not close #1 based on this preview.

## Validation

Offline tests exercise separate SYNC values/delay, MATCH direction, server-side recipe resolution, malformed/missing/out-of-range inputs, missing zones/programs, offline/running/unknown-model blockers, revoked grants, strict API routing and zero control calls. Card tests exercise explicit drafts, no silent fallback, ordinary-user routing and visibility/disabled controls. Native combined-device tests cannot be performed from this cloud environment and remain pending.

Native preview-only check: choose distinct values for both zones, check SYNC displays them and the duration difference; choose MATCH and confirm both outputs use zone 1. Check the ordinary-user whole-device allow/revoke flow and normal independent sends. Preview must not change the appliance or its prepared programs. No live combined-send test is authorized by this implementation.

Passed locally: **259 Python tests on each of 3.12.14 and 3.14.8; 132 frontend tests**, compilation and `git diff --check`. English/German UI and documents reviewed for equivalence. No Actions triggered under the standing CI pause.
