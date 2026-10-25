"""Hardware-free Issue #3 tests plus Issue #4 repository initialization."""

import asyncio
import importlib
import json
from pathlib import Path
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.airfryer_recipes import (
    AirfryerRecipesRuntime,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / DOMAIN


class TestIntegrationLifecycle(unittest.TestCase):
    def test_setup_and_unload_config_entry(self):
        record = {"schema_version": 1, "recipes": []}

        async def load():
            return record

        async def save(data):
            nonlocal record
            record = data

        async def run():
            entry = SimpleNamespace(runtime_data=None)
            hass = SimpleNamespace(data={})
            fake = RecipeRepository(load, save)
            calls = []
            api_stub = types.ModuleType("custom_components.airfryer_recipes.websocket_api")
            api_stub.register_commands = lambda hass: calls.append("registered")
            with patch.dict(sys.modules, {"custom_components.airfryer_recipes.websocket_api": api_stub}):
                with patch("custom_components.airfryer_recipes.storage.create_repository", return_value=fake):
                    self.assertTrue(await async_setup_entry(hass, entry))
                    self.assertEqual(calls, ["registered"])
                    self.assertTrue(await async_unload_entry(hass, entry))
                    self.assertNotIn("repository", hass.data[DOMAIN])
                    self.assertTrue(await async_setup_entry(hass, entry))
                    self.assertEqual(calls, ["registered"])
            self.assertIsInstance(entry.runtime_data, AirfryerRecipesRuntime)
            self.assertEqual(await entry.runtime_data.recipes.async_list(), ())

        asyncio.run(run())


class StubConfigFlow:
    def __init_subclass__(cls, **kwargs):
        cls.integration_domain = kwargs["domain"]

    def _set_confirm_only(self):
        self.confirm_only = True

    def async_show_form(self, *, step_id):
        return {"type": "form", "step_id": step_id}

    def async_create_entry(self, *, title, data):
        return {"type": "create_entry", "title": title, "data": data}


class TestConfigFlow(unittest.TestCase):
    def _load_stubbed_flow(self):
        ha = types.ModuleType("homeassistant")
        config_entries = types.ModuleType("homeassistant.config_entries")
        config_entries.ConfigFlow = StubConfigFlow
        config_entries.ConfigFlowResult = dict
        ha.config_entries = config_entries
        with patch.dict(
            sys.modules,
            {"homeassistant": ha, "homeassistant.config_entries": config_entries},
        ):
            sys.modules.pop("custom_components.airfryer_recipes.config_flow", None)
            module = importlib.import_module(
                "custom_components.airfryer_recipes.config_flow"
            )
        self.addCleanup(
            sys.modules.pop, "custom_components.airfryer_recipes.config_flow", None
        )
        return module.AirfryerRecipesConfigFlow

    def test_flow_confirmation_before_creating_entry(self):
        flow_class = self._load_stubbed_flow()
        self.assertEqual(flow_class.integration_domain, DOMAIN)
        flow = flow_class()
        self.assertEqual(
            asyncio.run(flow.async_step_user()), {"type": "form", "step_id": "user"}
        )
        self.assertTrue(flow.confirm_only)
        self.assertEqual(
            asyncio.run(flow.async_step_user({})),
            {"type": "create_entry", "title": "Airfryer Recipes", "data": {}},
        )


class TestPackagedMetadata(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["domain"], DOMAIN)
        self.assertTrue(manifest["config_flow"])
        self.assertTrue(manifest["single_config_entry"])
        self.assertEqual(manifest["integration_type"], "hub")
        self.assertEqual(manifest["iot_class"], "calculated")
        self.assertEqual(manifest["requirements"], [])
        self.assertNotIn("dependencies", manifest)
        self.assertTrue(manifest["version"])

    def test_hacs_metadata(self):
        hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
        self.assertEqual(hacs["name"], "Airfryer Recipes")
        self.assertIn("homeassistant", hacs)

    def test_translations_complete_and_structurally_identical(self):
        en = json.loads((INTEGRATION / "translations/en.json").read_text(encoding="utf-8"))
        de = json.loads((INTEGRATION / "translations/de.json").read_text(encoding="utf-8"))
        strings = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))

        def keys(value):
            if isinstance(value, dict):
                return {key: keys(child) for key, child in value.items()}
            return "text"

        self.assertEqual(keys(en), keys(de))
        self.assertEqual(strings, en)
        self.assertNotEqual(
            en["config"]["step"]["user"]["description"],
            de["config"]["step"]["user"]["description"],
        )

    def test_brand_icon_is_present(self):
        icon = INTEGRATION / "brand" / "icon.png"
        self.assertTrue(icon.exists(), "HACS requires integration-local brand/icon.png")
        self.assertEqual(icon.read_bytes()[:8], bytes((137, 80, 78, 71, 13, 10, 26, 10)))
