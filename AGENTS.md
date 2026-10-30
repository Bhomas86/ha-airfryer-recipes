# AGENTS.md — Airfryer Recipes

[English](AGENTS.md) | [Deutsch](AGENTS.de.md)

This file contains binding project instructions for Codex and other coding agents.
Read this file and `docs/REQUIREMENTS.md` before every task. Do not assume that
a higher-cost model is better for every task.

## Bilingual reporting and documentation — mandatory

**German is the project owner's working language; English is required for the wider community.**

- **Every new or updated report or non-code project document must have complete
  German and English versions.** Use `*.md` for English and matching `*.de.md`
  for German, with reciprocal language links at the top.
- This applies to requirements, roadmaps, architecture decisions, test reports,
  test checklists, issue descriptions, PR descriptions, release notes and user
  documentation. Do not publish English-only or German-only reports.
- In pull requests and issues use **Deutsch first, English second** as clearly
  marked sections. Make both sections independently understandable.
- Communication with the owner should prioritize clear German. Technical code
  identifiers and comments may use English. User-visible UI strings require
  both `en` and `de` translations; English remains the default/fallback.
- Documentation translations must remain semantically equivalent; whenever one
  language changes, update the other in the **same PR**. Include a review check.
- Use GPT-6.1 Sol — Low for small translations and reports; choose Medium
  or High when complexity or risk warrants it under the policy below.

## Model policy (explicit project choices)

Effective 2026-10-29, the owner requires **GPT-6.1 Sol exclusively**.
Only the reasoning effort varies: **Low, Medium or High** (German:
**niedrig, mittel, hoch**). This replaces the previous model policy.

| Configuration | When to recommend |
| --- | --- |
| **GPT-6.1 Sol — Low** | Small documentation, translations, formatting and straightforward low-risk maintenance |
| **GPT-6.1 Sol — Medium** | **DEFAULT for normal development.** Scoped features, Python implementation, normal bug fixes, unit tests and reviews |
| **GPT-6.1 Sol — High** | Multi-module architecture, complex Home Assistant lifecycle/async integration, migrations, difficult debugging, safety and concurrency |

These names represent choices available to the project owner, not a claim that
an agent can inspect or change ChatGPT/Codex's model selector.

### Mandatory model/task preflight — before every task package

1. Read the task and assess **scope, complexity, safety impact, and uncertainty**.
2. Print a short **Model check** with (a) recommended configuration from the
   exact table above, (b) why, (c) the actual current selected configuration
   **only if reliably provided by the environment or the owner**.
3. **Never pretend to know the selected model.** If it is not visible, ask the
   owner to confirm it before substantive code changes.
4. If the selected configuration is not suitable, **STOP BEFORE EDITING,
   IMPLEMENTING OR RUNNING A LONG REASONING TASK**. Explain why and propose the
   least-expensive suitable configuration; request that the owner switch it.
   Do not silently switch models or keep coding after identifying a mismatch.
5. Use **GPT-6.1 Sol for every task**. Recommend Low for simple tasks,
   Medium for normal development, and High for complex or safety-critical work.
6. Justify the recommended effort briefly. High is an allowed effort level,
   not an exception requiring a different model. Never claim to switch the
   selected effort automatically.
7. Re-evaluate if task scope changes materially or a previously hidden
   complexity/safety risk emerges. Stop and propose a model adjustment.

Example preflight:

```text
Model check
Task: Implement recipe JSON validation and unit tests.
Recommended: GPT-6.1 Sol — Medium (scoped implementation).
Selected: Not verifiable in this environment.
Action: Confirm current model before implementation; do not claim to switch it.
```

## Architecture and scope

- Home Assistant custom integration, project domain `airfryer_recipes`.
- **Recipes are device-independent**. Select physical device and zone at send time.
- Store recipes in Home Assistant, with a versioned schema and safe migrations.
- Keep recipe validation, storage, adapter/device control, and frontend separate.
- MVP recipes contain a single cooking phase; use a data structure that can
  support multiple phases later without destructive migration.
