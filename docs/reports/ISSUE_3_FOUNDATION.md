# Development report – Issue #3: Home Assistant integration shell

[English](ISSUE_3_FOUNDATION.md) | [Deutsch](ISSUE_3_FOUNDATION.de.md)

**Status: 2026-10-24.** The following implementation lives on a feature branch and has not been validated on a real Home Assistant instance.

## Implemented

- `custom_components/airfryer_recipes/manifest.json`: Domain, version, documentation, codeowner, config-flow enablement and one config entry.
- `config_flow.py`: Confirm-only setup without cloud credentials or device connectivity. Advanced onboarding and sample recipes remain future work.
- `__init__.py`: Async setup, config-entry setup and unload with no network or appliance calls.
- `const.py`: Shared integration constants.
- `strings.json`, `translations/en.json`, `translations/de.json`: Both onboarding languages.
- `hacs.json` and `custom_components/airfryer_recipes/brand/icon.png`: HACS repository metadata and original branding icon.
- `tests/test_integration_skeleton.py`: Isolated tests for setup/unload, stubbed config flow, metadata, translations and icon.
- Both READMEs updated to distinguish actual work from planned features.

## Outstanding GitHub setting

The HACS validator requires repository topics. The available GitHub connection cannot change this repository setting. The owner should open [the repository](https://github.com/Bhomas86/ha-airfryer-recipes), select the gear icon under **About** on the right, and add topics such as `home-assistant`, `hacs`, `airfryer` and `recipes`. **Do not disable or ignore HACS validation.** The icon location has been corrected to `custom_components/airfryer_recipes/brand/icon.png`.

## Known limitations

**Not a production release.** Recipe storage, management panel, dashboard, device discovery, Airfryer Control adapter and safe device-command coordination remain unimplemented. This confirm-only flow is **not** the full guided onboarding wizard from requirement 27. A package layout does not prove that installation succeeds on real Home Assistant.

Unit tests use a simulated Home Assistant API, **not a real HA runtime**. CI results must be inspected after opening the PR. No real appliance was contacted.

## Local acceptance (pending)

1. Use a separate test instance or back up the production system first.
2. Copy `custom_components/airfryer_recipes` to a Home Assistant test config directory; restart HA.
3. Open **Settings → Devices & services → Add integration → Airfryer Recipes**, then confirm.
4. Reload, restart and remove the entry; inspect the HA logs for import or async problems.
5. Verify it configures without Airfryer Control and prevents a duplicate entry.
6. Switch UI languages between English and German to check translations.
7. Record PASS/FAIL/NOT TESTED with HA versions and logs.

**Release gate:** PR review only; no HACS beta until real Home Assistant setup tests pass.

## References

- [Issue #3](https://github.com/Bhomas86/ha-airfryer-recipes/issues/3)
- [Home Assistant config flow](https://contributors.home-assistant.io/core/integrations/config-flow/)
- [Home Assistant manifest](https://contributors.home-assistant.io/core/integrations/manifest/)
- [HACS requirements](https://www.hacs.xyz/docs/publish/integration/)
