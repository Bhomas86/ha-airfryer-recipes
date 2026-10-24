"""Airfryer Recipes integration, local recipe persistence and WebSocket API.

Airfryer Control is optional. No network/device control is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .const import DOMAIN
from .recipe_repository import RecipeRepository

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass(slots=True)
class AirfryerRecipesRuntime:
    """Services owned by the configured local recipe library."""

    recipes: RecipeRepository


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the local library, then publish it to authenticated commands."""
    from .storage import create_repository
    from .websocket_api import register_commands

    recipes = create_repository(hass)
    await recipes.async_load()

    state = hass.data.setdefault(DOMAIN, {})
    state["repository"] = recipes
    if not state.get("websocket_registered", False):
        register_commands(hass)
        state["websocket_registered"] = True

    entry.runtime_data = AirfryerRecipesRuntime(recipes=recipes)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Disable API access when the integration entry is unloaded."""
    state = hass.data.get(DOMAIN)
    if state is not None:
        state.pop("repository", None)
        # HA does not expose a normal integration command unregistration hook.
        # Registered handlers now report 'not_configured' until reloaded.
    return True
