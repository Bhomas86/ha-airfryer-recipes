# Final review of permissions, errors and documentation

[Deutsch](FINAL_REVIEW.de.md) | [English](FINAL_REVIEW.md)

Review date: 2026-11-04. Baseline: b21, public commit 15190d2fa580eb7402f2fff36e2a55103646802f. Scope: current single-phase recipe library, dashboard, whole-device permissions, private artwork, supervised settings and storage. The two confirmed defects below are corrected in b22. This is a scoped code/automated review, not a claim of general appliance compatibility or completion of every planned roadmap feature.

## Owner evidence

The owner confirms both artwork styles and that the card now works as planned. Their screenshot shows completion of the 44-step b21 temperature/Proof sequence with matching reported values after each command. The later message “Prüfung mit Gärten ist durch” confirms the requested Proof recipe workflow in the context of the preceding instructions: save/select a 31 °C / 60-minute recipe and use both zones with a granted ordinary user. The owner did not separately restate every parameter/observation, so this is owner-reported acceptance, not an independently captured measurement matrix. It does not establish duration endpoints, temperature accuracy while cooking or a general compatibility approval.

Restart persistence was accepted on earlier beta versions. At the beginning of this review, the b21/b22 restart check was not separately confirmed; the owner had chosen the code review rather than that check. After b22 publication, the owner replied “Dies hat geklappt” to the focused save/favorite/restart instructions. The b22 native save/restart check is now owner-confirmed. This is acceptance of that workflow, not a claim that every injected storage-error case was reproduced on the appliance installation.

## Findings and fixes

1. **Favorite writes could exceed the reader's 500-entry limit.** Deleted recipe references accumulated, so valid successive favorite operations could create a store that failed to load after restart and prevented integration setup. Reproduced with 501 saved references. Writes now share the recipe/reader capacity bound, and an explicit favorite change prunes only that user's deleted references. Clearing a deleted reference is supported. Live recipe IDs are read after acquiring the favorite lock to avoid discarding newer queued choices. Other users and the recipe library are untouched; failed saves keep the previous in-memory state. Already damaged/unsupported stores are not automatically truncated or overwritten.
2. **A native HA Store write failure could be falsely acknowledged.** Inspection and isolated execution of the Home Assistant 2026.10.0 Store write handler confirmed that SerializationError/WriteError can be logged without propagating an exception. Existing mock tests only simulated raised errors. b22 uses the public Store with atomic_writes=True and checks its file contents independently in HA's executor before publishing application changes. The check verifies outer key/major version and exact typed JSON payload instead of trusting a returned None or read cache. This covers recipes, their rolling backup, favorites, device grants, send history and artwork. New writes during shutdown are rejected. Missing/malformed/mismatched files surface as generic storage failures; no synchronous file I/O is introduced in the event loop. HA-managed Lovelace resources remain under HA's own collection API.

An accepted settings transmission remains accepted if history persistence fails: history_saved is false, the previous history stays visible and the command is never resent just to save it. Failed permission writes invalidate old confirmations through the access revision, retain the previous stored grant and report failure rather than claiming a durable permission change.

## Permission and failure review

| Surface | Authenticated ordinary user | Administrator |
| --- | --- | --- |
| Shared recipes | Read; no CRUD/import/export management | CRUD, import preview/confirmation and export |
| Personal favorites | Only own user ID from the authenticated connection | Only own personal favorites through that API |
| Device discovery, history, private artwork | Current whole-device grant; scoped before reads and rechecked after awaited reads | Administrator access |
| Supervised settings | Current device grant for every zone/program, connection-bound one-use confirmation | Same fresh device/contract/state checks |
| Grant management, artwork writes, batch tools | Denied in backend | Administrator-only; access-management/image handlers also recheck active role |

Reviewed websocket_api.py, control_api.py, device_access.py, beta_send.py, beta_batch.py, HTTP export, persistence modules, resource/panel registration and frontend connection/role/late-reply behavior. Normal users cannot select another user's favorite identity or turn a card configuration into a grant. No per-zone/program grants were introduced. Revocation/regrant, inactive/system users, stale confirmations, connection changes, busy/cooking/unknown states and dry run remain covered. Unknown send outcomes stop further control and require explicit fresh re-arming; no retry or queued replay was added.

HTTP export retains the native authenticated admin check, short-lived signed path, named JSON attachment and no-store/nosniff headers. HA 2026.10.0 async_sign_path uses the current WebSocket refresh token when available. Private images remain authenticated device-scoped data and are absent from recipe exports. Client errors do not expose raw upstream responses or storage paths; detailed exceptions stay in HA's server logs. No additional blocking authorization defect was identified in the reviewed scope.

## Validation and release decision

Passed locally: **232 Python tests on each of Python 3.12.14 and 3.14.8**, **125 frontend tests**, compilation, module/version consistency, local Markdown links, complete DE/EN document pairs and git diff formatting. New regressions cover favorite capacity/delete/reload/isolation/write failure and native-style silent failures for every application store, backup-before-primary behavior, typed on-disk comparison, shutdown and accepted-send/history-failure behavior. Storage tests use temporary files and simulated HA Store/executor interfaces; they are not native HA runtime tests. The actual HA Store handler was separately exercised with a fake failing write to reproduce the swallowed exception. No LAN/appliance/cloud-control access and no GitHub Actions.

Documentation now records the latest owner acceptance, replaces the obsolete no-dashboard/no-sender checklist, distinguishes current capabilities from historical reports and names the exact supported controller 1.0.3-beta.3. The 44-step settings test and device-control fields are unchanged. No schema migration or capability promotion is performed.

**b22 is a corrective beta, not a release candidate or stable release.** The focused native b22 save/restart check in [the current checklist](../LOCAL_TEST_CHECKLIST.md) is now owner-confirmed. Before candidate promotion, official HACS/Hassfest validation remains outstanding. Those official validators were not run here; local manifest/HACS metadata/translation tests are not presented as replacements. Python 3.14 is now checked locally. The owner's no-Actions instruction remains in force. Broader cooking/time-boundary behavior and deferred features are outside this review's acceptance scope.
