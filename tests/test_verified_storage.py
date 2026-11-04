"""Silent native Store failure must not become a successful application save."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch, AsyncMock

from custom_components.airfryer_recipes.verified_storage import VerifiedStore
from custom_components.airfryer_recipes.device_access import create_device_access
from custom_components.airfryer_recipes.sent_settings import create_sent_settings
from custom_components.airfryer_recipes.favorites import create_favorites
from custom_components.airfryer_recipes.appearance import repository, default_appearance
from custom_components.airfryer_recipes.storage import create_repository, STORAGE_KEY, BACKUP_KEY
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import CookingPhase, create_recipe
from custom_components.airfryer_recipes.beta_send import BetaSender


class VerifiedStorageTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.root=Path(directory.name);self.fail=set();self.stores={}
        owner=self
        class NativeStore:
            def __init__(self,hass,version,key,*,atomic_writes=False):
                owner.assertTrue(atomic_writes)
                self.key=key;self.version=version;self.path=str(owner.root/key);self.cached=None
                owner.stores[key]=self
            async def async_load(self):
                return deepcopy(self.cached)
            async def async_save(self,data):
                self.cached=deepcopy(data)
                if self.key in owner.fail:return  # HA logs some failures and returns.
                Path(self.path).write_text(json.dumps({'key':self.key,'version':self.version,'data':data}),encoding='utf8')
        storage=ModuleType('homeassistant.helpers.storage');storage.Store=NativeStore
        self.patch=patch.dict(sys.modules,{'homeassistant.helpers.storage':storage})
        self.patch.start();self.addCleanup(self.patch.stop)
        async def executor(func,*args):return func(*args)
        self.hass=NS(data={DOMAIN:{}},async_add_executor_job=executor,is_stopping=False)

    async def test_disk_is_verified_instead_of_trusting_a_successful_return_or_cache(self):
        store=VerifiedStore(self.hass,1,'fixture');await store.async_save({'value':1})
        self.fail.add('fixture')
        with self.assertRaises(OSError):await store.async_save({'value':2})
        self.assertEqual(await store.async_load(),{'value':2})  # Misleading cache.
        self.assertEqual(json.loads((self.root/'fixture').read_text())['data'],{'value':1})

    async def test_absent_or_malformed_disk_and_shutdown_do_not_acknowledge_saves(self):
        store=VerifiedStore(self.hass,1,'fixture');self.fail.add('fixture')
        with self.assertRaises(OSError):await store.async_save({'value':1})
        (self.root/'fixture').write_text('bad JSON')
        with self.assertRaises(OSError):await store.async_save({'value':1})
        self.fail.clear();self.hass.is_stopping=True
        with self.assertRaises(OSError):await store.async_save({'value':2})
        self.assertEqual((self.root/'fixture').read_text(),'bad JSON')

    async def test_data_types_and_outer_storage_identity_must_match(self):
        store=VerifiedStore(self.hass,1,'fixture');await store.async_save({'value':True})
        self.fail.add('fixture')
        with self.assertRaises(OSError):await store.async_save({'value':1})
        (self.root/'fixture').write_text(json.dumps({'key':'wrong','version':1,'data':{'value':True}}))
        with self.assertRaises(OSError):await store.async_save({'value':True})

    async def test_silent_permission_write_failure_retains_grants_and_invalidates_old_tokens(self):
        access=create_device_access(self.hass);await access.async_load()
        await access.set('user','device',True);revision=access.revision
        self.fail.add(f'{DOMAIN}.device_access')
        with self.assertRaises(OSError):await access.set('user','device',False)
        self.assertEqual(access.devices_for('user'),{'device'})
        self.assertGreater(access.revision,revision);self.assertFalse(access.updating)

    async def test_silent_image_history_and_favorite_failures_do_not_publish_new_values(self):
        appearance=await repository(self.hass);old=default_appearance();new=default_appearance('outline')
        await appearance.save('device',old);self.fail.add(f'{DOMAIN}.appearance')
        with self.assertRaises(OSError):await appearance.save('device',new)
        self.assertEqual(appearance.get('device'),old)
        history=create_sent_settings(self.hass);await history.async_load()
        await history.record('device',1,CookingPhase('airfry',180,7));before=history.get('device')
        self.fail.add(f'{DOMAIN}.sent_settings')
        with self.assertRaises(OSError):await history.record('device',1,CookingPhase('proof',31,60))
        self.assertEqual(history.get('device'),before)
        self.hass.data[DOMAIN]['sent_settings']=history
        self.hass.services=NS(async_call=AsyncMock(return_value={
            'ok':True,'ergebnis':'angenommen','versuche':1,'variante':'multi_app',
            'gesendet':{'programm':'proof','temperatur':31,'minuten':60,'zone':1}}))
        result=await BetaSender(self.hass).send_once('device',1,CookingPhase('proof',31,60),'fixture-context')
        self.assertEqual(result['outcome'],'accepted');self.assertFalse(result['history_saved'])
        self.hass.services.async_call.assert_awaited_once()
        self.assertEqual(history.get('device'),before)
        favorites=create_favorites(self.hass);await favorites.async_load()
        self.fail.add(f'{DOMAIN}.favorites')
        with self.assertRaises(OSError):await favorites.async_set('user','recipe',True)
        self.assertEqual(await favorites.async_get('user'),[])

    async def test_silent_recipe_or_backup_failure_preserves_published_library(self):
        repo=create_repository(self.hass);await repo.async_load()
        first=create_recipe('First',program='airfry',temperature_c=180,duration_minutes=7)
        second=create_recipe('Second',program='proof',temperature_c=31,duration_minutes=60)
        await repo.async_create(first)
        for key in [BACKUP_KEY,STORAGE_KEY]:
            self.fail={key}
            with self.assertRaises(OSError):await repo.async_create(second)
            self.assertEqual(await repo.async_list(),(first,))
            self.assertEqual(len(json.loads((self.root/STORAGE_KEY).read_text())['data']['recipes']),1)
