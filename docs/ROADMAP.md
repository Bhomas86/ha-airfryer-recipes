# Roadmap — Airfryer Recipes

[English](ROADMAP.md) | [Deutsch](ROADMAP.de.md)

**Status:** Architecture and all **31 requirements approved**. The integration shell is merged; persistence and API are under review in PR #13/#14, and the administrator panel is in development in Issue #6. No tested HACS release exists. The [architecture specification](ARCHITECTURE.md) defines implementation boundaries.

## Implementation priorities and dependency order

| Stage | Issue | Deliverable | Dependency | Verification |
| --- | --- | --- | --- | --- |
| 0 · Foundation | [PR #2](https://github.com/Bhomas86/ha-airfryer-recipes/pull/2) | Recipe model, JSON codec, tests, 31 bilingual requirements, architecture, Codex policy | Owner review | Python 3.12/3.14 CI; source review |
| 1 · HA shell | [#3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3) | Installable integration skeleton, config flow, localization, HACS metadata | PR #2 | HA startup without upstream adapter |
| 2 · Persistence | [#4](https://github.com/Bhomas86/ha-airfryer-recipes/issues/4) | Versioned Store, CRUD, migrations, JSON import/export | #3 | Restart/migration/invalid input tests |
| 3 · Authenticated API | [#5](https://github.com/Bhomas86/ha-airfryer-recipes/issues/5) | Server-side authorization and typed WebSocket operations | #3, #4 | Admin vs normal user and malformed request tests |
| 4 · Recipe editor | [#6](https://github.com/Bhomas86/ha-airfryer-recipes/issues/6) | Responsive German/English admin panel | #4, #5 | CRUD/permissions tested without air fryer |
| 5 · Safe device link | [#7](https://github.com/Bhomas86/ha-airfryer-recipes/issues/7) | Airfryer Control adapter, capability detection, safe send coordinator, dry-run | #3, #5 | Mock-based safe sends; local Cosori checklist |
| 6 · Main dashboard | [#8](https://github.com/Bhomas86/ha-airfryer-recipes/issues/8) | Interactive zones, recipe/manual selection, feedback, graphical card editor | #4, #5, #7 | Phone/tablet render; both zones and offline behavior |
| 7 · Personalization | [#9](https://github.com/Bhomas86/ha-airfryer-recipes/issues/9) | Device image gallery, optional safe uploads, draggable hotspots | #8 | Responsive positions, permissions and upload safety |
| 8 · Beta readiness | [#10](https://github.com/Bhomas86/ha-airfryer-recipes/issues/10) | HACS beta, bilingual release docs, diagnostics, optional completion push | #3–#8, optional #9 | CI + local HA/real-device tests |
| Later | [#1](https://github.com/Bhomas86/ha-airfryer-recipes/issues/1) | SYNC and MATCH dashboard buttons using existing upstream actions | #7, #8 | Real-device confirmation and safety checks |

## Development ownership and workflow

- **ChatGPT can prepare:** architecture, data models, Python utilities, tests, documentation, reviews, small bounded feature branches and PRs.
- **Codex can implement:** larger Home Assistant lifecycle changes, administrative panel, adapter and dashboard features in focused task packages. Apply the **four-choice model policy** in [AGENTS.md](../AGENTS.md) before each package; **GPT-5.6 Sol High is the default**, not GPT-6.1.
- **GitHub Actions:** mocks/static/unit tests only, no household device access or credentials.
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
