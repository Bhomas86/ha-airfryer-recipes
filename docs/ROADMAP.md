# Roadmap — Airfryer Recipes

[English](ROADMAP.md) | [Deutsch](ROADMAP.de.md)

**Status (2026-10-29):** All 31 requirements are agreed. Recipe storage, authenticated API and locally accepted administrator management are merged. PR #19 with device preview and program selection was merged on 2026-10-25; HACS prerelease `0.1.0b2` passed phone acceptance. PR #20 corrects the HACS version listing. Issue #7 remains open for safe live transmission: the beta contract and model-specific capabilities require local verification. The dashboard (#8) follows. See the [acceptance report](reports/ISSUE_7_DRY_RUN_UI.md) and [architecture](ARCHITECTURE.md).

**Review on 2026-10-30:** The unchanged beta contract still does not justify live approval. Model-specific evidence and fresh device confirmation remain missing; see the [contract re-review](reports/ISSUE_7_BETA_REVIEW.md).

**Next test package 0.1.0b3:** Separate supervised interface test before appliance acceptance, requested by the owner. No normal device control or compatibility approval. [Implementation and local tests](reports/ISSUE_7_BETA_SEND.md).

**Beta correction 0.1.0b4:** The first local attempt was blocked before sending by the freshness gate. Preparation now requests one new read-only status query. Real transmission remains unaccepted. [Review and repeat test](reports/ISSUE_7_STATUS_REFRESH.md).

**Local acceptance 2026-10-30: Both zones PASS** for Air Fry at 170 °C for one minute, without heating or changing the other zone. Next package: bounded recipe/manual transmission in the administrator panel. [Acceptance and limits](reports/ISSUE_7_LOCAL_ACCEPTANCE.md). Further updates temporarily use no GitHub Actions.

## Implementation priorities and dependency order

| Stage | Issue | Deliverable | Dependency | Verification |
| --- | --- | --- | --- | --- |
| 0 · Foundation | [PR #2](https://github.com/Bhomas86/ha-airfryer-recipes/pull/2) | Recipe model, JSON codec, tests, 31 bilingual requirements, architecture, Codex policy | Owner review | Python 3.12/3.14 CI; source review |
| 1 · HA shell | [#3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3) | Installable integration skeleton, config flow, localization, HACS metadata | PR #2 | HA startup without upstream adapter |
| 2 · Persistence | [#4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4) | Versioned Store, CRUD, migrations, JSON import/export | #3 | Restart/migration/invalid input tests |
| 3 · Authenticated API | [#5](https://github.com/Bhomas86/ha-airfryer-recipes/issues/5) | Server-side authorization and typed WebSocket operations | #3, #4 | Admin vs normal user and malformed request tests |
| 4 · Recipe editor | [#6](https://github.com/Bhomas86/ha-airfryer-recipes/issues/6) | Responsive German/English admin panel | #4, #5 | CRUD/permissions tested without air fryer |
| 5 · Safe device link | [#7](https://github.com/Bhomas86/ha-airfryer-recipes/issues/7) | Airfryer Control adapter, verified device cooking programs, safe send coordinator, dry-run | #3, #5 | Mock-based safe sends; local Cosori checklist |
| 6 · Main dashboard | [#8](https://github.com/Bhomas86/ha-airfryer-recipes/issues/8) | Interactive zones, recipe/manual selection, device-specific program choices, feedback, graphical card editor | #4, #5, #7 | Phone/tablet render; both zones, cooking programs and offline behavior |
| 7 · Personalization | [#9](https://github.com/Bhomas86/ha-airfryer-recipes/issues/9) | Device image gallery, optional safe uploads, draggable hotspots | #8 | Responsive positions, permissions and upload safety |
| 8 · Beta readiness | [#10](https://github.com/Bhomas86/ha-airfryer-recipes/issues/10) | HACS beta, bilingual release docs, diagnostics, optional completion push | #3–#8, optional #9 | CI + local HA/real-device tests |
| Later | [#1](https://github.com/Bhomas86/ha-airfryer-recipes/issues/1) | SYNC and MATCH dashboard buttons using existing upstream actions | #7, #8 | Real-device confirmation and safety checks |

**Proposed follow-up to #6:** Rename a category across all affected recipes or merge it into another, for example “Backen” into “Aufbacken”. Define the preview, permission check, safe persistence and rollback behavior before implementing it. The current selection list does not change existing categories automatically.

**Program selection after #7:** The administrator dry-run preview reads program choices from Airfryer Control's public capability service and visibly labels confirmed, estimated and unreported values. The later recipe-editor guidance and send controls will use only verified device data and validate it again in the backend. Recipes will not store a fixed device binding.

## Development ownership and workflow

- **ChatGPT can prepare:** architecture, data models, Python utilities, tests, documentation, reviews, small bounded feature branches and PRs.
- **Codex can implement:** larger Home Assistant lifecycle changes, administrative panel, adapter and dashboard features in focused task packages. Apply the [AGENTS.md model policy](../AGENTS.md) before each package: **GPT-6.1 Sol exclusively**, with **Low, Medium or High** reasoning effort. Low suits simple tasks, Medium normal development, and High complex architecture or safety work. This policy applies from 2026-10-29 and supersedes older model recommendations in issues and reports.
- **GitHub Actions:** Limited allowance: prefer targeted local checks and small, path-filtered automatic PR checks. Schedule the full Python matrix and comprehensive HACS/Hassfest acceptance at larger section boundaries or before releases. No code CI for documentation-only changes and no additional automatic merge runs. Mocks only; no real-device access or credentials.
- **Owner/local Home Assistant:** integration install/restart and real Cosori tests. Use the [local checklist](LOCAL_TEST_CHECKLIST.md).
- **Pull requests:** feature branches, bilingual German-first reports/PR bodies, tests and review before merging. Never automatically merge.

## First useful milestones

**Milestone A — Recipes work without air fryer** after #3–#6: create, edit, import/export and retain recipes through restart on a HA instance, with correct admin permissions.

**Milestone B — Safe end-to-end device configuration** after #7–#8: tap Cosori zone, select a recipe or manual values, review and explicitly transmit, without starting heat remotely; visible connection status and errors.

**Milestone C — Polished HACS beta** after #9/#10 as appropriate: graphical customization, tests, help/docs, optional reliable completion notification, diagnostics and releases.

Avoid promising release dates before a real installation and safety testing are complete.

## Release quality requirements

- Passing CI and Home Assistant integration startup checks
- No blocking file I/O in async event loop
- No silent remote start, offline replay, auto-retry or dry-run device commands
- Correct read/admin permissions enforced by backend
- Backups before schema migrations and safe JSON import conflict handling
- Full **English and German** UI, issues, PR descriptions, docs, test reports and release notes; German first for reports
- Local Cosori tests documented as PASS / FAIL / NOT TESTED without claiming unperformed verification

Beta 0.1.0b5: At the owner’s request, supervised recipe/manual transmission for all six currently reported IDs in the reviewed contract. No general model approval. [Implementation and limits](reports/ISSUE_7_RECIPE_SEND.md), [60-case acceptance](reports/BETA_0_1_0B5_TEST_PLAN.md). Local validation only; no GitHub Actions.

Owner decision: one confirmation for the complete supervised list, then sequential single steps with fresh state checks and stopping. Beta 0.1.0b6 contains at most twelve ordinary test settings across both zones, not automatic cooking. [Implementation and acceptance](reports/ISSUE_7_GUIDED_BATCH.md). No GitHub Actions.
