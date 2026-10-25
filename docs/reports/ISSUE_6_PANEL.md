# Issue #6 – Administrator recipe panel

[English](ISSUE_6_PANEL.md) | [Deutsch](ISSUE_6_PANEL.de.md)

## Implementation

This feature branch builds on PR #14 and therefore PR #13. It registers a bundled local recipe page visible only to HA administrators. The UI uses only authenticated WebSocket commands: list/search/categories/tags, create, edit, duplicate, confirmed deletion, JSON export, and import with a conflict preview and explicit confirmation. An optional sample recipe is created only on request. The layout is designed for narrow phone screens and includes complete English/German text with English fallback. It shows the configured HA temperature unit while continuing to store Celsius.

The recipe editor offers existing categories. “Add new category” is the final choice; a name differing only in letter case reuses the existing spelling. Renaming or merging a category across all recipes is tracked as a separate follow-up.

Shared favorites are stored in recipe records, remaining compatible with older recipes. Personal favorites are stored separately under the authenticated HA user ID. Regular users cannot access the admin panel; the backend permits them to change only their own personal favorites. Device and zone control are outside this panel.

The panel uses Home Assistant's `frontend`, `http`, `panel_custom` and `websocket_api` components. These required components are declared in the integration manifest; a missing `http` entry was added after a Hassfest failure.

## Verification and limits

Automated offline tests cover the Python lifecycle, data model, favorite persistence, WebSocket authorization and key frontend flows. They use neither a real HA instance nor an appliance. The project owner opened the integration and admin panel on a phone running Home Assistant OS/Core 2026.10.3. They created a recipe and confirmed that both the recipe and personal favorite survived an HA restart. Editing, duplication, confirmed deletion of the copy, and filtering by name, category and favorite also worked. The category selector and reuse of “Aufbacken” when entering `aufBACKen` were confirmed on the phone. JSON export/import and permissions have not yet been clearly checked locally.

The phone test exposed a missing exit control and no way to open HA's sidebar. The panel header now provides a “Leave” link to the HA home page and a menu button that fires HA's `hass-toggle-menu` event. The project owner then confirmed that both controls work on the phone. The current revision passed 9 frontend and 55 Python offline tests.

For further local acceptance: after a backup, install the updated branch, restart HA and continue the [local test checklist](../LOCAL_TEST_CHECKLIST.md). Pay particular attention to JSON export/import, personal favorites with a second user, regular-user permissions and import conflicts. Do not test live appliance transmission. Hassfest, HACS, Python 3.12 and Python 3.14 passed on GitHub for code commit `9bc513f`.

Program entry is currently free text because no air fryer adapter supplies verified device functions yet. After Issue #7, the recipe editor should offer these programs as choices; Issue #8 will show only functions of the selected air fryer at send time. The necessary backend validation is not implemented yet.
