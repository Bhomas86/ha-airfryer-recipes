"""Register the local administrator recipe panel with Home Assistant."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .const import DOMAIN

PANEL_PATH = "airfryer-recipes"
MODULE_URL = f"/api/{DOMAIN}/panel.js"


async def async_register_panel(hass: Any) -> None:
    """Serve a bundled module and expose it through HA's custom panel API."""
    from homeassistant.components import panel_custom
    from homeassistant.components.http import StaticPathConfig

    state = hass.data[DOMAIN]
    if not state.get("static_registered"):
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                MODULE_URL,
                str(Path(__file__).parent / "frontend" / "panel.js"),
                cache_headers=False,
            )
        ])
        state["static_registered"] = True
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_PATH,
        webcomponent_name="airfryer-recipes-panel",
        sidebar_title="Airfryer Recipes",
        sidebar_icon="mdi:chef-hat",
        module_url=f"{MODULE_URL}?v=0.1.0b5",
        require_admin=True,
        config_panel_domain=DOMAIN,
    )


def async_remove_panel(hass: Any) -> None:
    """Remove navigation on unload; the static route remains for reload."""
    from homeassistant.components import frontend

    frontend.async_remove_panel(hass, PANEL_PATH)
