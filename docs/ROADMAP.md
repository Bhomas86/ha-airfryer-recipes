# Roadmap

Current status: **Foundation PR in progress. Not installable through HACS yet.**

## Phase 0 — Documentation and pure recipe core (this PR)
- [x] Codex model/task preflight and escalation policy (`AGENTS.md`)
- [x] Consolidated decisions 1–30
- [x] Device-independent recipe schema, validations and versioned JSON codec
- [x] Offline Python unit tests
- [ ] GitHub CI confirmed passing
- [ ] Owner review and merge

## Phase 1 — Home Assistant integration foundation
- [ ] Manifest, HACS metadata and initial config flow
- [ ] Local HA storage via async `Store`
- [ ] Transaction-safe schema migrations with backups and rollback behavior
- [ ] Admin permission checks for changes; user access for control
- [ ] Recipe CRUD backend and JSON import/export with conflict preview
- [ ] No dependency on Airfryer Control for recipe management

## Phase 2 — Recipe administration UI
- [ ] Home Assistant administrator panel, fully localized en/de
- [ ] Create/edit/duplicate/delete with confirmation and search
- [ ] Categories, tags, shared and user favorites
- [ ] Optional sample recipes during guided setup

## Phase 3 — Device adapters and safe transmission
- [ ] Adapter contract: model, zones, capabilities, online state
- [ ] Airfryer Control adapter; validate upstream action schema
- [ ] Program/temperature/time compatibility and user confirmation
- [ ] Offline/unknown/active-zone safeguards
- [ ] Server-side dry-run, manually requested retry only
- [ ] Run local device tests on Cosori CAF-DC111S-AEU

## Phase 4 — Graphical dashboard
- [ ] Model-specific or generic selectable device image
- [ ] Tappable zones for recipe and manual programming
- [ ] Responsive editor, custom images and relative hotspots
- [ ] Completion status/remaining time and optional notifications
- [ ] Clear transmission, errors and offline presentation

## Phase 5 — Optional enhancements
- [ ] UI for upstream SYNC and MATCH actions (#1)
- [ ] Home Assistant automation actions (after dashboard MVP)
- [ ] Multiple cooking phases
- [ ] Additional device adapters and models

## Release gates
- Unit tests and CI passing
- HA configuration/setup tests passing before claiming HACS compatibility
- Safety behavior verified: no unexpected start, no offline replay
- English and German user-facing strings and release notes
- Device testing documented separately; do not invent successful tests
- Stable and opt-in beta releases; preserve recipe storage
