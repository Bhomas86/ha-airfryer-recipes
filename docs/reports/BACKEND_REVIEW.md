# Backend review – PR #13 and PR #14

[English](BACKEND_REVIEW.md) | [Deutsch](BACKEND_REVIEW.de.md)

As of 25 October 2026. Review of GitHub PR refs `a9137a6` (#13) and `bfe4f6d` (#14). The two confirmed defects were subsequently fixed by commit `5b3bfdc` directly on PR #13's feature branch.

## Project status

PR #12 is in `main`. PR #13 implements recipe CRUD, versioned storage and confirmed JSON import. PR #14 is stacked directly on it and adds nine WebSocket commands. The graphical recipe manager in Issue #6 has not started. Some architecture and roadmap status statements are outdated.

## PR #13: Findings

1. **Blocking: A valid library can become unreadable after restart.** `RecipeRepository._commit()` permits 500 recipes within all field limits. `async_load()` serializes stored data again and calls `import_library_json()`, which limits uploads to 1 MB. A reproducible offline check successfully stored 500 valid recipes, then failed to reload them with `RecipeValidationError: invalid or oversized JSON input`. Original data remained intact, but the integration cannot start. Stored-data validation must be separated from the upload limit and tested at the limits across restart.
2. **Medium: A confirmed import loses its confirmation token after a storage error.** `async_confirm_import()` removes the token before `_commit()`. A simulated `OSError` left data unchanged; after the error was cleared, the same attempt was rejected as expired. A new preview is necessary. A regression test is missing.
3. **Open: Migrations.** Version 1 is checked and later versions are safely rejected. An actual migration with rollback has not been implemented. The separate rolling snapshot is not a complete HA backup.

Positive results: CRUD and writes are serialized by a lock; failed writes do not publish new in-memory state. Import preview, duplicate detection and explicit conflict policy exist. Storage and integration do not require Airfryer Control. Tests cover restart, concurrent creates and simulated storage failures.

## PR #14: Architecture and security

Read commands use the authenticated HA connection; mutations and import/export use server-side `require_admin`. Client `is_admin` fields are ignored. The recipe model validates fields and bounds JSON uploads; unexpected storage failures return no internal paths to clients. The API contains no device commands. Authorization was tested only with an HA stub, not a real HA instance. PR #14 inherits PR #13's storage defect. Issue #6 therefore lacks a reliable restart check and a real HA test of registration and permissions.

## Checks and next steps

PR #13: compilation and 36 offline tests passed. PR #14: compilation and 48 offline tests passed. GitHub's public check pages show successful Python 3.12/3.14, Hassfest and HACS checks for the reviewed PRs; API access to detailed PR metadata was denied. Two focused reproductions confirmed the size and import defects. No product code was changed.

Both fixes are in commit `5b3bfdc`: separate validation for local storage and JSON uploads, and retryable import confirmation after a storage failure. Two regression tests were added. Subsequently, 38 offline tests passed on the PR #13 base and 50 passed on the PR #14 base with the fix commit. Real HA checks remain necessary before Issue #6: configure without Airfryer Control, verify recipes survive restart, test backup recovery on a test copy, verify administrator and regular-user permissions, and send malformed WebSocket requests. No device commands are needed. GPT-6 Sol – High remains suitable for renewed review; reassess if migration or a confirmed authorization defect proves more complex.
