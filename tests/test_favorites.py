"""Offline persistence checks for personal favorites."""

import unittest

from custom_components.airfryer_recipes.favorites import FavoriteRepository


class Store:
    def __init__(self):
        self.value = None
        self.fail = False

    async def async_load(self):
        return self.value

    async def async_save(self, value):
        if self.fail:
            raise OSError("storage unavailable")
        self.value = value


class FavoriteTests(unittest.IsolatedAsyncioTestCase):
    async def test_users_are_isolated_and_preferences_survive_restart(self):
        store = Store()
        repo = FavoriteRepository(store)
        await repo.async_load()
        await repo.async_set("admin", "recipe-1", True)
        self.assertEqual(await repo.async_get("other"), [])
        fresh = FavoriteRepository(store)
        await fresh.async_load()
        self.assertEqual(await fresh.async_get("admin"), ["recipe-1"])
        await fresh.async_set("admin", "recipe-1", False)
        self.assertEqual(await fresh.async_get("admin"), [])

    async def test_failed_write_does_not_publish_preference(self):
        store = Store()
        repo = FavoriteRepository(store)
        await repo.async_load()
        store.fail = True
        with self.assertRaises(OSError):
            await repo.async_set("admin", "recipe-1", True)
        self.assertEqual(await repo.async_get("admin"), [])
        self.assertIsNone(store.value)
