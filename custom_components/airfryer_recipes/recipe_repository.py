"""Device-independent, transactional recipe repository.

No Home Assistant imports or appliance access: the persistence callbacks are
injected by the integration. Persist first, then publish in-memory changes.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
from time import monotonic
from typing import Any, Awaitable, Callable, Literal
from uuid import uuid4

from .recipe_model import (
    MAX_RECIPES,
    Recipe,
    RecipeValidationError,
    export_library_json,
    import_library_json,
    load_library_json,
)

LoadCallback = Callable[[], Awaitable[dict[str, Any] | None]]
SaveCallback = Callable[[dict[str, Any]], Awaitable[None]]
ConflictPolicy = Literal["skip", "replace_ids"]
PREVIEW_TTL_SECONDS = 300
MAX_PENDING_PREVIEWS = 20


class RecipeConflictError(RecipeValidationError):
    """A recipe ID, name or library revision conflicts with another value."""


class RecipeNotFoundError(KeyError):
    """The requested recipe does not exist."""


class RecipePreviewExpiredError(RecipeConflictError):
    """A preview has expired, become stale or been consumed."""


@dataclass(frozen=True, slots=True)
class ImportPreview:
    """Immutable, non-destructive summary of an import."""

    token: str
    incoming_count: int
    duplicate_ids: tuple[str, ...]
    duplicate_names: tuple[str, ...]
    revision: int


@dataclass(slots=True)
class _PendingImport:
    created_at: float
    revision: int
    recipes: tuple[Recipe, ...]


def _name_key(recipe: Recipe) -> str:
    return recipe.name.casefold()


def _validate_unique(recipes: tuple[Recipe, ...]) -> None:
    if len(recipes) > MAX_RECIPES:
        raise RecipeValidationError("too many recipes")
    ids = [recipe.id for recipe in recipes]
    names = [_name_key(recipe) for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise RecipeConflictError("duplicate recipe IDs")
    if len(names) != len(set(names)):
        raise RecipeConflictError("duplicate recipe names")


def _encode(recipes: tuple[Recipe, ...]) -> dict[str, Any]:
    """Produce a versioned, validated payload for Home Assistant Store."""
    return json.loads(export_library_json(recipes))


class RecipeRepository:
    """Async repository with serial writes and short-lived import previews."""

    def __init__(self, load: LoadCallback, save: SaveCallback) -> None:
        self._load = load
        self._save = save
        self._lock = asyncio.Lock()
        self._records: dict[str, Recipe] = {}
        self._pending: dict[str, _PendingImport] = {}
        self._revision = 0
        self._loaded = False

    async def async_load(self) -> None:
        """Load once; invalid or future-version storage must never be reset."""
        async with self._lock:
            if self._loaded:
                return
            raw = await self._load()
            if raw is None:
                recipes: list[Recipe] = []
            else:
                # Reject unknown schemas instead of returning an empty library.
                recipes = load_library_json(json.dumps(raw, ensure_ascii=False))
            _validate_unique(tuple(recipes))
            self._records = {recipe.id: recipe for recipe in recipes}
            self._loaded = True

    def _require_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("recipe repository has not been loaded")

    async def async_list(self) -> tuple[Recipe, ...]:
        """Get an immutable snapshot, sorted by name."""
        async with self._lock:
            self._require_loaded()
            return tuple(sorted(self._records.values(), key=lambda r: (r.name.casefold(), r.id)))

    async def async_get(self, recipe_id: str) -> Recipe:
        async with self._lock:
            self._require_loaded()
            try:
                return self._records[recipe_id]
            except KeyError as err:
                raise RecipeNotFoundError(recipe_id) from err

    async def async_export_json(self) -> str:
        """Export all recipes; no device, zone or private settings included."""
        async with self._lock:
            self._require_loaded()
            return export_library_json(tuple(self._records.values()))

    async def _commit(self, records: dict[str, Recipe]) -> None:
        """Publish a new snapshot only after awaited storage write succeeded."""
        recipes = tuple(records.values())
        _validate_unique(recipes)
        await self._save(_encode(recipes))
        self._records = records
        self._revision += 1
        self._pending.clear()

    async def async_create(self, recipe: Recipe) -> Recipe:
        async with self._lock:
            self._require_loaded()
            if recipe.id in self._records:
                raise RecipeConflictError("recipe ID already exists")
            if any(_name_key(r) == _name_key(recipe) for r in self._records.values()):
                raise RecipeConflictError("recipe name already exists")
            await self._commit({**self._records, recipe.id: recipe})
            return recipe

    async def async_update(self, recipe: Recipe) -> Recipe:
        async with self._lock:
            self._require_loaded()
            if recipe.id not in self._records:
                raise RecipeNotFoundError(recipe.id)
            if any(
                r.id != recipe.id and _name_key(r) == _name_key(recipe)
                for r in self._records.values()
            ):
                raise RecipeConflictError("recipe name already exists")
            await self._commit({**self._records, recipe.id: recipe})
            return recipe

    async def async_delete(self, recipe_id: str) -> None:
        async with self._lock:
            self._require_loaded()
            if recipe_id not in self._records:
                raise RecipeNotFoundError(recipe_id)
            next_records = dict(self._records)
            del next_records[recipe_id]
            await self._commit(next_records)

    async def async_preview_import(self, payload: str) -> ImportPreview:
        """Parse without saving; bind the preview to current library revision."""
        incoming = tuple(import_library_json(payload))
        _validate_unique(incoming)
        async with self._lock:
            self._require_loaded()
            ids = set(self._records)
            names = {_name_key(r) for r in self._records.values()}
            conflicts_ids = tuple(r.id for r in incoming if r.id in ids)
            conflicts_names = tuple(r.name for r in incoming if _name_key(r) in names)
            now = monotonic()
            self._pending = {
                key: item for key, item in self._pending.items()
                if now - item.created_at < PREVIEW_TTL_SECONDS
            }
            # Bounded memory even if many previews arrive without confirmation.
            if len(self._pending) >= MAX_PENDING_PREVIEWS:
                oldest = min(self._pending, key=lambda key: self._pending[key].created_at)
                del self._pending[oldest]
            token = str(uuid4())
            self._pending[token] = _PendingImport(now, self._revision, incoming)
            return ImportPreview(
                token=token,
                incoming_count=len(incoming),
                duplicate_ids=conflicts_ids,
                duplicate_names=conflicts_names,
                revision=self._revision,
            )

    async def async_confirm_import(
        self, token: str, *, policy: ConflictPolicy = "skip"
    ) -> int:
        """Import a preview exactly once, using an explicit conflict strategy.

        replace_ids may update an existing recipe of the *same ID*.
        A name conflict with a different ID is always rejected to avoid
        deleting unrelated recipes or silently renaming them.
        """
        if policy not in ("skip", "replace_ids"):
            raise ValueError("unsupported import conflict policy")
        async with self._lock:
            self._require_loaded()
            pending = self._pending.get(token)
            if (
                pending is None
                or monotonic() - pending.created_at >= PREVIEW_TTL_SECONDS
                or pending.revision != self._revision
            ):
                raise RecipePreviewExpiredError("import preview expired or library changed")
            next_records = dict(self._records)
            changed = 0
            for recipe in pending.recipes:
                match_by_name = next(
                    (r for r in next_records.values() if _name_key(r) == _name_key(recipe)),
                    None,
                )
                match_by_id = next_records.get(recipe.id)
                if policy == "skip" and (match_by_id or match_by_name):
                    continue
                if (
                    policy == "replace_ids"
                    and match_by_name is not None
                    and match_by_name.id != recipe.id
                ):
                    raise RecipeConflictError(
                        "name belongs to another recipe; rename it before importing"
                    )
                next_records[recipe.id] = recipe
                changed += 1
            if changed:
                await self._commit(next_records)
            else:
                self._pending.pop(token, None)
            return changed
