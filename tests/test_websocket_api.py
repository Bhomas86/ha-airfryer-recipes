"""Offline WebSocket protocol/authorization tests; no real HA or air fryer."""

from __future__ import annotations

import importlib
import json
import sys
import types
import unittest
from functools import wraps
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import create_recipe, recipe_to_dict
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository
from custom_components.airfryer_recipes.favorites import FavoriteRepository


class FakeConnection:
    def __init__(self, is_admin: bool = False, authenticated: bool = True):
        self.user = SimpleNamespace(is_admin=is_admin, id="u1") if authenticated else None
        self.messages = []

    def send_result(self, message_id, value):
        self.messages.append(("result", message_id, value))

    def send_error(self, message_id, code, message):
        self.messages.append(("error", message_id, code, message))


def _make_modules():
    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    ws = types.ModuleType("homeassistant.components.websocket_api")
    http = types.ModuleType("homeassistant.components.http")
    http_auth = types.ModuleType("homeassistant.components.http.auth")
    probatio = types.ModuleType("probatio")

    probatio.Required = lambda key: key
    probatio.Optional = lambda key, default=None: key
    ws.ERR_UNAUTHORIZED = "unauthorized"
    ws.ERR_NOT_FOUND = "not_found"
    ws.ERR_INVALID_FORMAT = "invalid_format"
    ws.registered = []

    def websocket_command(schema):
        def decorate(func):
            func._ws_command = schema["type"]
            return func
        return decorate

    def require_admin(func):
        @wraps(func)
        async def wrapper(hass, connection, msg):
            if connection.user is None or not connection.user.is_admin:
                connection.send_error(msg["id"], "unauthorized", "Administrator required")
                return
            await func(hass, connection, msg)
        return wrapper

    ws.websocket_command = websocket_command
    ws.require_admin = require_admin
    ws.async_response = lambda fn: fn
    ws.async_register_command = lambda hass, command: ws.registered.append(command)
    http_auth.async_sign_path = lambda hass, path, expiration: (
        f"{path}?authSig=test-{int(expiration.total_seconds())}"
    )
    components.websocket_api = ws
    components.http = http
    ha.components = components
    return {
        "probatio": probatio,
        "homeassistant": ha,
        "homeassistant.components": components,
        "homeassistant.components.http": http,
        "homeassistant.components.http.auth": http_auth,
        "homeassistant.components.websocket_api": ws,
    }


def make_recipe(name="Brötchen"):
    return create_recipe(name, program="airfry", temperature_c=170, duration_minutes=8)


class WebsocketTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = _make_modules()
        cls.modules_patch = patch.dict(sys.modules, cls.modules)
        cls.modules_patch.start()
        sys.modules.pop("custom_components.airfryer_recipes.websocket_api", None)
        cls.api = importlib.import_module("custom_components.airfryer_recipes.websocket_api")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("custom_components.airfryer_recipes.websocket_api", None)
        cls.modules_patch.stop()

    async def asyncSetUp(self):
        self.disk = None
        self.writes = 0
        self.fail_write = False

        async def load():
            return self.disk

        async def save(data):
            if self.fail_write:
                raise OSError("storage path: sensitive-internal-path")
            self.disk = data
            self.writes += 1

        self.repo = RecipeRepository(load, save)
        await self.repo.async_load()
        self.hass = SimpleNamespace(data={DOMAIN: {"repository": self.repo}})
        class FavoriteStore:
            value = None

            async def async_load(self):
                return self.value

            async def async_save(self, data):
                self.value = data

        self.favorites = FavoriteRepository(FavoriteStore())
        await self.favorites.async_load()
        self.hass.data[DOMAIN]["favorites"] = self.favorites
        self.admin = FakeConnection(is_admin=True)
        self.user = FakeConnection()

    async def call(self, command_name, connection, **kwargs):
        handler = getattr(self.api, f"ws_{command_name}")
        msg = {"id": len(connection.messages) + 1, "type": f"{DOMAIN}/{command_name}", **kwargs}
        await handler(self.hass, connection, msg)
        return connection.messages[-1]

    async def test_read_list_and_get_allowed_for_non_admin(self):
        recipe = make_recipe()
        await self.repo.async_create(recipe)
        result = await self.call("list", self.user)
        self.assertEqual(result[0], "result")
        self.assertEqual(result[2]["recipes"][0]["name"], "Brötchen")
        self.assertEqual((await self.call("get", self.user, recipe_id=recipe.id))[2]["recipe"]["id"], recipe.id)

    async def test_missing_recipe_returns_structured_error(self):
        error = await self.call("get", self.user, recipe_id="missing")
        self.assertEqual(error[0:3], ("error", 1, "not_found"))

    async def test_unauthenticated_connection_cannot_read(self):
        no_user = FakeConnection(authenticated=False)
        error = await self.call("list", no_user)
        self.assertEqual(error[2], "unauthorized")

    async def test_non_admin_mutations_all_denied_even_with_fake_is_admin(self):
        recipe = recipe_to_dict(make_recipe())
        recipe.pop("id")
        calls = (
            ("create", {"recipe": recipe}),
            ("update", {"recipe": recipe_to_dict(make_recipe())}),
            ("duplicate", {"recipe_id": "anything", "name": "New"}),
            ("delete", {"recipe_id": "anything"}),
            ("import_preview", {"payload": '{"schema_version":1,"recipes":[]}'}),
            ("import_confirm", {"token": "a-token"}),
            ("export", {}),
            ("devices", {}),
            ("prepare_send", {"device_id": "ha-device", "zone_id": 1, "settings": {}}),
        )
        for name, args in calls:
            response = await self.call(name, self.user, **args, is_admin=True)
            self.assertEqual(response[2], "unauthorized", name)
        self.assertEqual(self.writes, 0)

    async def test_admin_create_update_duplicate_delete(self):
        original = recipe_to_dict(make_recipe())
        original.pop("id")
        created = await self.call("create", self.admin, recipe=original)
        self.assertEqual(created[0], "result")
        saved = created[2]["recipe"]
        self.assertNotIn("device_id", saved)
        saved["name"] = "Brötchen kurz"
        updated = await self.call("update", self.admin, recipe=saved)
        self.assertEqual(updated[2]["recipe"]["name"], "Brötchen kurz")
        copy = await self.call(
            "duplicate", self.admin, recipe_id=saved["id"], name="Brötchen Kopie"
        )
        self.assertNotEqual(copy[2]["recipe"]["id"], saved["id"])
        self.assertEqual(len((await self.call("list", self.user))[2]["recipes"]), 2)
        response = await self.call("delete", self.admin, recipe_id=saved["id"])
        self.assertEqual(response[2]["deleted"], saved["id"])

    async def test_client_supplied_id_is_rejected_on_create(self):
        original = recipe_to_dict(make_recipe())
        response = await self.call("create", self.admin, recipe=original)
        self.assertEqual(response[2], "invalid_format")
        self.assertEqual(self.writes, 0)

    async def test_invalid_recipe_and_oversized_payload_do_not_write(self):
        recipe = recipe_to_dict(make_recipe())
        recipe.pop("id")
        recipe["phases"][0]["temperature_c"] = 99999
        self.assertEqual((await self.call("create", self.admin, recipe=recipe))[2], "invalid_format")
        self.assertEqual(
            (await self.call("import_preview", self.admin, payload="x" * 1_000_001))[2],
            "invalid_format",
        )
        self.assertEqual(self.writes, 0)

    async def test_import_preview_requires_explicit_confirmation(self):
        recipe = make_recipe("Maiskolben")
        payload = json.dumps({"schema_version": 1, "recipes": [recipe_to_dict(recipe)]})
        preview = await self.call("import_preview", self.admin, payload=payload)
        self.assertEqual(preview[0], "result")
        self.assertEqual(self.writes, 0)
        token = preview[2]["token"]
        result = await self.call("import_confirm", self.admin, token=token)
        self.assertEqual(result[2]["imported"], 1)
        self.assertEqual(self.writes, 1)
        self.assertEqual(
            (await self.call("import_confirm", self.admin, token=token))[2],
            "preview_expired",
        )

    async def test_import_confirmation_invalidated_by_intervening_write(self):
        payload = json.dumps({"schema_version": 1, "recipes": [recipe_to_dict(make_recipe())]})
        token = (await self.call("import_preview", self.admin, payload=payload))[2]["token"]
        original = recipe_to_dict(make_recipe("Other"))
        original.pop("id")
        await self.call("create", self.admin, recipe=original)
        self.assertEqual(
            (await self.call("import_confirm", self.admin, token=token))[2],
            "preview_expired",
        )

    async def test_admin_export_returns_short_lived_named_download(self):
        result = await self.call("export", self.admin)
        self.assertEqual(result[0], "result")
        self.assertEqual(
            result[2],
            {
                "url": "/api/airfryer_recipes/export?authSig=test-30",
                "filename": "Airfryer-Rezepte-Home-Assistant.json",
                "expires_seconds": 30,
            },
        )
        self.assertNotIn("payload", result[2])

    async def test_disk_errors_do_not_leak_internal_paths(self):
        self.fail_write = True
        recipe = recipe_to_dict(make_recipe())
        recipe.pop("id")
        response = await self.call("create", self.admin, recipe=recipe)
        self.assertEqual(response[2], "storage_error")
        self.assertNotIn("sensitive-internal-path", str(response))
        self.assertEqual((await self.repo.async_list()), ())

    async def test_unloaded_library_refuses_requests(self):
        self.hass.data[DOMAIN].pop("repository")
        response = await self.call("list", self.user)
        self.assertEqual(response[2], "not_configured")

    async def test_personal_favorites_are_bound_to_authenticated_user(self):
        recipe = make_recipe()
        await self.repo.async_create(recipe)
        self.assertEqual((await self.call("favorites", self.user))[2], {"recipe_ids": []})
        result = await self.call("set_favorite", self.user, recipe_id=recipe.id, favorite=True)
        self.assertEqual(result[0], "result")
        self.assertEqual((await self.call("favorites", self.user))[2], {"recipe_ids": [recipe.id]})
        another = FakeConnection()
        another.user.id = "u2"
        self.assertEqual((await self.call("favorites", another))[2], {"recipe_ids": []})
        self.assertEqual((await self.call("set_favorite", another, recipe_id="missing", favorite=True))[2], "not_found")

    async def test_device_discovery_is_admin_only_and_requires_loaded_recipes(self):
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices",
                   return_value={"devices": [], "live_send_enabled": False}) as discover:
            for user in (self.user, FakeConnection(authenticated=False)):
                self.assertEqual((await self.call("devices", user))[2], "unauthorized")
            discover.assert_not_called()
            self.assertEqual((await self.call("devices", self.admin))[2],
                             {"devices": [], "live_send_enabled": False})
            discover.assert_called_once_with(self.hass)
            self.hass.data[DOMAIN].pop("repository")
            self.assertEqual((await self.call("devices", self.admin))[2], "not_configured")
            self.assertEqual(discover.call_count, 1)

    async def test_prepare_send_validates_and_always_returns_dry_run(self):
        discovery = {"devices": [{"device_id": "ha-device", "connectivity": "reported_online",
                                 "zones": [{"zone_id": 1, "status": "idle"}]}]}
        params = {"device_id": "ha-device", "zone_id": 1,
                  "settings": {"program": "airfry", "temperature_c": 180, "duration_minutes": 10}}
        with patch("custom_components.airfryer_recipes.command_preview.discover_devices",
                   return_value=discovery) as read:
            for user in (self.user, FakeConnection(authenticated=False)):
                self.assertEqual((await self.call("prepare_send", user, **params))[2], "unauthorized")
            read.assert_not_called()
            result = await self.call("prepare_send", self.admin, **params)
            self.assertEqual(result[2]["mode"], "dry_run")
            self.assertFalse(result[2]["transmitted"])
            self.assertFalse(result[2]["accepted_by_adapter"])
            for flag in ("dry_run", "live_send_enabled", "is_admin"):
                response = await self.call("prepare_send", self.admin, **params, **{flag: False})
                self.assertEqual(response[2], "invalid_format")
            self.assertEqual(read.call_count, 1)
            discovery["devices"] = []
            self.assertEqual((await self.call("prepare_send", self.admin, **params))[2], "target_not_found")
            self.hass.data[DOMAIN].pop("repository")
            self.assertEqual((await self.call("prepare_send", self.admin, **params))[2], "not_configured")
            self.assertEqual(read.call_count, 2)
        self.assertEqual(self.writes, 0)

    def test_commands_register_once_per_explicit_call(self):
        ws = self.modules["homeassistant.components.websocket_api"]
        ws.registered.clear()
        self.api.register_commands(self.hass)
        commands = {handler._ws_command for handler in ws.registered}
        self.assertEqual(len(commands), 13)
        self.assertEqual(
            commands,
            {f"{DOMAIN}/{name}" for name in (
                "list", "get", "create", "update", "duplicate", "delete",
                "import_preview", "import_confirm", "export", "favorites", "set_favorite",
                "devices",
                "prepare_send",
            )},
        )


if __name__ == "__main__":
    unittest.main()
