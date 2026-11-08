"""No appliance calls: plan both zones without authorizing transmission."""
from copy import deepcopy
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch
import unittest

from custom_components.airfryer_recipes.multi_zone import preview
from custom_components.airfryer_recipes.device_access import AccessDenied
from custom_components.airfryer_recipes.command_preview import PreviewTargetNotFound
from custom_components.airfryer_recipes.recipe_model import create_recipe

P1 = {"program": "airfry", "temperature_c": 180, "duration_minutes": 7}
P2 = {"program": "roast", "temperature_c": 190, "duration_minutes": 10}


class MultiZoneTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = NS(data={"airfryer_recipes": {"repository": NS(async_get=AsyncMock())}}, services=NS(async_call=AsyncMock()))
        self.connection = NS(user=NS(id="user"))
        self.device = {"device_id": "d", "model": "CAF-DC111S-AEU", "connectivity": "reported_online",
            "zones": [{"zone_id": 1, "status": "idle"}, {"zone_id": 2, "status": "idle"}],
            "programs": [{"id": p, "temperature_c": {"min": 120, "max": 230}, "duration_minutes": {"min": 1, "max": 60}} for p in ("airfry", "roast")]}
        self.auth = patch("custom_components.airfryer_recipes.multi_zone.authorize_device", new=AsyncMock(return_value=("grant", 1)))
        self.discover = patch("custom_components.airfryer_recipes.multi_zone.discover_devices", new=AsyncMock(return_value={"devices": [self.device]}))
        self.permission = self.auth.start()
        self.discovery = self.discover.start()
        self.addCleanup(self.auth.stop)
        self.addCleanup(self.discover.stop)

    async def run_preview(self, mode="sync", sources=None):
        return await preview(self.hass, self.connection, "d", mode, sources or {"1": {"settings": deepcopy(P1)}, "2": {"settings": deepcopy(P2)}})

    async def test_sync_preserves_settings_and_plans_difference_without_transmission(self):
        result = await self.run_preview()
        self.assertEqual([z["settings"] for z in result["zones"]], [P1, P2])
        self.assertEqual([z["planned_delay_minutes"] for z in result["zones"]], [3, 0])
        self.assertFalse(result["transmitted"])
        self.assertFalse(result["live_send_enabled"])
        self.assertIn("multi_contract_unreviewed", result["blocking_reasons"])
        self.hass.services.async_call.assert_not_called()
        self.discovery.assert_awaited_once_with(self.hass, allowed_device_ids={"d"})

    async def test_match_copies_zone_one_to_both(self):
        result = await self.run_preview("match", {"1": {"settings": P1}})
        self.assertEqual([z["settings"] for z in result["zones"]], [P1, P1])
        self.assertEqual([z["planned_delay_minutes"] for z in result["zones"]], [0, 0])

    async def test_recipe_resolved_on_server_without_editing_it(self):
        recipe = create_recipe("Private recipe", **P1)
        self.hass.data["airfryer_recipes"]["repository"].async_get.return_value = recipe
        result = await self.run_preview("match", {"1": {"recipe_id": recipe.id}})
        self.assertEqual(result["zones"][0]["settings"], P1)
        self.assertNotIn("Private recipe", str(result))

    async def test_unshared_device_rejected_before_discovery(self):
        self.permission.side_effect = AccessDenied
        with self.assertRaises(AccessDenied):
            await self.run_preview()
        self.discovery.assert_not_called()

    async def test_grant_revoked_during_read_rejects_result(self):
        self.permission.side_effect = [("grant", 1), ("grant", 2)]
        with self.assertRaises(AccessDenied):
            await self.run_preview()

    async def test_missing_second_zone_never_falls_back(self):
        self.device["zones"].pop()
        with self.assertRaises(PreviewTargetNotFound):
            await self.run_preview()

    async def test_malformed_or_out_of_range_inputs_are_never_clamped(self):
        for settings in ({**P1, "temperature_c": 999}, {**P1, "program": "unknown"}, {**P1, "start": True}, {**P1, "duration_minutes": True}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                await self.run_preview("match", {"1": {"settings": settings}})
        self.device["programs"][0]["temperature_c"]["max"] = 170
        with self.assertRaises(ValueError):
            await self.run_preview()
        self.hass.services.async_call.assert_not_called()

    async def test_missing_program_or_zone_values_do_not_authorize_send(self):
        with self.assertRaises(ValueError):
            await self.run_preview("sync", {"1": {"settings": P1}})
        with self.assertRaises(ValueError):
            await self.run_preview("start", {"1": {"settings": P1}})
        self.device["programs"] = []
        with self.assertRaises(ValueError):
            await self.run_preview()

    async def test_offline_active_and_unknown_models_are_visible_blockers(self):
        self.device["connectivity"] = "offline"
        self.device["model"] = "other"
        self.device["zones"][1]["status"] = "cooking"
        result = await self.run_preview()
        self.assertTrue({"zone_not_idle", "connection_unknown", "model_unsupported"} <= set(result["blocking_reasons"]))
        self.assertFalse(result["live_send_enabled"])
        self.hass.services.async_call.assert_not_called()
