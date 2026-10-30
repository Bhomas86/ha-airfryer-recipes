# Issue #7 – Interface for supervised beta appliance tests

[Deutsch](ISSUE_7_BETA_SEND.de.md) | [English](ISSUE_7_BETA_SEND.md)

As of 2026-10-30. Model check: GPT-6.1 Sol – High, confirmed by the owner.

## Scope and decision

The owner requested implementation before real appliance acceptance and a new test beta. Accordingly, `0.1.0b3` adds a separate explicitly confirmed initial test while compatibility remains unverified. For this test, this replaces the previous requirement for real evidence before any implementation. General device control remains blocked; estimated capabilities grant no general send permission. The existing `prepare_send` preview remains unchanged with zero control calls.

The only permitted test is CAF-DC111S-AEU, zone 1 or 2, `airfry`, 170 °C, one minute. Only Airfryer Control 1.0.2-beta.1 is allowed. Its public `programm_senden` service receives `variante=multi_app`, `einmal=true`, `streng=true`, `bestaetigen=false`. Start-capable variants, zones 0/3, raw, SYNC and MATCH are unreachable.

## Backend and interface

`beta_send.py` encapsulates test transmission. `beta_prepare` and `beta_confirm` are administrator-only WebSocket commands. Current active administrator rights are additionally fetched from HA; the service receives a server-owned user context. Confirmation uses only the server token's target/settings; extra fields are rejected.

Both actual zones and an idle/off aggregate state are required; active, prepared, unknown and unreported zones are rejected. SYNC/MATCH must explicitly be 0 and the temperature unit Celsius. Capability service and runtime must agree on the same successful report, at most 15 seconds old, and revision. Any new report invalidates confirmation even if values match. Adapter instance, zone states and program ranges are also bound. After the final asynchronous authorization check, state is checked synchronously again. Device/zone states are read only; no private upstream control methods or additional cloud credentials are used.

Tokens last 15 seconds, belong to one user and are single-use; at most 32 are pending, only the newest per user. Consumption precedes revalidation. Per-device locking rejects immediately without a queue. In-flight calls and unknown-outcome blocking survive integration reload. Errors or incomplete responses never trigger retries; further attempts for that device remain blocked until HA restarts. Unload discards tokens and prevents transmission that has not begun. It cannot recall a command already submitted.

The interface separates “Prepare real device test” from “Send once to the appliance”, displays exact device/zone/settings and requires another dialog before the real attempt. A lost response consumes the visible token and shows “Outcome unknown”. Only a fully matching service response counts as adapter acceptance; `confirmed_on_device` and `compatibility_verified` always remain `false`. Recipe storage and import/export are unchanged.

WebSocket schemas now use HA-provided `voluptuous`; the previous undeclared `probatio` import was also corrected in the test stub. The panel module receives a version identifier to avoid stale module caches.

## Automated validation

Passed locally: 101 Python tests on Python 3.12.14, 20 frontend tests via `node tests/test_panel.mjs`, Python compilation and `git diff --check`. New tests cover zero control calls on preparation/blocking, both zones, timestamp/version/model bounds, administrator revocation, state changes, token consumption/expiry, concurrency, cancellation/reload and unknown responses. The existing storage-error output is an expected negative test. Native HA schema validation in a full HA runtime was unavailable locally; API tests use HA stubs.

This completed section requests exactly one `[full-ci]` PR run with Python 3.12/3.14, frontend tests once, HACS and Hassfest. No additional intermediate runs or repeated testing of unchanged revisions. AGENTS documents the new marker.

## Local appliance acceptance

Back up first; install exactly Airfryer Control 1.0.2-beta.1 and Airfryer Recipes v0.1.0b3, restart HA and fully reopen the app. Test only beside the empty appliance under supervision. Capabilities remain labeled estimated/unverified.

1. Open recipe management. Check the existing device preview first: explicitly nothing transmitted and no appliance changes.
2. Set both zones to idle/off at the appliance, cancel prepared programs, select Celsius and disable SYNC/MATCH. Do not press Start. Select the Cosori and zone 1.
3. In the separate “Supervised beta device test” section, prepare the real test and acknowledge the warning. If freshness blocks it, await a new successful Airfryer Control report and prepare promptly. Device discovery itself does not force a new cloud report.
4. Check device, zone 1, Air Fry, 170 °C and one minute in the confirmation. Only if correct, select “Send once to the appliance” and confirm within 15 seconds. An intervening report/state change aborts without a control call; prepare again.
5. If accepted by the adapter, inspect the appliance directly: correct zone, Air Fry, 170 °C, one minute; other zone unchanged; **no heating**, manual start still required. Do not press Start. Only the owner can mark these points PASS.
6. Cancel the prepared program at the appliance. Return both zones to idle/off and await a new report. Repeat for zone 2; zone 1 must remain unchanged.
7. Do not resend after an unknown outcome. Check the appliance and end testing. A full HA restart clears the local uncertainty block but does not prove that a previous command did not arrive. Test again only after resolving the appliance state and finishing old requests. If heating starts or the wrong zone changes, stop at the appliance and perform no further attempts.
8. Normal users must not access the section or commands. Check recipe management, favorites and import/export afterward. If needed, return to v0.1.0b2 and restart HA; the recipe format is unchanged.

Report for each zone: **PASS / FAIL / NOT TESTED**, displayed outcome, program/temperature/time at the appliance, other zone unchanged yes/no, heating started yes/no. For blocked tests, quote the displayed reason. Publish no credentials, device identifiers or raw diagnostics.

## Limitations

Appliance acceptance: **NOT TESTED**. No evidence for `proof`, other programs, free values or changes during cooking. Polling cannot prevent physical buttons or another app from changing state between validation and transmission. No automatic device confirmation; an accepted cloud command is insufficient. Expand testing only after documented local acceptance; Issue #7 remains open.
