"""Dashboard resource lifecycle without a running HA or device service."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from custom_components.airfryer_recipes.card_resource import CARD_MODULE_URL, CARD_URL, async_register_card_resource
from custom_components.airfryer_recipes.const import DOMAIN, FRONTEND_VERSION


class Resources:
    def __init__(self, items=(), fail=None):
        self.items = deepcopy(list(items))
        self.loaded = False
        self.calls = []
        self.fail = fail

    async def async_get_info(self):
        if self.fail == "load":
            raise OSError("private storage path")
        await asyncio.sleep(0)
        self.loaded = True
        return {"resources": len(self.items)}

    def async_items(self):
        assert self.loaded, "Read lazy collection before loading"
        return deepcopy(self.items)

    async def async_create_item(self, data):
        if self.fail == "create":
            raise OSError("private storage path")
        self.calls.append(("create", deepcopy(data)))
        self.items.append({"id": "created", "url": data["url"], "type": data["res_type"]})

    async def async_update_item(self, item_id, data):
        if self.fail == "update":
            raise OSError("private storage path")
        self.calls.append(("update", item_id, deepcopy(data)))
        item = next(i for i in self.items if i["id"] == item_id)
        item.update(url=data["url"], type=data["res_type"])


class CardResourceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.extra = []
        frontend = ModuleType("homeassistant.components.frontend")
        frontend.add_extra_js_url = lambda hass, url: self.extra.append(url)
        constants = ModuleType("homeassistant.components.lovelace.const")
        constants.LOVELACE_DATA = "lovelace"
        self.stub = patch.dict(sys.modules, {
            "homeassistant.components.frontend": frontend,
            "homeassistant.components.lovelace.const": constants,
        })
        self.stub.start()
        self.addCleanup(self.stub.stop)

    def hass(self, resources=None, mode="storage", dictionary=False):
        data = {"resources": resources, "resource_mode": mode}
        return SimpleNamespace(data={DOMAIN: {}, "lovelace": data if dictionary else SimpleNamespace(**data)})

    async def test_create_loads_collection_first_and_reload_does_not_duplicate(self):
        resources = Resources()
        hass = self.hass(resources)
        await async_register_card_resource(hass)
        await async_register_card_resource(hass)
        self.assertEqual(resources.calls, [("create", {"res_type": "module", "url": CARD_MODULE_URL})])
        self.assertEqual(self.extra, [])

    async def test_upgrade_manual_entry_preserves_its_id_and_foreign_resources(self):
        foreign = [{"id": "other", "url": "/local/other/card.js?v=1", "type": "module"},
                   {"id": "remote", "url": "https://example.invalid" + CARD_URL, "type": "module"},
                   {"id": "bad", "url": "http://[bad", "type": "js"}]
        resources = Resources([{"id": "manual", "url": CARD_URL + "?v=0.1.0b14", "type": "js"}, *foreign])
        await async_register_card_resource(self.hass(resources, dictionary=True))
        self.assertEqual(resources.items[0], {"id": "manual", "url": CARD_MODULE_URL, "type": "module"})
        self.assertEqual(resources.items[1:], foreign)
        self.assertEqual(resources.calls, [("update", "manual", {"res_type": "module", "url": CARD_MODULE_URL})])

    async def test_current_resource_is_left_untouched(self):
        resources = Resources([{"id": "current", "url": CARD_MODULE_URL, "type": "module"}])
        await async_register_card_resource(self.hass(resources))
        self.assertEqual(resources.calls, [])
        self.assertEqual(self.extra, [])

    async def test_existing_duplicates_are_updated_without_deleting_or_adding_rows(self):
        resources = Resources([{"id": "a", "url": CARD_URL + "?v=old", "type": "module"},
                               {"id": "b", "url": CARD_URL, "type": "js"}])
        await async_register_card_resource(self.hass(resources))
        self.assertEqual([i["id"] for i in resources.items], ["a", "b"])
        self.assertTrue(all(i["url"] == CARD_MODULE_URL and i["type"] == "module" for i in resources.items))
        self.assertEqual([c[0] for c in resources.calls], ["update", "update"])

    async def test_yaml_or_missing_storage_uses_fallback_once_without_writing(self):
        for mode, resources in (("yaml", Resources()), ("storage", None)):
            with self.subTest(mode=mode):
                self.extra.clear()
                hass = self.hass(resources, mode=mode)
                await async_register_card_resource(hass)
                await async_register_card_resource(hass)
                self.assertEqual(self.extra, [CARD_MODULE_URL])
                if resources:
                    self.assertFalse(resources.loaded)
                    self.assertEqual(resources.calls, [])

    async def test_storage_failures_fall_back_without_exposing_exception_or_blocking_retry(self):
        for failure in ("load", "create", "update"):
            with self.subTest(failure=failure):
                self.extra.clear()
                resources = Resources([{"id": "existing", "url": CARD_URL, "type": "module"}] if failure == "update" else [], failure)
                hass = self.hass(resources)
                with self.assertLogs("custom_components.airfryer_recipes.card_resource", level="WARNING") as logs:
                    await async_register_card_resource(hass)
                self.assertNotIn("private storage path", str(logs.output))
                self.assertEqual(self.extra, [CARD_MODULE_URL])
                resources.fail = None
                await async_register_card_resource(hass)
                self.assertEqual(resources.items[0]["url"], CARD_MODULE_URL)

    async def test_concurrent_registration_creates_only_one_resource(self):
        resources = Resources()
        hass = self.hass(resources)
        await asyncio.gather(async_register_card_resource(hass), async_register_card_resource(hass))
        self.assertEqual(len(resources.items), 1)
        self.assertEqual(len(resources.calls), 1)

    def test_manifest_and_frontend_dependency_share_the_module_version(self):
        root = Path(__file__).resolve().parents[1] / "custom_components" / DOMAIN
        manifest = json.loads((root / "manifest.json").read_text())
        self.assertEqual(manifest["version"], FRONTEND_VERSION)
        self.assertIn("lovelace", manifest["dependencies"])
        self.assertIn(f'"./panel.js?v={FRONTEND_VERSION}"', (root / "frontend/card.js").read_text())
