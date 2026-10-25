"""Dry-run invariants using only simulated discovery; no appliance access."""

from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from custom_components.airfryer_recipes.command_preview import prepare_preview, PreviewTargetNotFound
from custom_components.airfryer_recipes.recipe_model import RecipeValidationError


class PreviewTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = {"program": "airfry", "temperature_c": 170, "duration_minutes": 8}
        self.hass = SimpleNamespace(services=Mock(), states=Mock())
        self.discovery = {"devices": [{"device_id": "ha-device", "connectivity": "reported_online",
                                      "zones": [{"zone_id": 1, "status": "idle"},
                                                {"zone_id": 2, "status": "idle"}],
                                      "programs": [{"id": "airfry", "limits_status": "estimated",
                                                    "send_status": "unverified"}]}]}
        self.patch = patch("custom_components.airfryer_recipes.command_preview.discover_devices",
                           return_value=self.discovery)
        self.read = self.patch.start()
        self.addCleanup(self.patch.stop)

    async def preview(self, **kwargs):
        return await prepare_preview(self.hass, **{"device_id": "ha-device", "zone_id": 1,
                                                  "settings": self.settings, **kwargs})

    async def test_both_zones_return_exact_values_without_calls_or_mutation(self):
        original = deepcopy(self.discovery)
        for zone in (1, 2):
            result = await self.preview(zone_id=zone)
            self.assertEqual(result["settings"], self.settings)
            self.assertEqual(result["mode"], "dry_run")
            for key in ("live_send_enabled", "transmitted", "accepted_by_adapter", "confirmed_on_device"):
                self.assertIs(result[key], False)
            self.assertIn("freshness_unverified", result["blocking_reasons"])
        self.assertEqual(self.discovery, original)
        self.assertEqual(self.hass.services.mock_calls, [])
        self.assertEqual(self.hass.states.mock_calls, [])

    async def test_even_claimed_live_capability_cannot_enable_send(self):
        self.discovery["live_send_enabled"] = True
        device = self.discovery["devices"][0]
        device.update(freshness="fresh", capabilities={"send_settings": True})
        self.assertFalse((await self.preview())["live_send_enabled"])
        self.assertEqual(self.hass.services.mock_calls, [])

    async def test_active_paused_unknown_and_offline_zones_remain_blocked(self):
        for status in ("cooking", "preheating", "paused", "drawer_open", "unknown", "offline"):
            self.discovery["devices"][0]["zones"][0]["status"] = status
            result = await self.preview()
            self.assertIn("zone_not_idle", result["blocking_reasons"])
            self.assertFalse(result["transmitted"])
        for connectivity in ("offline", "unknown"):
            self.discovery["devices"][0]["connectivity"] = connectivity
            result = await self.preview()
            self.assertIn("device_offline" if connectivity == "offline" else "connection_unknown",
                          result["blocking_reasons"])

    async def test_each_request_rereads_target_and_reconnect_never_replays(self):
        await self.preview()
        self.discovery["devices"][0]["zones"] = []
        with self.assertRaises(PreviewTargetNotFound):
            await self.preview()
        self.discovery["devices"] = []
        with self.assertRaises(PreviewTargetNotFound):
            await self.preview()
        self.assertEqual(self.read.call_count, 3)
        self.assertEqual(self.hass.services.mock_calls, [])

    async def test_invalid_inputs_rejected_before_reading_adapter(self):
        for args in ({"zone_id": True}, {"zone_id": "1"}, {"zone_id": 4},
                     {"device_id": ""}, {"device_id": False}, {"device_id": "a" * 129}):
            with self.assertRaises(RecipeValidationError):
                await self.preview(**args)
        for settings in ({}, {**self.settings, "temperature_c": True},
                         {**self.settings, "temperature_c": float("nan")},
                         {**self.settings, "duration_minutes": 0},
                         {**self.settings, "duration_minutes": 1.5},
                         {**self.settings, "program": ""},
                         {**self.settings, "program": " airfry "},
                         {**self.settings, "program": "x" * 65},
                         {**self.settings, "readyStart": False}):
            with self.assertRaises(RecipeValidationError):
                await self.preview(settings=settings)
        self.read.assert_not_called()

    async def test_capability_provenance_explains_program_blocker(self):
        result = await self.preview()
        self.assertIn("program_limits_unverified", result["blocking_reasons"])
        self.assertNotIn("program_not_reported", result["blocking_reasons"])
        program = self.discovery["devices"][0]["programs"][0]
        program.update(limits_status="confirmed", send_status="confirmed")
        result = await self.preview()
        self.assertNotIn("program_limits_unverified", result["blocking_reasons"])
        result = await self.preview(settings={**self.settings, "program": "proof"})
        self.assertIn("program_not_reported", result["blocking_reasons"])

    async def test_errors_are_not_retried(self):
        self.read.side_effect = ValueError("adapter failed")
        with self.assertRaises(ValueError):
            await self.preview()
        self.read.assert_called_once()
        self.assertEqual(self.hass.services.mock_calls, [])
