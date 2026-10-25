# Issue #6 – Administrator recipe panel

[English](ISSUE_6_PANEL.md) | [Deutsch](ISSUE_6_PANEL.de.md)

## Implementation

This feature branch builds on PR #14 and therefore PR #13. It registers a bundled local recipe page visible only to HA administrators. The UI uses only authenticated WebSocket commands: list/search/categories/tags, create, edit, duplicate, confirmed deletion, JSON export, and import with a conflict preview and explicit confirmation. An optional sample recipe is created only on request. The layout is designed for narrow phone screens and includes complete English/German text with English fallback. It shows the configured HA temperature unit while continuing to store Celsius.

The recipe editor offers existing categories. “Add new category” is the final choice; a name differing only in letter case reuses the existing spelling. Renaming or merging a category across all recipes is tracked as a separate follow-up.

Shared favorites are stored in recipe records, remaining compatible with older recipes. Personal favorites are stored separately under the authenticated HA user ID. Regular users cannot access the admin panel; the backend permits them to change only their own personal favorites. Device and zone control are outside this panel.

The panel uses Home Assistant's `frontend`, `http`, `panel_custom` and `websocket_api` components. These required components are declared in the integration manifest; a missing `http` entry was added after a Hassfest failure.

JSON export no longer creates a nameless browser blob. An administrator receives a download path over WebSocket that is bound to their HA session and valid for 30 seconds. The HTTP endpoint rechecks administrator access and serves `Airfryer-Rezepte-Home-Assistant.json` with caching disabled. This is intended to prevent the Android app from assigning a UUID filename.

## Verification and limits

Automated offline tests cover the Python lifecycle, data model, favorite persistence, WebSocket/HTTP authorization and key frontend flows. They use neither a real HA instance nor an appliance. The current revision passed 10 frontend and 59 Python offline tests.

| Local check on HA OS/Core 2026.10.3 | Result |
| --- | --- |
| Setup and administrator page on a phone | **PASSED** |
| Create a recipe; recipe and personal favorite survive restart | **PASSED** |
| Edit, duplicate and confirm deletion of the copy | **PASSED** |
| Search/filter by name, category and favorite | **PASSED** |
| Category selector; `aufBACKen` reuses “Aufbacken” | **PASSED** |
| Open the HA sidebar and leave the panel | **PASSED** |
| Export JSON, select it again and detect three matching IDs/names in preview | **PASSED** |
| New Android filename `Airfryer-Rezepte-Home-Assistant.json` | **PASSED** |
| Confirm import with `skip`; matching recipes remain unchanged and are not added again | **PASSED** |
| Import with `replace_ids`; replace existing recipes without creating duplicates | **PASSED** |
| Panel is hidden from a regular user without administrator permission | **PASSED** |
| Direct panel URL as a regular user redirects to that user's home page | **PASSED** |
| Separate personal favorites with a second administrator | **PASSED** |
| Recipe changes by one administrator are visible to the other | **PASSED** |

The English UI remains open for further local acceptance. Do not test live appliance transmission.

Program entry is currently free text because no air fryer adapter supplies verified device functions yet. After Issue #7, the recipe editor should offer these programs as choices; Issue #8 will show only functions of the selected air fryer at send time. The necessary backend validation is not implemented yet.
