"""Airfryer Recipes integration.

The foundation provides the configuration-entry lifecycle only.
No device adapters, network access, settings transfer, or recipe storage yet.

Keep Home Assistant imports behind TYPE_CHECKING here so pure recipe-model
unit tests can run in GitHub CI without installing Home Assistant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass(slots=True)
class AirfryerRecipesRuntime:
    """Placeholder for per-entry services added in later issues."""


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a recipe library without requiring any air fryer integration."""
    entry.runtime_data = AirfryerRecipesRuntime()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the entry; no listeners, tasks or network sessions exist yet."""
    # There are no platforms or subscriptions to unload in the scaffold.
    return True
