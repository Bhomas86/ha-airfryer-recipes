# Roadmap — Airfryer Recipes

[English](ROADMAP.md) | [Deutsch](ROADMAP.de.md)

**b26 acceptance / b27 download fix (2026-11-09):** Owner confirms SYNC/MATCH, canceled confirmation, no heating start, diagnostic export, restart persistence and exactly one actual completion notice. PR #48 merged under conditional approval. Follow-up replaces cryptic blob filenames with an authenticated, named HTTP attachment of the same preview. Native filename verification pending; no send changes. [Acceptance and checks](reports/B26_ACCEPTANCE_AND_DOWNLOAD.md).

**b26 test-beta release preparation (2026-11-08):** Owner requests a published beta and authorizes PR #48 approval after successful tests. Keep PR open until native results are confirmed. Includes #1 and #10 acceptance, current final validation and stable 0.1.0 preparation. No new code or Actions. [Release and test checklist](releases/0.1.0b26.md).

**Owner decision / b26 (2026-11-08):** Protection is implemented in Airfryer Recipes without controller changes. Own one-shot sender validates both zones after login at the HTTP boundary, shares locks/uncertain outcomes and supports exact confirmation plus server dry run. Controller-patch dependency removed. 285 Python 3.12 and 135 frontend tests passed; native acceptance pending. [Current behavior and tests](reports/ISSUE_1_OWN_GUARD.md).

**Authorized continuation (2026-11-08):** PR #48 now includes the controller follow-up report, explicit request/strict response preparation, conservative snapshot blockers, and a tested upstream state-guard patch proposal. Live SYNC/MATCH remains disabled pending controller correction. 266 Python 3.12 and 133 frontend tests passed; 3.14 unavailable in this runtime. [Current scope](reports/ISSUE_1_CONTROLLER_103.md).

**Controller review (2026-11-08):** Stable 1.0.3 and beta 1.0.4-beta.1 now provide explicit values, strict/once/reset options and structured SYNC/MATCH results. The busy-return defect is fixed. Twelve isolated real-function/mock-API cases still reproduce sending with a missing/unknown zone. Live #1 remains blocked; existing owner-reported successful action tests remain valid. [Evidence and focused correction](reports/ISSUE_1_CONTROLLER_103.md).

**Issue #1 (2026-11-05):** PR #47 merged with owner authorization. b25 development adds separate, server-validated SYNC/MATCH previews; no combined device sends. Reviewed controller beta.3 and current beta.4 still lack explicit strict one-shot values and safe prepared-zone handling. Live #1 remains blocked pending a public upstream contract and native acceptance. [Evidence and exact requirements](reports/ISSUE_1_SYNC_MATCH.md).

**Issue #10 (2026-11-05):** b24 development implements administrator-only allowlisted diagnostic preview/download and opt-in Companion completion notices. Default-off, fresh cooking→finished reports only; no replay or retry. Native acceptance remains pending. PR #46 b23 Actions passed. [Scope and checks](reports/ISSUE_10_SUPPORT.md).

**b23 (2026-11-04):** Owner confirms the focused b22 save/restart check and requests removal of unverified limit/send comments. Program selections now display only localized names; missing-program warnings and backend capability data/checks remain. Official HACS/Hassfest evidence is still separate. [Change and checks](releases/0.1.0b23.md).

**b22 final review (2026-11-04):** Owner confirms the completed 44-step reported-value sequence, card and Proof recipe workflow. Fix favorite capacity/deleted-reference accumulation and verify native Store files after writes. 232 Python tests per 3.12/3.14 plus 125 frontend tests passed. Current native save/restart and official HACS/Hassfest evidence remain pending before a candidate. [Review and scope](reports/FINAL_REVIEW.md).

**b21 (2026-11-04):** Owner confirms both b20 styles; B becomes first/default without a standalone UI release. Review/pin controller 1.0.3-beta.3, enable model-specific temperatures and Proof with unverified provenance, and expand the supervised run to 44 settings on both zones. Native endpoint/Proof acceptance pending. [Review and test table](reports/ISSUE_7_CONTROLLER_BETA3.md).

**b20 (2026-11-04):** Owner requests both approved artwork designs as a card setting. A uses a thin active outline and small markers; B uses invisible but tappable configured image zones, with visible selection beside the photo. Designer rectangles stay visible for positioning. Implemented; native acceptance pending. [Settings and checks](releases/0.1.0b20.md).

**b19 (2026-11-03):** Owner confirms b18 custom-image saving after a page reload. Add same-page card refresh after successful saves, refresh on reattachment and visible save feedback; preserve device permissions and cooking drafts. New native refresh acceptance pending. [Fix and local checks](releases/0.1.0b19.md).

**b18 (2026-11-03):** Owner confirmed b17 editor. Private device gallery/uploads and relative zone boxes with admin-only writes implemented; new native acceptance pending. [Setup and limits](releases/0.1.0b18.md).

