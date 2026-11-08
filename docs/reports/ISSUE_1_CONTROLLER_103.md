# Controller 1.0.3: SYNC/MATCH follow-up review

[English](ISSUE_1_CONTROLLER_103.md) | [Deutsch](ISSUE_1_CONTROLLER_103.de.md)

Reviewed 2026-11-08: stable `v1.0.3` at `75d30c800ae79eea2254e5d4f5da31ec154398e7` and current `v1.0.4-beta.1` at `ca92b375547c75b698e25a21f8a8734688174e47` in `misterm2310/airfryer-control`. This supersedes the earlier beta.3/beta.4 contract findings where noted below. The owner's earlier successful SYNC/MATCH action tests remain valid local evidence; no new appliance testing was performed here.

## Implemented upstream

`services.py` now accepts `zone1`/`zone2` with `programm`, `temperatur`, `minuten`, MATCH `quelle`, `einmal`, `streng` and `zuruecksetzen`. The actions support optional structured responses (`ok`, `ergebnis`, `gesendet`, `revision_vorher`). `sync_plans` accepts explicit values and rejects out-of-range values under strict mode. The caller must still supply explicit source values rather than relying on default input helpers.

`async_send_sync(..., once=True, reset=False)` passes `retry=False` to the combined write and avoids reset writes. The busy helper now raises `SyncBlocked`, aborting the outer routine. This resolves the previously reported busy-return defect. `readyStart: true` remains fixed in the payload. Automatic reset remains the upstream default, so an eventual integration must explicitly use `zuruecksetzen: false`, `einmal: true`, `streng: true` and request a response.

## Remaining reproduced issue

`_check_and_reset` rejects offline, members of `BUSY`, and members of `PREPARED` when reset is disabled. It does not require both zone reports to exist or their statuses to be explicitly safe. `_zone_status` returns `None` for a missing zone; an unrecognized status is also absent from both sets. Both cases return from the check normally, allowing `startMultiCook`.

An idle check in Airfryer Recipes before the action cannot close this gap: the controller refreshes again inside its action and can obtain a different or incomplete report. No private-API bypass, monkey-patching or live enablement was added.

## Offline experiment and results

Executed the actual function/class ASTs from each pinned `senden.py`: `build_sync_payload`, `_zone_status`, `SyncBlocked`, `_check_and_reset`, `async_send_sync`. External coordinator/API objects were mocked; type annotations deferred. The BUSY/PREPARED sets used the matching controller state strings. Explicit plans were supplied; `once=True`, `reset=False`. Both refresh methods and the API write were `AsyncMock`, so **no device, cloud or network call occurred**.

| Case after mocked refresh | 1.0.3 | 1.0.4-beta.1 |
| --- | --- | --- |
| Both zones ready | One mocked write; retry false; readyStart true | Same |
| Zone 1 cooking | Blocked, zero writes | Same |
| Zone 1 prepared | Blocked, zero writes | Same |
| Offline | Blocked, zero writes | Same |
| Zone 2 absent | **One mocked write** | **One mocked write** |
| Zone 1 unknown | **One mocked write** | **One mocked write** |

These are 12 isolated contract cases, not the project test suite or a real HA integration/device acceptance. No full suite was rerun for this documentation-only review. No GitHub Actions triggered.

## Focused requested correction

After refresh, fail closed unless **both** zones are present and explicitly in an allowed inactive state; missing/unknown states must raise `SyncBlocked` before any reset/write. Also verify online, absence of report errors and fresh successful report metadata at that boundary. Keep this check before the combined write, including after any authorized reset. Add regressions for a zone missing after refresh and an unknown zone status; both must result in zero `bypass_v2` calls.

A minimal reproducer in the controller's existing test environment can provide a mocked coordinator whose `async_refresh` returns normally and a fryer with `online=True`, `state.zones={1: SimpleNamespace(status="bereit")}`, and a mocked `api.bypass_v2`. Invoke `async_send_sync` with two explicit valid plans, `once=True`, `reset=False`: the current implementation calls `bypass_v2` once. Repeat with both zones present but zone 1 status `"unbekannt"`; the result is the same. Expected: `SyncBlocked` and zero writes.

Issue #1 and live combined transmission remain open pending the correction, re-review and focused native acceptance. Existing per-zone sending and preview are unchanged. Controller 1.0.3/1.0.4 has not been added to our live-version allowlist merely because its new API exists.

## Follow-up implementation in PR #48

The owner authorized publishing this review and continuing development. `multi_contract.py` now builds exact immutable zone values, fixed `quelle: 1`, `einmal: true`, `streng: true`, `zuruecksetzen: false`; validates consistent structured outcomes and exact typed echoed values; and identifies reviewed controller versions without enabling live calls. The planner additionally checks current report age/revision, missing/duplicate/unknown zones and displays the remaining controller guard gap in English/German. Every preview still returns `transmitted: false` and `live_send_enabled: false`. No transport function or private API bypass was added.

A concrete [controller patch proposal](../upstream/README.md) is included, with pinned, attributed upstream function fixtures. Tests reproduce the unpatched missing/unknown-zone write, then exercise the proposed guard against those states, stale data and a zone disappearing during refresh. A valid idle report still results in exactly one mocked prepare-only write with retry disabled. The proposed patch applies to the pinned source and compiles. It has not been installed or submitted to the controller project; full upstream/native acceptance remains outstanding.

Current local results: **266 Python tests on Python 3.12.14 and 133 frontend tests passed**, compilation and formatting checks passed. The final added reset-loop guard was followed by the 16 targeted multi-zone/contract tests, which passed. Python 3.14 is not installed in the current runtime and was not rerun for these changes. No Actions, real device calls or mobile notifications were triggered. The earlier 259-test dual-version result applies only to the previous implementation.
