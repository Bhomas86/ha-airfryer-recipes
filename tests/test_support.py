"""Privacy and completion regressions: no hardware or external notifications."""
import asyncio
from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock, patch

from custom_components.airfryer_recipes.device_access import AccessDenied
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.support import (
    CompletionTracker, Support, diagnostics, sample, validate_rules,
)

NOW = datetime.now(timezone.utc)


def state(status, seconds=0, **attributes):
    return NS(state=status, attributes={"gemeldet": True, "verbindung": "ok",
        "letzte_meldung": (NOW + timedelta(seconds=seconds)).isoformat(),
        "revision": 100 + seconds, **attributes})


def rule():
    return dict(entity_id="sensor.zone1", unique_id="private_zone1_status",
                config_entry_id="entry", device_id="device", target="mobile_app_phone",
                owner="admin", language="de")


class TrackerTests(unittest.TestCase):
    def test_completion_once_per_zone_and_cycle(self):
        tracker = CompletionTracker()
        self.assertFalse(tracker.observe("one", state("gart", -2), NOW))
        self.assertFalse(tracker.observe("two", state("gart", -2), NOW))
        self.assertTrue(tracker.observe("one", state("fertig", -1), NOW))
        self.assertFalse(tracker.observe("one", state("fertig", -1), NOW))
        self.assertTrue(tracker.observe("two", state("fertig", -1), NOW))
        self.assertFalse(tracker.observe("one", state("gart"), NOW))
        self.assertTrue(tracker.observe("one", state("fertig", 1), NOW + timedelta(seconds=1)))

    def test_never_infer_finished_from_countdown_idle_cancel_or_pause(self):
        for status in ("bereit", "aus", "pausiert", "schublade_offen", "unavailable", "unknown", "warmhalten"):
            with self.subTest(status=status):
                tracker = CompletionTracker()
                tracker.observe("one", state("gart", -3), NOW)
                self.assertFalse(tracker.observe("one", state(status, -2), NOW))
                self.assertFalse(tracker.observe("one", state("fertig", -1), NOW))

    def test_offline_bad_or_missing_report_clears_arm(self):
        for attrs in ({"gemeldet": False}, {"verbindung": "offline"}, {"letzte_meldung": "invalid"},
                      {"letzte_meldung": NOW.replace(tzinfo=None).isoformat()}, {"revision": True},
                      {"letzte_meldung": (NOW - timedelta(seconds=500)).isoformat()},
                      {"letzte_meldung": (NOW + timedelta(seconds=2)).isoformat()}):
            tracker = CompletionTracker()
            tracker.observe("one", state("gart", -3), NOW)
            self.assertFalse(tracker.observe("one", state("fertig", -2, **attrs), NOW))
            self.assertFalse(tracker.observe("one", state("fertig", -1), NOW))

    def test_start_restart_and_long_gap_do_not_notify(self):
        tracker = CompletionTracker()
        self.assertFalse(tracker.observe("one", state("fertig"), NOW))
        tracker.observe("one", state("gart", -91), NOW - timedelta(seconds=91))
        self.assertFalse(tracker.observe("one", state("fertig"), NOW))
        tracker.observe("one", state("gart", -1), NOW)
        tracker.clear()
        self.assertFalse(tracker.observe("one", state("fertig"), NOW))

    def test_duplicate_cooking_report_keeps_arm_but_reordered_report_drops_it(self):
        tracker = CompletionTracker()
        for _ in range(2):
            self.assertFalse(tracker.observe("one", state("gart", -2), NOW))
        self.assertTrue(tracker.observe("one", state("fertig", -1), NOW))
        tracker.observe("one", state("gart", -1), NOW)
        self.assertFalse(tracker.observe("one", state("fertig", -2), NOW))
        self.assertFalse(tracker.observe("one", state("fertig"), NOW))

    def test_diagnostics_never_copies_private_values_or_raw_objects(self):
        private = "token-cookie-password-192.168.1.1-personal-id"
        hass = NS(data={DOMAIN: {"repository": NS(name=private, recipes=[private]),
            "raw": {"secret": private}, "support": NS(available=True, rules=[private])}})
        data = diagnostics(hass)
        encoded = json.dumps(data)
        self.assertNotIn(private, encoded)
        self.assertTrue(all(type(v) in (int, bool, str) for v in data.values()))
        self.assertEqual(set(data), {"schema_version", "integration_version", "library_loaded",
            "favorites_loaded", "permissions_available", "history_available",
            "notifications_available", "notification_rule_count"})

    def test_rules_reject_arbitrary_services_duplicates_and_future_fields(self):
        for rows in ([dict(rule(), target="persistent_notification")], [rule(), rule()],
                     [dict(rule(), unexpected="secret")], [dict(rule(), language="xx")], [rule()] * 21):
            with self.assertRaises(ValueError):
                validate_rules(rows)


class SupportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.source = NS(unique_id="private_zone1_status", config_entry_id="entry", device_id="device")
        self.hass = NS(data={}, is_stopping=False, auth=NS(async_get_user=AsyncMock(return_value=NS(id="admin", is_admin=True, is_active=True))),
            services=NS(async_services=lambda: {"notify": {"mobile_app_phone": {}}}, async_call=AsyncMock()),
            bus=NS(async_listen=Mock(return_value=Mock())), states=NS(get=lambda _: self.current))
        self.store = NS(async_load=AsyncMock(return_value=None), async_save=AsyncMock())
        self.support = Support(self.hass, self.store)
        self.support.sources = AsyncMock(return_value={"sensor.zone1": self.source})
        self.connection = NS(user=NS(id="admin"))

    async def configure(self):
        await self.support.load()
        await self.support.configure(self.connection, "sensor.zone1", "mobile_app_phone", "de")

    async def event(self, status, seconds):
        self.current = state(status, seconds)
        await self.support.on_event(NS(data={"entity_id": "sensor.zone1", "new_state": self.current}))

    async def test_off_by_default_and_unload_removes_listener(self):
        await self.support.load()
        await self.event("gart", -2)
        await self.event("fertig", -1)
        self.hass.services.async_call.assert_not_called()
        unsubscribe = self.support.unsubscribe
        self.support.close()
        unsubscribe.assert_called_once()
        self.assertTrue(self.support.closed)

    async def test_delivery_has_no_private_fields_and_no_retry(self):
        await self.configure()
        with patch.dict("sys.modules", {"homeassistant.core": NS(Context=NS)}):
            await self.event("gart", -2)
            self.hass.services.async_call.side_effect = OSError("private-error")
            await self.event("fertig", -1)
            await self.event("fertig", -1)
        self.hass.services.async_call.assert_awaited_once()
        call = self.hass.services.async_call.call_args
        self.assertEqual(call.args[:2], ("notify", "mobile_app_phone"))
        self.assertEqual(call.args[2], {"title": "Airfryer Recipes", "message": "Fach 1 meldet: fertig."})

    async def test_revoked_admin_and_rebound_source_cannot_send(self):
        for changed in ("admin", "source"):
            await self.configure()
            await self.event("gart", -2)
            if changed == "admin":
                self.hass.auth.async_get_user.return_value.is_admin = False
            else:
                self.source.unique_id = "different_zone1_status"
            await self.event("fertig", -1)
            self.hass.services.async_call.assert_not_called()
            self.hass.auth.async_get_user.return_value.is_admin = True

    async def test_storage_failure_does_not_activate_rule(self):
        await self.support.load()
        self.store.async_save.side_effect = OSError("disk full")
        with self.assertRaises(OSError):
            await self.support.configure(self.connection, "sensor.zone1", "mobile_app_phone", "de")
        self.assertEqual(self.support.rules, [])

    async def test_corrupt_storage_preserved_and_notifications_disabled(self):
        self.store.async_load.return_value = {"schema_version": 2, "rules": []}
        await self.support.load()
        self.assertFalse(self.support.available)
        self.hass.bus.async_listen.assert_not_called()
        self.store.async_save.assert_not_called()

    async def test_disable_persists_and_discards_armed_state(self):
        await self.configure()
        await self.event("gart", -2)
        await self.support.configure(self.connection, "sensor.zone1", "", "de")
        await self.event("fertig", -1)
        self.assertEqual(self.support.rules, [])
        self.hass.services.async_call.assert_not_called()

    async def test_normal_user_cannot_configure(self):
        await self.support.load()
        self.hass.auth.async_get_user.return_value.is_admin = False
        with self.assertRaises(AccessDenied):
            await self.support.configure(self.connection, "sensor.zone1", "mobile_app_phone", "de")
        self.store.async_save.assert_not_called()

    async def test_arbitrary_target_or_unloaded_source_rejected(self):
        await self.support.load()
        for entity, target in (("sensor.zone1", "turn_on"), ("sensor.fake", "mobile_app_phone")):
            with self.assertRaises(ValueError):
                await self.support.configure(self.connection, entity, target, "de")
        self.store.async_save.assert_not_called()


    async def test_real_source_filter_requires_reviewed_loaded_zone_entities(self):
        source = NS(platform="airfryer_control", domain="sensor", disabled_by=None,
                    config_entry_id="entry", device_id="device", unique_id="private_zone1_status", entity_id="sensor.zone1")
        unrelated = NS(**{**source.__dict__, "entity_id": "sensor.other", "unique_id": "private_status"})
        disabled = NS(**{**source.__dict__, "entity_id": "sensor.disabled", "disabled_by": "user"})
        loader = NS(async_get_integration=AsyncMock(return_value=NS(version="1.0.3-beta.3")))
        registry = NS(async_get=lambda _: NS(entities={s.entity_id: s for s in (source, unrelated, disabled)}))
        helpers = NS(entity_registry=registry)
        self.hass.config_entries = NS(async_loaded_entries=lambda _: [NS(entry_id="entry")])
        support = Support(self.hass, self.store)
        with patch.dict("sys.modules", {"homeassistant.helpers": helpers, "homeassistant.loader": loader}):
            self.assertEqual(set(await support.sources()), {"sensor.zone1"})
            loader.async_get_integration.return_value.version = "future"
            self.assertEqual(await support.sources(), {})
            loader.async_get_integration.side_effect = Exception("private")
            self.assertEqual(await support.sources(), {})
