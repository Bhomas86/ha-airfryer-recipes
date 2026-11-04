# Restarting a test without restarting Home Assistant

[Deutsch](ISSUE_7_MANUAL_RECOVERY.de.md) | [English](ISSUE_7_MANUAL_RECOVERY.md)

## Finding and scope

The owner reports v0.1.0b6 stopping after two confirmed steps, apparently when switching from Air Fry to Roast on zone 1. A need to clear prepared programs is plausible but not established by the generic message. The screenshot confirms two reports, not the complete sequence. The owner explicitly requests a deliberate new attempt without HA restart, remains beside the appliance and can intervene.

Version 0.1.0b7 adds **“Device checked – enable a new test”**. First cancel all prepared programs at the appliance and return both zones to idle/off. Select that button and acknowledge the notice. It reads a new status only, sending no reset, stop, start or settings command. A matching fresh report invalidates old single-use confirmations and clears this device's local test block. Then show a new list and start once. No replay of old steps or continuation of old tokens.

Re-arming checks current administrator rights, unchanged adapter/device ownership, both idle zones, Celsius and SYNC/MATCH off. In-flight calls or active runs block it. Old plans are stopped first; submitted commands cannot be recalled, and re-arming is blocked while a call remains in flight. Missing, stale, active or still-prepared zones preserve the block. This explicit supervised re-arm replaces the earlier HA-restart requirement for new attempts. It does not prove that a previous uncertain command never arrived; the owner resolves physical appliance state.

## Failure details

An explicit adapter rejection is distinguished from unknown transport outcome. Only a numeric error code is exposed; raw data, account identifiers and free-form errors are discarded. Sequence failures show step, program, zone and code when available. Other failures also identify the affected step. No next command follows rejection. Whether prepared programs need resetting between programs remains a local question; this version does not automatically reset them.

## Validation and repeat test

138 Python tests and 31 frontend tests passed locally, with compilation and git diff --check. New tests cover re-arming without control calls, old tokens, absent consent, current permissions, pending calls, active runs, failed state checks and exact rejection at step 3. No GitHub Actions, HACS/Hassfest, Python 3.14 or real HA/appliance checks for this change.

Back up and install v0.1.0b7; restart HA once for the update and fully reopen the Companion app. Retain exactly Airfryer Control 1.0.2-beta.1. Subsequent retries need no further HA restart: cancel programs physically, check/re-arm, show a new list and start once. Remain beside the empty appliance and do not press Start. If it stops again, report the full step message and code. Stop at the appliance on heating or wrong-zone changes. Real acceptance of re-arming and the cause of step 3: NOT TESTED / UNRESOLVED.
