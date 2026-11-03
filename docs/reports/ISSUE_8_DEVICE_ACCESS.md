# Whole-device permissions for ordinary HA users

[Deutsch](ISSUE_8_DEVICE_ACCESS.de.md) | [English](ISSUE_8_DEVICE_ACCESS.md)

**Local follow-up 2026-11-03: PASS** for default deny, both zones after whole-device grant and device removal after revoke/refresh. This does not establish additional real in-flight revocation or permission-restart acceptance.

Beta 0.1.0b16 implements requirement 17 after the owner accepted the basic card flow: sending to both zones, reuse after physical reset, correct per-zone last-sent settings and survival across HA restart. The earlier Grill 200 °C attempt was blocked by the reviewed adapter range; it is not evidence of a zone-2 permission failure. No new Grill endpoint or broader temperature acceptance is inferred.

The owner also confirmed automatic upgrade of the existing dashboard resource URL; creation on a fresh HA instance remains untested.

**Owner's scope correction:** share an entire device with a user, including all its zones and available programs. There are no per-zone, per-program or per-menu grants. Existing model/program/range, idle-state and supervised-confirmation gates still apply; Proof and wider temperatures remain deferred.

## Behavior and storage

Administrators open the recipe library's **Device permissions → Manage device access** section, choose an active ordinary HA user and a discovered device, then explicitly grant it. Existing grants have a Revoke button. Admins implicitly retain all devices and alone manage recipes, imports/exports, permission configuration and guided test tools. Ordinary users receive no device access by default. They refresh their card after a grant/revocation and may select recipes or manual values for both zones of a shared device. They see that device's shared last-sent snapshots. Recipe data stays device-independent and unchanged.

Grants use the separate HA Store `airfryer_recipes.device_access`, schema 1: user IDs mapped to device IDs. A healthy repository/lock is reused across integration reloads; ordinary-user confirmations are volatile and never restored. Missing grants deny access; damaged/newer data remains untouched and disables grants/writes while admin control and recipe management remain usable. Failed saves preserve previous grants. No device command is sent by permission management; discovery only uses the existing read-only capability service.

These permissions govern **Airfryer Recipes**. They do not restrict the independent Airfryer Control integration, other HA actions or vendor applications.

## Backend enforcement

The new authenticated `control` endpoint accepts only the allowlisted discovery, history, dry-run, selected recipe/manual preparation, confirmation, cancellation and read-only recovery operations. Its action-specific fields are exact; user identity always comes from the authenticated connection. No client field can select another actor or enable admin tools. `access_list` and `access_set` are admin-only and recheck the current active admin after asynchronous discovery. Inactive/system ordinary accounts cannot be granted/used. Revocation also works for a deleted user or unavailable device.

Ordinary discovery filters device IDs **before** capability-service calls, then filters/rechecks again before returning. History and preview authorize the selected device before reading and afterward; preview remains server-enforced dry run with zero control calls. Without any grants discovery returns no devices without consulting the adapter. The existing admin endpoints stay admin-only.

The single-shot sender rechecks active account/device permission during preparation, after fresh validation and immediately before transport. Tokens bind user, connection, exact settings, recipe snapshot, device and zone. Every permission edit advances a runtime revision **before** persistence and blocks ordinary sends during the write. Conservatively, any edit invalidates all previously prepared ordinary-user confirmations, including after revoke/regrant or a failed write. The rightful owner's confirmation token is consumed before asynchronous authorization; it cannot be retried after failure. An active owner can cancel even after revocation. An already submitted transport cannot be recalled; withdrawal prevents new submissions and never starts a retry.

The card routes ordinary users through scoped control, shows only returned devices and retains default test mode and one exact-value confirmation. Account/role changes clear cached grants/drafts/history; offline/page-leave guards and cancellation remain active. The visual card editor cannot grant permissions. Ordinary recovery needs physical-reset acknowledgement, checks fresh idle state and cannot interrupt an admin batch. No heating start, queue, retry, running-zone override, raw command, SYNC or MATCH is added. Adapter pin `1.0.2-beta.1` and the reviewed CAF-DC111S-AEU contract remain unchanged.

## Local acceptance without new appliance sends

1. Install v0.1.0b16 through HACS, restart HA and fully reload both sessions. Existing card/resource configuration remains; the resource URL updates to b16.
2. Use an existing separate **ordinary HA account**, not the admin's session. With no device grant, its card must show no permitted device. The recipe-management panel remains admin-only.
3. As admin: recipe library → Device permissions → Manage device access → choose user/device → Grant device access. No zone/program selection should exist.
4. Refresh the ordinary user's card. Both zones and reported programs of that device should be available. Keep `dry_run: true`; check a recipe/manual preview on each zone. No settings are transmitted and history does not change.
5. Revoke as admin, refresh the ordinary card: the device must disappear. Grant again, restart HA, and check the grant persists. Other users/devices remain unshared. Existing grants can be revoked even when the device is offline.

Backend tests also simulate revocation between preparation and confirmation and during final validation; no real-device run is needed to establish those automated checks. Native two-account HA/Companion acceptance of this new package remains pending. These checks do not claim that every program endpoint or all interruption cases have been accepted on the appliance.

## Verification

Passed locally: **203 Python and 93 frontend tests** (62 panel, 27 card, 4 module loading), compilation, documentation links/language pairs and diff formatting. New coverage includes default deny, whole-device/user isolation, restart, damaged/newer/failed storage, concurrent writes, inactive/system accounts, forged fields/actors, filtered discovery, history, dry run, exact recipe sends to both zones through real routes/repository/sender, revocation/regrant, write-in-progress revocation, cleanup and admin-only mutations/tools. Native new permission UI/two-account HA, HACS/Hassfest and Python 3.14 were not run. No GitHub Actions. Only the current verified beta remains published; older betas become drafts with tags/code/assets preserved.
