"""Offline checks for the authenticated, named JSON export download."""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import create_recipe
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository


class ExportHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        aiohttp = types.ModuleType("aiohttp")
        aiohttp_web = types.ModuleType("aiohttp.web")

        class Response:
            def __init__(
                self, *, body=None, content_type=None, charset=None, headers=None,
                status=200,
            ):
                self.body = body
                self.content_type = content_type
                self.charset = charset
                self.headers = headers or {}
                self.status = status

        aiohttp.hdrs = SimpleNamespace(
            CACHE_CONTROL="Cache-Control",
            CONTENT_DISPOSITION="Content-Disposition",
        )
        aiohttp.web = aiohttp_web
        aiohttp_web.Request = dict
        aiohttp_web.Response = Response

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
            "aiohttp": aiohttp,
            "aiohttp.web": aiohttp_web,
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
        self.assertEqual(registered, [self.http.RecipeExportView, self.http.DiagnosticExportView])

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

    def test_diagnostic_attachment_has_fixed_name_and_exact_preview(self):
        from custom_components.airfryer_recipes.diagnostic_download import previews
        async def run():
            hass = SimpleNamespace(data={DOMAIN: {"repository": object()}},
                auth=SimpleNamespace(async_get_user=AsyncMock(return_value=SimpleNamespace(is_admin=True,is_active=True))))
            value = {"schema_version":1,"notification_rule_count":0}
            token = previews(hass).create("admin",value)
            value["notification_rule_count"] = 99
            class Request(dict): pass
            request=Request(hass_user=SimpleNamespace(id="admin",is_admin=True));request.app={"hass":hass}
            response=await self.http.DiagnosticExportView().get(request,token)
            self.assertEqual(response.status,200)
            self.assertEqual(response.headers["Content-Disposition"],'attachment; filename="airfryer-recipes-diagnostics.json"')
            self.assertEqual(response.headers["Cache-Control"],"no-store")
            self.assertEqual(response.headers["X-Content-Type-Options"],"nosniff")
            self.assertEqual(json.loads(response.body)["notification_rule_count"],0)
            self.assertTrue(self.http.DiagnosticExportView.requires_auth)
        asyncio.run(run())

    def test_diagnostic_download_rejects_other_users_revocation_and_unload(self):
        from custom_components.airfryer_recipes.diagnostic_download import previews
        async def run():
            current=SimpleNamespace(is_admin=True,is_active=True)
            hass=SimpleNamespace(data={DOMAIN:{"repository":object()}},auth=SimpleNamespace(async_get_user=AsyncMock(return_value=current)))
            token=previews(hass).create("owner",{"schema_version":1})
            class Request(dict): pass
            request=Request(hass_user=SimpleNamespace(id="other",is_admin=True));request.app={"hass":hass}
            self.assertEqual((await self.http.DiagnosticExportView().get(request,token)).status,404)
            request["hass_user"].id="owner";current.is_admin=False
            self.assertEqual((await self.http.DiagnosticExportView().get(request,token)).status,401)
            current.is_admin=True;current.is_active=False
            self.assertEqual((await self.http.DiagnosticExportView().get(request,token)).status,401)
            current.is_active=True;hass.data[DOMAIN].pop("repository")
            self.assertEqual((await self.http.DiagnosticExportView().get(request,token)).status,503)
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
