"""Authenticated HTTP download for recipe-library exports."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

from aiohttp import hdrs, web

from homeassistant.components.http import KEY_HASS, HomeAssistantView

from .const import DOMAIN, EXPORT_FILENAME, EXPORT_URL

_LOGGER = logging.getLogger(__name__)


class RecipeExportView(HomeAssistantView):
    """Download the current recipe library with an explicit filename."""

    url = EXPORT_URL
    name = "api:airfryer_recipes:export"

    async def get(self, request: web.Request) -> web.Response:
        """Return a versioned JSON export to an authenticated administrator."""
        if not request["hass_user"].is_admin:
            return web.Response(status=HTTPStatus.UNAUTHORIZED)

        hass = request.app[KEY_HASS]
        repository = hass.data.get(DOMAIN, {}).get("repository")
        if repository is None:
            return web.Response(status=HTTPStatus.SERVICE_UNAVAILABLE)

        try:
            payload = await repository.async_export_json()
        except Exception:
            _LOGGER.exception("Recipe export failed")
            return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return web.Response(
            body=payload.encode("utf-8"),
            content_type="application/json",
            charset="utf-8",
            headers={
                hdrs.CONTENT_DISPOSITION: f'attachment; filename="{EXPORT_FILENAME}"',
                hdrs.CACHE_CONTROL: "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )


def register_http_view(hass: Any) -> None:
    """Register the export endpoint once across config-entry reloads."""
    state = hass.data[DOMAIN]
    if state.get("http_registered"):
        return
    hass.http.register_view(RecipeExportView)
    state["http_registered"] = True
