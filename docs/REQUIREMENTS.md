# Requirements — Airfryer Recipes

[English](REQUIREMENTS.md) | [Deutsch](REQUIREMENTS.de.md)

**b22 final review (2026-11-04):** Owner confirms the completed 44-step reported-value sequence, card and Proof recipe workflow. Fix favorite capacity/deleted-reference accumulation and verify native Store files after writes. 232 Python tests per 3.12/3.14 plus 125 frontend tests passed. Current native save/restart and official HACS/Hassfest evidence remain pending before a candidate. [Review and scope](reports/FINAL_REVIEW.md).

**b21 (2026-11-04):** Owner confirms both b20 styles; B becomes first/default without a standalone UI release. Review/pin controller 1.0.3-beta.3, enable model-specific temperatures and Proof with unverified provenance, and expand the supervised run to 44 settings on both zones. Native endpoint/Proof acceptance pending. [Review and test table](reports/ISSUE_7_CONTROLLER_BETA3.md).

**b20 (2026-11-04):** Owner requests both approved artwork designs as a card setting. A uses a thin active outline and small markers; B uses invisible but tappable configured image zones, with visible selection beside the photo. Designer rectangles stay visible for positioning. Implemented; native acceptance pending. [Settings and checks](releases/0.1.0b20.md).

**b19 (2026-11-03):** Owner confirms b18 custom-image saving after a page reload. Add same-page card refresh after successful saves, refresh on reattachment and visible save feedback; preserve device permissions and cooking drafts. New native refresh acceptance pending. [Fix and local checks](releases/0.1.0b19.md).

**b18 (2026-11-03):** Owner confirmed b17 editor. Private device gallery/uploads and relative zone boxes with admin-only writes implemented; new native acceptance pending. [Setup and limits](releases/0.1.0b18.md).

**b17 (2026-11-03):** Three local b16 grant checks passed. Add card sizes, independent graphic size and status/history display switches; preserve defaults and backend checks. [Implementation and checks](releases/0.1.0b17.md).

Status: **Agreed product requirements, not an implemented feature list**.
Last consolidated: 2026-10-24. Project language policy: English default UI language; complete English and German documentation, with German-first reports to the project owner.

## Confirmed requirements

