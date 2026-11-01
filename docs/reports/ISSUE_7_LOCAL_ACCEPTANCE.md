# Local acceptance – both zones

[Deutsch](ISSUE_7_LOCAL_ACCEPTANCE.de.md) | [English](ISSUE_7_LOCAL_ACCEPTANCE.md)

## Complete supervised sequence — 2026-11-01

**PASS for all twelve displayed settings.** The owner supplied the completed sequence screenshot (`Screenshot_20261101_143711_Home Assistant.jpg`) and stated: “Alle Prüfungen bestanden und Gerät ist wieder aus.” (“All checks passed and the appliance is off again.”) The panel shows twelve successful entries and reports matching settings after every command. Test appliance: Cosori Turbo Tower Pro Smart CAF-DC111S-AEU. This is owner-performed local acceptance; Cloud Codex had no appliance access.

| Program | Temperature | Duration | Zone 1 | Zone 2 |
| --- | --- | --- | --- | --- |
| Air Fry | 180 °C | 7 min | PASS | PASS |
| Roast | 190 °C | 10 min | PASS | PASS |
| Bake | 180 °C | 6 min | PASS | PASS |
| Grill | 205 °C | 1 min | PASS | PASS |
| Reheat | 70 °C | 5 min | PASS | PASS |
| Dry | 55 °C | 360 min | PASS | PASS |

The complete run passed the earlier program-change and Dry failure points. It exercised the guided sequence with ending of its own prepared zones between program groups. The final appliance-off state is confirmed by the owner; the panel screenshot itself shows the completed sequence, not an independent off-state report or a reset transport trace.

The shown list is the corrected sequence introduced in 0.1.0b9 and retained in 0.1.0b10. The exact installed version is not visible in the supplied screenshot and is not independently recorded. The agreed adapter contract remains Airfryer Control 1.0.2-beta.1; its version was not re-established from this screenshot.

Acceptance covers these nominal supervised settings and the completed sequence. It does not establish all temperature/duration endpoints, Proof support, every individual-test UI path, arbitrary saved recipes, active-zone changes, SYNC/MATCH, reconnect/error cases or general compatibility. The [owner model ranges and adapter restrictions](ISSUE_7_MODEL_TEMPERATURES.md) remain separate. No capability flags or send permissions are changed by this documentation.

Next work: a model-aware upstream adapter change is needed for the complete Turbo Tower temperature ranges and Proof, followed by contract review and focused supervised acceptance. Additional error/endpoint cases remain in the [extended acceptance plan](BETA_0_1_0B5_TEST_PLAN.md); the twelve nominal checks are not all sixty cases.

Documentation only: German/English parity, local documentation links and git diff --check reviewed. No code tests were rerun for this report, no new device commands, no GitHub Actions and no new beta release.

## Earlier individual acceptance — 2026-10-30

The following records the scope and next steps at that earlier date; the completed sequence above supersedes its then-untested nominal programs.

2026-10-30. Confirmed by the owner in chat; no appliance tests by Cloud Codex.
Test context: Airfryer Recipes 0.1.0b4, agreed upstream version Airfryer Control 1.0.2-beta.1.

| Check | Zone 1 | Zone 2 |
| --- | --- | --- |
| Settings arrived at the selected zone | PASS | PASS |
| Air Fry, 170 °C, one minute | PASS | PASS |
| No heating started | PASS | PASS |
| Other zone remained unchanged | PASS | PASS |

Status refresh enabled the repeat test. Adapter acceptance remaining on screen is this beta's final result, not a running test. Zone 2 required explicitly changing the zone selection in the device preview; the owner then confirmed duration, temperature, zone, no heating and unchanged zone 1.

This confirms only supervised individual transmission of these test settings to both zones. Other programs, limits, free recipe transmission, active zones, SYNC/MATCH and automatic device confirmation are NOT TESTED. Issue #7 remains open.

Next implementation package: select a recipe or manual values for transmission in the existing administrator panel, reusing the tested send path and single-use confirmations. Approve programs and limits only with traceable verification. The existing preview remains free of control calls. Local beta acceptance follows; the dashboard is separate future work.

Documentation only. Reviewed German/English parity; git diff --check passed. No new device calls, GitHub Actions or new beta for this report. Until instructed otherwise, subsequent updates use local checks only, with no GitHub Actions.
