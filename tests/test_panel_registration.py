"""Offline checks for panel registration, permissions and reload behavior."""

import asyncio
from pathlib import Path
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.panel import (
    MODULE_URL,
    PANEL_PATH,
    async_register_panel,
    async_remove_panel,
)


class PanelRegistrationTests(unittest.TestCase):
    def test_admin_panel_uses_local_module_and_registers_once(self):
        calls = []

        class StaticPathConfig:
            def __init__(self, url_path, path, cache_headers=True):
                self.url_path = url_path
                self.path = path
                self.cache_headers = cache_headers

        class Http:
            async def async_register_static_paths(self, paths):
                calls.append(("static", paths))

        async def register_panel(hass, **kwargs):
            calls.append(("panel", kwargs))

        ha = types.ModuleType("homeassistant")
        components = types.ModuleType("homeassistant.components")
        panel_custom = types.ModuleType("homeassistant.components.panel_custom")
        frontend = types.ModuleType("homeassistant.components.frontend")
        http = types.ModuleType("homeassistant.components.http")
        panel_custom.async_register_panel = register_panel
        frontend.async_remove_panel = lambda hass, path: calls.append(("remove", path))
        http.StaticPathConfig = StaticPathConfig
        components.panel_custom = panel_custom
        components.frontend = frontend
        ha.components = components
        hass = SimpleNamespace(data={DOMAIN: {}}, http=Http())
        with patch.dict(sys.modules, {
            "homeassistant": ha,
            "homeassistant.components": components,
            "homeassistant.components.panel_custom": panel_custom,
            "homeassistant.components.frontend": frontend,
            "homeassistant.components.http": http,
        }):
            asyncio.run(async_register_panel(hass))
            async_remove_panel(hass)
            asyncio.run(async_register_panel(hass))

        self.assertEqual(len([call for call in calls if call[0] == "static"]), 1)
        self.assertEqual(len([call for call in calls if call[0] == "panel"]), 2)
        static = calls[0][1][0]
        self.assertEqual(static.url_path, MODULE_URL)
        self.assertTrue(Path(static.path).is_file())
        self.assertFalse(static.cache_headers)
        self.assertTrue(calls[1][1]["require_admin"])
        self.assertEqual(calls[1][1]["frontend_url_path"], PANEL_PATH)
        self.assertEqual(calls[2], ("remove", PANEL_PATH))
