"""Offline WebSocket protocol/authorization tests; no real HA or air fryer."""

from __future__ import annotations

import importlib
import json
import sys
import types
import unittest
from functools import wraps
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_components.airfryer_recipes.beta_send import BetaSender, Target

from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import create_recipe, recipe_to_dict
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository
from custom_components.airfryer_recipes.favorites import FavoriteRepository


class FakeConnection:
    def __init__(self, is_admin: bool = False, authenticated: bool = True):
        self.user = SimpleNamespace(is_admin=is_admin, id="u1") if authenticated else None
        self.messages = []
        self.subscriptions = {}

    def send_result(self, message_id, value):
        self.messages.append(("result", message_id, value))

    def send_error(self, message_id, code, message):
        self.messages.append(("error", message_id, code, message))


def _make_modules():
    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    core.Context = SimpleNamespace
    components = types.ModuleType("homeassistant.components")
    ws = types.ModuleType("homeassistant.components.websocket_api")
    http = types.ModuleType("homeassistant.components.http")
    http_auth = types.ModuleType("homeassistant.components.http.auth")
    voluptuous = types.ModuleType("voluptuous")

    voluptuous.Required = lambda key: key
    voluptuous.Optional = lambda key, default=None: key
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
        "voluptuous": voluptuous,
        "homeassistant": ha,
        "homeassistant.core": core,
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
            ("beta_recover", {"device_id": "device", "acknowledge_physical_reset": True}),
            ("batch_prepare", {"device_id": "device"}),
            ("batch_start", {"token": "x", "acknowledge_supervised_batch": True}),
            ("batch_next", {"run_id": "x", "next_token": "x"}),
            ("batch_stop", {"run_id": "x"}),
            ("beta_prepare", {"device_id": "ha-device", "zone_id": 1, "acknowledge_unverified": True}),
            ("beta_confirm", {"token": "forged", "acknowledge_supervised_test": True}),
            ("beta_cancel", {"token": "forged"}),
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

    async def test_beta_routes_use_authenticated_user_and_reject_extra_control_fields(self):
        sender = SimpleNamespace(prepare=AsyncMock(return_value={"transmitted": False}),
                                 confirm=AsyncMock(return_value={"outcome": "accepted"}))
        self.hass.data[DOMAIN]["beta_sender"] = sender
        params = {"device_id": "ha-device", "zone_id": 1, "acknowledge_unverified": True}
        self.assertEqual((await self.call("beta_prepare", self.admin, **params))[0], "result")
        self.assertEqual(sender.prepare.await_args.args[:4], ("u1", "ha-device", 1, True))
        self.assertEqual(sender.prepare.await_args.args[4].user_id, "u1")
        forged = await self.call("beta_prepare", self.admin, **params, settings={"readyStart": False})
        self.assertEqual(forged[2], "invalid_format")
        self.assertEqual(sender.prepare.await_count, 1)
        result = await self.call("beta_confirm", self.admin, token="one", acknowledge_supervised_test=True)
        self.assertEqual(result[0], "result")
        call = sender.confirm.await_args
        self.assertEqual(call.args[:3], ("u1", "one", True))
        self.assertEqual(call.args[3].user_id, "u1")
        self.assertIs(call.kwargs["owner"], self.admin)
        forged = await self.call("beta_confirm", self.admin, token="one",
                                 acknowledge_supervised_test=True, device_id="other")
        self.assertEqual(forged[2], "invalid_format")
        self.assertEqual(sender.confirm.await_count, 1)

    async def test_beta_source_is_forwarded_only_inside_authenticated_preparation(self):
        sender = SimpleNamespace(prepare=AsyncMock(return_value={"transmitted": False}))
        self.hass.data[DOMAIN]["beta_sender"] = sender
        source = {"recipe_id": "server-recipe"}
        params = {"device_id": "ha-device", "zone_id": 2,
                  "acknowledge_unverified": True, "source": source}
        self.assertEqual((await self.call("beta_prepare", self.user, **params))[2], "unauthorized")
        sender.prepare.assert_not_awaited()
        self.assertEqual((await self.call("beta_prepare", self.admin, **params))[0], "result")
        self.assertEqual(sender.prepare.await_args.kwargs["source"], source)
        self.assertIs(sender.prepare.await_args.kwargs["permit"].owner, self.admin)
        self.assertEqual(sender.prepare.await_args.args[0], self.admin.user.id)

    async def test_beta_block_reason_is_allowlisted_and_unload_disables_routes(self):
        from custom_components.airfryer_recipes.beta_send import BetaTestBlocked

        sender = SimpleNamespace(prepare=AsyncMock(side_effect=BetaTestBlocked("freshness")))
        self.hass.data[DOMAIN]["beta_sender"] = sender
        params = {"device_id": "ha-device", "zone_id": 1, "acknowledge_unverified": True}
        result = await self.call("beta_prepare", self.admin, **params)
        self.assertEqual(result[2:], ("beta_test_blocked", "freshness"))
        self.hass.data[DOMAIN].pop("repository")
        self.assertEqual((await self.call("beta_prepare", self.admin, **params))[2], "not_configured")
        self.assertEqual(sender.prepare.await_count, 1)

    def real_beta_sender(self):
        self.hass.auth = SimpleNamespace(async_get_user=AsyncMock(
            return_value=SimpleNamespace(is_admin=True, is_active=True)))
        async def call(domain, service, data, **kwargs):
            self.assertEqual((domain, service), ("airfryer_control", "programm_senden"))
            self.assertTrue(data["einmal"])
            self.assertTrue(data["streng"])
            self.assertFalse(data["bestaetigen"])
            return {"ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app",
                    "gesendet": {key: data[key] for key in ("programm", "temperatur", "minuten", "zone")}}
        self.hass.services = SimpleNamespace(async_call=AsyncMock(side_effect=call))
        sender = BetaSender(self.hass)
        sender._read = AsyncMock(return_value=Target("Kitchen", ("same",)))
        self.hass.data[DOMAIN]["beta_sender"] = sender
        return sender

    async def test_saved_recipes_through_real_routes_and_sender_preserve_library_on_both_zones(self):
        sender = self.real_beta_sender()
        from custom_components.airfryer_recipes.beta_batch import SAMPLES
        recipes = [await self.repo.async_create(create_recipe(f"{program} {temp}", program=program,
                    temperature_c=temp, duration_minutes=minutes)) for program, temp, minutes in SAMPLES]
        before = await self.repo.async_export_json()
        for recipe in recipes:
            for zone in (1, 2):
                prepared = await self.call("beta_prepare", self.admin, device_id="device", zone_id=zone,
                    acknowledge_unverified=True, source={"recipe_id": recipe.id})
                self.assertEqual(prepared[0], "result")
                self.assertEqual(len(self.admin.subscriptions), 1)
                result = await self.call("beta_confirm", self.admin, token=prepared[2]["token"],
                                         acknowledge_supervised_test=True)
                self.assertEqual(result[2]["outcome"], "accepted")
                sent = self.hass.services.async_call.await_args.args[2]
                phase = recipe.phases[0]
                self.assertEqual((sent["zone"], sent["programm"], sent["temperatur"], sent["minuten"]),
                                 (zone, phase.program, phase.temperature_c, phase.duration_minutes))
                self.assertFalse(self.admin.subscriptions)
        self.assertEqual(self.hass.services.async_call.await_count, 44)
        self.assertFalse(sender.pending)
        self.assertEqual(await self.repo.async_export_json(), before)

    async def test_reconnect_and_cancel_routes_cannot_replay_owned_tokens(self):
        self.real_beta_sender()
        prepared = await self.call("beta_prepare", self.admin, device_id="device", zone_id=1,
                                   acknowledge_unverified=True)
        token = prepared[2]["token"]
        other = FakeConnection(is_admin=True)
        result = await self.call("beta_confirm", other, token=token, acknowledge_supervised_test=True)
        self.assertEqual(result[2:], ("beta_test_blocked", "connection_changed"))
        result = await self.call("beta_cancel", other, token=token)
        self.assertEqual(result[2:], ("beta_test_blocked", "confirmation"))
        self.assertTrue((await self.call("beta_cancel", self.admin, token=token))[2]["discarded"])
        self.assertFalse(self.admin.subscriptions)
        self.assertEqual((await self.call("beta_confirm", self.admin, token=token,
                          acknowledge_supervised_test=True))[2:], ("beta_test_blocked", "confirmation"))
        self.hass.services.async_call.assert_not_awaited()

    async def test_recipe_edit_via_api_invalidates_old_confirmation_without_overwriting_the_edit(self):
        self.real_beta_sender()
        recipe = await self.repo.async_create(make_recipe())
        prepared = await self.call("beta_prepare", self.admin, device_id="device", zone_id=2,
                                   acknowledge_unverified=True, source={"recipe_id": recipe.id})
        from dataclasses import replace
        edited = replace(recipe, phases=(replace(recipe.phases[0], temperature_c=190),))
        self.assertEqual((await self.call("update", self.admin, recipe=recipe_to_dict(edited)))[0], "result")
        before = await self.repo.async_export_json()
        result = await self.call("beta_confirm", self.admin, token=prepared[2]["token"],
                                 acknowledge_supervised_test=True)
        self.assertEqual(result[2:], ("beta_test_blocked", "recipe_changed"))
        self.hass.services.async_call.assert_not_awaited()
        self.assertEqual(await self.repo.async_export_json(), before)
        self.assertEqual((await self.repo.async_get(recipe.id)).phases[0].temperature_c, 190)
        self.assertFalse(self.admin.subscriptions)

    async def test_legacy_program_spelling_requires_explicit_recipe_update_before_send(self):
        sender = self.real_beta_sender()
        recipe = await self.repo.async_create(create_recipe("Piccolinies", program="Airfry", temperature_c=180, duration_minutes=7))
        result = await self.call("beta_prepare", self.admin, device_id="device", zone_id=1,
                                 acknowledge_unverified=True, source={"recipe_id": recipe.id})
        self.assertEqual(result[2:], ("beta_test_blocked", "program_unsupported"))
        self.assertEqual((await self.repo.async_get(recipe.id)).phases[0].program, "Airfry")
        sender._read.assert_not_awaited()
        self.hass.services.async_call.assert_not_awaited()
        from dataclasses import replace
        corrected = replace(recipe, phases=(replace(recipe.phases[0], program="airfry"),))
        await self.call("update", self.admin, recipe=recipe_to_dict(corrected))
        for zone in (1, 2):
            prepared = await self.call("beta_prepare", self.admin, device_id="device", zone_id=zone,
                acknowledge_unverified=True, source={"recipe_id": recipe.id})
            self.assertEqual(prepared[2]["settings"], {"program": "airfry", "temperature_c": 180, "duration_minutes": 7})
            result = await self.call("beta_confirm", self.admin, token=prepared[2]["token"], acknowledge_supervised_test=True)
            self.assertEqual(result[2]["outcome"], "accepted")
        self.assertEqual(await self.repo.async_get(recipe.id), corrected)
        self.assertEqual(self.hass.services.async_call.await_count, 2)

    async def test_disconnect_cleanup_revokes_confirmation_and_failed_prepare_removes_subscription(self):
        sender = self.real_beta_sender()
        prepared = await self.call("beta_prepare", self.admin, device_id="device", zone_id=1,
                                   acknowledge_unverified=True)
        callback = self.admin.subscriptions[prepared[1]]
        callback()
        self.admin.subscriptions.clear()  # HA clears the connection on close.
        self.assertFalse(sender.pending)
        self.assertEqual((await self.call("beta_confirm", self.admin, token=prepared[2]["token"],
            acknowledge_supervised_test=True))[2:], ("beta_test_blocked", "confirmation"))
        from custom_components.airfryer_recipes.beta_send import BetaTestBlocked
        sender._read.side_effect = BetaTestBlocked("connection")
        result = await self.call("beta_prepare", self.admin, device_id="device", zone_id=1,
                                 acknowledge_unverified=True)
        self.assertEqual(result[2:], ("beta_test_blocked", "connection"))
        self.assertFalse(self.admin.subscriptions)
        self.hass.services.async_call.assert_not_awaited()

    async def test_cancel_route_rejects_extra_targets_and_control_fields(self):
        sender = SimpleNamespace(cancel=AsyncMock(return_value={"discarded": True, "transmitted": False}))
        self.hass.data[DOMAIN]["beta_sender"] = sender
        result = await self.call("beta_cancel", self.admin, token="one", device_id="other")
        self.assertEqual(result[2], "invalid_format")
        sender.cancel.assert_not_awaited()
        await self.call("beta_cancel", self.admin, token="one")
        sender.cancel.assert_awaited_once_with("u1", "one", owner=self.admin)

    async def test_batch_routes_bind_websocket_owner_and_register_disconnect_stop(self):
        active = SimpleNamespace(cleanup=None)
        batch = SimpleNamespace(prepare=AsyncMock(return_value={"token": "batch"}),
            start=AsyncMock(return_value={"run_id": "batch", "next_token": "one", "total": 12}),
            next=AsyncMock(return_value={"done": True}), stop=Mock(),
            owned=Mock(return_value=active), runs={"batch": active})
        with patch.object(self.api, "_batch", return_value=batch):
            result = await self.call("batch_prepare", self.admin, device_id="ha-device")
            self.assertEqual(result[0], "result")
            self.assertIs(batch.prepare.await_args.args[1], self.admin)
            result = await self.call("batch_start", self.admin, token="batch", acknowledge_supervised_batch=True)
            self.assertEqual(result[0], "result")
            self.admin.subscriptions[result[1]]()
            batch.stop.assert_called_with(active, disconnected=True)
            await self.call("batch_next", self.admin, run_id="batch", next_token="one")
            self.assertIs(batch.next.await_args.args[1], self.admin)
            forged = await self.call("batch_next", self.admin, run_id="batch", next_token="one", settings={})
            self.assertEqual(forged[2], "invalid_format")
            self.assertEqual(batch.next.await_count, 1)

    async def test_recovery_requires_ack_stops_old_plans_and_uses_server_user_context(self):
        old = SimpleNamespace(device="device")
        sender = SimpleNamespace(_authorized=AsyncMock(), recover=AsyncMock(return_value={"rearmed": True, "transmitted": False}))
        batch = SimpleNamespace(sender=sender, runs={"old": old}, stop=Mock())
        with patch.object(self.api, "_batch", return_value=batch):
            params = {"device_id": "device", "acknowledge_physical_reset": False}
            self.assertEqual((await self.call("beta_recover", self.admin, **params))[2], "beta_test_blocked")
            batch.stop.assert_not_called()
            params["acknowledge_physical_reset"] = True
            self.assertEqual((await self.call("beta_recover", self.admin, **params))[0], "result")
            batch.stop.assert_called_once_with(old)
            self.assertEqual(sender.recover.await_args.args[:3], (self.admin.user.id, "device", True))
            self.assertEqual(sender.recover.await_args.args[3].user_id, self.admin.user.id)

    def test_commands_register_once_per_explicit_call(self):
        ws = self.modules["homeassistant.components.websocket_api"]
        ws.registered.clear()
        self.api.register_commands(self.hass)
        commands = {handler._ws_command for handler in ws.registered}
        self.assertEqual(len(commands), 28)
        self.assertEqual(
            commands,
            {f"{DOMAIN}/{name}" for name in (
                "list", "get", "create", "update", "duplicate", "delete",
                "import_preview", "import_confirm", "export", "favorites", "set_favorite",
                "devices", "sent_settings", "control", "access_list", "access_set", "appearance_get", "appearance_set", "appearance_upload",
                "prepare_send", "beta_prepare", "beta_confirm", "beta_cancel",
                "batch_prepare", "batch_start", "batch_next", "batch_stop", "beta_recover",
            )},
        )

    async def test_sent_settings_is_admin_only_read_only_and_rejects_extra_fields(self):
        history = SimpleNamespace(get=Mock(return_value={"available": True, "zones": {}}))
        self.hass.data[DOMAIN]["sent_settings"] = history
        for user in (self.user, FakeConnection(authenticated=False)):
            self.assertEqual((await self.call("sent_settings", user, device_id="device"))[2], "unauthorized")
        history.get.assert_not_called()
        result = await self.call("sent_settings", self.admin, device_id="device")
        self.assertEqual(result[2], {"available": True, "zones": {}})
        history.get.assert_called_once_with("device")
        for params in ({"settings": {}}, {"zone_id": 1}, {"device_id": ""}, {"device_id": 1}):
            result = await self.call("sent_settings", self.admin, **({"device_id": "device"} | params))
            self.assertEqual(result[2], "invalid_format")
        self.assertEqual(history.get.call_count, 1)

    async def access_setup(self):
        from custom_components.airfryer_recipes.device_access import DeviceAccess
        self.admin.user.id = "admin"
        self.user.user.id = "user"
        users = {uid: SimpleNamespace(id=uid, name=uid.title(), is_admin=uid == "admin", is_active=True, system_generated=False) for uid in ("admin", "user", "other")}
        self.hass.auth = SimpleNamespace(async_get_user=AsyncMock(side_effect=lambda uid: users.get(uid)), async_get_users=AsyncMock(side_effect=lambda: list(users.values())))
        access = DeviceAccess(SimpleNamespace(async_load=AsyncMock(return_value=None), async_save=AsyncMock()))
        await access.async_load()
        self.hass.data[DOMAIN]["device_access"] = access
        return access, users

    async def control(self, action, **params):
        return await self.call("control", self.user, action=action, parameters=params)

    async def test_device_permissions_list_and_change_require_current_admin(self):
        access, users = await self.access_setup()
        users["system"] = SimpleNamespace(id="system", name="System", is_active=True, is_admin=False, system_generated=True)
        discovery = {"devices": [{"device_id": "device", "name": "Kitchen"}]}
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices", new=AsyncMock(return_value=discovery)):
            self.assertEqual((await self.call("access_list", self.user))[2], "unauthorized")
            self.assertEqual((await self.call("access_set", self.user, user_id="user", device_id="device", allowed=True))[2], "unauthorized")
            listed = (await self.call("access_list", self.admin))[2]
            self.assertEqual({u["id"] for u in listed["users"]}, {"user", "other"})
            result = await self.call("access_set", self.admin, user_id="user", device_id="device", allowed=True)
            self.assertEqual(result[2], {"saved": True})
            self.assertEqual(access.devices_for("user"), {"device"})
            users["admin"].is_admin = False
            self.assertEqual((await self.call("access_set", self.admin, user_id="user", device_id="device", allowed=False))[2], "unauthorized")

    async def test_grant_rejects_forged_zone_program_flags_and_unknown_targets(self):
        access, users = await self.access_setup()
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices", new=AsyncMock(return_value={"devices": [{"device_id": "device", "name": "Kitchen"}]})):
            for extra in ({"zone_id": 1}, {"program": "airfry"}, {"is_admin": True}, {"allowed": 1}):
                params = {"user_id": "user", "device_id": "device", "allowed": True} | extra
                self.assertEqual((await self.call("access_set", self.admin, **params))[2], "invalid_format")
            self.assertEqual((await self.call("access_set", self.admin, user_id="user", device_id="missing", allowed=True))[2], "target_not_found")
            self.assertEqual((await self.call("access_set", self.admin, user_id="admin", device_id="device", allowed=True))[2], "invalid_format")
            users["user"].is_active = False
            self.assertEqual((await self.call("access_set", self.admin, user_id="user", device_id="device", allowed=True))[2], "unauthorized")
        self.assertEqual(access.devices_for("user"), set())

    async def test_revocation_does_not_require_deleted_device_or_user_to_exist(self):
        access, users = await self.access_setup()
        await access.set("deleted", "unavailable", True)
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices", new=AsyncMock()) as discover:
            self.assertEqual((await self.call("access_set", self.admin, user_id="deleted", device_id="unavailable", allowed=False))[2], {"saved": True})
            discover.assert_not_awaited()
        self.assertEqual(access.devices_for("deleted"), set())

    async def test_control_discovery_only_reads_and_returns_permitted_devices(self):
        access, _ = await self.access_setup()
        result = {"status": "adapter_beta", "devices": [{"device_id": "device", "zones": [{"zone_id": 1}, {"zone_id": 2}]}, {"device_id": "private", "zones": []}]}
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices", new=AsyncMock(return_value=result)) as discover:
            denied = (await self.control("devices"))[2]
            self.assertEqual(denied["devices"], [])
            discover.assert_not_awaited()
            await access.set("user", "device", True)
            visible = (await self.control("devices"))[2]
            discover.assert_awaited_once_with(self.hass, allowed_device_ids={"device"})
            self.assertEqual([d["device_id"] for d in visible["devices"]], ["device"])
            self.assertEqual(len(visible["devices"][0]["zones"]), 2)

    async def test_control_discovery_rechecks_revocation_before_returning_data(self):
        access, _ = await self.access_setup()
        await access.set("user", "device", True)
        async def revoke(*args, **kwargs):
            await access.set("user", "device", False)
            return {"devices": [{"device_id": "device"}]}
        with patch("custom_components.airfryer_recipes.device_discovery.discover_devices", new=revoke):
            self.assertEqual((await self.control("devices"))[2], "unauthorized")

    async def test_control_history_all_zones_of_granted_device_only(self):
        access, _ = await self.access_setup()
        history = SimpleNamespace(get=Mock(return_value={"available": True, "zones": {"1": {}, "2": {}}}))
        self.hass.data[DOMAIN]["sent_settings"] = history
        self.assertEqual((await self.control("sent_settings", device_id="device"))[2], "unauthorized")
        history.get.assert_not_called()
        await access.set("user", "device", True)
        self.assertEqual(set((await self.control("sent_settings", device_id="device"))[2]["zones"]), {"1", "2"})
        self.assertEqual((await self.control("sent_settings", device_id="private"))[2], "unauthorized")
        history.get.assert_called_once_with("device")

    async def test_control_dry_run_requires_grant_and_uses_target_scope(self):
        access, _ = await self.access_setup()
        params = {"device_id": "device", "zone_id": 2, "settings": {"program": "airfry", "temperature_c": 180, "duration_minutes": 7}}
        with patch("custom_components.airfryer_recipes.command_preview.discover_devices", new=AsyncMock(return_value={"devices": [{"device_id": "device", "connectivity": "reported_online", "zones": [{"zone_id": 2, "status": "idle"}]}]})) as discover:
            self.assertEqual((await self.control("prepare_send", **params))[2], "unauthorized")
            discover.assert_not_awaited()
            await access.set("user", "device", True)
            result = (await self.control("prepare_send", **params))[2]
            self.assertFalse(result["transmitted"])
            self.assertEqual(result["mode"], "dry_run")
            discover.assert_awaited_once_with(self.hass, allowed_device_ids={"device"})

    async def test_control_envelope_cannot_invoke_admin_actions_or_override_actor(self):
        await self.access_setup()
        for action in ("create", "batch_start", "access_set", "raw_send"):
            self.assertEqual((await self.control(action))[2], "invalid_format")
        self.assertEqual((await self.control("devices", user_id="admin"))[2], "invalid_format")
        self.assertEqual((await self.control("beta_prepare", device_id="device", zone_id=1, acknowledge_unverified=True, source=None))[2], "invalid_format")
        self.assertEqual((await self.call("control", self.user, action="devices", parameters={}, is_admin=True))[2], "invalid_format")
        self.assertEqual((await self.call("control", FakeConnection(authenticated=False), action="devices", parameters={}))[2], "unauthorized")

    async def test_control_real_sender_sends_recipe_to_both_zones_and_preserves_library(self):
        from custom_components.airfryer_recipes.sent_settings import SentSettings
        access, _ = await self.access_setup()
        await access.set("user", "device", True)
        recipe = await self.repo.async_create(make_recipe())
        history = SentSettings(SimpleNamespace(async_load=AsyncMock(return_value=None), async_save=AsyncMock()))
        await history.async_load()
        self.hass.data[DOMAIN]["sent_settings"] = history
        self.hass.services = SimpleNamespace(async_call=AsyncMock())
        sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = sender
        with patch("custom_components.airfryer_recipes.beta_send.read_target", new=AsyncMock(return_value=Target("Kitchen", ("same",)))):
            for zone in (1, 2):
                result = await self.control("beta_prepare", device_id="device", zone_id=zone, source={"recipe_id": recipe.id}, acknowledge_unverified=True)
                self.assertEqual(result[0], "result")
                self.assertTrue(self.user.subscriptions)
                self.hass.services.async_call.return_value = {"ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app", "gesendet": {"programm": "airfry", "temperatur": 170, "minuten": 8, "zone": zone}}
                result = await self.control("beta_confirm", token=result[2]["token"], acknowledge_supervised_test=True)
                self.assertEqual(result[2]["outcome"], "accepted")
                self.assertFalse(self.user.subscriptions)
        self.assertEqual(self.hass.services.async_call.await_count, 2)
        self.assertEqual(self.hass.services.async_call.await_args.kwargs["context"].user_id, "user")
        self.assertEqual(set(history.get("device")["zones"]), {"1", "2"})
        self.assertEqual(await self.repo.async_get(recipe.id), recipe)
        self.assertEqual((await self.call("delete", self.user, recipe_id=recipe.id))[2], "unauthorized")

    async def test_control_revoked_token_is_not_reusable_but_can_be_discarded(self):
        access, _ = await self.access_setup()
        await access.set("user", "device", True)
        self.hass.services = SimpleNamespace(async_call=AsyncMock())
        sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = sender
        with patch("custom_components.airfryer_recipes.beta_send.read_target", new=AsyncMock(return_value=Target("Kitchen", ("same",)))):
            result = await self.control("beta_prepare", device_id="device", zone_id=1, source={"settings": {"program": "airfry", "temperature_c": 170, "duration_minutes": 1}}, acknowledge_unverified=True)
            token = result[2]["token"]
            await self.call("access_set", self.admin, user_id="user", device_id="device", allowed=False)
            result = await self.control("beta_confirm", token=token, acknowledge_supervised_test=True)
            self.assertEqual(result[2], "beta_test_blocked")
            self.assertEqual((await self.control("beta_cancel", token=token))[2]["discarded"], False)
            self.assertFalse(self.user.subscriptions)
        self.hass.services.async_call.assert_not_awaited()

    async def test_control_recovery_is_explicit_read_only_and_requires_grant(self):
        access, _ = await self.access_setup()
        self.hass.services = SimpleNamespace(async_call=AsyncMock())
        sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = sender
        with patch("custom_components.airfryer_recipes.beta_send.read_target", new=AsyncMock(return_value=Target("Kitchen", ("same",)))) as read:
            self.assertEqual((await self.control("beta_recover", device_id="device", acknowledge_physical_reset=True))[2], "beta_test_blocked")
            read.assert_not_awaited()
            await access.set("user", "device", True)
            result = await self.control("beta_recover", device_id="device", acknowledge_physical_reset=True)
            self.assertEqual(result[2], {"rearmed": True, "transmitted": False})
        self.hass.services.async_call.assert_not_awaited()

    async def test_private_appearance_requires_grant_and_cannot_be_written_by_user(self):
        from custom_components.airfryer_recipes.appearance import AppearanceStore, default_appearance
        access,_ = await self.access_setup()
        artwork=AppearanceStore(SimpleNamespace(async_load=AsyncMock(return_value=None),async_save=AsyncMock()))
        await artwork.load();await artwork.save("device",default_appearance("outline"));self.hass.data[DOMAIN]["appearance"]=artwork
        self.assertEqual((await self.control("appearance_get",device_id="device"))[2],"unauthorized")
        for action,params in (("appearance_get",{"device_id":"device"}),("appearance_set",{"device_id":"device","appearance":default_appearance()}),("appearance_upload",{"image":"x"})):
            self.assertEqual((await self.call(action,self.user,**params))[2],"unauthorized")
        await access.set("user","device",True)
        self.assertEqual((await self.control("appearance_get",device_id="device"))[2]["preset"],"outline")
        self.assertEqual((await self.control("appearance_set",device_id="device",appearance=default_appearance()))[2],"invalid_format")
        await access.set("user","device",False)
        self.assertEqual((await self.control("appearance_get",device_id="device"))[2],"unauthorized")

    async def test_admin_appearance_save_read_reset_and_strict_envelope(self):
        from custom_components.airfryer_recipes.appearance import AppearanceStore, default_appearance
        await self.access_setup()
        artwork=AppearanceStore(SimpleNamespace(async_load=AsyncMock(return_value=None),async_save=AsyncMock()))
        await artwork.load();self.hass.data[DOMAIN]["appearance"]=artwork
        for value in (default_appearance("side_by_side"),default_appearance()):
            self.assertEqual((await self.call("appearance_set",self.admin,device_id="device",appearance=value))[2],{"saved":True})
            self.assertEqual((await self.call("appearance_get",self.admin,device_id="device"))[2],value)
        self.assertEqual((await self.call("appearance_get",self.admin,device_id="device",user_id="forged"))[2],"invalid_format")


if __name__ == "__main__":
    unittest.main()
