"""Private per-device artwork and relative zone boxes. Never a control path."""
from __future__ import annotations
import asyncio
import base64
from copy import deepcopy
from io import BytesIO
import math
from typing import Any
from .const import DOMAIN

MAX_IMAGE = 350_000
PRESETS = {'stacked', 'side_by_side', 'outline', 'custom'}

def default_appearance(preset='stacked'):
    boxes = {'1': [5, 8, 90, 39], '2': [5, 53, 90, 39]}
    if preset == 'side_by_side':
        boxes = {'1': [4, 15, 43, 75], '2': [53, 15, 43, 75]}
    return {'preset': preset, 'image': None, 'zones': boxes}

def validate(value):
    if not isinstance(value, dict) or set(value) != {'preset', 'image', 'zones'} or value['preset'] not in PRESETS:
        raise ValueError('Invalid appearance')
    image = value['image']
    if value['preset'] == 'custom':
        if not isinstance(image, str) or len(image) > MAX_IMAGE * 2 or not image.startswith('data:image/png;base64,'):
            raise ValueError('Invalid image')
        raw = base64.b64decode(image.split(',', 1)[1], validate=True)
        if len(raw) > MAX_IMAGE or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Invalid image')
    elif image is not None:
        raise ValueError('Unexpected image')
    boxes = value['zones']
    if not isinstance(boxes, dict) or set(boxes) != {'1', '2'}:
        raise ValueError('Invalid zones')
    for box in boxes.values():
        if not isinstance(box, list) or len(box) != 4 or any(type(n) not in (int, float) or not math.isfinite(n) for n in box):
            raise ValueError('Invalid zone rectangle')
        x, y, w, h = box
        if x < 0 or y < 0 or w < 8 or h < 8 or x+w > 100 or y+h > 100:
            raise ValueError('Zone outside image')
    a,b=boxes.values()
    if min(a[0]+a[2], b[0]+b[2]) > max(a[0],b[0]) and min(a[1]+a[3], b[1]+b[3]) > max(a[1],b[1]):
        raise ValueError('Overlapping zones')
    return deepcopy(value)

def normalize_image(encoded):
    """Decode and rebuild pixels off the event loop; no metadata or SVG."""
    from PIL import Image, ImageOps
    import warnings
    if not isinstance(encoded, str) or len(encoded) > 1_400_000:
        raise ValueError('Image too large')
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > 1_000_000:
        raise ValueError('Image too large')
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(BytesIO(raw)) as source:
            if source.format not in {'PNG', 'JPEG', 'WEBP'} or getattr(source, 'n_frames', 1) != 1 or source.width*source.height > 8_000_000:
                raise ValueError('Unsupported image')
            source.load()
            pixels = ImageOps.exif_transpose(source).convert('RGBA')
            pixels.thumbnail((800, 800))
            clean = Image.new('RGBA', pixels.size)
            clean.paste(pixels)
            while True:
                out = BytesIO(); clean.save(out, format='PNG')
                if len(out.getvalue()) <= MAX_IMAGE or max(clean.size) <= 64:
                    break
                clean = clean.resize((max(1, int(clean.width * .75)), max(1, int(clean.height * .75))))
    raw = out.getvalue()
    if len(raw) > MAX_IMAGE:
        raise ValueError('Normalized image too large')
    return 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')

class AppearanceStore:
    def __init__(self, store):
        self.store=store; self.devices={}; self.available=False; self.lock=asyncio.Lock()
    async def load(self):
        try:
            raw=await self.store.async_load()
            if raw is not None:
                if not isinstance(raw,dict) or set(raw)!={'schema_version','devices'} or type(raw['schema_version']) is not int or raw['schema_version']!=1 or not isinstance(raw['devices'],dict) or len(raw['devices'])>32:
                    raise ValueError('Invalid appearance storage')
                for did,value in raw['devices'].items():
                    if not isinstance(did,str) or not 0<len(did)<=128: raise ValueError('Invalid device')
                    validate(value)
                self.devices=deepcopy(raw['devices'])
            self.available=True
        except Exception:
            self.available=False
    def get(self, did):
        if not self.available: raise ValueError('Appearance storage unavailable')
        return deepcopy(self.devices.get(did,default_appearance()))
    async def save(self,did,value):
        if not self.available or not isinstance(did,str) or not 0<len(did)<=128: raise ValueError('Appearance storage unavailable')
        value=validate(value)
        async with self.lock:
            updated=deepcopy(self.devices)
            if value == default_appearance(): updated.pop(did,None)
            else: updated[did]=value
            if len(updated)>32: raise ValueError('Appearance capacity')
            await self.store.async_save({'schema_version':1,'devices':updated})
            self.devices=updated

async def repository(hass):
    state=hass.data[DOMAIN]
    async with state.setdefault('appearance_load_lock',asyncio.Lock()):
        if 'appearance' not in state:
            from homeassistant.helpers.storage import Store
            repo=AppearanceStore(Store(hass,1,f'{DOMAIN}.appearance'))
            await repo.load();state['appearance']=repo
        return state['appearance']
