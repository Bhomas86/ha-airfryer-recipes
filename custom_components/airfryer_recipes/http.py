"""Authenticated HTTP download for recipe-library exports."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

from aiohttp import hdrs, web

from homeassistant.components.http import KEY_HASS, HomeAssistantView

from .const import DOMAIN, EXPORT_FILENAME, EXPORT_URL
from .diagnostic_download import DIAGNOSTIC_FILENAME, DIAGNOSTIC_URL, previews
from .recipe_repository import RecipePreviewExpiredError

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


class DiagnosticExportView(HomeAssistantView):
    """Real attachment response, preserving the displayed preview and filename."""

    url = DIAGNOSTIC_URL + "/{preview_id}/" + DIAGNOSTIC_FILENAME
    name = "api:airfryer_recipes:diagnostics"

    async def get(self, request, preview_id):
        user = request["hass_user"]
        if not user.is_admin:
            return web.Response(status=HTTPStatus.UNAUTHORIZED)
        hass = request.app[KEY_HASS]
        state = hass.data.get(DOMAIN, {})
        if state.get("repository") is None:
            return web.Response(status=HTTPStatus.SERVICE_UNAVAILABLE)
        from .device_access import active_user, AccessDenied
        try:
            current = await active_user(hass, user.id)
            if not current.is_admin:
                return web.Response(status=HTTPStatus.UNAUTHORIZED)
            payload = previews(hass).read(user.id, preview_id)
        except AccessDenied:
            return web.Response(status=HTTPStatus.UNAUTHORIZED)
        except RecipePreviewExpiredError:
            return web.Response(status=HTTPStatus.NOT_FOUND)
        return web.Response(body=payload, content_type="application/json", charset="utf-8",
            headers={hdrs.CONTENT_DISPOSITION: f'attachment; filename="{DIAGNOSTIC_FILENAME}"',
                     hdrs.CACHE_CONTROL: "no-store", "X-Content-Type-Options": "nosniff"})


def register_http_view(hass: Any) -> None:
    """Register the export endpoint once across config-entry reloads."""
    state = hass.data[DOMAIN]
    if state.get("http_registered"):
        return
    hass.http.register_view(RecipeExportView)
    hass.http.register_view(DiagnosticExportView)
    state["http_registered"] = True
