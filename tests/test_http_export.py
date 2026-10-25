"""Offline checks for the authenticated, named JSON export download."""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import create_recipe
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository


class ExportHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ha = types.ModuleType("homeassistant")
        components = types.ModuleType("homeassistant.components")
        http = types.ModuleType("homeassistant.components.http")

        class HomeAssistantView:
            requires_auth = True

        http.KEY_HASS = "hass"
        http.HomeAssistantView = HomeAssistantView
        components.http = http
        ha.components = components
        cls.modules_patch = patch.dict(sys.modules, {
            "homeassistant": ha,
            "homeassistant.components": components,
            "homeassistant.components.http": http,
        })
        cls.modules_patch.start()
        sys.modules.pop("custom_components.airfryer_recipes.http", None)
        cls.http = importlib.import_module("custom_components.airfryer_recipes.http")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("custom_components.airfryer_recipes.http", None)
        cls.modules_patch.stop()

    def test_view_registers_once(self):
        registered = []
        hass = SimpleNamespace(
            data={DOMAIN: {}},
            http=SimpleNamespace(register_view=lambda view: registered.append(view)),
        )
        self.http.register_http_view(hass)
        self.http.register_http_view(hass)
        self.assertEqual(registered, [self.http.RecipeExportView])

    def test_admin_download_has_expected_name_and_versioned_json(self):
        async def run():
            async def load():
                return None

            async def save(data):
                return None

            repository = RecipeRepository(load, save)
            await repository.async_load()
            await repository.async_create(create_recipe(
                "Brötchen", program="airfry", temperature_c=170, duration_minutes=8
            ))
            hass = SimpleNamespace(data={DOMAIN: {"repository": repository}})

            class Request(dict):
                pass

            request = Request(
                hass_user=SimpleNamespace(is_admin=True)
            )
            request.app = {"hass": hass}
            response = await self.http.RecipeExportView().get(request)
            self.assertEqual(response.status, 200)
            self.assertEqual(
                response.headers["Content-Disposition"],
                'attachment; filename="Airfryer-Rezepte-Home-Assistant.json"',
            )
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            payload = json.loads(response.body.decode("utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["recipes"][0]["name"], "Brötchen")

        asyncio.run(run())

    def test_non_admin_download_is_refused(self):
        class Request(dict):
            app = {}

        response = asyncio.run(self.http.RecipeExportView().get(Request(
            hass_user=SimpleNamespace(is_admin=False)
        )))
        self.assertEqual(response.status, 401)


if __name__ == "__main__":
    unittest.main()
