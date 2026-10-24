"""Hardware-free regression tests for Issue #3 Home Assistant scaffolding.

HA is deliberately stubbed to keep GitHub Actions offline. These tests do
NOT replace an actual Home Assistant OS installation / config flow check.
"""

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
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.airfryer_recipes.const import DOMAIN


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / DOMAIN


class TestIntegrationLifecycle(unittest.TestCase):
    def test_setup_is_device_independent(self):
        result = asyncio.run(async_setup(SimpleNamespace(), {}))
        self.assertTrue(result)

    def test_setup_and_unload_config_entry(self):
        entry = SimpleNamespace(runtime_data=None)
        self.assertTrue(asyncio.run(async_setup_entry(SimpleNamespace(), entry)))
        self.assertIsInstance(entry.runtime_data, AirfryerRecipesRuntime)
        self.assertTrue(asyncio.run(async_unload_entry(SimpleNamespace(), entry)))


class StubConfigFlow:
    """Stand-in for the HA flow class; not a real HA integration test."""

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
        icon = ROOT / "brand" / "icon.png"
        self.assertTrue(icon.exists(), "HACS requires a root brand/icon.png")
        self.assertEqual(icon.read_bytes()[:8], bytes((137, 80, 78, 71, 13, 10, 26, 10)))


if __name__ == "__main__":
    unittest.main()
