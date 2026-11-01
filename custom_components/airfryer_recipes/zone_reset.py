"""Resolve reviewed per-zone switch controls through HA registries."""
from typing import Any
from .beta_send import UPSTREAM, require


def zone_switch(hass: Any, device_id: str, entry_id: str, zone: int) -> str:
    from homeassistant.helpers import device_registry as dr, entity_registry as er

    require(type(zone) is int and zone in (1, 2), "reset_unavailable")
    device = dr.async_get(hass).async_get(device_id)
    require(device is not None and device.disabled_by is None, "reset_unavailable")
    require(entry_id in device.config_entries, "reset_unavailable")
    identities = [value for domain, value in device.identifiers if domain == UPSTREAM]
    require(len(identities) == 1, "reset_unavailable")
    registry = er.async_get(hass)
    matches = [e.entity_id for e in er.async_entries_for_device(registry, device_id)
               if e.platform == UPSTREAM and e.config_entry_id == entry_id
               and e.disabled_by is None and e.entity_id.startswith("switch.")
               and e.unique_id == f"{identities[0]}_zone{zone}_gart"]
    require(len(matches) == 1, "reset_unavailable")
    state = hass.states.get(matches[0])
    require(state is not None and state.state in ("on", "off"), "reset_unavailable")
    require(hass.services.has_service("switch", "turn_off"), "reset_unavailable")
    return matches[0]
