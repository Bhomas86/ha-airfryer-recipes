"""Device-independent recipe definitions and versioned JSON serialization.

This module intentionally does not import Home Assistant or any device adapter.
It cannot initiate or queue appliance commands.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = 1
MAX_IMPORT_BYTES = 1_000_000
MAX_RECIPES = 500
MAX_PHASES = 8  # Reserved for future multi-phase support.


class RecipeValidationError(ValueError):
    """Invalid or unsupported recipe data."""


def _validated_text(value: object, label: str, limit: int, *, optional: bool = False) -> str:
    if not isinstance(value, str):
        raise RecipeValidationError(f"{label} must be a string")
    cleaned = value.strip()
    if not optional and not cleaned:
        raise RecipeValidationError(f"{label} cannot be empty")
    if len(cleaned) > limit:
        raise RecipeValidationError(f"{label} exceeds {limit} characters")
    return cleaned


def _validated_int(value: object, label: str, minimum: int, maximum: int) -> int:
    # bool is a subclass of int and must not be accepted as a recipe value.
    if type(value) is not int or not minimum <= value <= maximum:
        raise RecipeValidationError(f"{label} must be an integer from {minimum} to {maximum}")
    return value


@dataclass(frozen=True, slots=True)
class CookingPhase:
    """One preparation phase; supported programs and limits are adapter-specific."""

    program: str
    temperature_c: int
    duration_minutes: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "program", _validated_text(self.program, "program", 64))
        _validated_int(self.temperature_c, "temperature_c", 0, 400)
        _validated_int(self.duration_minutes, "duration_minutes", 1, 1440)


@dataclass(frozen=True, slots=True)
class Recipe:
    """Recipe without any associated appliance, cooking zone or user favorites."""

    id: str
    name: str
    phases: tuple[CookingPhase, ...]
    description: str = ""
    category: str = ""
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _validated_text(self.id, "id", 128))
        object.__setattr__(self, "name", _validated_text(self.name, "name", 100))
        object.__setattr__(
            self, "description", _validated_text(self.description, "description", 500, optional=True)
        )
        object.__setattr__(
            self, "category", _validated_text(self.category, "category", 64, optional=True)
        )
        if not isinstance(self.phases, tuple) or not 1 <= len(self.phases) <= MAX_PHASES:
            raise RecipeValidationError(f"phases must contain 1 to {MAX_PHASES} steps")
        if not all(isinstance(phase, CookingPhase) for phase in self.phases):
            raise RecipeValidationError("all phases must be CookingPhase objects")
        if not isinstance(self.tags, tuple) or len(self.tags) > 20:
            raise RecipeValidationError("tags must be a tuple of at most 20 labels")
        tags = tuple(_validated_text(tag, "tag", 32) for tag in self.tags)
        if len({tag.casefold() for tag in tags}) != len(tags):
            raise RecipeValidationError("duplicate tags are not allowed")
        object.__setattr__(self, "tags", tags)


def create_recipe(
    name: str,
    *,
    program: str,
    temperature_c: int,
    duration_minutes: int,
    description: str = "",
    category: str = "",
    tags: tuple[str, ...] = (),
) -> Recipe:
    """Build a new single-phase recipe with a stable random identifier."""
    return Recipe(
        id=str(uuid4()),
        name=name,
        description=description,
        category=category,
        tags=tags,
        phases=(CookingPhase(program, temperature_c, duration_minutes),),
    )


def recipe_to_dict(recipe: Recipe) -> dict[str, Any]:
    """Encode a recipe using stable, JSON-serializable fields."""
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "category": recipe.category,
        "tags": list(recipe.tags),
        "phases": [
            {
                "program": phase.program,
                "temperature_c": phase.temperature_c,
                "duration_minutes": phase.duration_minutes,
            }
            for phase in recipe.phases
        ],
    }


def recipe_from_dict(raw: object) -> Recipe:
    """Validate all fields and reject ambiguous/unsupported structures."""
    if not isinstance(raw, dict):
        raise RecipeValidationError("recipe must be an object")
    allowed = {"id", "name", "description", "category", "tags", "phases"}
    if unknown := set(raw) - allowed:
        raise RecipeValidationError(f"unknown recipe fields: {sorted(unknown)}")
    phases = raw.get("phases")
    if not isinstance(phases, list) or not phases:
        raise RecipeValidationError("phases must be a nonempty list")
    if len(phases) > MAX_PHASES:
        raise RecipeValidationError("too many phases")
    converted = []
    for phase in phases:
        if not isinstance(phase, dict) or set(phase) != {
            "program", "temperature_c", "duration_minutes"
        }:
            raise RecipeValidationError("phase must contain program, temperature_c and duration_minutes")
        converted.append(CookingPhase(**phase))
    tags = raw.get("tags", [])
    if not isinstance(tags, list):
        raise RecipeValidationError("tags must be a list")
    try:
        return Recipe(
            id=raw["id"],
            name=raw["name"],
            description=raw.get("description", ""),
            category=raw.get("category", ""),
            tags=tuple(tags),
            phases=tuple(converted),
        )
    except KeyError as exc:
        raise RecipeValidationError(f"missing field: {exc.args[0]}") from exc


def export_library_json(recipes: list[Recipe] | tuple[Recipe, ...]) -> str:
    """Export a versioned collection; duplicate IDs are never silently ignored."""
    if len(recipes) > MAX_RECIPES:
        raise RecipeValidationError("too many recipes to export")
    ids = [recipe.id for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise RecipeValidationError("duplicate recipe IDs")
    payload = {"schema_version": SCHEMA_VERSION, "recipes": [recipe_to_dict(x) for x in recipes]}
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def import_library_json(payload: str) -> list[Recipe]:
    """Read a versioned JSON collection without modifying persistent storage."""
    if not isinstance(payload, str) or len(payload.encode("utf-8")) > MAX_IMPORT_BYTES:
        raise RecipeValidationError("invalid or oversized JSON input")
    return load_library_json(payload)


def load_library_json(payload: str) -> list[Recipe]:
    """Validate trusted local storage without applying the upload size limit."""
    try:
        data = json.loads(payload)
    except (ValueError, TypeError) as exc:
        raise RecipeValidationError("invalid JSON") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "recipes"}:
        raise RecipeValidationError("library must contain schema_version and recipes")
    if type(data["schema_version"]) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise RecipeValidationError("unsupported library schema version")
    items = data["recipes"]
    if not isinstance(items, list) or len(items) > MAX_RECIPES:
        raise RecipeValidationError("recipes must be a list of at most 500 entries")
    results = [recipe_from_dict(item) for item in items]
    ids = [recipe.id for recipe in results]
    if len(set(ids)) != len(ids):
        raise RecipeValidationError("duplicate recipe IDs")
    return results
