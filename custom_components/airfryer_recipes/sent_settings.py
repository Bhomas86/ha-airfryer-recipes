"""Persistent accepted settings per HA device and zone, never a command queue."""
from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .const import DOMAIN
from .recipe_model import CookingPhase


class SentSettings:
    def __init__(self, store: Any) -> None:
        self.store = store
        self.devices: dict = {}
        self.available = False
        self.lock = asyncio.Lock()

    async def async_load(self) -> None:
        try:
            data = await self.store.async_load()
            if data is not None:
                if not isinstance(data, dict) or set(data) != {"schema_version", "devices"} or type(data["schema_version"]) is not int or data["schema_version"] != 1:
                    raise ValueError("Unsupported history")
                devices = data["devices"]
                if not isinstance(devices, dict) or len(devices) > 256:
                    raise ValueError("Invalid history")
                for device, zones in devices.items():
                    if not isinstance(device, str) or not 0 < len(device) <= 128 or not isinstance(zones, dict) or not set(zones) <= {"1", "2"}:
                        raise ValueError("Invalid history target")
                    for record in zones.values():
                        if not isinstance(record, dict) or set(record) != {"settings", "recipe_id", "sent_at"}:
                            raise ValueError("Invalid history record")
                        if asdict(CookingPhase(**record["settings"])) != record["settings"]:
                            raise ValueError("Invalid history settings")
                        rid = record["recipe_id"]
                        if rid is not None and (not isinstance(rid, str) or not 0 < len(rid) <= 128):
                            raise ValueError("Invalid recipe reference")
                        stamp = datetime.fromisoformat(record["sent_at"])
                        if stamp.tzinfo is None:
                            raise ValueError("Invalid history timestamp")
                self.devices = deepcopy(devices)
            self.available = True
        except Exception:
            # Preserve damaged/newer storage. Recipes and sending remain usable;
            # writes stay disabled until a successful integration reload.
            self.available = False

    def get(self, device: str) -> dict:
        return {"available": self.available, "zones": deepcopy(self.devices.get(device, {}))}

    async def record(self, device: str, zone: int, phase: CookingPhase, recipe_id: str | None = None) -> None:
        if (not self.available or type(zone) is not int or zone not in (1, 2)
                or not isinstance(device, str) or not 0 < len(device) <= 128
                or not isinstance(phase, CookingPhase)
                or (recipe_id is not None and (not isinstance(recipe_id, str) or not 0 < len(recipe_id) <= 128))):
            raise ValueError("History unavailable")
        async with self.lock:
            next_devices = deepcopy(self.devices)
            if device not in next_devices and len(next_devices) >= 256:
                raise ValueError("History capacity")
            next_devices.setdefault(device, {})[str(zone)] = {
                "settings": asdict(phase), "recipe_id": recipe_id,
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.store.async_save({"schema_version": 1, "devices": next_devices})
            self.devices = next_devices


def create_sent_settings(hass: Any) -> SentSettings:
    from homeassistant.helpers.storage import Store
    return SentSettings(Store(hass, 1, f"{DOMAIN}.sent_settings"))
