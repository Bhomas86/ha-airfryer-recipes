# Architecture — Airfryer Recipes

[English](ARCHITECTURE.md) | [Deutsch](ARCHITECTURE.de.md)

**Decision ADR-001 / Requirement 31: Modular Home Assistant custom integration.** Approved 2026-10-24. This document defines the target architecture. Recipe storage, the WebSocket API and the administrator panel are merged through PR #16. Read-only discovery and an administrator-only server-enforced dry-run preview are implemented as parts of Issue #7; device control, dashboard and diagnostics remain planned. See the [upstream contract review](reports/ISSUE_7_DISCOVERY.md).

## Objectives and deployment

Deliver **one HACS-installable integration** with one Python backend and two bundled JavaScript entry points: an administrator recipe-management panel and a Lovelace dashboard card/editor. No separate container, server, database, local proxy, or exposed inbound port. Initially integrate with the **existing Airfryer Control** custom integration; recipe management must work even without it.

The domain is `airfryer_recipes`. Home Assistant OS on Proxmox is a target deployment, but the architecture must be portable.

## Components and responsibilities

| Component | Responsibilities | Must not do |
| --- | --- | --- |
| `recipe_model.py` and validation | Device-independent recipe data, single-phase MVP, forward-compatible phase structure, JSON schema validation | Access the network, control a device |
| Storage/repository | Home Assistant `Store` persistence, schema versioning, backups, migrations, CRUD, import preview and duplicate resolution | Assume Airfryer Control is installed |
| Authenticated WebSocket API | Typed read/write requests, admin-only mutations and settings, user-level allowed control, clear response/errors | Trust frontend checks as authorization |
| Admin recipe panel | Search, categories/tags, favorites, CRUD, import/export, optional samples and device-image personalization | Send commands without backend validation |
| Lovelace card and visual editor | Responsive tappable device/zone illustration, recipe/manual tabs, status and offline display, dry-run and explicit Send | Directly bypass the backend to call upstream control |
| Device registry and capability service | Discover supported HA devices, zones, status and capabilities; verified model-profile fallback | Assume all upstream actions work for all models |
| Adapter protocol + Airfryer Control adapter | Normalize model/zones/program/ranges/status and map validated requests to known existing HA actions | Own credentials, reimplement VeSync authentication, start heating |
| Command coordinator | Recheck current device/zone state, enforce permissions and safety, validate and confirm adjustments, suppress sends in dry-run mode, return verified/sent/unconfirmed/error status | Queue offline commands, automatically retry, start the heater |
| Diagnostics | Export allowlisted technical data; local errors with redaction and review notice | Export passwords, tokens, cookies, IP addresses or user/device identifiers |

## Frontend/backend contract

Use **authenticated Home Assistant WebSocket commands** under `airfryer_recipes/*` for recipe lists, mutations, device capabilities, status, dry-run previews and send requests. The names below describe the target protocol. Recipe operations, administrator-only `devices`, and `prepare_send` as a dry-run preview are implemented. `device_state`, `confirm_send`, device preferences and diagnostics remain planned:

- `airfryer_recipes/list`, `get`, `create`, `update`, `duplicate`, `delete`
- `airfryer_recipes/import_preview`, `import_confirm`, `export`
- `airfryer_recipes/devices`, `device_state`, `prepare_send`, `confirm_send`
- `airfryer_recipes/preferences`, `update_preferences`, `diagnostics`

Admin-only commands: create/edit/delete/import, shared defaults and security/card policies, device image upload or hotspot changes. Normal HA users may read recipes and perform **permitted** sends. Server-side authorization must use the authenticated connection user, not a client-provided admin flag. All responses are structured and localized on the frontend.

**Two-step transmission:** For a supported idle zone, an explicit send may follow validation immediately. If values must change for compatibility, or an admin-enabled running-zone change is requested, return a short-lived server-side confirmation token binding device, zone, exact values, user and state revision; require explicit confirmation and revalidate state. A token must never itself start cooking.

