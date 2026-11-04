"""Store adapter tests with public Store stubs and real temporary JSON files."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from custom_components.airfryer_recipes.recipe_model import RecipeValidationError, create_recipe
from custom_components.airfryer_recipes.storage import BACKUP_KEY, STORAGE_KEY, create_repository


def sample(name):
    return create_recipe(name, program="airfry", temperature_c=170, duration_minutes=8)


class FakeHassStore:
    contents = {}
    fail_key = None

    def __init__(self, hass, version, key, *, atomic_writes=False):
        assert atomic_writes
        self.key = key
        self.version = version
        self.path = str(self.root / key)

    async def async_load(self):
        return deepcopy(self.contents.get(self.key))

    async def async_save(self, data):
        if self.key == self.fail_key:
            raise OSError("simulated disk failure")
        self.contents[self.key] = deepcopy(data)
        Path(self.path).write_text(json.dumps({'key':self.key,'version':self.version,'data':data}),encoding='utf8')


class HomeAssistantPersistenceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        FakeHassStore.contents = {}
        FakeHassStore.fail_key = None
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        FakeHassStore.root=Path(self.directory.name)
        async def executor(func,*args):return func(*args)
        self.hass=types.SimpleNamespace(async_add_executor_job=executor,is_stopping=False)
        self.ha = types.ModuleType("homeassistant")
        self.helpers = types.ModuleType("homeassistant.helpers")
        self.storage = types.ModuleType("homeassistant.helpers.storage")
        self.storage.Store = FakeHassStore
        self.patch = patch.dict(sys.modules, {
            "homeassistant": self.ha,
            "homeassistant.helpers": self.helpers,
            "homeassistant.helpers.storage": self.storage,
        })
        self.patch.start()
        self.addCleanup(self.patch.stop)

    async def test_stored_recipes_survive_new_repository(self):
        repo = create_repository(self.hass)
        await repo.async_load()
        await repo.async_create(sample("A"))
        await repo.async_create(sample("B"))
        self.assertIn(STORAGE_KEY, FakeHassStore.contents)
        self.assertIn(BACKUP_KEY, FakeHassStore.contents)
        self.assertEqual(len(FakeHassStore.contents[BACKUP_KEY]["recipes"]), 1)
        reloaded = create_repository(self.hass)
        await reloaded.async_load()
        self.assertEqual({r.name for r in await reloaded.async_list()}, {"A", "B"})

    async def test_failed_backup_prevents_changing_active_library(self):
        repo = create_repository(self.hass)
        await repo.async_load()
        await repo.async_create(sample("A"))
        snapshot = deepcopy(FakeHassStore.contents[STORAGE_KEY])
        FakeHassStore.fail_key = BACKUP_KEY
        with self.assertRaises(OSError):
            await repo.async_create(sample("B"))
        self.assertEqual(FakeHassStore.contents[STORAGE_KEY], snapshot)
        self.assertEqual(len(await repo.async_list()), 1)

    async def test_failed_primary_write_preserves_old_snapshot(self):
        repo = create_repository(self.hass)
        await repo.async_load()
        await repo.async_create(sample("A"))
        FakeHassStore.fail_key = STORAGE_KEY
        with self.assertRaises(OSError):
            await repo.async_create(sample("B"))
        self.assertEqual(len(FakeHassStore.contents[STORAGE_KEY]["recipes"]), 1)
        self.assertEqual(len(FakeHassStore.contents[BACKUP_KEY]["recipes"]), 1)
        self.assertEqual(len(await repo.async_list()), 1)

    async def test_newer_schema_never_resets_existing_recipes(self):
        data = {"schema_version": 500, "recipes": []}
        FakeHassStore.contents[STORAGE_KEY] = deepcopy(data)
        repo = create_repository(self.hass)
        with self.assertRaises(RecipeValidationError):
            await repo.async_load()
        self.assertEqual(FakeHassStore.contents[STORAGE_KEY], data)
        self.assertNotIn(BACKUP_KEY, FakeHassStore.contents)
