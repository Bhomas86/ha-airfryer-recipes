"""Reviewed public SYNC/MATCH contract; deliberately no transport function.

The controller's remaining state-check gap prevents live enablement. Request and
response validation can be completed independently without appliance writes.
"""
from dataclasses import asdict
from datetime import datetime, timezone

from .beta_send import validate_settings
from .recipe_model import CookingPhase, RecipeValidationError
from .model_profiles import TURBO_TOWER_MODEL

REVIEWED_VERSIONS = {
    "1.0.3": "75d30c800ae79eea2254e5d4f5da31ec154398e7",
    "1.0.4-beta.1": "ca92b375547c75b698e25a21f8a8734688174e47",
}


async def describe_contract(hass):
    version = None
    try:
        from homeassistant.loader import async_get_integration
        integration = await async_get_integration(hass, "airfryer_control")
        if integration.version in REVIEWED_VERSIONS:
            version = integration.version
    except Exception:
        pass  # The optional controller never prevents recipe management.
    return {"reviewed_version": version, "explicit_values": version is not None,
            "live_send_enabled": False,
            "own_guard_available": version is not None,
            "blocking_reason": "multi_confirmation_required" if version else "multi_contract_unreviewed"}


def snapshot_blockers(device, now=None):
    """Assess the current normalized snapshot, not a promise about a later refresh."""
    now = now or datetime.now(timezone.utc)
    blockers = []
    if device.get("model") != TURBO_TOWER_MODEL:
        blockers.append("model_unsupported")
    if device.get("connectivity") != "reported_online":
        blockers.append("connection_unknown")
    try:
        reported = datetime.fromisoformat(device.get("reported_at", ""))
        fresh = 0 <= (now - reported).total_seconds() <= 15
    except (ValueError, TypeError):
        fresh = False
    if not fresh or type(device.get("revision")) is not int or device["revision"] < 0:
        blockers.append("freshness_unverified")
    zones = device.get("zones")
    if (not isinstance(zones, list) or len(zones) != 2
            or any(not isinstance(z, dict) or type(z.get("zone_id")) is not int for z in zones)
            or {z["zone_id"] for z in zones} != {1, 2}):
        blockers.append("zone_report_missing")
    elif any(z.get("status") not in ("idle", "off") for z in zones):
        blockers.append("zone_not_idle")
    return blockers


def build_request(device_id, operation, phases):
    """Build immutable explicit values with all protective options fixed."""
    if not isinstance(device_id, str) or not 0 < len(device_id) <= 128 or device_id.strip() != device_id:
        raise RecipeValidationError("Invalid device ID")
    if operation not in ("sync", "match") or not isinstance(phases, dict) or set(phases) != {"1", "2"}:
        raise RecipeValidationError("Expected two explicit zone phases")
    values = {}
    for zone in ("1", "2"):
        phase = phases[zone]
        if not isinstance(phase, CookingPhase):
            raise RecipeValidationError("Invalid zone phase")
        validate_settings(phase)
        values[f"zone{zone}"] = {"programm": phase.program, "temperatur": phase.temperature_c,
                                "minuten": phase.duration_minutes}
    if operation == "match" and asdict(phases["1"]) != asdict(phases["2"]):
        raise RecipeValidationError("MATCH must use zone 1 for both zones")
    return {"service": "sync_senden" if operation == "sync" else "match_senden",
            "data": {"geraet": device_id, **values, "quelle": 1, "einmal": True,
                     "streng": True, "zuruecksetzen": False}}


def normalize_response(payload, request, operation):
    """Return only an outcome enum; never expose raw errors or infer confirmation."""
    if not isinstance(payload, dict) or operation not in ("sync", "match"):
        return "unknown"
    revision = payload.get("revision_vorher")
    if payload.get("art") != operation or type(revision) is not int or revision < 0:
        return "unknown"
    outcome, ok = payload.get("ergebnis"), payload.get("ok")
    if outcome == "abgelehnt" and ok is False:
        return "rejected"
    if outcome != "angenommen" or ok is not True:
        return "unknown"
    expected = {zone: request["data"][zone] for zone in ("zone1", "zone2")}
    # JSON equality must preserve numeric types (bool/float are not valid echoes).
    echo = payload.get("gesendet")
    if not isinstance(echo, dict) or set(echo) != set(expected):
        return "unknown"
    for zone, wanted in expected.items():
        actual = echo[zone]
        if not isinstance(actual, dict) or set(actual) != set(wanted):
            return "unknown"
        if any(type(actual[k]) is not type(v) or actual[k] != v for k, v in wanted.items()):
            return "unknown"
    return "accepted"
