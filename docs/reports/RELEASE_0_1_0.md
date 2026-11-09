# Final release gate — 0.1.0

[English](RELEASE_0_1_0.md) | [Deutsch](RELEASE_0_1_0.de.md)

Owner instruction on 2026-11-09 explicitly authorizes merging PR #49, running final Actions, then merging the new release PR and publishing stable 0.1.0 **only after successful checks**. This overrides the earlier Actions pause for this release package; no repeated merge/publication permission is required. The owner accepts the download filename correction without a further native phone test. PR #49 was merged before this release branch was prepared.

## Reviewable final scope

The release branch updates manifest/frontend/cache versions to 0.1.0, changes normal-card beta wording to settings-only/manual-start wording and consolidates outdated beta READMEs into current bilingual setup/support instructions. It includes stable DE/EN release notes and records this explicit authorization. No change to control, permission, storage, diagnostic or notification algorithms; no schema migration.

Functional owner acceptance is documented in [b26 acceptance](B26_ACCEPTANCE_AND_DOWNLOAD.md). Our single-device/explicit-controller scope, coupled transport internals, conservative state checks, manual start, no retry and no cross-model compatibility promise remain. No real device/cloud/phone test is claimed from CI.

## Required gate and evidence handling

Create one release PR with `[full-ci]` in its title and a commit without skip-ci. Its changed manifest triggers HACS/Hassfest; its frontend/version changes trigger the full Python 3.12/3.14 matrix and frontend tests. This avoids duplicate full validation of the same code before/after merge. Inspect all job conclusions and retain the run URLs and exact tested PR head in the PR description and GitHub release.

Do not merge or publish if any required job fails. Correct relevant failures on this branch, rerun the checks needed for the changed state and wait for success. No unrelated workflow changes or bypass of a failed check.

After green results, re-read the PR head and merge it using the expected SHA. Verify the resulting main commit tree equals the tested head tree. Create tag `v0.1.0` at that main commit. Prepare a bilingual stable release (`prerelease: false`) and verify tag, manifest version and tree before publishing. Retain every older tag/commit/asset. Only after stable publication is verified, retire the currently published beta to draft so HACS presents stable 0.1.0 as the current release. Verify the final release list and issue/PR state.

Close #10 after the required validation and stable publication. #1 is already completed after owner acceptance; no new device test is requested. Historical reports preserve their original evidence limits, including unavailable intermediate 3.14 runs and the superseded controller-patch proposal.
