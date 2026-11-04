"""Separate local preferences for per-user recipe favorites."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any, Awaitable, Callable

from .const import DOMAIN
from .recipe_model import MAX_RECIPES

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
            if not isinstance(user_id, str) or not isinstance(recipe_ids, list) or len(recipe_ids) > MAX_RECIPES:
                raise ValueError("invalid favorite storage")
            if not all(isinstance(recipe_id, str) for recipe_id in recipe_ids):
                raise ValueError("invalid favorite storage")
            loaded[user_id] = set(recipe_ids)
        self._users = loaded

    async def async_get(self, user_id: str) -> list[str]:
        async with self._lock:
            return sorted(self._users.get(user_id, set()))

    async def async_set(
        self, user_id: str, recipe_id: str, favorite: bool, *,
        live_recipe_ids: Callable[[], Awaitable[set[str]]] | None = None,
    ) -> None:
        if type(favorite) is not bool or any(
            not isinstance(value, str) or not 0 < len(value) <= 128 or value != value.strip()
            for value in (user_id, recipe_id)
        ):
            raise ValueError("invalid favorite parameters")
        async with self._lock:
            users = deepcopy(self._users)
            current = users.setdefault(user_id, set())
            if live_recipe_ids is not None:
                # Read after acquiring our lock: an older queued snapshot must
                # not discard a newer favorite. Recipe reads never take this lock.
                live = await live_recipe_ids()
                if favorite and recipe_id not in live:
                    raise ValueError("recipe no longer exists")
                current.intersection_update(live)
            if favorite:
                current.add(recipe_id)
            else:
                current.discard(recipe_id)
            if len(current) > MAX_RECIPES:
                raise ValueError("too many favorites")
            if current == self._users.get(user_id, set()):
                return
            await self._store.async_save({
                "users": {key: sorted(ids) for key, ids in users.items() if ids}
            })
            self._users = users


def create_favorites(hass: Any) -> FavoriteRepository:
    """Use HA Store, leaving appliance and recipe data untouched."""
    from .verified_storage import VerifiedStore

    return FavoriteRepository(VerifiedStore(hass, 1, FAVORITES_KEY))
