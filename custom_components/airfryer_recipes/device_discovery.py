"""Read existing Airfryer Control state and its public capability service.

Registry/runtime inspection identifies only actually reported zones. The
``airfryer_control.faehigkeiten`` service is read-only and supplies program
metadata from the optional adapter. Neither source can authorize transmission.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

UPSTREAM_DOMAIN = "airfryer_control"
CAPABILITIES_SERVICE = "faehigkeiten"
STATUS_MAP = {
    "aus": "off", "bereit": "idle", "wartet_auf_start": "ready",
    "vorheizen": "preheating", "vorgeheizt": "preheated", "gart": "cooking",
    "wartet_auf_sync": "holding", "pausiert": "paused",
    "schublade_offen": "drawer_open", "fertig": "finished",
    "warmhalten": "keeping_warm", "offline": "offline",
}


def _bounded_int(value: Any, minimum: int, maximum: int) -> int | None:
    """Return an ordinary integer inside a public, defensive bound."""
    return value if type(value) is int and minimum <= value <= maximum else None


def _range(value: Any, minimum: int, maximum: int) -> dict[str, int] | None:
    """Normalize one two-value upstream range without clamping it."""
    if not isinstance(value, list) or len(value) != 2:
        return None
    low = _bounded_int(value[0], minimum, maximum)
    high = _bounded_int(value[1], minimum, maximum)
    if low is None or high is None or low > high:
        return None
    return {"min": low, "max": high}


def _reported_at(value: Any) -> str | None:
    """Allow only a short parseable ISO timestamp through the API."""
    if not isinstance(value, str) or len(value) > 64:
        return None
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return None
    return value


def normalize_capabilities(payload: Any) -> dict[str, Any] | None:
    """Allowlist the beta capability response and discard malformed fields."""
    if not isinstance(payload, dict) or not isinstance(payload.get("programme"), dict):
        return None
    programs = []
    for program_id, raw in payload["programme"].items():
        if (
            not isinstance(program_id, str)
            or not program_id
            or program_id != program_id.strip()
            or len(program_id) > 64
            or not isinstance(raw, dict)
        ):
            continue
        temperature = _range(raw.get("temperatur"), 0, 400)
        duration = _range(raw.get("minuten"), 1, 5000)
        suggestion = raw.get("vorschlag")
        suggested_temperature = (
            _bounded_int(suggestion.get("temperatur"), 0, 400)
            if isinstance(suggestion, dict) else None
        )
        suggested_duration = (
            _bounded_int(suggestion.get("minuten"), 1, 5000)
            if isinstance(suggestion, dict) else None
        )
        if temperature is None or duration is None:
            continue
        limits = {
            "vesync_app": "confirmed",
            "geschaetzt": "estimated",
        }.get(raw.get("grenzen"), "unknown")
        send = {
            "bestaetigt": "confirmed",
            "ungeprueft": "unverified",
        }.get(raw.get("senden"), "unknown")
        programs.append({
            "id": program_id,
            "temperature_c": temperature,
            "duration_minutes": duration,
            "suggested": {
                "temperature_c": suggested_temperature,
                "duration_minutes": suggested_duration,
            },
            "limits_status": limits,
            "send_status": send,
        })
    revision = _bounded_int(payload.get("revision"), 0, 2**63 - 1)
    return {
        "programs": programs,
        "model_known": payload.get("modell_bekannt") is True,
        "reported_at": _reported_at(payload.get("letzte_meldung")),
        "revision": revision,
        "connection": payload.get("verbindung")
        if payload.get("verbindung") in {"ok", "offline", "fehler"} else "unknown",
    }


def describe_devices(devices: Any, entries: Any) -> list[dict[str, Any]]:
    """Join HA registry IDs to loaded runtime data; expose only allowlisted fields.

    Account IDs, cloud device IDs, raw telemetry and exception strings never
    leave the adapter. A cached 'idle' value is descriptive, not send permission.
    Ambiguous ownership and malformed runtime data produce no usable device.
    """
    result = []
    for device in devices:
        identities = [value for domain, value in device.identifiers if domain == UPSTREAM_DOMAIN]
        if len(identities) != 1 or device.disabled_by is not None:
            continue
        matches = []
        for entry in entries:
            if entry.entry_id not in device.config_entries:
                continue
            runtime = getattr(entry, "runtime_data", None)
            fryers = getattr(runtime, "fryers", {})
            if isinstance(fryers, dict) and identities[0] in fryers:
                matches.append(fryers[identities[0]])
        if len(matches) != 1:
            continue
        fryer = matches[0]
        online = getattr(fryer, "online", None)
        last_error = getattr(fryer, "last_error", None)
        state = getattr(fryer, "state", None)
        reported_zones = getattr(state, "zones", {})
        if not isinstance(reported_zones, dict):
            reported_zones = {}
        zones = []
        for zone_id, zone in reported_zones.items():
            if type(zone_id) is not int or zone_id not in (1, 2, 3):
                continue
            raw_status = getattr(zone, "status", None)
            status = STATUS_MAP.get(raw_status, "unknown") if isinstance(raw_status, str) else "unknown"
            if online is False:
                status = "offline"
            elif online is not True or last_error:
                status = "unknown"
            zones.append({"zone_id": zone_id, "status": status})
        result.append({
            "device_id": device.id,
            "name": device.name_by_user or device.name or "Airfryer",
            "model": device.model,
            "adapter": UPSTREAM_DOMAIN,
            "connectivity": "offline" if online is False else (
                "unknown" if online is not True or last_error else "reported_online"
            ),
            "freshness": "unverified",
            "reported_at": None,
            "zones": sorted(zones, key=lambda zone: zone["zone_id"]),
            "programs": [],
            "capabilities": {"send_settings": False, "update_running": False,
                             "sync_finish": False, "match_zones": False},
            "send_block_reason": "upstream_contract_unverified",
        })
    return sorted(result, key=lambda device: device["device_id"])


async def discover_devices(hass: Any) -> dict[str, Any]:
    """Read reported zones and enrich them through the public read-only service."""
    from homeassistant.helpers import device_registry as dr

    try:
        entries = list(hass.config_entries.async_loaded_entries(UPSTREAM_DOMAIN))
        registry = dr.async_get(hass)
        devices = describe_devices(registry.devices.values(), entries)
    except (AttributeError, KeyError, TypeError, ValueError):
        # An incompatible optional adapter must not break recipe management.
        return {"status": "adapter_incompatible", "devices": [], "live_send_enabled": False}
    if not entries:
        return {"status": "adapter_missing", "devices": [], "live_send_enabled": False}
    try:
        service_available = hass.services.has_service(UPSTREAM_DOMAIN, CAPABILITIES_SERVICE)
    except (AttributeError, TypeError, ValueError):
        service_available = False
    if not service_available:
        return {"status": "adapter_outdated", "devices": devices, "live_send_enabled": False}

    capability_failures = 0
    for device in devices:
        try:
            payload = await hass.services.async_call(
                UPSTREAM_DOMAIN,
                CAPABILITIES_SERVICE,
                {"geraet": device["device_id"]},
                blocking=True,
                return_response=True,
            )
        except Exception:  # Optional adapter failures must not break recipe management.
            capability_failures += 1
            continue
        capabilities = normalize_capabilities(payload)
        if capabilities is None:
            capability_failures += 1
            continue
        device.update(capabilities)
        connection = capabilities["connection"]
        device["connectivity"] = {
            "ok": "reported_online", "offline": "offline",
        }.get(connection, "unknown")
        device["freshness"] = "reported" if capabilities["reported_at"] else "unverified"
        device["send_block_reason"] = "upstream_contract_beta"

    return {
        "status": "adapter_capabilities_error" if devices and capability_failures == len(devices)
        else "adapter_beta",
        "devices": devices,
        "live_send_enabled": False,
    }
