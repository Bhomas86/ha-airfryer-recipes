# Extended appliance acceptance – beta 0.1.0b5

[Deutsch](BETA_0_1_0B5_TEST_PLAN.de.md) | [English](BETA_0_1_0B5_TEST_PLAN.md)

**Not yet accepted on the appliance.** Earlier acceptance covers only Air Fry at 170 °C/one minute on both zones. The owner now requested supervised testing of all reported programs. No automatic sequence, heating tests or GitHub Actions.

## Preparation and controls

1. Back up HA; retain exactly Airfryer Control 1.0.2-beta.1. Install Airfryer Recipes v0.1.0b5, restart HA and fully reopen the app.
2. Open the recipe library as an administrator. Select appliance and zone in the upper device-preview section. Both zones must be closed, idle/off, without prepared programs; appliance Celsius, SYNC/MATCH off.
3. Select manual values or a single-phase recipe under settings source. Choose reported program, temperature and minutes. For real attempts, use **“Prepare selected settings for a supervised send”**. The preview button remains free of control commands. The separate button below still prepares only the original fixed 170-°C/one-minute test.
4. Await status refresh and inspect confirmation in the supervised beta section: exact device, zone, program, temperature and duration. Within 15 seconds select “Send once to the appliance” and accept the dialog.
5. Inspect settings directly, confirm the other zone is unchanged and heating stays off. **Do not press Start, including for long durations.** This tests settings transmission, not cooking. Cancel the prepared program at the appliance afterward and let both zones report idle/off again.
6. If heating starts, the wrong zone changes or the outcome is unknown, stop at the appliance and perform no further attempts. Do not bypass ordinary blocks; record test ID and guidance. Unknown-outcome blocks last until HA restarts; restarting does not prove a previous command never arrived.

## Sequence and result sheet

The [CSV result sheet](BETA_0_1_0B5_RESULTS.csv) contains 60 attempts. Open it in Excel/LibreOffice; record PASS, FAIL or NOT TESTED, other zone unchanged, heating off and any guidance. A failure stops at least the affected program block; heating, wrong-zone changes or unknown outcomes stop the whole acceptance. Retest deliberately after correction.

- **A – 12 attempts:** All six reported programs with ordinary manual values on zones 1 and 2.
- **B – 12 attempts:** After passing A, save those values as separate test recipes and send via recipe selection. Do not overwrite personal recipes.
- **C1/C2/C3 – 36 attempts:** After A/B pass for that program, test minimum temperature/one minute, maximum temperature/one minute and ordinary temperature/maximum beta duration. Duration is only prepared, never started or waited out.

| Program | Ordinary °C / min | Contract °C range | Beta maximum min |
| --- | --- | --- | --- |
| Air Fry | 180 / 7 | 120–205 | 60 |
| Roast | 190 / 10 | 120–205 | 240 |
| Bake | 180 / 6 | 80–205 | 240 |
| Grill | 205 / 1 | 205–240 | 30 |
| Reheat | 70 / 5 | 40–205 | 60 |
| Dry | 55 / 10 | 34–95 | 1440 |

These are reviewed upstream contract bounds, **not verified model capabilities**. Backend also enforces current reported limits; record blocking if those are narrower. Skip and report missing programs. `proof` stays blocked. Existing recipe format limits Dry to 1440 minutes even though upstream reports up to 2880.

## Additional checks without intended transmission

- For each program, prepare a temperature just outside the table's range: expect blocking, no clamping and no appliance change.
- Discard confirmation or wait over 15 seconds: no send. Prepare again for a new attempt.
- Edit/delete a test recipe in another session after preparing: old confirmation must block.
- Switch the appliance off before preparation: refresh or state checks must block. Reconnection must not replay commands.
- Open a drawer before preparation: no send. Test running/paused blocking only during otherwise normal appliance use; otherwise record NOT TESTED.
- Normal user account: no administrator test section. Check German/English and Fahrenheit user settings while the appliance stays Celsius; for example 356 °F must arrive as 180 °C.
- Check recipe management and JSON export afterward. Rejected recipes must remain unchanged.

Share no credentials, device identifiers or raw diagnostics. Test IDs and visible outcomes suffice for initial investigation.
