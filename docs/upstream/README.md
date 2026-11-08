# Controller state-guard proposal

[English](README.md) | [Deutsch](README.de.md)

`controller-sync-state-guard.patch` is a proposed change for `misterm2310/airfryer-control` stable 1.0.3, commit `75d30c800ae79eea2254e5d4f5da31ec154398e7`. It is **not installed**, not applied to the user's controller and not submitted upstream. It adds a fail-closed report guard before reset writes and immediately before the combined write. Both zone reports must exist, be explicitly inactive and safely idle (or prepared only during authorized reset preparation), with online/error checks and a report at most 15 seconds old. It does not add retries or start heating.

Review the 15-second freshness bound against the controller's actual successful refresh contract. This remains a proposal pending upstream review, complete controller tests and native acceptance. Apply to a clean controller checkout using `git apply --check /path/to/controller-sync-state-guard.patch`, then `git apply /path/to/controller-sync-state-guard.patch`. Do not patch a running installation blindly. This repository's tests execute only extracted functions with mocked device APIs.

The extracted fixture `tests/fixtures/controller_103_sync_functions.py.txt` originates from that commit's `senden.py`, copyright (c) 2026 misterm2310, under the MIT license retained in [LICENSE.airfryer-control](LICENSE.airfryer-control). Proposed changes retain that license. The fixture is for isolated contract regressions, not a vendored production controller.

Airfryer Recipes' `multi_contract.py` prepares exact service envelopes and validates response echoes. Preview identifies only the two reviewed versions and current-snapshot blockers. None of this enables live transmission: a preflight check cannot protect the controller's later refresh/write boundary. [Review and remaining gap](../reports/ISSUE_1_CONTROLLER_103.md).
