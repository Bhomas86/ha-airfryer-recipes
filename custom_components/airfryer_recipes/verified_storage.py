"""Verify HA Store writes on disk before publishing application state.

HA Store logs some write failures without raising them. Its read cache is not
proof of persistence. Writes still use HA's public Store and atomic-write option;
the independent read runs in HA's executor, never on the event loop.
"""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any


def _matches_file(path: str, key: str, version: int, expected: Any) -> bool:
    with open(path, encoding="utf-8") as stream:
        stored = json.load(stream)
    return (
        isinstance(stored, dict) and stored.get("key") == key
        and type(stored.get("version")) is int and stored["version"] == version
        and "data" in stored
        and json.dumps(stored["data"], sort_keys=True, allow_nan=False)
        == json.dumps(expected, sort_keys=True, allow_nan=False)
    )


class VerifiedStore:
    def __init__(self, hass: Any, version: int, key: str) -> None:
        from homeassistant.helpers.storage import Store
        self._hass, self._key, self._version = hass, key, version
        self._store = Store(hass, version, key, atomic_writes=True)

    async def async_load(self) -> Any:
        return await self._store.async_load()

    async def async_save(self, value: Any) -> None:
        if getattr(self._hass, "is_stopping", False):
            raise OSError("Storage write unavailable during shutdown")
        expected = deepcopy(value)
        try:
            await self._store.async_save(expected)
            persisted = await self._hass.async_add_executor_job(
                _matches_file, self._store.path, self._key, self._version, expected,
            )
        except (OSError, ValueError, TypeError, UnicodeError):
            raise OSError("Storage write could not be verified") from None
        if not persisted:
            raise OSError("Storage write could not be verified")
