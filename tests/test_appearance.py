"""Private artwork validation and isolated storage, without device access."""
import base64
from copy import deepcopy
from io import BytesIO
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock
from PIL import Image, PngImagePlugin
from custom_components.airfryer_recipes.appearance import AppearanceStore,default_appearance,normalize_image,validate

def encoded(fmt='PNG'):
    out=BytesIO();im=Image.new('RGB',(25,30),'blue')
    info=PngImagePlugin.PngInfo();info.add_text('secret','private metadata')
    im.save(out,format=fmt,**({'pnginfo':info} if fmt=='PNG' else {}));return base64.b64encode(out.getvalue()).decode()

class AppearanceTests(unittest.IsolatedAsyncioTestCase):
    def test_rebuilds_supported_images_without_metadata(self):
        for fmt in ('PNG','JPEG','WEBP'):
            result=normalize_image(encoded(fmt));raw=base64.b64decode(result.split(',')[1])
            self.assertNotIn(b'private metadata',raw)
            with Image.open(BytesIO(raw)) as im:self.assertEqual(im.format,'PNG');self.assertFalse(im.info)
    def test_rejects_svg_gif_fake_and_oversized_images(self):
        for data in (base64.b64encode(b'<svg onload="evil()"/>').decode(),encoded('GIF'),'not base64', 'A'*1400001):
            with self.assertRaises(Exception):normalize_image(data)
    def test_zone_boxes_are_bounded_nonoverlapping_and_finite(self):
        for box in ([-1,0,20,20],[90,0,20,20],[0,0,1,1],[float('nan'),0,20,20],[True,0,20,20]):
            d=default_appearance();d['zones']['1']=box
            with self.assertRaises(ValueError):validate(d)
        d=default_appearance();d['zones']['2']=d['zones']['1']
        with self.assertRaises(ValueError):validate(d)
    def test_rejects_remote_or_script_images_and_unknown_fields(self):
        for image in ('https://private.example/image','data:image/svg+xml,<svg/>','data:image/png;base64,AAAA'):
            d=default_appearance('custom');d['image']=image
            with self.assertRaises(ValueError):validate(d)
        d=default_appearance();d['extra']=True
        with self.assertRaises(ValueError):validate(d)
    async def test_device_isolation_restart_and_reset(self):
        disk=None
        async def save(value):nonlocal disk;disk=deepcopy(value)
        store=SimpleNamespace(async_load=AsyncMock(side_effect=lambda:disk),async_save=save)
        repo=AppearanceStore(store);await repo.load()
        d=default_appearance('custom');d['image']=normalize_image(encoded());await repo.save('a',d)
        await repo.save('b',default_appearance('side_by_side'))
        restored=AppearanceStore(store);await restored.load()
        self.assertEqual(restored.get('a'),d);self.assertEqual(restored.get('b')['preset'],'side_by_side')
        restored.get('a')['zones']['1'][0]=60;self.assertEqual(restored.get('a'),d)
        await restored.save('a',default_appearance());self.assertNotIn('a',disk['devices']);self.assertIn('b',disk['devices'])
    async def test_failed_write_preserves_previous_value(self):
        store=SimpleNamespace(async_load=AsyncMock(return_value=None),async_save=AsyncMock(side_effect=OSError('private')))
        repo=AppearanceStore(store);await repo.load()
        with self.assertRaises(OSError):await repo.save('a',default_appearance('outline'))
        self.assertEqual(repo.get('a'),default_appearance())
    async def test_newer_or_damaged_store_is_not_overwritten(self):
        for raw in ({'schema_version':2,'devices':{}},{'schema_version':1,'devices':{'a':{'evil':True}}}):
            store=SimpleNamespace(async_load=AsyncMock(return_value=raw),async_save=AsyncMock());repo=AppearanceStore(store);await repo.load()
            self.assertFalse(repo.available)
            with self.assertRaises(ValueError):await repo.save('a',default_appearance())
            store.async_save.assert_not_awaited()
