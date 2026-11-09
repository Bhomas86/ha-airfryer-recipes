# Reviewed controller transport sources

[English](README.md) | [Deutsch](README.de.md)

The owner requires controller-independent protection. The previous patch proposal was removed; **no controller patch is required, installed or submitted**. Production uses our own guarded sender, not the upstream SYNC/MATCH actions. [Current implementation](../reports/ISSUE_1_OWN_GUARD.md).

Test-only extracts originate from `misterm2310/airfryer-control`, commit `75d30c800ae79eea2254e5d4f5da31ec154398e7`, copyright (c) 2026 misterm2310, under the MIT license retained in [LICENSE.airfryer-control](LICENSE.airfryer-control):

- `tests/fixtures/controller_103_sync_functions.py.txt`: actual combined sender functions, retained to reproduce the original unknown/missing-zone defect with mocked device calls.
- `tests/fixtures/controller_103_transport.py.txt`: actual `bypass_v2`, `_once`, `_unwrap`, exercised with our guard and a mocked HTTP boundary. The complete `core/api.py` source is identical in reviewed 1.0.3 and 1.0.4-beta.1.

No upstream code is installed as a production controller. Our adapter composes the existing loaded transport without replacing any controller attributes or functions. Login/error handling stays with the transport; final report/identity/permission/expiry checks and one-shot submission are enforced by our integration.
