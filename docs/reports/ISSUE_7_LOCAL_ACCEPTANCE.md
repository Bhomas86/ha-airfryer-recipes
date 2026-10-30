# Local acceptance – both zones

[Deutsch](ISSUE_7_LOCAL_ACCEPTANCE.de.md) | [English](ISSUE_7_LOCAL_ACCEPTANCE.md)

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
