"""Offline persistence checks for personal favorites."""

import unittest
import asyncio
from unittest.mock import AsyncMock

from custom_components.airfryer_recipes.favorites import FavoriteRepository
from custom_components.airfryer_recipes.recipe_model import MAX_RECIPES


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

    async def test_writer_cannot_create_a_store_that_exceeds_the_reload_limit(self):
        store=Store();repo=FavoriteRepository(store);await repo.async_load()
        for index in range(MAX_RECIPES):await repo.async_set('user',f'recipe-{index}',True)
        before=store.value
        with self.assertRaisesRegex(ValueError,'too many favorites'):
            await repo.async_set('user','recipe-extra',True)
        self.assertIs(store.value,before)
        fresh=FavoriteRepository(store);await fresh.async_load()
        self.assertEqual(len(await fresh.async_get('user')),MAX_RECIPES)

    async def test_deleted_references_are_pruned_only_for_the_user_who_changes_favorites(self):
        store=Store();repo=FavoriteRepository(store);await repo.async_load()
        for index in range(MAX_RECIPES):await repo.async_set('user',f'deleted-{index}',True)
        await repo.async_set('other','other-favorite',True)
        await repo.async_set('user','current',True,live_recipe_ids=AsyncMock(return_value={'current'}))
        fresh=FavoriteRepository(store);await fresh.async_load()
        self.assertEqual(await fresh.async_get('user'),['current'])
        self.assertEqual(await fresh.async_get('other'),['other-favorite'])

    async def test_failed_cleanup_write_preserves_all_existing_preferences(self):
        store=Store();repo=FavoriteRepository(store);await repo.async_load()
        await repo.async_set('user','deleted',True);before=store.value;store.fail=True
        with self.assertRaises(OSError):
            await repo.async_set('user','current',True,live_recipe_ids=AsyncMock(return_value={'current'}))
        self.assertIs(store.value,before);self.assertEqual(await repo.async_get('user'),['deleted'])

    async def test_live_ids_are_read_after_the_favorite_lock_and_missing_recipes_are_not_added(self):
        store=Store();repo=FavoriteRepository(store);await repo.async_load()
        live={'old'};read=AsyncMock(side_effect=lambda:set(live))
        await repo._lock.acquire()
        task=asyncio.create_task(repo.async_set('user','new',True,live_recipe_ids=read))
        await asyncio.sleep(0);read.assert_not_awaited()
        live.add('new');repo._lock.release();await task
        self.assertEqual(await repo.async_get('user'),['new'])
        with self.assertRaisesRegex(ValueError,'recipe no longer exists'):
            await repo.async_set('user','missing',True,live_recipe_ids=read)
        self.assertEqual(await repo.async_get('user'),['new'])