| # | Decision | Details |
| --- | --- | --- |
| 1 | Device-independent recipes (B) | Choose appliance and cooking zone only when sending. |
| 2 | Single phase, extensible schema (B) | MVP uses one phase; data model can support multiple phases later. |
| 3 | Separate recipe management (A) | A dedicated Home Assistant management view plus a simple dashboard card. |
| 4 | Graphical dashboard, status and manual control | Appliance illustration with tappable zone 1/2. Each zone supports recipe dropdown **or** manual time/temperature/program. Show status and remaining time when reported; explicit Send button. |
| 5 | Adapter architecture (B) | First adapter for Airfryer Control, additional integrations later. |
| 6 | Running-zone safety (A + optional B) | By default block changes while cooking. Admin may enable with confirmation in card editor, only when device supports it. Unknown status blocks. |
| 7 | Device graphics (C) | Recognizable model images; neutral fallback when unknown. |
| 8 | Remember manual values (C) | Remember most recent manual values per device and zone across restarts; optionally save as a new recipe; never overwrite existing recipe silently. |
| 9 | Independent multi-zone operation (B) | Both zones remain independently selectable/visible; later optional SYNC/MATCH UI. **Upstream Airfryer Control already exposes SYNC and MATCH actions, but not in its device overview**. Verify signatures and behavior. See issue #1. |
| 10 | Optional completion notifications (B) | Disabled by default; opt into mobile push to chosen recipient/device; only on reliable completion signal. |
| 11 | Rich recipe organization (C) | Categories, favorites, search, free-form tags, recently used. In the recipe editor, choose an existing category or add a new one as the final option; reuse names that differ only in letter case. |
| 12 | JSON import and export (B) | Single or all recipes; validate schema and detect duplicates; use a human-readable export filename. Keep local HA backups. |
| 13 | Visual card editor + device personalization (B+) | Toggle labels/status/timer, choose graphic size; 'Customize Airfryer' opens gallery, own image upload, drag/drop zone hotspot positions stored in relative coordinates per device, and reset. Include a 'Missing your model?' GitHub issue link. Per-card A/B setting: A shows a subtle active outline and small zone markers; B keeps the same configured touch areas invisible on the active dashboard. Positioning/resizing rectangles remain visible in the designer (owner decision 2026-11-04). Both styles accepted; B is first/default when no explicit style is configured (owner decision 2026-11-04). |
| 14 | Automatic discovery + profile fallback (B) | Detect model, zones and supported capabilities from adapters where possible; verified profiles fill gaps. Once the adapter exists, offer verified cooking programs as choices in the recipe editor while keeping recipes device-independent. Unknown controls remain off. |
| 15 | Manual retry, offline UI (B+) | Show sending/error details; preserve selected settings; never auto-retry. Offline graphic grayed out and sending disabled; show distinct unknown state. |
| 16 | Independent recipe library (B) | Missing or broken Airfryer Control must not prevent editing/importing/exporting recipes. |
| 17 | Two permission levels (B) | Administrators edit/delete recipes and configure safety; normal HA users may select recipes and manually control explicitly shared whole devices, including every zone and available program. No per-zone/program/menu grants (owner correction 2026-11-02). Enforce in backend. |
| 18 | Localization and units | English and German as for Battery Flow Card; **English default/fallback**. Use HA user language; temperature displayed according to HA °C/°F setting, stored in Celsius. User recipe names are not auto-translated. |
| 19 | Versioned data with migrations (B) | Persist locally; migrate on updates only after backup; preserve originals on failure; HACS updates do not replace storage. |
| 20 | Device compatibility adaptation (B) | Offer only verified cooking programs of the selected air fryer in device controls. If program/time/temp is unsupported, warn and propose available substitutions; require explicit user approval; original recipe unchanged. |
| 21 | Shared and personal preferences (C) | Shared recipes and default favorites; optional personal favorites; recent-use history per device and zone. |
| 22 | Responsive UI with configurable size (B) | Auto layout for phone/tablet/desktop; compact/default/large options; proportional graphics/hotspots. |
| 23 | Simple recipes only (A) | Name, optional description, category/tags, favorite, program, temperature and duration; no recipe photos, ingredients or detailed cooking instructions. |
| 24 | Dashboard first; actions later (A + planned B) | MVP is interactive card. Internal sending API designed to allow future HA actions/scripts; do not prioritize them now. |
| 25 | Safe diagnostic export (B+) | Allowlisted technical data, secrets never included, warning/preview before download; explicitly tell user passwords/tokens/login data are excluded, and to review the export. |
| 26 | Optional dry-run mode (B) | Card editor option; full UI, but server-side no device control calls; show would-be payload and label clearly. |
| 27 | Guided onboarding (B) | Detect device if present, choose model/zones, optional sample recipes, help add card; permit setup without appliance. |
| 28 | Stable releases + beta (B) | HACS via GitHub Releases; optional prereleases, CI checks, English/German release notes; no automatic breaking migrations. |
| 29 | Automated + real tests (B) | Offline mock CI, documented local test checklist; real Cosori test only on user's HA, no cloud/LAN access for Codex. |
| 30 | Structured GitHub/Codex workflow (B) | AGENTS.md, bilingual requirements/roadmap/reports and issue/PR descriptions, dedicated branches, automated checks. Enforce explicit model/task check and escalation rules in AGENTS.md. From 2026-10-29: GPT-6.1 Sol exclusively, with Low, Medium or High reasoning effort; supersedes earlier model recommendations. Use Actions sparingly: small targeted development checks, full runs at section boundaries; no code CI for documentation-only changes or duplicate merge runs. |
| 31 | Modular Home Assistant architecture (B) | One HACS package with Python backend, separate admin recipe panel and Lovelace dashboard card, versioned local store, authenticated backend API and replaceable device adapters. No additional services. See [Architecture](ARCHITECTURE.md). |

