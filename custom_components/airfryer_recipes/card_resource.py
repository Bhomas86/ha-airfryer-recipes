"""Register the bundled card in HA's dashboard resource collection."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urlsplit

from .const import DOMAIN, FRONTEND_VERSION

CARD_URL = f"/api/{DOMAIN}/card.js"
CARD_MODULE_URL = f"{CARD_URL}?v={FRONTEND_VERSION}"
_LOGGER = logging.getLogger(__name__)


def _is_our_resource(url: Any) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return not parts.scheme and not parts.netloc and parts.path == CARD_URL


async def async_register_card_resource(hass: Any) -> None:
    """Create/update our module only; do not edit dashboard cards or YAML."""
    from homeassistant.components.frontend import add_extra_js_url

    state = hass.data[DOMAIN]
    lock = state.setdefault("card_resource_lock", asyncio.Lock())
    async with lock:
        try:
            try:
                from homeassistant.components.lovelace.const import LOVELACE_DATA
            except ImportError:
                data = hass.data.get("lovelace")
            else:
                data = hass.data.get(LOVELACE_DATA)
            resources = getattr(data, "resources", None)
            mode = getattr(data, "resource_mode", None)
            if isinstance(data, dict):
                resources, mode = data.get("resources"), data.get("resource_mode", data.get("mode"))
            if mode == "storage" and resources is not None:
                # Use HA's public load helper before inspecting lazy storage.
                await resources.async_get_info()
                matches = [item for item in resources.async_items() if _is_our_resource(item.get("url"))]
                if not matches:
                    await resources.async_create_item({"res_type": "module", "url": CARD_MODULE_URL})
                for item in matches:
                    if item.get("url") != CARD_MODULE_URL or item.get("type") != "module":
                        await resources.async_update_item(item["id"], {"res_type": "module", "url": CARD_MODULE_URL})
                return
        except Exception:
            # Optional resource persistence must not break the recipe library.
            # Do not include internal exception paths or user resource URLs.
            _LOGGER.warning("Dashboard resource registration failed; using extra module %s", CARD_MODULE_URL)

        # YAML resources are user-managed; missing/failed storage uses the
        # supported frontend fallback without changing configuration files.
        if state.get("card_extra_module") != CARD_MODULE_URL:
            add_extra_js_url(hass, CARD_MODULE_URL)
            state["card_extra_module"] = CARD_MODULE_URL
