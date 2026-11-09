# SYNC/MATCH with our own guarded sender

[English](ISSUE_1_OWN_GUARD.md) | [Deutsch](ISSUE_1_OWN_GUARD.de.md)

**Owner decision, 2026-11-08:** implement protection in Airfryer Recipes; the controller will not be changed. Implemented in b26 development/PR #48. This supersedes the earlier dependency on a controller patch. No new beta or stable release is published by this change. Native acceptance remains pending.

## Behavior

The two-zone card retains separate SYNC/MATCH previews and, outside test mode, adds **Prepare SYNC / Prepare MATCH**. SYNC uses both explicit zone drafts; MATCH uses zone 1 for both. An exact confirmation lists both programs, temperatures and durations. The backend, not the UI, enforces dry run: no token and no write in test mode. Both administrator and ordinary-user requests use the same authenticated, whole-device-scoped coordinator.

After an unknown result, no automatic retry is possible. Check both zones physically, cancel prepared programs at the appliance and explicitly request the read-only re-arm. Neither preparation, cancellation nor recovery starts or stops the appliance. Accepted history failures are reported separately and never cause resending. Independent per-zone history remains separate.

## Controller stays unchanged

Supported combined-send versions are exactly Airfryer Control **1.0.3** (`75d30c800ae79eea2254e5d4f5da31ec154398e7`) and **1.0.4-beta.1** (`ca92b375547c75b698e25a21f8a8734688174e47`). Their complete `core/api.py` files are identical. Single-zone `_program`/`async_send` functions and sensor/entity source contracts were compared with the previous reviewed beta.3 and remain unchanged; those existing paths now also accept these exact versions. Other releases fail closed.

The new sender does **not** invoke `sync_senden` or `match_senden`, which refresh internally after a caller's checks. It composes the loaded controller transport through a per-call delegate: the actual `bypass_v2(..., retry=False)` uses its normal login and `_once` handling, but the HTTP-boundary `_post` on our delegate runs our final check after any login awaits. It then delegates that single request to the existing transport. No attribute, function, service, coordinator plan or controller installation is patched or replaced. No independent cloud client, credentials or token storage is added. The proposal to patch the controller was removed.

This is intentionally a narrowly version-pinned adapter to controller internals, rather than a promise of compatibility with arbitrary future controllers. Native integration acceptance must check the reviewed versions and actual payload behavior. The application cannot freeze physical appliance changes or recall a request already on the network; its final guard checks the latest known HA report immediately before the transport submission.

## Server-side guards

1. Read current HA identity and whole-device permission before resolving recipes or requesting state. Recheck permission after reads and at the HTTP boundary. No per-zone grants or client-supplied administrator flag.
2. Require one uniquely bound registry device, loaded config entry, unchanged coordinator/fryer/API and account identity, exact CAF-DC111S-AEU model and reviewed version. Recipes remain device-independent; snapshots must still match at send time.
3. Request a read-only refresh and require a successful **new** report after the request time. Both zones must be explicitly reported, inactive and idle/off. Reject missing, unknown, cooking, paused, drawer-open, prepared, offline, error, non-Celsius and already combined states. Timestamp must be timezone-aware, not future-dated and at most 15 seconds old; revision must be an ordinary nonnegative integer.
4. Validate both phases against the program/model bounds, reported capability ranges and temperature steps. No clamping or substitution.
5. Bind a one-use, 15-second confirmation to owner, WebSocket lifetime, device permission, both phases, recipes and report identity. Consume before awaits; recheck all bindings after authentication work. Changing state, grant, recipe, account, runtime, connection or expiry blocks before HTTP. Unload and cancellation invalidate pending/in-flight permits.
6. Share the existing sender's per-device busy and uncertain sets with single sends and batch tools. Reject concurrent work instead of queueing. Unknown outcomes remain latched across integration reload; re-arm requires explicit physical-reset acknowledgement and fresh safe state.
7. Construct a fixed prepare-only `startMultiCook` payload with `readyStart: true`, reviewed app mode names, exact phases, SYNC hold times or MATCH copies, Celsius and no timers/reset calls. Enforce the expected endpoint, device, account, method and payload at the boundary. At most one device-command HTTP request (normal login traffic may precede it); malformed/error/auth/timeout outcomes never retry. Raw errors, credentials and payloads are not returned or logged by this adapter.

## Evidence

**285 Python tests on Python 3.12.14 and 135 frontend tests passed.** Compilation, translation/documentation checks and `git diff --check` passed. Python 3.14 is absent from this runtime and was not rerun. No GitHub Actions or real HA/cloud/appliance/mobile calls were made. Tests use only fake credentials and mocked HTTP.

Transport tests execute the actual pinned controller `bypass_v2`, `_once` and `_unwrap` methods against our delegate and a mocked HTTP operation. They cover exact prepare-only submission, missing/unknown zones after login, permission revocation after login, disconnect/unload/cancel, expiry, wrong owner connection, shared lock, unknown/auth/malformed responses, no retry, history failure, explicit re-arm and prevention of a second HTTP call. Real binding tests cover registry/runtime identity, fresh-read requirements and a zone disappearing during refresh. The original missing/unknown-zone bug is retained as a separate isolated regression proving why our final boundary is necessary. Source extracts retain the upstream MIT license.

## Native acceptance before closing #1

Install the candidate with reviewed controller 1.0.3 or 1.0.4-beta.1 and restart HA. Start with card test mode enabled.

1. Set different values in both zones; inspect SYNC and MATCH previews. The appliance must remain unchanged. A missing/unknown/offline zone or invalid settings must prevent a real preparation.
2. For a supervised **settings-only** check, physically clear both zones and combined mode. Disable test mode, choose SYNC, verify both values in confirmation and accept once. Do not press Start. Both reported settings/combined mode should match and no heating should begin. Cancel prepared programs physically.
3. Repeat MATCH with different zone drafts: both should receive zone 1 settings. Cancel physically again. This is not a temperature-accuracy or cooking-duration test.
4. Repeat a canceled confirmation and a whole-device permission revoke with an ordinary user: no write. Check independent zone controls, saved history and completion settings remain available.
5. If an outcome is unknown, inspect the appliance and clear prepared programs physically; only then use explicit re-arm. No queued or automatic resend may occur.

Record actual outcomes; cloud mocks do not establish native device compatibility. #1 stays open until this focused acceptance is complete, **not** pending a controller modification.
