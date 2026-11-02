"""Whole-device grants and revocation during single-shot sending."""
import asyncio
from copy import deepcopy
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, patch

from custom_components.airfryer_recipes.device_access import DeviceAccess, AccessDenied, authorize_device
from custom_components.airfryer_recipes.beta_send import BetaSender, BetaTestBlocked, Target
from custom_components.airfryer_recipes.const import DOMAIN


class Store:
    def __init__(self, raw=None):
        self.raw = deepcopy(raw)
        self.fail = False
        self.wait = None
        self.entered = asyncio.Event()

    async def async_load(self):
        return deepcopy(self.raw)

    async def async_save(self, raw):
        self.entered.set()
        if self.wait:
            await self.wait.wait()
        if self.fail:
            raise OSError("private path")
        self.raw = deepcopy(raw)


class DeviceAccessTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store = Store()
        self.access = DeviceAccess(self.store)
        await self.access.async_load()
        self.user = NS(is_admin=False, is_active=True)
        self.hass = NS(data={DOMAIN: {"device_access": self.access}}, auth=NS(async_get_user=AsyncMock(return_value=self.user)),
                       services=NS(async_call=AsyncMock(return_value={"ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app", "gesendet": {"programm": "airfry", "temperatur": 170, "minuten": 1, "zone": 1}})))
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        self.read = AsyncMock(return_value=Target("Kitchen", ("same",)))
        self.patcher = patch("custom_components.airfryer_recipes.beta_send.read_target", self.read)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    async def prepare(self, device="device", zone=1, owner=None):
        from custom_components.airfryer_recipes.beta_send import SendPermit
        return await self.sender.prepare("user", device, zone, True, None, permit=SendPermit(owner=owner))

    async def test_default_deny_and_grant_is_for_whole_device(self):
        with self.assertRaises(AccessDenied):
            await authorize_device(self.hass, "user", "device")
        await self.access.set("user", "device", True)
        for zone in (1, 2):
            result = await self.prepare(zone=zone)
            self.assertEqual(result["zone_id"], zone)
        with self.assertRaises(BetaTestBlocked):
            await self.prepare("other-device")
        self.hass.services.async_call.assert_not_awaited()

    async def test_restart_preserves_grants_and_user_device_isolation(self):
        await asyncio.gather(self.access.set("user", "device", True), self.access.set("other", "second", True))
        restored = DeviceAccess(self.store)
        await restored.async_load()
        self.assertEqual(restored.devices_for("user"), {"device"})
        self.assertEqual(restored.devices_for("other"), {"second"})
        self.assertEqual(restored.devices_for("missing"), set())
        returned = restored.devices_for("user")
        returned.add("forged")
        self.assertEqual(restored.devices_for("user"), {"device"})

    async def test_corrupt_or_newer_storage_is_preserved_and_denies_users(self):
        for raw in ({"schema_version": 2, "users": {}}, {"schema_version": 1, "users": {"u": ["a", "a"]}}, {"schema_version": 1, "users": {"u": [{"device_id": "x", "zone": 1}]}}, {"users": {}}):
            store = Store(raw)
            access = DeviceAccess(store)
            await access.async_load()
            self.assertFalse(access.available)
            self.assertEqual(access.devices_for("u"), set())
            with self.assertRaises(ValueError):
                await access.set("u", "device", True)
            self.assertEqual(store.raw, raw)

    async def test_invalid_ids_flags_and_noop_do_not_change_storage(self):
        for uid, did, allowed in (("", "d", True), ("u", " d", True), ("u", "d", 1)):
            with self.assertRaises(ValueError):
                await self.access.set(uid, did, allowed)
        self.assertFalse(await self.access.set("u", "d", False))
        self.assertIsNone(self.store.raw)

    async def test_allowed_send_uses_exactly_one_transport_attempt(self):
        await self.access.set("user", "device", True)
        prepared = await self.prepare()
        result = await self.sender.confirm("user", prepared["token"], True, None)
        self.assertEqual(result["outcome"], "accepted")
        self.hass.services.async_call.assert_awaited_once()
        with self.assertRaises(BetaTestBlocked):
            await self.sender.confirm("user", prepared["token"], True, None)

    async def test_revocation_and_regrant_cannot_revive_old_confirmation(self):
        await self.access.set("user", "device", True)
        prepared = await self.prepare()
        await self.access.set("user", "device", False)
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender.confirm("user", prepared["token"], True, None)
        await self.access.set("user", "device", True)
        with self.assertRaises(BetaTestBlocked):
            await self.sender.confirm("user", prepared["token"], True, None)
        self.hass.services.async_call.assert_not_awaited()

    async def test_revocation_during_preparation_or_final_validation_blocks_control(self):
        for stage in ("prepare", "confirm"):
            await self.access.set("user", "device", True)
            self.read.side_effect = None
            prepared = await self.prepare() if stage == "confirm" else None
            async def revoke(*args, **kwargs):
                await self.access.set("user", "device", False)
                return Target("Kitchen", ("same",))
            self.read.side_effect = revoke
            with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
                if prepared:
                    await self.sender.confirm("user", prepared["token"], True, None)
                else:
                    await self.prepare()
        self.hass.services.async_call.assert_not_awaited()

    async def test_write_in_progress_blocks_and_failed_write_preserves_old_grants(self):
        await self.access.set("user", "device", True)
        prepared = await self.prepare()
        old = deepcopy(self.store.raw)
        self.store.entered.clear()
        self.store.wait = asyncio.Event()
        self.store.fail = True
        task = asyncio.create_task(self.access.set("user", "device", False))
        await self.store.entered.wait()
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender.confirm("user", prepared["token"], True, None)
        self.store.wait.set()
        with self.assertRaises(OSError):
            await task
        self.assertEqual(self.store.raw, old)
        self.assertEqual(self.access.devices_for("user"), {"device"})
        with self.assertRaises(BetaTestBlocked):
            await self.sender.confirm("user", prepared["token"], True, None)
        self.hass.services.async_call.assert_not_awaited()

    async def test_inactive_user_wrong_owner_and_admin_tools_remain_blocked(self):
        await self.access.set("user", "device", True)
        owner = object()
        prepared = await self.prepare(owner=owner)
        with self.assertRaisesRegex(BetaTestBlocked, "connection_changed"):
            await self.sender.confirm("user", prepared["token"], True, None, owner=object())
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender._authorized("user")  # Guided admin tools.
        self.user.is_active = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender.confirm("user", prepared["token"], True, None, owner=owner)
        self.hass.services.async_call.assert_not_awaited()

    async def test_admin_bypass_does_not_require_permission_store(self):
        self.hass.data[DOMAIN].pop("device_access")
        self.user.is_admin = True
        self.assertIsNone(await authorize_device(self.hass, "admin", "device"))
        await self.prepare()

    async def test_owner_can_cancel_after_revocation_without_sending(self):
        await self.access.set("user", "device", True)
        prepared = await self.prepare()
        await self.access.set("user", "device", False)
        self.assertTrue((await self.sender.cancel("user", prepared["token"]))["discarded"])
        self.hass.services.async_call.assert_not_awaited()

    async def test_system_account_cannot_use_an_ordinary_user_grant(self):
        await self.access.set("user", "device", True)
        self.user.system_generated = True
        with self.assertRaises(AccessDenied):
            await authorize_device(self.hass, "user", "device")

    async def test_regrant_before_first_confirmation_still_requires_a_new_token(self):
        await self.access.set("user", "device", True)
        prepared = await self.prepare()
        await self.access.set("user", "device", False)
        await self.access.set("user", "device", True)
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender.confirm("user", prepared["token"], True, None)
        self.assertNotIn(prepared["token"], self.sender.pending)
        self.hass.services.async_call.assert_not_awaited()
