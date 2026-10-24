# Requirements — Airfryer Recipes

[English](REQUIREMENTS.md) | [Deutsch](REQUIREMENTS.de.md)

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
| 11 | Rich recipe organization (C) | Categories, favorites, search, free-form tags, recently used. |
| 12 | JSON import and export (B) | Single or all recipes; validate schema and detect duplicates. Keep local HA backups. |
| 13 | Visual card editor + device personalization (B+) | Toggle labels/status/timer, choose graphic size; 'Customize Airfryer' opens gallery, own image upload, drag/drop zone hotspot positions stored in relative coordinates per device, and reset. Include a 'Missing your model?' GitHub issue link. |
| 14 | Automatic discovery + profile fallback (B) | Detect model, zones and supported capabilities from adapters where possible; verified profiles fill gaps. Unknown controls remain off. |
| 15 | Manual retry, offline UI (B+) | Show sending/error details; preserve selected settings; never auto-retry. Offline graphic grayed out and sending disabled; show distinct unknown state. |
| 16 | Independent recipe library (B) | Missing or broken Airfryer Control must not prevent editing/importing/exporting recipes. |
| 17 | Two permission levels (B) | Administrators edit/delete recipes and configure safety; normal HA users may select recipes and manually control permitted zones. Enforce in backend. |
| 18 | Localization and units | English and German as for Battery Flow Card; **English default/fallback**. Use HA user language; temperature displayed according to HA °C/°F setting, stored in Celsius. User recipe names are not auto-translated. |
| 19 | Versioned data with migrations (B) | Persist locally; migrate on updates only after backup; preserve originals on failure; HACS updates do not replace storage. |
| 20 | Device compatibility adaptation (B) | If program/time/temp is unsupported, warn and propose available substitutions; require explicit user approval; original recipe unchanged. |
| 21 | Shared and personal preferences (C) | Shared recipes and default favorites; optional personal favorites; recent-use history per device and zone. |
| 22 | Responsive UI with configurable size (B) | Auto layout for phone/tablet/desktop; compact/default/large options; proportional graphics/hotspots. |
| 23 | Simple recipes only (A) | Name, optional description, category/tags, favorite, program, temperature and duration; no recipe photos, ingredients or detailed cooking instructions. |
| 24 | Dashboard first; actions later (A + planned B) | MVP is interactive card. Internal sending API designed to allow future HA actions/scripts; do not prioritize them now. |
| 25 | Safe diagnostic export (B+) | Allowlisted technical data, secrets never included, warning/preview before download; explicitly tell user passwords/tokens/login data are excluded, and to review the export. |
| 26 | Optional dry-run mode (B) | Card editor option; full UI, but server-side no device control calls; show would-be payload and label clearly. |
| 27 | Guided onboarding (B) | Detect device if present, choose model/zones, optional sample recipes, help add card; permit setup without appliance. |
| 28 | Stable releases + beta (B) | HACS via GitHub Releases; optional prereleases, CI checks, English/German release notes; no automatic breaking migrations. |
| 29 | Automated + real tests (B) | Offline mock CI, documented local test checklist; real Cosori test only on user's HA, no cloud/LAN access for Codex. |
| 30 | Structured GitHub/Codex workflow (B) | AGENTS.md, bilingual requirements/roadmap/reports and issue/PR descriptions, dedicated branches, automated checks. Enforce explicit model/task check and escalation rules in AGENTS.md. |

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

- Real device currently proven via upstream Airfryer Control: **Cosori Turbo
  Tower Pro Smart CAF-DC111S-AEU**, zone 2 temperature/time transmission.
- This does **not** confirm upstream SYNC/MATCH on the device or any
  functionality in this new project.
- Code review, tests and documented local test outcomes precede stable releases.
