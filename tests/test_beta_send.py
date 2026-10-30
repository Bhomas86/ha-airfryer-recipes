"""Commissioning safety tests; fake public services only, no appliance access."""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS, ModuleType
import sys
import unittest
from unittest.mock import AsyncMock, Mock, patch

from custom_components.airfryer_recipes.beta_send import (
    BetaSender, BetaTestBlocked, Target, read_target, TEST_SETTINGS,
)
from custom_components.airfryer_recipes.const import DOMAIN


class SenderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = NS(data={DOMAIN: {}}, auth=NS(async_get_user=AsyncMock(
            return_value=NS(is_admin=True, is_active=True))),
            services=NS(async_call=AsyncMock(return_value={
                "ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app",
                "gesendet": {"programm": "airfry", "temperatur": 170, "minuten": 1, "zone": 1},
                "raw": "secret", "bestaetigt": True,
            })))
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        self.read = AsyncMock(return_value=Target("Kitchen", ("same",)))
        p = patch("custom_components.airfryer_recipes.beta_send.read_target", self.read)
        p.start()
        self.addCleanup(p.stop)

    async def prepare(self, user="u1", device="device", zone=1):
        return await self.sender.prepare(user, device, zone, True, "user-context")

    async def confirm(self, token, user="u1"):
        return await self.sender.confirm(user, token, True, "user-context")

    async def test_prepare_never_sends_and_result_does_not_claim_confirmation(self):
        prepared = await self.prepare()
        self.assertEqual(prepared["settings"], TEST_SETTINGS)
        self.assertFalse(prepared["transmitted"])
        self.hass.services.async_call.assert_not_awaited()
        self.read.assert_awaited_once_with(self.hass, "device", 1, refresh=True, context="user-context")
        result = await self.confirm(prepared["token"])
        self.assertEqual(self.read.await_args.kwargs, {})  # Confirmation never refreshes again.
        self.assertEqual(result["outcome"], "accepted")
        self.assertFalse(result["confirmed_on_device"])
        self.assertNotIn("secret", str(result))
        self.hass.services.async_call.assert_awaited_once_with(
            "airfryer_control", "programm_senden",
            {"geraet": "device", "zone": 1, "programm": "airfry", "temperatur": 170,
             "minuten": 1, "variante": "multi_app", "einmal": True,
             "streng": True, "bestaetigen": False},
            blocking=True, return_response=True, context="user-context")
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(prepared["token"])

    async def test_acknowledgements_must_be_true_and_admin_is_rechecked(self):
        for value in (False, 1, "true", None):
            with self.assertRaisesRegex(BetaTestBlocked, "acknowledgement"):
                await self.sender.prepare("u1", "device", 1, value, "user-context")
        token = (await self.prepare())["token"]
        self.hass.auth.async_get_user.return_value.is_admin = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_tokens_are_user_bound_and_new_prepare_invalidates_old(self):
        first = (await self.prepare())["token"]
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(first, "u2")
        second = (await self.prepare())["token"]
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(first)
        await self.confirm(second)

    async def test_expired_confirmation_never_sends(self):
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=1):
            token = (await self.prepare())["token"]
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=20):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_state_or_session_changes_consume_confirmation(self):
        token = (await self.prepare())["token"]
        self.read.return_value = Target("Kitchen", ("new session",))
        with self.assertRaisesRegex(BetaTestBlocked, "state_changed"):
            await self.confirm(token)
        self.assertNotIn(token, self.sender.pending)
        self.hass.services.async_call.assert_not_awaited()

    async def test_change_during_final_auth_await_is_blocked(self):
        token = (await self.prepare())["token"]
        self.read.return_value = Target("Kitchen", ("same",), lambda: False)
        with self.assertRaisesRegex(BetaTestBlocked, "state_changed"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_concurrent_confirmation_is_rejected_without_queue(self):
        a = (await self.prepare())["token"]
        b = (await self.prepare(user="u2"))["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def call(*args, **kwargs):
            entered.set()
            await finish.wait()
            return None
        self.hass.services.async_call.side_effect = call
        task = asyncio.create_task(self.confirm(a))
        await entered.wait()
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.confirm(b, "u2")
        finish.set()
        await task
        self.hass.services.async_call.assert_awaited_once()

    async def test_exception_unknown_and_no_retry_even_after_integration_reload(self):
        self.hass.services.async_call.side_effect = TimeoutError("private")
        token = (await self.prepare())["token"]
        self.assertEqual((await self.confirm(token))["outcome"], "unknown")
        self.sender.close()
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        with self.assertRaisesRegex(BetaTestBlocked, "outcome_unknown"):
            await self.prepare()
        self.hass.services.async_call.assert_awaited_once()

    async def test_cancellation_keeps_uncertain_latch_and_clears_busy(self):
        token = (await self.prepare())["token"]
        self.hass.services.async_call.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await self.confirm(token)
        self.assertIn("device", self.sender.uncertain)
        self.assertNotIn("device", self.sender.busy)

    async def test_unload_while_reading_prevents_send(self):
        token = (await self.prepare())["token"]
        async def read(*args):
            self.sender.close()
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        with self.assertRaisesRegex(BetaTestBlocked, "not_configured"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_untrusted_upstream_response_never_confirms_or_retries(self):
        for response in (None, {"ok": True, "bestaetigt": True},
                         {"ok": False, "ergebnis": "abgelehnt", "fehler": "private"}):
            self.sender.uncertain.clear()
            token = (await self.prepare())["token"]
            self.hass.services.async_call.return_value = response
            result = await self.confirm(token)
            self.assertEqual(result["outcome"], "unknown")
            self.assertFalse(result["confirmed_on_device"])
            self.assertNotIn("private", str(result))
        self.assertEqual(self.hass.services.async_call.await_count, 3)

    async def test_expiry_during_revalidation_and_inactive_admin_are_blocked(self):
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=1):
            token = (await self.prepare())["token"]
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", side_effect=[2, 20]):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.confirm(token)
        self.hass.auth.async_get_user.return_value.is_active = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.prepare()
        self.hass.services.async_call.assert_not_awaited()

    async def test_adapter_read_failure_never_leaks_error_or_sends(self):
        self.read.side_effect = RuntimeError("private-cloud-id")
        with self.assertRaisesRegex(BetaTestBlocked, "^adapter_data$"):
            await self.prepare()
        self.hass.services.async_call.assert_not_awaited()

    async def test_active_service_lock_survives_reload(self):
        token = (await self.prepare())["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def call(*args, **kwargs):
            entered.set()
            await finish.wait()
            return None
        self.hass.services.async_call.side_effect = call
        task = asyncio.create_task(self.confirm(token))
        await entered.wait()
        self.sender.close()
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.prepare()
        finish.set()
        await task

    async def test_parallel_preparation_cannot_queue_refresh_or_send(self):
        entered, finish = asyncio.Event(), asyncio.Event()
        async def read(*args, **kwargs):
            entered.set()
            await finish.wait()
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        task = asyncio.create_task(self.prepare())
        await entered.wait()
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.prepare(user="u2")
        finish.set()
        await task
        self.read.assert_awaited_once()
        self.hass.services.async_call.assert_not_awaited()

    async def test_failed_new_preparation_invalidates_previous_token(self):
        token = (await self.prepare())["token"]
        self.read.side_effect = BetaTestBlocked("refresh_failed")
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_failed"):
            await self.prepare()
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(token)
        self.assertNotIn("device", self.sender.busy)
        self.hass.services.async_call.assert_not_awaited()


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.reported = datetime.now(timezone.utc)
        self.zones = {i: NS(status="bereit", active=False) for i in (1, 2)}
        self.fryer = NS(model="CAF-DC111S-AEU", online=True, last_error=None,
                        last_report=self.reported, revision=7,
                        state=NS(status="bereit", active=False, sync_type=0,
                                 temp_unit="celsius", zones=self.zones))
        self.runtime = NS(fryers={"cloud-private": self.fryer})
        self.entry = NS(entry_id="entry", runtime_data=self.runtime)
        self.device = NS(id="ha-device", name="Kitchen", name_by_user=None,
                         model=self.fryer.model, disabled_by=None,
                         identifiers={("airfryer_control", "cloud-private")}, config_entries={"entry"})
        self.registry = NS(async_get=Mock(return_value=self.device))
        self.integration = NS(version="1.0.2-beta.1")
        self.payload = {"programme": {"airfry": {"temperatur": [120, 205], "minuten": [1, 60],
                        "grenzen": "geschaetzt", "senden": "ungeprueft"}}, "verbindung": "ok",
                        "letzte_meldung": self.reported.isoformat(), "revision": 7}
        self.hass = NS(config_entries=NS(async_loaded_entries=Mock(return_value=[self.entry])),
                       services=NS(has_service=Mock(return_value=True),
                                   async_call=AsyncMock(return_value=self.payload)),
                       states=NS(get=Mock(return_value=NS(state="ready"))))
        helpers = ModuleType("homeassistant.helpers")
        dr = ModuleType("homeassistant.helpers.device_registry")
        dr.async_get = lambda hass: self.registry
        helpers.device_registry = dr
        er = ModuleType("homeassistant.helpers.entity_registry")
        self.entities = [NS(entity_id="sensor.airfryer_status", platform="airfryer_control",
                            config_entry_id="entry", disabled_by=None)]
        er.async_get = lambda hass: "registry"
        er.async_entries_for_device = Mock(side_effect=lambda registry, device_id: self.entities)
        helpers.entity_registry = er
        loader = ModuleType("homeassistant.loader")
        loader.async_get_integration = AsyncMock(return_value=self.integration)
        p = patch.dict(sys.modules, {"homeassistant.helpers": helpers,
                                    "homeassistant.helpers.device_registry": dr,
                                    "homeassistant.helpers.entity_registry": er,
                                    "homeassistant.loader": loader})
        p.start()
        self.addCleanup(p.stop)

    async def read(self, zone=1):
        return await read_target(self.hass, "ha-device", zone)

    async def test_both_zones_and_no_control_calls(self):
        for zone in (1, 2):
            target = await self.read(zone)
            self.assertTrue(target.unchanged())
            self.assertNotIn("cloud-private", str(target.fingerprint))
        self.assertTrue(all(c.args[1] == "faehigkeiten" for c in self.hass.services.async_call.await_args_list))

    async def test_unverified_program_is_only_allowed_inside_fixed_test_envelope(self):
        await self.read()
        del self.payload["programme"]["airfry"]
        with self.assertRaisesRegex(BetaTestBlocked, "capabilities"):
            await self.read()

    async def test_other_models_versions_and_zones_block(self):
        for zone in (True, 0, 3, "1"):
            with self.assertRaisesRegex(BetaTestBlocked, "target"):
                await self.read(zone)
        self.integration.version = "1.0.1"
        with self.assertRaisesRegex(BetaTestBlocked, "adapter_version"):
            await self.read()
        self.integration.version = "1.0.2-beta.1"
        self.device.model = "Other"
        with self.assertRaisesRegex(BetaTestBlocked, "model"):
            await self.read()

    async def test_stale_future_naive_and_mismatched_report_block(self):
        for stamp in (self.reported - timedelta(seconds=16), self.reported + timedelta(seconds=1),
                      self.reported.replace(tzinfo=None), None):
            self.fryer.last_report = stamp
            with self.assertRaisesRegex(BetaTestBlocked, "freshness"):
                await self.read()
        self.fryer.last_report = self.reported
        self.payload["revision"] = 8
        with self.assertRaisesRegex(BetaTestBlocked, "freshness"):
            await self.read()

    async def test_unknown_connection_and_active_other_zone_block(self):
        self.payload["verbindung"] = "fehler"
        with self.assertRaisesRegex(BetaTestBlocked, "connection"):
            await self.read()
        self.payload["verbindung"] = "ok"
        for status in ("gart", "pausiert", "schublade_offen", "wartet_auf_start", "unknown"):
            self.zones[2].status = status
            with self.assertRaisesRegex(BetaTestBlocked, "zones"):
                await self.read()

    async def test_missing_zones_sync_unknown_and_fahrenheit_block(self):
        self.fryer.state.sync_type = None
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.sync_type = 1
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.sync_type = 0
        self.fryer.state.temp_unit = "fahrenheit"
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.temp_unit = "celsius"
        del self.zones[2]
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()

    async def test_guard_catches_changes_after_async_read(self):
        target = await self.read()
        self.fryer.last_error = "new error"
        self.assertFalse(target.unchanged())
        self.fryer.last_error = None
        self.fryer.state.zones[2].status = "gart"
        self.assertFalse(target.unchanged())

    async def refreshing_read(self):
        return await read_target(self.hass, "ha-device", 1, refresh=True, context="admin-context")

    async def test_stale_report_is_refreshed_through_one_public_read_only_call(self):
        self.fryer.last_report = self.reported - timedelta(seconds=90)
        async def service(domain, name, data, **kwargs):
            if (domain, name) == ("homeassistant", "update_entity"):
                self.fryer.last_report = datetime.now(timezone.utc)
                self.payload["letzte_meldung"] = self.fryer.last_report.isoformat()
                return None
            return self.payload
        self.hass.services.async_call.side_effect = service
        target = await self.refreshing_read()
        self.assertTrue(target.unchanged())
        calls = self.hass.services.async_call.await_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args, ("homeassistant", "update_entity",
                                       {"entity_id": ["sensor.airfryer_status"]}))
        self.assertEqual(calls[0].kwargs, {"blocking": True, "context": "admin-context"})
        self.assertEqual(calls[1].args[1], "faehigkeiten")
        self.assertFalse(any(c.args[1] == "programm_senden" for c in calls))

    async def test_refresh_returning_without_new_report_is_rejected_even_if_cache_is_recent(self):
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_failed"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_awaited_once()

    async def test_refresh_timeout_does_not_retry_or_expose_exception(self):
        self.hass.services.async_call.side_effect = TimeoutError("private")
        with self.assertRaisesRegex(BetaTestBlocked, "^refresh_failed$"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_awaited_once()

    async def test_refresh_requires_loaded_enabled_upstream_sensor_from_selected_entry(self):
        self.entities[:] = [
            NS(entity_id="button.control", platform="airfryer_control", config_entry_id="entry", disabled_by=None),
            NS(entity_id="sensor.other", platform="other", config_entry_id="entry", disabled_by=None),
            NS(entity_id="sensor.wrong_entry", platform="airfryer_control", config_entry_id="other", disabled_by=None),
            NS(entity_id="sensor.disabled", platform="airfryer_control", config_entry_id="entry", disabled_by="user"),
        ]
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_unavailable"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_not_awaited()

    async def test_read_without_refresh_does_not_invoke_update_service(self):
        await self.read()
        self.hass.services.async_call.assert_awaited_once_with(
            "airfryer_control", "faehigkeiten", {"geraet": "ha-device"},
            blocking=True, return_response=True)
