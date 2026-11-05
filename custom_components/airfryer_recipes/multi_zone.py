"""SYNC/MATCH planning only: no upstream control contract is safe yet."""
from dataclasses import asdict

from .const import DOMAIN
from .beta_send import validate_settings
from .command_preview import PreviewTargetNotFound
from .device_discovery import discover_devices
from .device_access import authorize_device, AccessDenied
from .model_profiles import TURBO_TOWER_MODEL
from .recipe_model import CookingPhase, RecipeValidationError


async def preview(hass, connection, device_id, mode, sources):
    if mode not in ("sync", "match") or not isinstance(sources, dict):
        raise RecipeValidationError("Choose SYNC or MATCH")
    expected = {"1", "2"} if mode == "sync" else {"1"}
    if set(sources) != expected:
        raise RecipeValidationError("Select explicit settings for every required zone")
    uid = connection.user.id
    permission = await authorize_device(hass, uid, device_id)
    phases = {}
    for zone, source in sources.items():
        if not isinstance(source, dict):
            raise RecipeValidationError("Invalid settings source")
        if set(source) == {"recipe_id"} and isinstance(source["recipe_id"], str):
            recipe = await hass.data[DOMAIN]["repository"].async_get(source["recipe_id"])
            if len(recipe.phases) != 1:
                raise RecipeValidationError("Choose a single-phase recipe")
            phase = recipe.phases[0]
        elif set(source) == {"settings"} and isinstance(source["settings"], dict) and set(source["settings"]) == {"program", "temperature_c", "duration_minutes"}:
            phase = CookingPhase(**source["settings"])
            if phase.program != source["settings"]["program"]:
                raise RecipeValidationError("Invalid program")
        else:
            raise RecipeValidationError("Choose recipe or manual settings")
        validate_settings(phase)
        phases[zone] = phase
    if mode == "match":
        phases["2"] = phases["1"]
    discovery = await discover_devices(hass, allowed_device_ids={device_id})
    device = next((d for d in discovery["devices"] if d["device_id"] == device_id), None)
    if device is None or {z["zone_id"] for z in device["zones"]} != {1, 2}:
        raise PreviewTargetNotFound
    reasons = ["multi_contract_unsafe", "freshness_unverified", "multi_device_acceptance_pending"]
    if device.get("model") != TURBO_TOWER_MODEL:
        reasons.append("model_unsupported")
    if device.get("connectivity") != "reported_online":
        reasons.append("connection_unknown")
    if any(z["status"] not in ("idle", "off") for z in device["zones"]):
        reasons.append("zone_not_idle")
    for phase in phases.values():
        program = next((p for p in device.get("programs", []) if p.get("id") == phase.program), None)
        if program is None:
            raise RecipeValidationError("Program is not reported by this device")
        for key, value in (("temperature_c", phase.temperature_c), ("duration_minutes", phase.duration_minutes)):
            limits = program.get(key)
            if not isinstance(limits, dict) or not limits["min"] <= value <= limits["max"]:
                raise RecipeValidationError("Settings outside reported bounds")
    if await authorize_device(hass, uid, device_id) != permission:
        raise AccessDenied
    longest = max(p.duration_minutes for p in phases.values())
    return {"mode": "dry_run", "operation": mode, "transmitted": False,
            "live_send_enabled": False, "blocking_reasons": reasons,
            "zones": [{"zone_id": int(z), "settings": asdict(p),
                       "planned_delay_minutes": longest - p.duration_minutes if mode == "sync" else 0}
                      for z, p in sorted(phases.items())]}
