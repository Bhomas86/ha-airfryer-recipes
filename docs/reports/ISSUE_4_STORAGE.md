# Development report – Issue #4: Local recipe storage

[English](ISSUE_4_STORAGE.md) | [Deutsch](ISSUE_4_STORAGE.de.md)

**Status:** This development branch contains the first backend recipe repository, not yet operable through the user interface and not tested in real Home Assistant.

## Implemented

- Device-independent asynchronous CRUD repository: `create`, `get`, `list`, `update`, `delete`, and JSON export.
- Version-validated persistence via Home Assistant `Store` in `.storage/airfryer_recipes.recipes`, without a separate database or Airfryer Control requirement.
- Before each change, the previous snapshot is saved to `airfryer_recipes.recipes.backup`. Corrupted, unknown and newer schemas never lead to silently overwriting the existing library with an empty one.
- **Import preview and explicit confirmation:** conflicts by ID and name are reported. Existing recipes can be skipped or deliberately replaced when IDs match; a name conflict with a different ID is never silently overwritten.
- Concurrent writes serialized by `asyncio.Lock`. Failed writes do not publish updated in-memory repository contents.
- Offline unit tests without Home Assistant, cloud or appliance access.

## Limitations and further work

- **No graphical recipe UI or WebSocket API yet** (issues #5 and #6).
- Shared/personal favorites, last manual values and usage history still require separate persistence.
- **No historical schema transformation yet.** Only v1 exists. Unknown versions safely fail closed; future changes require a concrete, tested migration/rollback plan.
- The rolling snapshot is a previous-version backup, not a full long-term Home Assistant backup. Regular HA backups remain necessary.
- Real Home Assistant startup, restart and recovery testing are pending.
- No device-control commands are implemented.

## Local acceptance (not performed)

1. Back up a separate Home Assistant test instance and install the branch integration.
2. Set up and restart HA; check logs for setup/storage errors.
3. Create recipe data through a future test API or local test code and verify persistence after restart.
4. Test newer schema, corrupted JSON and intentionally failed migration **only on copied test data**.
5. Verify backup and recovery before marking the issue complete.

**Model policy:** GPT-5.6 Sol High remains the project's default Codex configuration for this bounded repository task. Evaluate complex future migrations separately; never use GPT-6.1 without approval.
