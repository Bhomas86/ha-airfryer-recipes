# Recipe program picker and explicit identifier correction

[Deutsch](ISSUE_7_EDITOR_PROGRAM_PICKER.de.md) | [English](ISSUE_7_EDITOR_PROGRAM_PICKER.md)

The owner could not carry out saved-recipe acceptance because the editor required program text input. The supplied preview screenshot shows Piccolinies at 180 °C / 7 minutes with `Airfry` marked as not reported. The reviewed adapter reports the distinct identifier `airfry`. Recipe schema v1 deliberately preserves identifier case and does not associate a recipe with a device. This is an authoring gap; it is not evidence of an appliance transmission failure.

Beta 0.1.0b12 offers a native select in the recipe editor using `selectedDevice().programs`. It uses the same translated program names and provenance labels as the preview. Option values are the exact reported IDs. A new recipe starts with an empty required choice, not an implicitly selected program. The model profile's descriptive Proof entry does not add a selectable adapter program.

An existing unreported identifier is retained as the selected option and marked as missing. The preview links directly to editing that recipe and scrolls the editor into view. The owner chooses the reported program and saves the same recipe ID; no other records are changed. There is no case folding, alias lookup, migration, automatic substitution or program mapping at send time. Editing/viewing alone performs no mutation or device control.

A separate toggle enables free program input when adapter choices exist. Without reported programs, the text field remains available. Only the program ID is stored, never device/zone/profile metadata. Selecting another program does not clamp temperature/time or replace the owner's values. Existing backend permission, provenance, program, range and fresh-state checks still govern any later supervised send. Proof, wider temperatures and the exact adapter version pin remain unchanged.

Before rebuilding the editor DOM, capture its current draft: name, description, raw tags, shared favorite, category/new-category text, program and values. This prevents program/mode switches, capability refreshes or other renders from resetting unsaved fields. The last rendered unit interprets an existing temperature field when the HA unit setting changes. New editor instances reset transient mode/category state. Multi-phase editing remains disabled; a recipe editor left open when admin permission is lost is hidden and cannot save. Saving a recipe discards old visible test confirmations/previews.

## Validation

Passed locally: **164 Python tests, 59 frontend tests**, compilation, local documentation links and git diff --check. Frontend checks cover localized reported choices, empty required selection, exclusion of profile-only programs, preserved `Airfry` until explicit save, same-ID correction with unchanged values, no device/zone persistence, custom/no-adapter mode, draft/category/tag/favorite preservation, capability refresh, unit conversion and permission loss. An integrated API/repository/sender test rejects the legacy spelling without a device read or send, then accepts the explicitly updated recipe on zones 1 and 2 using mocked device transport.

Frontend tests use VM/DOM stubs. A separate Chromium/native-FormData smoke page was prepared, but Chromium exited before executing it because the cloud environment rejected a socket operation (`setsockopt: Operation not permitted`); no browser pass is claimed. Real HA/Companion, new physical appliance tests, HACS/Hassfest and Python 3.14 were not run. No GitHub Actions.

## Focused owner check

Install v0.1.0b12 and restart HA; fully reopen the app. Keep the same Airfryer Control version used with the previous beta. If needed, refresh devices and select the air fryer in the device preview.

1. Select Piccolinies. Use “Edit recipe program” or its normal Edit button. Choose Air Fry / Heißluft-Frittieren from the program dropdown, retain 180 °C and 7 minutes, then save. The preview must now show the reported choice instead of the old missing `Airfry` option.
2. Create a separate test recipe using the dropdown without typing a program identifier. Select program, temperature and duration and save. Check that reopening the recipe retains the choice and values.
3. Continue [R1/R2 and interruption acceptance](ISSUE_7_RECIPE_LIFECYCLE.md) with the corrected saved recipe. Remain beside the appliance, do not press Start and cancel prepared settings between sends.

New editor and corrected saved-recipe acceptance on the owner's HA: **NOT TESTED**. The earlier twelve-program/zone settings sequence remains accepted at its documented nominal values; this fix does not expand that scope.
