"""Server-enforced dry-run preview; deliberately has no device control interface.

This is the first coordinator stage, not a live command coordinator. A client
cannot opt out of dry run. Discovery data cannot grant transmission permission.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .device_discovery import discover_devices
from .recipe_model import CookingPhase, RecipeValidationError


class PreviewTargetNotFound(ValueError):
    """The device or actually reported zone is no longer available."""


def prepare_preview(
    hass: Any, *, device_id: str, zone_id: int, settings: dict[str, Any]
) -> dict[str, Any]:
    """Validate exact desired settings and read the target again on every request.

    No settings are clamped, persisted, queued, or transmitted. Limits and
    cooking programs cannot be verified against the current upstream contract.
    Only the device-independent recipe bounds are validated here.
    """
    if not isinstance(device_id, str) or not device_id or len(device_id) > 128:
        raise RecipeValidationError("Invalid device ID")
    if type(zone_id) is not int or zone_id not in (1, 2, 3):
        raise RecipeValidationError("Invalid zone ID")
    if not isinstance(settings, dict) or set(settings) != {
        "program", "temperature_c", "duration_minutes"
    }:
        raise RecipeValidationError("Expected program, temperature_c and duration_minutes")
    phase = CookingPhase(**settings)
    if phase.program != settings["program"]:
        raise RecipeValidationError("Program must not contain surrounding whitespace")
    discovery = discover_devices(hass)
    device = next((item for item in discovery["devices"] if item["device_id"] == device_id), None)
    if device is None:
        raise PreviewTargetNotFound
    zone = next((item for item in device["zones"] if item["zone_id"] == zone_id), None)
    if zone is None:
        raise PreviewTargetNotFound

    reasons = ["upstream_contract_unverified", "freshness_unverified", "program_limits_unverified"]
    if device["connectivity"] != "reported_online":
        reasons.append("device_offline" if device["connectivity"] == "offline" else "connection_unknown")
    if zone["status"] not in ("idle", "off", "ready", "finished"):
        reasons.append("zone_not_idle")
    return {
        "mode": "dry_run",
        "live_send_enabled": False,
        "transmitted": False,
        "accepted_by_adapter": False,
        "confirmed_on_device": False,
        "device_id": device_id,
        "zone_id": zone_id,
        "settings": asdict(phase),
        "zone_status": zone["status"],
        "blocking_reasons": reasons,
    }