- Device detection is automatic when possible, with verified model profiles as
  fallback. Never enable unverified capabilities.
- First adapter targets **Airfryer Control**. It remains an **optional**
  dependency; recipe management must work without it.
- SYNC and MATCH are existing upstream Home Assistant actions, but need
  verification of exact signatures and device behavior before the optional UI
  buttons are wired. Keep them separate from regular per-zone sending.
- Interactive device image: model presets, neutral fallback, optional uploaded
  image, relative-coordinate draggable cooking-zone hotspots.
- Recipe/admin editor and dashboard/normal-user controls are distinct.
  **Enforce access control in the backend, not only by hiding buttons.**
- English is the default/fallback, German fully supported. Keep README.md
  and README.de.md aligned; user-created recipe names are not translated.
- Internally store temperature in Celsius; convert for display and validate
  against real device limits before sending.

## Non-negotiable safety

- **Never remotely start a heating cycle** as a side effect of sending settings;
  respect physical manual-start requirements and appliance safeguards.
- Default to blocking changes to an actively cooking zone. Admin may explicitly
  enable changes with confirmation; reject when device state is unknown.
- No old or queued commands should be replayed after reconnect.
- No automatic retry of failed sends; user must re-confirm.
- Test/dry-run mode must suppress all actual device-control calls **server-side**.
- If adapter integration is missing/offline, preserve recipe editing and
  disable device transmission with a clear status.
- Never hardcode secrets or include passwords, session keys, IDs or network
  addresses in public repo or diagnostics. Diagnostic exports use an allowlist
  of safe fields and warn users to review before sharing.

## Workflow

1. Work on a feature branch; propose a PR. Do not push directly to `main`.
2. Keep task packages bounded and state the model preflight first.
3. Write unit tests before/alongside feature code; mock upstream device
   responses. Never call a real appliance from CI or cloud Codex.
4. Real-world checks are performed manually on the owner's Home Assistant
   instance using `docs/LOCAL_TEST_CHECKLIST.md` (to be completed).
   Cloud Codex has **GitHub-only** access; no route to LAN/Proxmox/VeSync secrets.
5. Before marking a task complete: report what changed, automated tests that
   actually ran, unavailable checks, risks, and precise local test steps.
6. Preserve stored recipe data and migration rollback paths across upgrades.
7. Keep all reports, PR descriptions, issue descriptions, release notes, public docs and user-facing features fully bilingual. German comes first for reports; English is the UI fallback. Update both translations together.
8. Follow Home Assistant asyncio guidance; avoid synchronous file I/O in its
   event loop, and do not bypass built-in permission checks.
9. Record decisions in `docs/REQUIREMENTS.md` and staged work in
   `docs/ROADMAP.md`. Do not label planned features as implemented.

**Current owner instruction (2026-10-30): Do not trigger GitHub Actions for further updates until instructed otherwise; validate locally only. This overrides the general budget rules below. Suppress automatic PR/push runs when publishing (for example, `[skip ci]` in the commit); do not manually dispatch workflows.**

## GitHub Actions budget (effective 2026-10-30)

- Use GitHub Actions sparingly; the available allowance is limited.
- During development, run targeted local checks first, batch changes and use only small, relevant automatic jobs.
- Documentation-only changes must not trigger code, HACS or Hassfest runs. Cancel superseded runs on the same branch.
- Run the full Python matrix and comprehensive validation at the end of a larger section or before release. Do not repeat unchanged checks without a new reason.
- Avoid duplicate automatic checks for the same state on a PR and its subsequent merge. Required safety and release checks remain mandatory; plan their scope around the section.
- Full offline validation: manually run “Offline unit tests” with `full_suite=true`. Run HACS/Hassfest for relevant metadata changes or through the manual “Home Assistant and HACS validation” workflow.
- A completed section may request the full matrix in its single PR run using `[full-ci]` in the PR title. This avoids a separate duplicate run before a beta release; do not use the marker for intermediate work.

## Helpful references

- Home Assistant developer docs: https://developers.home-assistant.io/
- Upstream Airfryer Control: https://github.com/misterm2310/airfryer-control
