# Local acceptance checklist

[Deutsch](LOCAL_TEST_CHECKLIST.de.md) | [English](LOCAL_TEST_CHECKLIST.md)

Current: **b23**, exactly **Airfryer Control 1.0.3-beta.3** for supervised settings on CAF-DC111S-AEU. The dashboard, recipe manager, whole-device grants, private artwork and supervised sender are implemented. [Current review and evidence](reports/FINAL_REVIEW.md). Real HA/appliance checks are performed only by the owner; cloud Codex and Actions have no LAN/appliance access.

## Focused b22 save/restart check

This checks the corrected persistence path and requires no appliance transmission. The card, whole-device grant flow, completed 44-step reported-value sequence and Proof recipe test are owner-confirmed; do not automatically repeat all device settings for these storage fixes.

1. Install b22, restart HA and reopen the app. Keep the card in test mode.
2. Save a harmless recipe edit (for example its description), change a personal favorite and confirm both changes succeeded. If a spare recipe is available, mark it as a favorite, delete it as admin, then change another favorite; no stale deleted reference should prevent saving. There is no need to create 501 favorites manually.
3. Note the current Proof recipe, device photo/zone positions, selected A/B style, device grants and separate last-sent values for both zones.
4. Restart HA and fully reopen the app. Check the recipe edit/favorite and noted settings are retained; the granted ordinary user still sees the intended device. No old confirmation or automatic settings transmission may resume.
5. Report PASS / FAIL / NOT TESTED with installed versions and the specific observation. The owner has now reported this b22 save/restart check passed. The b23 label-only change does not require repeating the storage or 44-step appliance tests.

## Permissions and failure regression, when relevant

- [ ] New ordinary user has no device by default. A whole-device grant exposes both zones and all reported programs; revocation removes new reads/sends after refreshing. No per-zone/program/menu grants.
- [ ] Ordinary users cannot use admin recipe mutations/import/export, image writes, grant management or batch tools, even through direct WebSocket calls. Personal favorites belong only to the authenticated user.
- [ ] Test mode sends no device control command. Unknown/offline/cooking states block settings; connection loss/reconnect never retries an old command.
- [ ] Missing/broken Airfryer Control leaves recipe management usable. A different controller version cannot pass the pinned supervised contract.
- [ ] Invalid import/future schema leaves original data unchanged. Test backup recovery only on a disposable copy; no migration is claimed for schema version 1.
- [ ] If a storage error occurs naturally, the UI must not falsely confirm saving. An accepted device transmission with failed history saving must remain accepted and must not be resent merely to save it. Do not damage production storage to provoke errors; automated tests cover simulated failures.

## Existing user workflows

- [ ] Recipe create/edit/copy/confirmed delete, categories, tags, search and shared/personal favorites; duplicate names/case handling.
- [ ] Versioned JSON import preview and explicit conflict choice; authenticated named export excludes device images, grants and account data.
- [ ] Recipe/manual source selection, zone-specific drafts/history, either zone selectable without sending, correct reported programs including Proof and unverified provenance.
- [ ] A shows thin active outline/small markers; B keeps configured photo zones invisible and tappable. Designer rectangles stay visible, scale with the image and persist after Save appearance. Card A/B choice uses the separate HA Save button.
- [ ] German/English UI and °C/°F display; stored temperatures remain Celsius. Native keyboard/accessibility/mobile variants not explicitly reported remain separate checks.

For the large supervised temperature run, use [the exact table/procedure](reports/ISSUE_7_CONTROLLER_BETA3.md). It contains 44 settings on both zones, not cooking or duration-boundary acceptance. Remain beside the empty appliance, do not press Start, and cancel final preparations physically.

## Release status and later work

Before candidate/stable promotion, retain the focused native restart result and official HACS/Hassfest validation. Local mock/metadata tests are recorded separately; no Actions may run until the owner changes that instruction. Diagnostics export, guided onboarding, notifications, active-zone modification and SYNC/MATCH are planned separately and must not be presented as implemented here. Record any real check as PASS / FAIL / NOT TESTED, with version, expected/actual outcome and no credentials, cloud IDs or raw diagnostic dumps.
