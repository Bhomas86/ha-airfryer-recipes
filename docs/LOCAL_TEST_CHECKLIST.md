# Local test checklist — appliance tests

[English](LOCAL_TEST_CHECKLIST.md) | [Deutsch](LOCAL_TEST_CHECKLIST.de.md)

**This project has read-only device discovery but no live send adapter or dashboard.** Do not run these
steps until the corresponding phase has been implemented and a beta build is
available for manual installation. Real tests take place only in the owner's
Home Assistant environment; Cloud Codex and GitHub Actions must not contact
the local network or real VeSync device.

## Before any real-device test

- [ ] Record Home Assistant, HACS integration and adapter versions.
- [ ] Confirm backup and working upstream Airfryer Control integration.
- [ ] Check appliance is empty, unobstructed and attended.
- [ ] Verify recipe app test mode means **no actual device commands**.
- [ ] Verify live mode still requires a deliberate Send action.
- [ ] Check current state of each zone; never assume stale state means idle.
- [ ] Confirm manual start is required at the device and no unexpected heater start occurs.

## Independent zone testing

- [ ] Send test mode settings to zone 1; no real transmission occurs.
- [ ] Send test mode settings to zone 2; no real transmission occurs.
- [ ] Send simple supported settings to idle zone 1 and inspect appliance display.
- [ ] Send simple supported settings to idle zone 2 and inspect appliance display.
- [ ] Verify no unintended changes in the other zone.
- [ ] Verify program, target temperature and time individually (if supported).
- [ ] During active cooking, verify default blocking.
- [ ] After admin opt-in, verify confirmation and adapter support before changes.
- [ ] Verify no automatic heater start.
- [ ] Offline and unknown state: controls disabled; graphic grayed out.
- [ ] Disconnect/reconnect: no automatic retry or queued commands.
- [ ] Upstream integration removed: recipe editor still works.

## Data and localization

- [ ] Without Airfryer Control, open the “Airfryer Recipes” admin sidebar on a phone; verify there is no horizontal overflow.
- [ ] Create, edit, duplicate and confirm deletion; verify saved recipes remain after restarting HA.
- [ ] Choose an existing category in the recipe editor; “Add new category” is last and reuses an existing name when only letter case differs.
- [ ] Test shared and personal favorites separately; a second user's personal favorites remain independent.
- [ ] Preview JSON imports with matching names/IDs and apply only after deliberate selection; verify export uses `Airfryer-Rezepte-Home-Assistant.json`.
- [ ] As a regular user, verify the admin panel is inaccessible and write WebSocket commands are denied.
- [ ] Create/edit/delete/duplicate/export/import in both languages.
- [ ] Import an invalid JSON file and a future schema version; preserve data.
- [ ] Check schema migration backup and rollback using a test copy only.
- [ ] Verify normal users cannot modify recipes or safety preferences.
- [ ] Check °C/°F presentation, device-specific limits and range warnings.
- [ ] Inspect diagnostic preview for any secrets before sharing.
- [ ] Compare German and English reports and release notes for completeness.

## Future SYNC / MATCH test (not MVP)

- [ ] Confirm the exact HA actions and required argument ordering.
- [ ] Configure both zones with different durations.
- [ ] Run SYNC only in supported, approved appliance state.
- [ ] Verify correct device display and manual-start behavior.
- [ ] Run MATCH separately and verify equal settings only.
- [ ] Verify unsupported model safely hides/disables both controls.

Document each test as PASS / FAIL / NOT TESTED, with reproducible notes.
