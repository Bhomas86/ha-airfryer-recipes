"""Offline discovery safety: no import of upstream code and no control calls."""

import json
import sys
import types
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock, patch

from custom_components.airfryer_recipes.device_discovery import (
    describe_devices,
    discover_devices,
    normalize_capabilities,
)


class DiscoveryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.device = NS(id="ha-device", name="Kitchen", name_by_user=None,
                         model="CAF-DC111S-AEU", disabled_by=None,
                         identifiers={("airfryer_control", "private-cloud-id")},
                         config_entries={"entry"})
        self.fryer = NS(online=True, last_error=None,
                        state=NS(zones={1: NS(status="bereit"), 2: NS(status="gart")}))
        self.runtime = NS(fryers={"private-cloud-id": self.fryer},
                          api=Mock(), async_request_refresh=Mock())
        self.entry = NS(entry_id="entry", runtime_data=self.runtime)

    def describe(self):
        return describe_devices([self.device], [self.entry])

    def test_two_reported_zones_are_read_only_and_freshness_is_not_invented(self):
        device = self.describe()[0]
        self.assertEqual(device["zones"], [{"zone_id": 1, "status": "idle"},
                                          {"zone_id": 2, "status": "cooking"}])
        self.assertEqual(device["freshness"], "unverified")
        self.assertIsNone(device["reported_at"])
        self.assertFalse(any(device["capabilities"].values()))
        self.assertEqual(device["programs"], [])
        self.assertEqual(self.runtime.api.mock_calls, [])
        self.runtime.async_request_refresh.assert_not_called()

    def test_missing_reported_zone_is_not_synthesized_as_idle(self):
        del self.fryer.state.zones[1]
        self.assertEqual(self.describe()[0]["zones"], [{"zone_id": 2, "status": "cooking"}])

    def test_offline_error_and_unknown_states_never_claim_idle(self):
        self.fryer.online = False
        self.assertEqual(self.describe()[0]["zones"][0]["status"], "offline")
        self.fryer.online = True
        self.fryer.last_error = "private-error"
        self.assertEqual(self.describe()[0]["zones"][0]["status"], "unknown")
        self.fryer.last_error = None
        self.fryer.state.zones[1].status = "new-upstream-status"
        self.assertEqual(self.describe()[0]["zones"][0]["status"], "unknown")

    def test_unknown_model_has_no_guessed_programs_or_control_capabilities(self):
        self.device.model = "unknown-model"
        self.assertEqual(self.describe()[0]["programs"], [])
        self.assertFalse(any(self.describe()[0]["capabilities"].values()))

    def test_credentials_raw_data_and_error_messages_are_not_exposed(self):
        self.fryer.raw_multi = {"token": "private-token"}
        self.fryer.last_error = "private-error"
        self.fryer.info = {"accountId": "private-account"}
        encoded = json.dumps(self.describe())
        for private in ("private-cloud-id", "private-token", "private-error", "private-account"):
            self.assertNotIn(private, encoded)

    def test_disabled_unloaded_and_ambiguous_devices_are_excluded(self):
        self.assertEqual(describe_devices([self.device], []), [])
        self.assertEqual(describe_devices([self.device], [self.entry, self.entry]), [])
        self.device.disabled_by = "user"
        self.assertEqual(self.describe(), [])

    def test_incompatible_runtime_and_invalid_zones_fail_closed(self):
        self.fryer.state.zones = {True: NS(status="bereit"), 4: NS(status="bereit"),
                                 "2": NS(status="bereit")}
        self.assertEqual(self.describe()[0]["zones"], [])
        self.entry.runtime_data = None
        self.assertEqual(self.describe(), [])

    async def test_hass_discovery_handles_missing_or_incompatible_optional_adapter(self):
        helpers = types.ModuleType("homeassistant.helpers")
        dr = types.ModuleType("homeassistant.helpers.device_registry")
        helpers.device_registry = dr
        dr.async_get = Mock(return_value=NS(devices={self.device.id: self.device}))
        services = NS(has_service=Mock(return_value=False), async_call=Mock())
        hass = NS(config_entries=NS(async_loaded_entries=Mock(return_value=[])), services=services)
        with patch.dict(sys.modules, {"homeassistant.helpers": helpers,
                                     "homeassistant.helpers.device_registry": dr}):
            self.assertEqual(await discover_devices(hass), {
                "status": "adapter_missing", "devices": [], "live_send_enabled": False})
            hass.config_entries.async_loaded_entries.return_value = [self.entry]
            result = await discover_devices(hass)
            self.assertEqual(result["status"], "adapter_outdated")
            self.assertEqual(len(result["devices"]), 1)
            dr.async_get.side_effect = ValueError("private-failure")
            self.assertEqual(await discover_devices(hass), {
                "status": "adapter_incompatible", "devices": [], "live_send_enabled": False})
        services.async_call.assert_not_called()

    async def test_public_capability_service_is_allowlisted_without_enabling_send(self):
        helpers = types.ModuleType("homeassistant.helpers")
        dr = types.ModuleType("homeassistant.helpers.device_registry")
        helpers.device_registry = dr
        dr.async_get = Mock(return_value=NS(devices={self.device.id: self.device}))
        payload = {
            "geraet": "private-name", "modell": "CAF-DC111S-AEU",
            "modell_bekannt": False, "zonen": [1, 2, 3],
            "programme": {
                "airfry": {
                    "temperatur": [120, 205], "minuten": [1, 60],
                    "vorschlag": {"temperatur": 195, "minuten": 15},
                    "grenzen": "geschaetzt", "senden": "ungeprueft",
                },
            },
            "verbindung": "ok", "letzte_meldung": "2026-10-25T21:02:00+00:00",
            "revision": 7, "secret": "must-not-leak",
        }
        async_call = AsyncMock(return_value=payload)
        services = NS(has_service=Mock(return_value=True), async_call=async_call)
        hass = NS(config_entries=NS(async_loaded_entries=Mock(return_value=[self.entry])),
                  services=services)
        with patch.dict(sys.modules, {"homeassistant.helpers": helpers,
                                     "homeassistant.helpers.device_registry": dr}):
            result = await discover_devices(hass)
        self.assertEqual(result["status"], "adapter_beta")
        self.assertFalse(result["live_send_enabled"])
        device = result["devices"][0]
        self.assertEqual(device["programs"], [{
            "id": "airfry", "temperature_c": {"min": 120, "max": 205},
            "duration_minutes": {"min": 1, "max": 60},
            "suggested": {"temperature_c": 195, "duration_minutes": 15},
            "limits_status": "estimated", "send_status": "unverified",
        }])
        self.assertEqual(device["reported_at"], "2026-10-25T21:02:00+00:00")
        self.assertEqual(device["revision"], 7)
        self.assertEqual(device["zones"], [{"zone_id": 1, "status": "idle"},
                                           {"zone_id": 2, "status": "cooking"}])
        self.assertNotIn("secret", json.dumps(result))
        async_call.assert_awaited_once_with(
            "airfryer_control", "faehigkeiten", {"geraet": "ha-device"},
            blocking=True, return_response=True,
        )

    def test_malformed_capability_fields_fail_closed(self):
        payload = {
            "modell_bekannt": "yes", "verbindung": "private-state",
            "letzte_meldung": "not-a-time", "revision": True,
            "programme": {
                " valid ": {},
                "broken": {"temperatur": [205, 120], "minuten": [1, 60]},
                "bake": {"temperatur": [120, 205], "minuten": [1, 240],
                         "vorschlag": {"temperatur": 180, "minuten": 20},
                         "grenzen": "new-value", "senden": "new-value"},
            },
        }
        normalized = normalize_capabilities(payload)
        self.assertEqual([program["id"] for program in normalized["programs"]], ["bake"])
        self.assertEqual(normalized["programs"][0]["limits_status"], "unknown")
        self.assertEqual(normalized["connection"], "unknown")
        self.assertIsNone(normalized["reported_at"])
        self.assertIsNone(normalized["revision"])
        self.assertFalse(normalized["model_known"])