## Recipe storage and migration

Store recipe collections using Home Assistant's async `Store` helper under integration-specific storage keys, not inside the source directory. Include a schema version, atomic writes via the helper, and a migration plan that preserves a backup of original data and rejects unsupported newer versions. Separate device-independent recipes from per-device/per-zone last manual settings and per-user favorites. Internally store temperature in Celsius, display using the HA unit preference. JSON export/import is versioned and must validate content and preview duplicate conflicts without changing live storage until confirmation. Export uses a short-lived download path bound to the authenticated HA session; the HTTP endpoint rechecks administrator access and sends a human-readable filename with caching disabled.

**Keep storage and adapter lifecycles independent.** Inability to discover Airfryer Control must not block setup, recipe CRUD, or JSON import/export.

## Device integration and fail-safe controls

The adapter contract should expose typed device IDs, model identifiers, zone IDs, programs and limits, connectivity, zone status, reporting freshness and capability flags (`sync_finish`, `match_zones`, supported setting updates). Unknown or stale state is distinct from offline and **blocks live sends**. Offline devices render in grayscale with disabled send controls. Verified profiles may fill missing descriptive capabilities but cannot authorize a dangerous feature.

All device-control operations are routed through the command coordinator. By default, never change an active cooking zone; an administrator may enable confirmation-based changes only if the adapter/device allows it. Never remotely start heating as a side effect of configuration; respect appliance manual-start rules. Never queue or replay commands after reconnection, never silently retry. Server-side dry-run must make **zero real device-control calls**. Send results should distinguish `accepted_by_adapter` from `confirmed_on_device` when confirmation cannot be obtained.

The first device for manual verification is the **Cosori Turbo Tower Pro Smart CAF-DC111S-AEU**. Upstream Airfryer Control has already been used to send time and temperature to lower Zone 2. **SYNC and MATCH are upstream actions but their signatures and correct device behavior must be verified before optional dashboard controls are activated** (issue #1).

## UI and image resources

Two JavaScript entry points may share TypeScript/Lit components but should ship as locally bundled, versioned assets inside the integration. No runtime CDN dependency. Register frontend resources using supported Home Assistant mechanisms and avoid synchronous file I/O in the event loop. Preset images should be project-owned/licensed illustrations; user-uploaded images are stored locally with safe types, size limits and authenticated access. Store tappable zone hotspot locations in relative coordinates, with a neutral fallback for unknown devices and a button linking to GitHub issues for missing models.

English (`en`) is the **UI fallback language**. German (`de`) is fully supported. Project reports, issue and PR bodies, documentation and release notes are **fully bilingual, German first**, with `*.de.md` and corresponding English `*.md`.

## Quality gates and staged implementation

1. Merge and verify foundation PR #2 (model, guidelines, offline unit tests).
2. Config flow, manifest/HACS skeleton and backend startup without Airfryer Control.
3. Persistent repository with migrations, CRUD and import/export.
4. WebSocket API with authenticated admin/user permissions.
5. Admin recipe panel and frontend localization.
6. Device adapter + command coordinator and mocked safety tests.
7. Graphical Lovelace dashboard, device images and responsive editor.
8. Local manual Cosori tests; optional notifications, diagnostics and beta release. SYNC/MATCH later.

Each step has a separate issue/PR, automated offline tests and bilingual review. Do not claim HACS readiness until the integration actually installs and initializes in HA.

## Developer references

- [Home Assistant integration development](https://developers.home-assistant.io/docs/creating_component_index/)
- [Custom panels](https://developers.home-assistant.io/docs/frontend/custom-ui/creating-custom-panels/)
- [WebSocket extensions](https://developers.home-assistant.io/docs/frontend/extending/websocket-api)
- [Internationalization](https://developers.home-assistant.io/docs/internationalization/core/)
- [Airfryer Control upstream](https://github.com/misterm2310/airfryer-control)
