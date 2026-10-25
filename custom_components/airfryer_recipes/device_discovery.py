"""Read existing Airfryer Control state without refreshing or controlling it.

Upstream 5a3c530 has no per-device successful-report timestamp. A loaded
coordinator or an available HA entity does not prove fresh device telemetry.
This module deliberately cannot authorize transmission.
"""

from __future__ import annotations

from typing import Any

UPSTREAM_DOMAIN = "airfryer_control"
STATUS_MAP = {
    "aus": "off", "bereit": "idle", "wartet_auf_start": "ready",
    "vorheizen": "preheating", "vorgeheizt": "preheated", "gart": "cooking",
    "wartet_auf_sync": "holding", "pausiert": "paused",
    "schublade_offen": "drawer_open", "fertig": "finished",
    "warmhalten": "keeping_warm", "offline": "offline",
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


def discover_devices(hass: Any) -> dict[str, Any]:
    """Read registries and loaded entries only; never request an upstream refresh."""
    from homeassistant.helpers import device_registry as dr

    try:
        entries = list(hass.config_entries.async_loaded_entries(UPSTREAM_DOMAIN))
        registry = dr.async_get(hass)
        devices = describe_devices(registry.devices.values(), entries)
    except (AttributeError, KeyError, TypeError, ValueError):
        # An incompatible optional adapter must not break recipe management.
        return {"status": "adapter_incompatible", "devices": [], "live_send_enabled": False}
    return {
        "status": "adapter_loaded" if entries else "adapter_missing",
        "devices": devices,
        "live_send_enabled": False,
    }
