"""Accepted settings are durable snapshots, never queued device commands."""
import asyncio
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from custom_components.airfryer_recipes.beta_send import BetaSender
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import CookingPhase
from custom_components.airfryer_recipes.sent_settings import SentSettings


class Store:
    def __init__(self, value=None):
        self.value = deepcopy(value)
        self.fail = False
        self.writes = 0

    async def async_load(self):
        return deepcopy(self.value)

    async def async_save(self, value):
        await asyncio.sleep(0)
        if self.fail:
            raise OSError("private storage path")
        self.value = deepcopy(value)
        self.writes += 1


class HistoryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store = Store()
        self.history = SentSettings(self.store)
        await self.history.async_load()
        self.phase = CookingPhase("airfry", 180, 7)

    async def test_restart_zone_device_isolation_and_defensive_copies(self):
        other = CookingPhase("roast", 190, 10)
        await asyncio.gather(self.history.record("a", 1, self.phase, "recipe"), self.history.record("a", 2, other), self.history.record("b", 1, other))
        restored = SentSettings(self.store)
        await restored.async_load()
        self.assertTrue(restored.available)
        self.assertEqual(restored.get("a")["zones"]["1"]["recipe_id"], "recipe")
        self.assertEqual(restored.get("a")["zones"]["2"]["settings"]["program"], "roast")
        self.assertEqual(restored.get("b")["zones"]["1"]["settings"]["temperature_c"], 190)
        self.assertEqual(restored.get("missing"), {"available": True, "zones": {}})
        returned = restored.get("a")
        returned["zones"]["1"]["settings"]["temperature_c"] = 1
        self.assertEqual(restored.get("a")["zones"]["1"]["settings"]["temperature_c"], 180)
        self.assertEqual(self.store.writes, 3)

    async def test_failed_save_retains_previous_snapshot_and_does_not_replace_disk(self):
        await self.history.record("a", 1, self.phase)
        before = deepcopy(self.store.value)
        self.store.fail = True
        with self.assertRaises(OSError):
            await self.history.record("a", 1, CookingPhase("roast", 190, 10))
        self.assertEqual(self.store.value, before)
        self.assertEqual(self.history.get("a")["zones"], before["devices"]["a"])

    async def test_damaged_and_newer_stores_are_preserved_and_writes_disabled(self):
        await self.history.record("a", 1, self.phase)
        valid = deepcopy(self.store.value)
        malformed = deepcopy(valid)
        malformed["devices"]["a"]["1"]["settings"]["duration_minutes"] = True
        naive = deepcopy(valid)
        naive["devices"]["a"]["1"]["sent_at"] = "2026-11-02T09:00:00"
        for value in ({"schema_version": 2, "devices": {}}, {"schema_version": 1, "devices": []}, malformed, naive, {"unknown": "preserve"}):
            store = Store(value)
            history = SentSettings(store)
            await history.async_load()
            self.assertFalse(history.available)
            with self.assertRaises(ValueError):
                await history.record("a", 1, self.phase)
            self.assertEqual(store.value, value)
            self.assertEqual(store.writes, 0)

    async def test_invalid_targets_never_write(self):
        for device, zone, recipe in (("", 1, None), ("a", True, None), ("a", 3, None), ("a", 1, [])):
            with self.assertRaises(ValueError):
                await self.history.record(device, zone, self.phase, recipe)
        self.assertEqual(self.store.writes, 0)

    async def test_only_exact_adapter_acceptance_writes_history(self):
        service = AsyncMock()
        hass = SimpleNamespace(data={DOMAIN: {"sent_settings": self.history}}, services=SimpleNamespace(async_call=service))
        sender = BetaSender(hass)
        for response in ({"ok": False, "ergebnis": "abgelehnt"}, {}, {"ok": True, "ergebnis": "angenommen"}):
            service.return_value = response
            result = await sender.send_once("a", 1, self.phase, None)
            self.assertNotEqual(result["outcome"], "accepted")
            self.assertEqual(self.store.writes, 0)
        service.return_value = {"ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app", "gesendet": {"programm": "airfry", "temperatur": 180, "minuten": 7, "zone": 1}}
        result = await sender.send_once("a", 1, self.phase, None, recipe_id="saved-recipe")
        self.assertTrue(result["history_saved"])
        self.assertFalse(result["confirmed_on_device"])
        self.assertEqual(self.history.get("a")["zones"]["1"]["recipe_id"], "saved-recipe")
        self.store.fail = True
        result = await sender.send_once("a", 1, self.phase, None)
        self.assertEqual(result["outcome"], "accepted")
        self.assertFalse(result["history_saved"])
        self.assertEqual(service.await_count, 5)  # Exactly one call per requested attempt.
        self.assertNotIn("private", str(result))