**b17 (2026-11-03):** Three local b16 grant checks passed. Add card sizes, independent graphic size and status/history display switches; preserve defaults and backend checks. [Implementation and checks](releases/0.1.0b17.md).

**b16 whole-device access (2026-11-02):** After basic card/history/restart acceptance, implement admin-managed user/device grants only, per the owner's correction: every zone and available program belongs to the device grant. Add scoped discovery/history/dry-run/supervised sending and revocation checks; keep recipe/security management and batch tools admin-only. 203 Python/93 frontend tests passed locally; new native two-account acceptance pending. [Implementation and procedure](reports/ISSUE_8_DEVICE_ACCESS.md). No GitHub Actions.

**b15 resource registration (2026-11-02):** Owner confirms b14 display after manual module registration. Register/update that same dashboard resource automatically in storage mode, preserve manual entry/other resources and retain YAML fallback. Keep only the current beta published; preserve older releases as drafts with tags/code/assets. 178 Python/84 frontend tests passed locally; automatic native acceptance pending. [Evidence and procedure](reports/ISSUE_8_CARD_RESOURCES.md). No GitHub Actions.

**Card loading correction 0.1.0b14 (2026-11-02):** Reproduced duplicate registration when a recipe panel already existed; guard its definition and import the current base class directly. Four full ES-module loading tests added; 170 Python/84 frontend tests passed locally. Owner confirmed b13 installed; native b14 visibility remains pending. [Evidence and fallback](reports/ISSUE_8_CARD_LOADING.md). No GitHub Actions.

**Dashboard beta 0.1.0b13 (2026-11-02):** Approved neutral design 1A implemented with separate persistent last-sent settings per zone, recipe/manual controls and visual editor. Default dry run; live controls reuse the existing administrator-only supervised beta. Ordinary-user backend device ACLs, personalization and native HA/Companion acceptance remain pending. [Implementation and local procedure](reports/ISSUE_8_DASHBOARD_CARD.md). 170 Python/80 frontend tests passed locally. No GitHub Actions.

**Recipe acceptance 2026-11-01: R1/R2 reported passed.** Following the editor correction, the owner confirms saved-recipe transmission on zones 1 and 2. R3–R7 and remaining editor variants stay separately pending. [Evidence and next checks](reports/ISSUE_7_LOCAL_ACCEPTANCE.md). Dashboard with backend user permissions remains the next implementation package after focused acceptance. Documentation only; no new release or GitHub Actions.

**Local acceptance 2026-11-01: All twelve steps PASS.** The owner confirmed the complete guided sequence with six programs on zones 1 and 2 and the appliance off afterward. [Exact settings and evidence limits](reports/ISSUE_7_LOCAL_ACCEPTANCE.md). Next open device work: model-aware adapter limits and Proof, followed by focused endpoint/error acceptance. No new app update or GitHub Actions for this documentation follow-up.

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

Owner requirement: a supervised stopped test must allow a new attempt without HA restart. Beta 0.1.0b7 permits explicit re-arming only after a fresh idle-state check, invalidating old tokens; no replay. [Implementation and unresolved failure](reports/ISSUE_7_MANUAL_RECOVERY.md). No GitHub Actions.

Beta 0.1.0b8: Integrate owner-identified zone switches to end own prepared settings before program changes. Fresh per-zone checks, turn_off only, no global stop. [Behavior and acceptance](reports/ISSUE_7_ZONE_RESET.md). No GitHub Actions.

Beta 0.1.0b9: Both individual-test buttons use the same form selection; scroll confirmation/errors into view. Limit Dry to 35–95 °C (owner report); sequence uses 55 °C / 360 minutes after successful single tests on both zones. This does not establish a minimum duration. [Correction and acceptance](reports/ISSUE_7_SELECTED_TEST_SETTINGS.md). No GitHub Actions.

Beta 0.1.0b10: Store and display seven owner-reported Turbo Tower temperature ranges separately from adapter capabilities. Supervised sending additionally enforces model limits while retaining reviewed adapter bounds; full ranges and Proof require an upstream change. [Profile and intersection](reports/ISSUE_7_MODEL_TEMPERATURES.md). No GitHub Actions.

Beta 0.1.0b11: Bind recipe/manual confirmations to the websocket; support server revocation before control submission, reject stale UI replies and offline requests. Twelve recipe transmissions simulated through routes/repository/sender with unchanged data. [Implementation and seven focused appliance cases](reports/ISSUE_7_RECIPE_LIFECYCLE.md). New real acceptance pending; dashboard with backend user permissions follows. Proof/wider temperatures deferred. No GitHub Actions.

Beta 0.1.0b12: Recipe editor dropdown uses programs reported by the selected air fryer; save exact identifiers and correct old identifiers only after explicit selection and saving. Custom/no-adapter input remains supported and drafts survive rerenders. [Implementation and repeated recipe acceptance](reports/ISSUE_7_EDITOR_PROGRAM_PICKER.md). This does not authorize sending or add programs. No GitHub Actions.
