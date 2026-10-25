# Issue #6 – Administrator recipe panel

[English](ISSUE_6_PANEL.md) | [Deutsch](ISSUE_6_PANEL.de.md)

## Implementation

This feature branch builds on PR #14 and therefore PR #13. It registers a bundled local recipe page visible only to HA administrators. The UI uses only authenticated WebSocket commands: list/search/categories/tags, create, edit, duplicate, confirmed deletion, JSON export, and import with a conflict preview and explicit confirmation. An optional sample recipe is created only on request. The layout is designed for narrow phone screens and includes complete English/German text with English fallback. It shows the configured HA temperature unit while continuing to store Celsius.

Shared favorites are stored in recipe records, remaining compatible with older recipes. Personal favorites are stored separately under the authenticated HA user ID. Regular users cannot access the admin panel; the backend permits them to change only their own personal favorites. Device and zone control are outside this panel.

## Verification and limits

Automated offline tests cover the Python lifecycle, data model, favorite persistence, WebSocket authorization and key frontend flows. They use neither a real HA instance nor an appliance. The project owner opened the integration and admin panel on a phone running Home Assistant OS/Core 2026.10.3. They created a recipe and confirmed that both the recipe and personal favorite survived an HA restart. Other workflows and permissions have not yet been checked locally.

The phone test exposed a missing exit control and no way to open HA's sidebar. The panel header now provides a “Leave” link to the HA home page and a menu button that fires HA's `hass-toggle-menu` event. This fix passed 6 frontend and 55 Python offline tests. The actual menu behavior on the phone still needs verification after installing the updated branch.

For further local acceptance: after a backup, install the updated branch, restart HA and continue the [local test checklist](../LOCAL_TEST_CHECKLIST.md). Pay particular attention to recipe edits followed by restart, personal favorites with a second user, regular-user permissions and import conflicts. Do not test live appliance transmission. HACS/Hassfest checks for the updated revision are still pending.
