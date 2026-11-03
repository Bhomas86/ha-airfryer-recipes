"""Device-scoped dashboard access, separate from administrator test tools."""
from __future__ import annotations

from typing import Any

from .beta_send import BetaTestBlocked, SendPermit
from .const import DOMAIN
from .device_access import AccessDenied, authorize_device, device_scope
from .recipe_model import RecipeValidationError

FIELDS = {
    "appearance_get": {"device_id"},
    "devices": set(), "sent_settings": {"device_id"},
    "prepare_send": {"device_id", "zone_id", "settings"},
    "beta_prepare": {"device_id", "zone_id", "acknowledge_unverified", "source"},
    "beta_confirm": {"token", "acknowledge_supervised_test"},
    "beta_cancel": {"token"},
    "beta_recover": {"device_id", "acknowledge_physical_reset"},
}


async def execute(hass: Any, connection: Any, request_id: int, action: str, params: dict) -> dict:
    from homeassistant.core import Context
    from .command_preview import prepare_preview
    from .device_discovery import discover_devices

    if not isinstance(action, str) or action not in FIELDS or not isinstance(params, dict) or set(params) != FIELDS[action]:
        raise RecipeValidationError("Unexpected control parameters")
    if action == "beta_prepare" and not isinstance(params["source"], dict):
        raise RecipeValidationError("Choose recipe or manual settings")
    uid = connection.user.id
    if action == "appearance_get":
        from .appearance import repository
        snapshot = await authorize_device(hass, uid, params["device_id"])
        result = (await repository(hass)).get(params["device_id"])
        if await authorize_device(hass, uid, params["device_id"]) != snapshot:
            raise AccessDenied
        return result
    if action == "devices":
        allowed, snapshot = await device_scope(hass, uid)
        if allowed == set():
            return {"status": "no_device_access", "devices": [], "live_send_enabled": False}
        result = await discover_devices(hass, allowed_device_ids=allowed)
        if allowed is not None:
            result = {**result, "devices": [d for d in result["devices"] if d["device_id"] in allowed]}
        if await device_scope(hass, uid) != (allowed, snapshot):
            raise AccessDenied
        return result

    if action in {"sent_settings", "prepare_send"}:
        device = params["device_id"]
        snapshot = await authorize_device(hass, uid, device)
        if action == "sent_settings":
            result = hass.data[DOMAIN]["sent_settings"].get(device)
        else:
            result = await prepare_preview(hass, **params, allowed_device_ids={device})
        if await authorize_device(hass, uid, device) != snapshot:
            raise AccessDenied
        return result

    sender = hass.data[DOMAIN].get("beta_sender")
    if sender is None:
        raise BetaTestBlocked("not_configured")
    context = Context(user_id=uid)
    if action == "beta_prepare":
        # Authenticate/authorize before allocating a lifetime subscription.
        await authorize_device(hass, uid, params["device_id"])
        permit = SendPermit(owner=connection)
        connection.subscriptions[request_id] = lambda: sender.close_permit(permit, disconnected=True)
        permit.cleanup = lambda: connection.subscriptions.pop(request_id, None)
        try:
            return await sender.prepare(uid, params["device_id"], params["zone_id"],
                                        params["acknowledge_unverified"], context,
                                        source=params["source"], permit=permit)
        except BaseException:
            permit.close()
            raise
    if action == "beta_confirm":
        return await sender.confirm(uid, params["token"], params["acknowledge_supervised_test"], context, owner=connection)
    if action == "beta_cancel":
        # An active owner may discard their token even after permission loss.
        return await sender.cancel(uid, params["token"], owner=connection)
    return await sender.recover(uid, params["device_id"], params["acknowledge_physical_reset"], context)
