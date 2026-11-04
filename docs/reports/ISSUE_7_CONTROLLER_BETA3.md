# Reviewed controller beta, Proof and temperature-boundary run

[Deutsch](ISSUE_7_CONTROLLER_BETA3.de.md) | [English](ISSUE_7_CONTROLLER_BETA3.md)

**Current acceptance/review (b22, 2026-11-04):** Owner confirms card behavior, completion of all 44 reported-value steps and the subsequent Proof recipe test. Historical pending statements below describe their release-time evidence. Current b22 native restart and official metadata checks are still pending. [Exact evidence, fixes and release decision](FINAL_REVIEW.md).

The owner confirmed both b20 artwork styles and requested B first/default in the editor, without a standalone release. That preference is included with the controller work in b21. Existing explicit A/B choices remain unchanged. On 2026-11-04 the owner reported the upstream developer's temperature/Proof implementation and requested its review, integration and coverage in the large supervised run. This authorizes test preparation and implementation; appliance acceptance is still performed by the owner.

## Reviewed source and preserved transport

Latest published upstream prerelease at review: [Airfryer Control v1.0.3-beta.3](https://github.com/misterm2310/airfryer-control/releases/tag/v1.0.3-beta.3). Its tag and manifest identify commit [a9fc49e37c3d2698d21bfb361192717ff790eb6e](https://github.com/misterm2310/airfryer-control/tree/a9fc49e37c3d2698d21bfb361192717ff790eb6e). The supervised send path now requires exactly version 1.0.3-beta.3. Older releases, earlier betas and unreviewed future versions do not pass this gate. Recipe management/read-only discovery remain independent of live-send eligibility.

Reviewed files: modelle.py (Turbo Tower profile), faehigkeiten.py, services.py, senden.py, core/api.py, coordinator.py, core/parser.py, switch.py, sensor.py, __init__.py, const.py and manifest.json, all from that commit. The model-aware service accepts proof and the seven reported model temperature ranges. The fixed multi_app variant maps proof to Proof, requests startMultiCook with readyStart: true, and once=True passes retry=False to bypass_v2. Its _once branch does not relogin/replay that control request. streng=True rejects out-of-range values instead of clamping them; bestaetigen=False avoids treating cached upstream confirmation as our own evidence. The settings call fields and exactly-one-attempt result validation stay unchanged. Per-zone switch.turn_off still resolves the selected zone to endCook; it does not request a heating start.

Airfryer Recipes additionally checks exact CAF-DC111S-AEU identity, Celsius, both freshly reported zones inactive, SYNC/MATCH off, matching state/revision/capabilities and current authorization. Proof requires the capability report's 1 °C step. The step joins the confirmation/run fingerprint. Missing, malformed or unknown metadata stays blocking. Ordinary users still require a current whole-device grant. No raw API, alternative spelling, start-capable service or retry was added.

## Limits and provenance

| Program | Temperature °C | Upstream duration ceiling, minutes | Our beta duration ceiling | Run temperatures °C | Run duration, minutes |
| --- | --- | --- | --- | --- | --- |
| Air Fry | 120–230 | 60 | 60 | 120, 180, 230 | 7 |
| Roast | 175–230 | 240 | 240 | 175, 190, 230 | 10 |
| Bake | 80–205 | 240 | 240 | 80, 180, 205 | 6 |
| Grill | 160–230 | 30 | 30 | 160, 205, 230 | 1 |
| Reheat | 40–205 | 60 | 60 | 40, 70, 205 | 5 |
| Dry | 35–95 | 2880 | 1440 | 35, 55, 95 | 360 |
| Proof | 30–45, step 1 | 720, estimated | 720 | 30, 31, 35, 45 | 60 |

The upstream source label besitzer is normalized to owner_reported, not confirmed or unknown. UI labels explicitly retain unverified limits/sending. Temperature steps are allowlisted as ordinary bounded integers; booleans are rejected. Upstream's grouped owner-source label does not establish duration acceptance: the Proof ceiling is explicitly estimated, other duration bounds also remain unverified on this appliance, and our recipe/manual schema still caps all durations at 1440 minutes. The run checks temperatures, not duration endpoints or actual cooking. Existing accepted nominal transmissions do not establish the new endpoints or Proof.

## Large run and stop behavior

The full list has **44 settings**: 22 temperature/duration combinations, each sent to zone 1 then zone 2. It includes lower/nominal/upper temperatures for all seven programs and the adjacent Proof values 30/31 °C. The UI displays every setting and zone-ending transition before one explicit supervised confirmation. Missing programs or a report that cannot cover their entire sample group cause that whole program to appear as skipped, never silently dropping only its new endpoint. The complete acceptance requires no skipped program.

Before each different temperature/program pair, end and freshly verify both prepared zones owned by this run, then prepare the next pair. This also applies to temperature changes within the same program. A full run has 42 zone-ending actions between the 22 pairs; the final pair is canceled physically by the owner. Each next step consumes a new connection-bound nonce and rechecks state, capabilities and permissions. Stops, rejection, readback mismatch, unknown outcome, expiry, role/connection change or missing reset controls prevent further steps. No queue or automatic continuation/retry. The existing 20-minute run bound remains; an expired run cannot replay its steps. Reported matching values are not a general model/cooking approval.

## Evidence and local procedure

Local validation: **220 Python and 125 frontend tests**, compilation, language-pair/link checks and git diff formatting. New coverage includes real-shaped pinned capability data, owner provenance/step validation, version rejection, all seven programs, both-zone endpoint/Proof reads, a complete 44-step run through real sender/read_target with fake public services and fresh state, a 44-recipe-transmission WebSocket/repository path, same-program resets and missing/incomplete capability groups. Dry run with owner-reported Proof still makes no control call. No user photo, credentials or diagnostics are included in the fixture.

Separately executed isolated function bodies from the pinned upstream source: 30 successful boundary/Proof-step cases through _program, async_send and build_variants, plus seven strict below-bound rejections. Every transport was simulated; successful cases requested readyStart: true, multi_app and retry=False exactly once. This is not an upstream HA integration test or evidence from an appliance. No cloud/LAN/appliance access, GitHub Actions, HACS/Hassfest, Python 3.14 or native HA/Companion test was run.

Update Airfryer Control to **1.0.3-beta.3** and Airfryer Recipes to **b21**, restart HA and reopen the app. Physically cancel previous preparations, check both zones idle and remain beside the empty appliance; do not press Start. In the admin recipe panel, show the guided test sequence. Expect **44 steps, seven programs, no skips**, the table's values and explicit resets between temperature pairs. Review the list and confirm it once. Observe both zones, including no heat, unchanged opposite-zone values except its listed reset/send, and correct program/temperature/time for each step. If heating, unexpected behavior, a rejection or a stop occurs, cancel at the appliance and report the exact step/program/temperature/zone; do not replay a lost request. After completion cancel the final Proof settings physically. Report these observations separately from the UI's telemetry match. This new acceptance remains pending.
