"""Airfryer Recipes custom integration lifecycle.

This integration stores recipes locally. It does not control appliances;
Airfryer Control remains optional and will be connected in a future issue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .recipe_repository import RecipeRepository

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass(slots=True)
class AirfryerRecipesRuntime:
    """Per-config-entry services, initially the local recipe repository."""

    recipes: RecipeRepository


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load persistent recipes before reporting a successful setup."""
    from .storage import create_repository

    recipes = create_repository(hass)
    await recipes.async_load()
    entry.runtime_data = AirfryerRecipesRuntime(recipes=recipes)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload; there are no listeners, deferred writes or device connections."""
    return True