## Core user workflow

1. Admin creates a device-independent recipe with one cooking phase.
2. A user selects a supported air fryer and taps a zone on its image.
3. User chooses a saved recipe or manually sets program, temperature and time.
4. System validates device availability, capability, supported ranges and
   current zone state. On mismatch, it offers adaptations for confirmation.
5. User **explicitly** sends settings; appliance safeguards and manual-start
   requirements remain in force.
6. Show per-zone state and completion when accurate telemetry exists.

## Safety and privacy invariants

- No implicit heating start or timing-based remote-start workaround.
- No queued commands or auto-replays after reconnection, no automatic retry.
- Dry run means **zero backend device-control calls**.
- Unknown/offline state blocks sending; running changes need admin opt-in,
  explicit confirmation, and device support.
- Backend enforces permissions and safety even if UI is bypassed.
- Diagnostics are allowlist-based and exclude sensitive data.

## Out of scope for MVP / later enhancements

- Multi-phase cooking sequence execution (schema must remain extensible).
- SYNC and MATCH dashboard actions (issue #1); upstream exposes actions,
  but exact payload, device support and correct ordering need integration tests.
- Home Assistant automation service actions and voice control.
- Recipe photos, ingredients and full cooking instructions.
- Additional device adapters beyond Airfryer Control.

## Validation and acceptance

- Owner accepted the basic card flow: sends to both zones, reuse after physical reset, separate last-sent settings and persistence across HA restart. b16 adds explicit whole-device grants for ordinary users with backend enforcement and an admin management section. New native permission acceptance remains pending; ordinary users have no grants by default. [Evidence, scope and checklist](reports/ISSUE_8_DEVICE_ACCESS.md).

- 2026-11-02: Owner confirms b14 card display after manually adding the dashboard module resource. Beta b15 implements automatic resource creation/update, preserving that entry; automatic native acceptance and card transmission/history tests remain pending. Only the current beta stays published; older betas become drafts after new-release verification, with tags/code/assets preserved. [Evidence, implementation and release policy](reports/ISSUE_8_CARD_RESOURCES.md).

- Beta 0.1.0b14 corrects a reproduced duplicate-element module failure after the owner reported the card missing on b13. The card now imports the current exported base class; existing panel registrations are preserved. No send/permission/storage changes. Native verification remains pending. [Evidence and module-resource fallback](reports/ISSUE_8_CARD_LOADING.md).

- Owner-approved neutral card design 1A is implemented in beta 0.1.0b13: original stacked-drawer illustration, tappable zones, recipe/manual values and persistent accepted settings separately per device/zone. Switching zones sends nothing. New cards default to server-enforced dry run; live mode reuses administrator-only supervised beta. Normal-user device ACLs and native card acceptance remain pending. [Scope, installation and checks](reports/ISSUE_8_DASHBOARD_CARD.md).

- Owner-confirmed local acceptance on **Cosori Turbo Tower Pro Smart
  CAF-DC111S-AEU**: the complete supervised twelve-setting sequence passed on
  both zones on 2026-11-01, and the appliance was off afterward. See the
  [exact settings and evidence scope](reports/ISSUE_7_LOCAL_ACCEPTANCE.md).
- The owner subsequently confirmed saved-recipe transmission on zones 1 and 2 (R1/R2); R3–R7 remain pending for real acceptance. [Follow-up](reports/ISSUE_7_LOCAL_ACCEPTANCE.md).
- This does not establish all temperature/duration endpoints, Proof,
  active-zone changes, SYNC/MATCH or general compatibility.
- Code review, tests and documented local test outcomes precede stable releases.

Implementation note for requirements 14/15/26: Issue #7 exposes read-only discovery with disabled control capabilities. Airfryer Control `1.0.2-beta.1` adds the public read-only `faehigkeiten` service; the administrator preview allowlists its reported programs, ranges, provenance, connection, report time and revision. Estimated or unreported programs remain visibly unverified and never authorize transmission. The administrator-only `prepare_send` API and its [phone UI](reports/ISSUE_7_DRY_RUN_UI.md) remain server-enforced dry run and cannot transmit. See the [send contract](reports/ISSUE_7_COMMAND_CONTRACT.md) and [review](reports/ISSUE_7_DISCOVERY.md).

Beta acceptance decision on 2026-10-30: At the owner’s explicit request, implement a separate administrator-only supervised test transmission before real acceptance for CAF-DC111S-AEU, zone 1/2, Air Fry 170 °C and one minute. This is a bounded initial-test exception, not general send permission from estimated capabilities. Normal control remains blocked; see the [beta test contract and procedure](reports/ISSUE_7_BETA_SEND.md).

Correction 0.1.0b4: Supervised preparation requests exactly one new read-only device report through an eligible HA sensor. Old reports are never made artificially fresh; freshness, permissions and device gates remain mandatory. [Evidence and local acceptance](reports/ISSUE_7_STATUS_REFRESH.md).

Beta 0.1.0b5: At the owner’s request, supervised recipe/manual transmission for all six currently reported IDs in the reviewed contract. No general model approval. [Implementation and limits](reports/ISSUE_7_RECIPE_SEND.md), [60-case acceptance](reports/BETA_0_1_0B5_TEST_PLAN.md). Local validation only; no GitHub Actions.

Owner decision: one confirmation for the complete supervised list, then sequential single steps with fresh state checks and stopping. Beta 0.1.0b6 contains at most twelve ordinary test settings across both zones, not automatic cooking. [Implementation and acceptance](reports/ISSUE_7_GUIDED_BATCH.md). No GitHub Actions.

Owner requirement: a supervised stopped test must allow a new attempt without HA restart. Beta 0.1.0b7 permits explicit re-arming only after a fresh idle-state check, invalidating old tokens; no replay. [Implementation and unresolved failure](reports/ISSUE_7_MANUAL_RECOVERY.md). No GitHub Actions.

Beta 0.1.0b8: Integrate owner-identified zone switches to end own prepared settings before program changes. Fresh per-zone checks, turn_off only, no global stop. [Behavior and acceptance](reports/ISSUE_7_ZONE_RESET.md). No GitHub Actions.

Beta 0.1.0b9: Both individual-test buttons use the same form selection; scroll confirmation/errors into view. Limit Dry to 35–95 °C (owner report); sequence uses 55 °C / 360 minutes after successful single tests on both zones. This does not establish a minimum duration. [Correction and acceptance](reports/ISSUE_7_SELECTED_TEST_SETTINGS.md). No GitHub Actions.

Beta 0.1.0b10: Store and display seven owner-reported Turbo Tower temperature ranges separately from adapter capabilities. Supervised sending additionally enforces model limits while retaining reviewed adapter bounds; full ranges and Proof require an upstream change. [Profile and intersection](reports/ISSUE_7_MODEL_TEMPERATURES.md). No GitHub Actions.

Beta 0.1.0b11: Bind recipe/manual confirmations to the websocket; support server revocation before control submission, reject stale UI replies and offline requests. Twelve recipe transmissions simulated through routes/repository/sender with unchanged data. [Implementation and seven focused appliance cases](reports/ISSUE_7_RECIPE_LIFECYCLE.md). New real acceptance pending; dashboard with backend user permissions follows. Proof/wider temperatures deferred. No GitHub Actions.

Beta 0.1.0b12: Recipe editor dropdown uses programs reported by the selected air fryer; save exact identifiers and correct old identifiers only after explicit selection and saving. Custom/no-adapter input remains supported and drafts survive rerenders. [Implementation and repeated recipe acceptance](reports/ISSUE_7_EDITOR_PROGRAM_PICKER.md). This does not authorize sending or add programs. No GitHub Actions.
