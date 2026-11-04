# Dashboard card 1A — supervised beta

[Deutsch](ISSUE_8_DASHBOARD_CARD.de.md) | [English](ISSUE_8_DASHBOARD_CARD.md)

Implemented in 0.1.0b13 following the owner's approved neutral device-focused design. This is the first dashboard package for issue #8; normal-user device permissions, image uploads, customization and general live-control approval remain pending.

## Behavior

The bundled `custom:airfryer-recipes-card` has an original CSS illustration with two vertically stacked tappable drawers, separate zone selectors/status, recipe/manual selection, reported program choices, temperature/time fields and an explicit send button. Neutral slate accents follow HA theme colors. It contains no manufacturer logo, product photograph or third-party graphic. This describes the asset's origin, not legal clearance of another design.

The area below the zone selectors displays **Last sent · Zone X**, program, temperature and duration. It represents the last exact transmission accepted by the adapter, **not current appliance settings or device confirmation**. Switching zones only changes the selected zone and restores its draft or saved snapshot. Form edits, preview, cancellation, rejection and unknown results never overwrite the accepted snapshot. Refresh is read-only. Connection and zone status are reported snapshots; use Refresh to update them. There is no invented countdown or live appliance-state claim.

Unsent drafts are separate per device/zone for the lifetime of the card. Accepted snapshots survive reload/restart in the separate HA Store `airfryer_recipes.sent_settings` (schema 1, at most 256 devices, zones 1/2). Recipes remain device-independent and unchanged. A matching, unchanged recipe reference is restored as a recipe; an edited/deleted recipe restores the exact historical values in manual mode. Stored history is not revalidated as current send permission; every send follows the existing backend validation.

Only exact accepted responses from the existing sender record history, including supervised panel/sequence transmissions after this update. Earlier transmissions cannot be reconstructed. Async writes are serialized; failures preserve the previous snapshot and accepted transmission result. The card warns against resending merely to save history. Damaged/newer stores remain untouched with history writes disabled; recipe management remains usable. Reload reuses a healthy history object/lock so an old in-flight accepted write cannot race a new store instance. No history operation sends or queues commands.

## Safety and access

The card uses the existing **administrator-only supervised beta** backend. The new history endpoint is admin-only and read-only; forged writes/extra fields are rejected. Ordinary-user access awaits backend device/zone ACLs. This release does not grant wider rights through dashboard configuration.

New cards default to `dry_run: true`. The button then calls only the existing server-enforced `prepare_send` preview, with no device-control calls and no history update. `dry_run: false` enables the existing beta preparation and one confirmation showing exact server-resolved values. Tokens remain single-use, short-lived and bound to the authenticated connection; stale results, page leave, configuration change, disconnect and double taps cannot silently issue a new confirmation. There is no automatic retry/reconnect replay. Recovery after uncertain/rejected results still requires physical reset acknowledgement and a fresh read-only check. The card sends settings only; cooking starts physically at the appliance.

The exact adapter pin `1.0.2-beta.1`, CAF-DC111S-AEU target, backend state/range checks and six-program contract are unchanged. Proof and wider temperatures remain deferred. A missing configured/previously selected device never silently falls back to another appliance.

## Installation and local acceptance

1. Back up HA, install `v0.1.0b13` through HACS, restart HA and fully reopen the browser/Companion app. The integration loads the local card module automatically; no dashboard is changed automatically.
2. Dashboard → Edit → Add card → **Airfryer Recipes**. The visual editor supports title, optional HA device ID and test mode. If multiple devices are discovered and no ID is configured, select one in the card. If the picker is cached, fully reload the app; manual YAML also works:

   ```yaml
   type: custom:airfryer-recipes-card
   title: Airfryer Küche
   dry_run: true
   ```

3. Without appliance transmission: check the neutral layout at phone/tablet width, both drawer/zone buttons, recipe/manual fields and test preview. Switching zones, editing values and refreshing must send nothing. Initially **No settings sent yet** is expected; no historical data is invented.
4. Optional supervised live acceptance: as admin, beside the appliance with both zones idle, disable test mode and send one previously tested nominal setting. Confirm exact device/zone/values once, inspect the appliance, then physically cancel its preparation. Do not press Start. The selected zone alone should show its accepted history. Repeat on the other zone only if needed to check separation; switching back must show the first zone's history. No full twelve-step repetition is needed for this card package.
5. Reopen/restart HA and confirm history survives without any transmission. Edit a form without sending: history must stay unchanged. Check offline/page-leave behavior without heating. Normal users must see the beta permission message and cannot access the history/send endpoints.

## Verification

Passed locally: **170 Python tests**, **59 panel frontend tests**, **21 card frontend tests**, Python compilation and diff formatting. Tests cover zone/device isolation, durable snapshots, concurrent and failed writes, damaged/newer storage, permission/field checks, recipe references, dry-run-only routing, exact confirmation, cancellation, stale tokens, disconnect, double taps, units and configuration/editor behavior. Native browser/HA/Companion layout and new appliance acceptance **not run**. Standalone Chromium previously could not start under this environment's socket restrictions; no native-browser result is claimed. HACS/Hassfest and Python 3.14 were not run. No GitHub Actions requested or dispatched.
