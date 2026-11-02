"""Explicit whole-device grants; never infer permissions from card config."""
from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from .const import DOMAIN


class AccessDenied(Exception):
    """Authenticated user has no current device permission."""


def valid_id(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 128 and value == value.strip()


class DeviceAccess:
    def __init__(self, store: Any) -> None:
        self.store = store
        self.users: dict[str, set[str]] = {}
        self.available = False
        self.updating = False
        self.revision = 0
        self.lock = asyncio.Lock()

    async def async_load(self) -> None:
        try:
            raw = await self.store.async_load()
            if raw is not None:
                if not isinstance(raw, dict) or set(raw) != {"schema_version", "users"} or type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
                    raise ValueError("Unsupported permissions")
                users = raw["users"]
                if not isinstance(users, dict) or len(users) > 256:
                    raise ValueError("Invalid permissions")
                for uid, devices in users.items():
                    if not valid_id(uid) or not isinstance(devices, list) or len(devices) > 256 or any(not valid_id(d) for d in devices) or len(set(devices)) != len(devices):
                        raise ValueError("Invalid permissions")
                self.users = {uid: set(devices) for uid, devices in users.items()}
            self.available = True
        except Exception:
            # Preserve damaged/newer data. Admin operation and recipes remain
            # usable; ordinary users fail closed and writes stay disabled.
            self.available = False

    def devices_for(self, uid: str) -> set[str]:
        return set(self.users.get(uid, set())) if self.available and not self.updating else set()

    def snapshot(self) -> dict:
        return {"available": self.available, "grants": [
            {"user_id": uid, "device_id": device}
            for uid, devices in sorted(self.users.items()) for device in sorted(devices)
        ]}

    async def set(self, uid: str, device: str, allowed: bool) -> bool:
        if not self.available or not valid_id(uid) or not valid_id(device) or type(allowed) is not bool:
            raise ValueError("Invalid permission change")
        async with self.lock:
            users = deepcopy(self.users)
            devices = users.setdefault(uid, set())
            if (device in devices) == allowed:
                return False
            if allowed:
                devices.add(device)
            else:
                devices.discard(device)
            users = {key: value for key, value in users.items() if value}
            if len(users) > 256 or any(len(value) > 256 for value in users.values()):
                raise ValueError("Permission capacity")
            # Invalidate old confirmations before awaiting persistence, even
            # if this write fails. New preparation is needed afterward.
            self.revision += 1
            self.updating = True
            try:
                await self.store.async_save({"schema_version": 1, "users": {key: sorted(value) for key, value in users.items()}})
                self.users = users
            finally:
                self.updating = False
            return True


async def active_user(hass: Any, uid: str) -> Any:
    if not valid_id(uid):
        raise AccessDenied
    user = await hass.auth.async_get_user(uid)
    if user is None or not user.is_active:
        raise AccessDenied
    return user


async def device_scope(hass: Any, uid: str) -> tuple[set[str] | None, Any]:
    """None means administrator; ordinary users get a copy of explicit IDs."""
    user = await active_user(hass, uid)
    if user.is_admin:
        return None, None
    if getattr(user, "system_generated", False):
        return set(), None
    access = hass.data.get(DOMAIN, {}).get("device_access")
    if access is None:
        return set(), None
    return access.devices_for(uid), (access, access.revision)


async def authorize_device(hass: Any, uid: str, device: str) -> Any:
    if not valid_id(device):
        raise AccessDenied
    devices, snapshot = await device_scope(hass, uid)
    if devices is not None and device not in devices:
        raise AccessDenied
    return snapshot


def create_device_access(hass: Any) -> DeviceAccess:
    from homeassistant.helpers.storage import Store
    return DeviceAccess(Store(hass, 1, f"{DOMAIN}.device_access"))
