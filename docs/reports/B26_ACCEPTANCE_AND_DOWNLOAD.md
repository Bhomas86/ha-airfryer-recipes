# b26 acceptance and diagnostic download filename

[English](B26_ACCEPTANCE_AND_DOWNLOAD.md) | [Deutsch](B26_ACCEPTANCE_AND_DOWNLOAD.de.md)

## Owner acceptance, 2026-11-09

The owner reports the preceding b26 acceptance plan passed: SYNC/MATCH previews, canceling confirmation, preparing SYNC, preparing MATCH and no automatic heating start. Diagnostic export worked; the filename was cryptic. Rules survived restart. A follow-up explicitly confirms exactly one completion notice arrived on the phone after a real completed cooking cycle. These are owner-reported results, not independent cloud device measurements; the owner did not separately repeat the precise controller version/settings.

The supplied JSON identifies b26 and contains only the nine intended allowlisted technical fields (schema/integration version, loaded/available booleans and rule count), with no personal/device identifiers, names, recipes, credentials or network addresses. The attachment itself was not committed.

The owner's previous authorization permits PR #48 approval after passing tests. Following this acceptance, PR #48 was merged into main at `ba44ba5e9fb2f9ae53aceb3016a19f6c709f2dc3`. The filename correction is isolated in a follow-up branch; no controller or send behavior is changed. #1's focused native preparation acceptance is complete. #10 retains only this export polish/verification and final release validation as relevant follow-up.

## Scoped correction (b27 development)

The old download used a blob URL and the HTML download attribute. Android/Companion can name such downloads using their blob UUID. This is consistent with the uploaded filename; native WebView internals were not traced.

The new download uses an authenticated HTTP attachment with the same readable name in both URL basename and `Content-Disposition`: **`airfryer-recipes-diagnostics.json`**. No blob URL is used. The backend retains the exact preview JSON in a bounded, user-bound, memory-only cache for ten minutes. A separate administrator-only command signs a 30-second download link after verifying the preview belongs to that user. The HTTP handler rechecks active administrator status, ownership, expiry and loaded integration. It returns no-store/nosniff headers. New previews replace that user's old preview; capacity is 128 active users; expired entries are pruned and unload clears the cache. No arbitrary client JSON or custom filename is accepted. A friendly expired-preview message asks the user to show a fresh preview.

Diagnostic content/allowlisting, appliance controls and notification behavior are unchanged. English/German feedback and documentation updated together. No new beta published by this PR and no automatic merge of the filename correction.

## Verification and remaining step

Passed locally: **291 Python tests on 3.12.14 and 136 frontend tests**, compilation and `git diff --check`. New regressions check actual response filename/headers, immutable preview content, current admin and owner restrictions, expiry/replacement, cache bounds, signed URL and exact preview ID routing, and expired-preview UI feedback. Python 3.14 is unavailable in the current runtime; no new Actions or real HA/Companion calls.

After installing the correction and fully reopening the app, show a new diagnostic preview and download. Confirm the name is `airfryer-recipes-diagnostics.json` and its content matches the preview. **No repeat of SYNC/MATCH device tests is needed for this download-only correction.** Final current Python-matrix/HACS/Hassfest evidence and stable version/release metadata remain separate before the stable release; no additional Actions authorization is inferred from acceptance.
