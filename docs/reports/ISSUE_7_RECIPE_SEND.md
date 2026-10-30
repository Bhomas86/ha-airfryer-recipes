# Recipe and manual beta transmission

[Deutsch](ISSUE_7_RECIPE_SEND.de.md) | [English](ISSUE_7_RECIPE_SEND.md)

As of 2026-10-30. GPT-6.1 Sol – High, confirmed by the owner. Acceptance of all reported programs was explicitly requested. Extended real appliance acceptance: NOT TESTED.

Optional `source` in `beta_prepare` accepts exactly `recipe_id` or `settings` containing program, Celsius and minutes. Recipes resolve server-side; only one phase is allowed. The immutable phase is stored in the user-bound single-use token. Confirmation accepts no replacement targets/settings. Changed/deleted recipes, replaced repositories and in-progress writes block confirmation. No recipes are clamped, substituted or modified.

The six reviewed upstream IDs airfry/roast/bake/grill/reheat/dry are permitted only for supervised beta tests, when currently reported and inside both reported and reviewed contract bounds. Estimated limits remain unverified; unknown provenance and unreported programs block. Dry stops at the existing 1440-minute recipe limit. The fixed 170-°C/one-minute probe and control-free preview remain available.

Status refresh, unchanged fresh reports, active administrator rights, both idle zones, Celsius, SYNC/MATCH off, 15-second tokens and exactly one variant without retries remain mandatory. Unknown outcomes block further attempts until HA restarts. Adapter acceptance is still not device confirmation.

Passed locally: 119 Python tests (Python 3.12), 25 frontend tests, compilation and git diff --check. New cases cover twelve simulated program/zone transmissions, program-specific bounds/provenance, recipe resolution, tampering, edits/deletion, active storage writes, Fahrenheit conversion and UI token invalidation. GitHub Actions, HACS/Hassfest and Python 3.14 were not run for this change – explicitly local-only validation. Native HA and appliance acceptance belong to the owner.

[Extended test procedure and result sheet](BETA_0_1_0B5_TEST_PLAN.md). Earlier acceptance covers only Air Fry at 170 °C/one minute on both zones; no general approval or heating test.
