"""Separate local preferences for per-user recipe favorites."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from .const import DOMAIN

FAVORITES_KEY = f"{DOMAIN}.favorites"


class FavoriteRepository:
    """Persist personal favorites independently of the shared recipe library."""

    def __init__(self, store: Any) -> None:
        self._store = store
        self._lock = asyncio.Lock()
        self._users: dict[str, set[str]] = {}

    async def async_load(self) -> None:
        raw = await self._store.async_load()
        if raw is None:
            return
        users = raw.get("users") if isinstance(raw, dict) else None
        if not isinstance(users, dict):
            raise ValueError("invalid favorite storage")
        loaded: dict[str, set[str]] = {}
        for user_id, recipe_ids in users.items():
            if not isinstance(user_id, str) or not isinstance(recipe_ids, list) or len(recipe_ids) > 500:
                raise ValueError("invalid favorite storage")
            if not all(isinstance(recipe_id, str) for recipe_id in recipe_ids):
                raise ValueError("invalid favorite storage")
            loaded[user_id] = set(recipe_ids)
        self._users = loaded

    async def async_get(self, user_id: str) -> list[str]:
        async with self._lock:
            return sorted(self._users.get(user_id, set()))

    async def async_set(self, user_id: str, recipe_id: str, favorite: bool) -> None:
        if type(favorite) is not bool:
            raise ValueError("favorite must be a boolean")
        async with self._lock:
            users = deepcopy(self._users)
            current = users.setdefault(user_id, set())
            if favorite:
                current.add(recipe_id)
            else:
                current.discard(recipe_id)
            if current == self._users.get(user_id, set()):
                return
            await self._store.async_save({
                "users": {key: sorted(ids) for key, ids in users.items() if ids}
            })
            self._users = users


def create_favorites(hass: Any) -> FavoriteRepository:
    """Use HA Store, leaving appliance and recipe data untouched."""
    from homeassistant.helpers.storage import Store

    return FavoriteRepository(Store(hass, 1, FAVORITES_KEY))
