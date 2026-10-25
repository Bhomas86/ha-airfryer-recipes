# Issue #5 – Authenticated recipe WebSocket API

[English](ISSUE_5_WEBSOCKET.md) | [Deutsch](ISSUE_5_WEBSOCKET.de.md)

## Scope and dependency

This implementation **depends on the still-open Issue #4 storage code in PR #13**. Initially, the pull request targets that feature branch, not `main`.

Authenticated Home Assistant users can list and read recipes. Mutations are **restricted to administrators in the backend**, using the authenticated HA connection identity. A browser-controlled `is_admin` flag has no effect. No cloud connection, device adapter or **device commands** exist here.

## Protocol

Use the native Home Assistant WebSocket envelope, for example `{"id": 1, "type": "airfryer_recipes/list"}`.

| Command | Permission | Additional fields | Result |
| --- | --- | --- | --- |
| `list` | User | – | `recipes` |
| `get` | User | `recipe_id` | `recipe` |
| `create` | Admin | `recipe` without ID | `recipe` with server-generated ID |
| `update` | Admin | `recipe` with ID | Updated `recipe` |
| `duplicate` | Admin | `recipe_id`, `name` | Copy with new ID |
| `delete` | Admin | `recipe_id` | `deleted` |
| `import_preview` | Admin | `payload` as JSON string | Preview, conflicts and short-lived `token` |
| `import_confirm` | Admin | `token`, optional `policy` | `imported` |
| `export` | Admin | – | Short-lived signed `url`, `filename` and expiry |

All command names use the `airfryer_recipes/` prefix. Import conflict policies: `skip` (default) or `replace_ids` (only exact matching IDs).

## Safety and quality

- The native `require_admin` decorator checks the authenticated HA user before any mutation.
- The shared recipe model validates JSON fields and bounds.
- Responses return structured error codes without leaking internal storage or credentials.
- Unloading removes access to the active repository.
- No Airfryer/VeSync action can be called from this API.
- Personal favorites are stored separately by authenticated HA user ID; device-specific settings and per-zone control permissions remain future work.
- Authenticated administrators receive a download path valid for 30 seconds for JSON exports. The HTTP endpoint rechecks administrator access and serves `Airfryer-Rezepte-Home-Assistant.json` with caching disabled.

## Testing

GitHub Actions uses offline Home Assistant stubs to check authorization, mutations, import preview/confirmation, malformed input, unload behavior and translations. They **are not real HA installation tests**.

**Agreed local strategy:** No dedicated test server. The first real test will happen through the graphical recipe management UI in **Issue #6** on the existing Home Assistant instance, after a backup. No early device-control checks.

**Model policy:** GPT-5.6 Sol High remains the owner's chosen Codex default; the actual VS Code model selection cannot be inspected here. GPT-6 Sol High may be suggested for a deeper authorization review; GPT-6.1 Sol High requires an exceptional justification and approval.
