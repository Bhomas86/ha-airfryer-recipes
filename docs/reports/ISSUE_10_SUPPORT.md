# Diagnostics and completion notices — Issue #10

[English](ISSUE_10_SUPPORT.md) | [Deutsch](ISSUE_10_SUPPORT.de.md)

Implemented in the b24 development branch. Native acceptance is pending; this is not a stable release or a claim that mobile delivery was tested in Home Assistant.

## Administrator tools

Open the recipe library → **Diagnostics and completion notices**. Preview diagnostics, inspect the complete JSON, then explicitly download. Download uses only that displayed snapshot; nothing is uploaded or sent to GitHub. The backend constructs an allowlist of the integration/schema versions, loaded/available flags and notification-rule count. It excludes raw upstream telemetry, exception text, network addresses, account/device/user/entity IDs, service names, recipe data and images. There is no automatic sharing. Both the WebSocket command and fresh authenticated user lookup enforce administrator access.

Completion notices are off by default. Load settings and choose a loaded Airfryer Control zone status sensor and a `notify.mobile_app_*` service from the lists. Enable each desired zone separately; one destination per zone. An administrator may disable any rule. These are notification preferences, not device-control permissions: ordinary HA users retain whole-device grants, without per-zone control restrictions. Only administrators configure destinations. Target selection explicitly authorizes runtime delivery of completion notices to that Companion device. No test push is sent during configuration.

## Completion contract and privacy

Reviewed upstream: Airfryer Control **1.0.3-beta.3**, commit `a9fc49e37c3d2698d21bfb361192717ff790eb6e`, `sensor.py`, `entity.py` and `core/parser.py`. Only enabled, loaded upstream zone-1/2 status entities with their registry identity are accepted. Other upstream versions expose no selectable sources. Rules bind entity, unique ID, config entry and device; a rebound entity cannot inherit notifications.

Observe HA state events without polling or appliance service calls. A fresh, explicitly reported `gart` sample must precede `fertig`, with increasing report time and revision and at most 90 seconds between reports. Each sample must be no more than 90 seconds old, not future-dated, `gemeldet: true` and `verbindung: ok`. Unavailable, malformed, stale, idle, canceled, paused, drawer-open and unknown samples discard the arm. Repeated identical cooking reports preserve the arm; duplicate/reordered completion reports never send again. No inferred finish from remaining time or predicted finish timestamp. Conservative detection can miss a real completion after an interruption or pause; it does not synthesize a replacement notice.

Armed state exists only in memory. Restart/unload/configuration changes clear it; no completion is replayed. The original configuring administrator must still be active and an administrator when delivery is attempted. Source identity, target existence, current state and freshness are checked before sending. Messages contain only “Zone 1/2 reports: finished.” in the configured English/German language, plus the constant title “Airfryer Recipes”; no appliance/recipe names, temperatures or identifiers. Delivery errors have generic logs and no automatic retry. HA shutdown suppresses delivery. No heating/control commands are introduced.

Rules use a separate versioned, verified atomic local store. A failed save does not activate new settings; corrupt/newer data is preserved with notifications disabled. Recipes and device grants are unaffected. API failures expose generic errors. Settings and diagnostics are administrator-only.

## Validation and native acceptance

Offline tests cover privacy allowlisting, current administrator authorization, strict command envelopes, independent zones, duplicate/out-of-order reports, restart, stale/invalid/future timestamps, offline/unknown/cancellation/pause, revoked rights, rebound sources, default-off, failed delivery without retry, failed/corrupt storage, disable and listener cleanup. Frontend tests cover explicit preview, admin visibility, escaping and precise disable requests. No real device, mobile push or LAN access was used.

Native checks after installation/restart:

1. Administrator opens the tools; preview/download JSON and confirm the excluded data is absent. Ordinary users must not see tools and direct commands must be rejected.
2. Initially no rules. Enable one zone and choose the intended Companion destination; reload/restart and verify the rule persists. Configuration must send no push.
3. During an ordinary supervised cooking cycle started physically at the appliance, verify one notice only when that zone reports finished. Test the other zone independently. Do not heat an empty appliance solely for this test.
4. Cancel a cycle, disable a rule and check an offline/reconnection case: no false completion. A restart while already finished must not produce an old notice.
5. Disable rules after testing if unwanted. Verify recipe/card/device grants still work. Record actual outcomes before closing #10.

The release-readiness portion already has successful full Python/frontend and HACS/Hassfest Actions evidence on PR #46 for b23. That evidence does not validate these new changes. The owner authorized Actions specifically for #46; new work remains locally validated under the standing CI pause.

Local result: **249 Python tests on each of Python 3.12.14 and 3.14.8; 128 frontend tests passed**. Compilation and `git diff --check` passed. English/German documentation and UI text reviewed for equivalence.
