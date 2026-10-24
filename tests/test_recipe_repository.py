"""Offline transactional tests: no HA instance, no cloud and no appliance."""

import asyncio
from dataclasses import replace
import json
import unittest

from custom_components.airfryer_recipes.recipe_model import (
    create_recipe,
    export_library_json,
    RecipeValidationError,
)
from custom_components.airfryer_recipes.recipe_repository import (
    RecipeRepository,
    RecipeConflictError,
    RecipeNotFoundError,
    RecipePreviewExpiredError,
)


def sample(name="Brötchen"):
    return create_recipe(name, program="airfry", temperature_c=180, duration_minutes=8)


class MemoryStore:
    def __init__(self, initial=None):
        self.value = initial
        self.writes = 0
        self.fail = False

    async def load(self):
        return self.value

    async def save(self, value):
        if self.fail:
            raise OSError("simulated write failure")
        self.value = value
        self.writes += 1


class RepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mem = MemoryStore()
        self.repo = RecipeRepository(self.mem.load, self.mem.save)
        await self.repo.async_load()

    async def test_create_get_update_delete_survive_restart(self):
        original = sample()
        await self.repo.async_create(original)
        self.assertEqual(await self.repo.async_get(original.id), original)
        updated = replace(original, name="Tiefkühlbrötchen")
        await self.repo.async_update(updated)
        fresh = RecipeRepository(self.mem.load, self.mem.save)
        await fresh.async_load()
        self.assertEqual(await fresh.async_list(), (updated,))
        await fresh.async_delete(updated.id)
        self.assertEqual(await fresh.async_list(), ())
        with self.assertRaises(RecipeNotFoundError):
            await fresh.async_get(updated.id)

    async def test_duplicate_id_and_name_blocked(self):
        first = sample()
        await self.repo.async_create(first)
        with self.assertRaises(RecipeConflictError):
            await self.repo.async_create(first)
        with self.assertRaises(RecipeConflictError):
            await self.repo.async_create(sample("brötchen"))
        self.assertEqual(self.mem.writes, 1)

    async def test_write_failure_preserves_old_memory_and_disk(self):
        original = sample()
        await self.repo.async_create(original)
        before = self.mem.value
        self.mem.fail = True
        with self.assertRaises(OSError):
            await self.repo.async_update(replace(original, name="New"))
        self.assertEqual(await self.repo.async_list(), (original,))
        self.assertEqual(self.mem.value, before)

    async def test_bad_or_future_json_does_not_modify_storage(self):
        before = self.mem.value
        for payload in ('invalid JSON', '{"schema_version":2,"recipes":[]}'):
            with self.assertRaises(RecipeValidationError):
                await self.repo.async_preview_import(payload)
        self.assertEqual(self.mem.value, before)
        self.assertEqual(self.mem.writes, 0)

    async def test_unknown_stored_version_blocks_setup_without_overwriting(self):
        saved = {"schema_version": 99, "recipes": []}
        mem = MemoryStore(saved)
        repo = RecipeRepository(mem.load, mem.save)
        with self.assertRaises(RecipeValidationError):
            await repo.async_load()
        self.assertEqual(mem.value, saved)
        self.assertEqual(mem.writes, 0)

    async def test_import_requires_confirmation_and_skips_conflicts(self):
        original = sample()
        await self.repo.async_create(original)
        another = sample("Maiskolben")
        payload = export_library_json([original, another])
        preview = await self.repo.async_preview_import(payload)
        self.assertEqual(preview.duplicate_ids, (original.id,))
        self.assertEqual(preview.duplicate_names, ("Brötchen",))
        self.assertEqual(len(await self.repo.async_list()), 1)
        self.assertEqual(await self.repo.async_confirm_import(preview.token), 1)
        self.assertEqual(len(await self.repo.async_list()), 2)
        with self.assertRaises(RecipePreviewExpiredError):
            await self.repo.async_confirm_import(preview.token)

    async def test_expired_after_intervening_mutation(self):
        preview = await self.repo.async_preview_import(export_library_json([sample()]))
        await self.repo.async_create(sample("Other"))
        with self.assertRaises(RecipePreviewExpiredError):
            await self.repo.async_confirm_import(preview.token)

    async def test_replace_id_must_not_replace_different_name_match(self):
        original = sample()
        await self.repo.async_create(original)
        renamed_id = sample(original.name)
        preview = await self.repo.async_preview_import(export_library_json([renamed_id]))
        with self.assertRaises(RecipeConflictError):
            await self.repo.async_confirm_import(preview.token, policy="replace_ids")
        self.assertEqual(await self.repo.async_list(), (original,))

    async def test_replace_same_id_on_confirm(self):
        original = sample()
        await self.repo.async_create(original)
        revised = replace(original, name="Updated")
        preview = await self.repo.async_preview_import(export_library_json([revised]))
        self.assertEqual(await self.repo.async_confirm_import(preview.token, policy="replace_ids"), 1)
        self.assertEqual(await self.repo.async_get(original.id), revised)

    async def test_duplicate_names_inside_import_rejected(self):
        with self.assertRaises(RecipeConflictError):
            await self.repo.async_preview_import(export_library_json([sample("Foo"), sample("foo")]))
        self.assertEqual(self.mem.writes, 0)

    async def test_concurrent_creates_do_not_lose_updates(self):
        await asyncio.gather(
            self.repo.async_create(sample("A")),
            self.repo.async_create(sample("B")),
            self.repo.async_create(sample("C")),
        )
        self.assertEqual(len(await self.repo.async_list()), 3)
        self.assertEqual(self.mem.writes, 3)

    async def test_export_contains_only_recipe_data(self):
        await self.repo.async_create(sample())
        raw = json.loads(await self.repo.async_export_json())
        self.assertEqual(raw["schema_version"], 1)
        self.assertNotIn("device_id", str(raw))
        self.assertNotIn("access_token", str(raw))
