"""Home Assistant storage adapter for the device-independent recipe repository.

The active library and last-known-good snapshot have separate Store keys.
Nothing in this module communicates with an air fryer or external service.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .const import DOMAIN
from .recipe_repository import RecipeRepository

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.recipes"
BACKUP_KEY = f"{DOMAIN}.recipes.backup"


class _Persistence:
    def __init__(self, hass: Any) -> None:
        # The import is deferred so recipe tests work without Home Assistant.
        from homeassistant.helpers.storage import Store

        self._active = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._backup = Store(hass, STORAGE_VERSION, BACKUP_KEY)
        self._previous: dict[str, Any] | None = None

    async def async_load(self) -> dict[str, Any] | None:
        """Return the current payload without resetting a damaged store."""
        data = await self._active.async_load()
        self._previous = deepcopy(data)
        return data

    async def async_save(self, data: dict[str, Any]) -> None:
        """Write a recoverable previous snapshot before replacing active data."""
        if self._previous is not None:
            await self._backup.async_save(deepcopy(self._previous))
        await self._active.async_save(deepcopy(data))
        self._previous = deepcopy(data)


def create_repository(hass: Any) -> RecipeRepository:
    """Build the repository and its isolated HA Store dependencies."""
    persistence = _Persistence(hass)
    return RecipeRepository(persistence.async_load, persistence.async_save)
