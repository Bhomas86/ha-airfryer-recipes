"""Opt-in completion notices and strictly allowlisted diagnostics.

Only local HA status events are observed; no appliance queries or controls.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import logging
import re

from .const import DOMAIN, FRONTEND_VERSION
from .device_access import active_user, AccessDenied
from .recipe_model import RecipeValidationError

_LOGGER = logging.getLogger(__name__)
MAX_AGE = 90


def diagnostics(hass):
    """Construct values from constants/counts only; never copy external strings."""
    state = hass.data.get(DOMAIN, {})
    return {
        "schema_version": 1,
        "integration_version": FRONTEND_VERSION,
        "library_loaded": state.get("repository") is not None,
        "favorites_loaded": state.get("favorites") is not None,
        "permissions_available": getattr(state.get("device_access"), "available", False) is True,
        "history_available": getattr(state.get("sent_settings"), "available", False) is True,
        "notifications_available": getattr(state.get("support"), "available", False) is True,
        "notification_rule_count": len(getattr(state.get("support"), "rules", [])),
    }


def sample(state, now):
    """Accept only explicit, fresh, reported zone telemetry from the contract."""
    if state is None:
        return None
    attrs = state.attributes
    if attrs.get("gemeldet") is not True or attrs.get("verbindung") != "ok":
        return None
    revision = attrs.get("revision")
    try:
        report = datetime.fromisoformat(attrs.get("letzte_meldung", ""))
        age = (now - report).total_seconds()
    except (TypeError, ValueError):
        return None
    if type(revision) is not int or revision < 0 or not 0 <= age <= MAX_AGE:
        return None
    if state.state not in ("gart", "fertig"):
        return None
    return (state.state, report, revision)


class CompletionTracker:
    """No persisted arms, timers, replay or notification retries."""
    def __init__(self):
        self.previous = {}

    def clear(self):
        self.previous.clear()

    def observe(self, entity_id, state, now):
        current = sample(state, now)
        old = self.previous.pop(entity_id, None)
        if current is None:
            return False
        if old is not None and current[1:] == old[1:] and current[0] == old[0]:
            self.previous[entity_id] = old
            return False
        if old is not None and (current[1] <= old[1] or current[2] <= old[2]):
            return False
        if current[0] == "gart":
            self.previous[entity_id] = current
        return bool(old and old[0] == "gart" and current[0] == "fertig"
                    and 0 < (current[1] - old[1]).total_seconds() <= MAX_AGE)


def validate_rules(raw):
    if not isinstance(raw, list) or len(raw) > 20:
        raise ValueError("Invalid notification settings")
    keys = {"entity_id", "unique_id", "config_entry_id", "device_id", "target", "owner", "language"}
    for row in raw:
        if not isinstance(row, dict) or set(row) != keys:
            raise ValueError("Invalid notification rule")
        if any(not isinstance(v, str) or not 0 < len(v) <= 256 for v in row.values()):
            raise ValueError("Invalid notification value")
        if row["language"] not in ("de", "en") or not re.fullmatch(r"mobile_app_[a-z0-9_]+", row["target"]):
            raise ValueError("Invalid notification target")
    if len({r["entity_id"] for r in raw}) != len(raw):
        raise ValueError("Duplicate notification rule")
    return deepcopy(raw)


class Support:
    def __init__(self, hass, store):
        self.hass, self.store = hass, store
        self.rules = []
        self.available = False
        self.tracker = CompletionTracker()
        self.lock = asyncio.Lock()
        self.closed = False
        self.unsubscribe = None

    async def load(self):
        try:
            raw = await self.store.async_load()
            if raw is not None:
                if not isinstance(raw, dict) or set(raw) != {"schema_version", "rules"} or type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
                    raise ValueError("Unsupported notification storage")
                self.rules = validate_rules(raw["rules"])
            self.available = True
        except Exception:
            _LOGGER.warning("Notification settings unavailable; existing data preserved")
        if self.available:
            self.unsubscribe = self.hass.bus.async_listen("state_changed", self.on_event)

    def close(self):
        self.closed = True
        self.tracker.clear()
        if self.unsubscribe:
            self.unsubscribe()
            self.unsubscribe = None

    async def sources(self):
        from homeassistant.helpers import entity_registry as er
        from homeassistant.loader import async_get_integration
        try:
            integration = await async_get_integration(self.hass, "airfryer_control")
            if integration.version != "1.0.3-beta.3":
                return {}
            loaded = {e.entry_id for e in self.hass.config_entries.async_loaded_entries("airfryer_control")}
            return {e.entity_id: e for e in er.async_get(self.hass).entities.values()
                    if e.platform == "airfryer_control" and e.domain == "sensor"
                    and e.disabled_by is None and e.config_entry_id in loaded
                    and e.device_id and re.search(r"_zone[12]_status$", e.unique_id)}
        except Exception:
            # Optional adapter absence/failure must leave diagnostics and recipes usable.
            return {}

    def targets(self):
        return sorted(s for s in self.hass.services.async_services().get("notify", {})
                      if re.fullmatch(r"mobile_app_[a-z0-9_]+", s))

    async def settings(self):
        return {"available": self.available, "sources": sorted(await self.sources()),
                "targets": self.targets(), "rules": [{"entity_id": r["entity_id"], "target": r["target"]} for r in self.rules]}

    async def configure(self, connection, entity_id, target, language):
        async with self.lock:
            if self.closed or not self.available:
                raise OSError("Notification settings unavailable")
            user = await active_user(self.hass, connection.user.id)
            if not user.is_admin:
                raise AccessDenied
            sources = await self.sources()
            if target and (entity_id not in sources or target not in self.targets()):
                raise RecipeValidationError("Select a loaded zone sensor and mobile notification service")
            rules = [r for r in self.rules if r["entity_id"] != entity_id]
            if target:
                e = sources[entity_id]
                rules.append({"entity_id": entity_id, "target": target, "owner": user.id,
                              "language": language, "unique_id": e.unique_id,
                              "config_entry_id": e.config_entry_id, "device_id": e.device_id})
            rules = validate_rules(rules)
            user = await active_user(self.hass, connection.user.id)
            if not user.is_admin:
                raise AccessDenied
            self.tracker.clear()
            await self.store.async_save({"schema_version": 1, "rules": rules})
            self.rules = rules

    async def on_event(self, event):
        entity_id = event.data.get("entity_id")
        rule = next((r for r in self.rules if r["entity_id"] == entity_id), None)
        if self.closed or getattr(self.hass, "is_stopping", False) or not self.available or not rule:
            return
        # Consume before the first await, so concurrent duplicate events cannot send twice.
        completed = self.tracker.observe(entity_id, event.data.get("new_state"), datetime.now(timezone.utc))
        if not completed:
            return
        try:
            async with self.lock:
                user = await active_user(self.hass, rule["owner"])
                sources = await self.sources()
                source = sources.get(entity_id)
                if (self.closed or getattr(self.hass, "is_stopping", False) or rule not in self.rules or not user.is_admin or not source
                        or any(getattr(source, key) != rule[key] for key in ("unique_id", "device_id", "config_entry_id"))
                        or rule["target"] not in self.targets()):
                    return
                # A delayed event must still match the current state, not a newer cooking cycle.
                if self.hass.states.get(entity_id) is not event.data.get("new_state"):
                    return
                if sample(event.data.get("new_state"), datetime.now(timezone.utc)) is None:
                    return
                user = await active_user(self.hass, rule["owner"])
                if not user.is_admin or self.closed or getattr(self.hass, "is_stopping", False):
                    return
                from homeassistant.core import Context
                zone = "1" if source.unique_id.endswith("_zone1_status") else "2"
                message = f"Fach {zone} meldet: fertig." if rule["language"] == "de" else f"Zone {zone} reports: finished."
                await self.hass.services.async_call("notify", rule["target"],
                    {"title": "Airfryer Recipes", "message": message}, blocking=True,
                    context=Context(user_id=user.id))
        except Exception:
            # Never repeat a send with an unknown delivery outcome; no private data in logs.
            _LOGGER.warning("Completion notification failed or was denied; no retry")


async def async_setup_support(hass):
    from .verified_storage import VerifiedStore
    support = Support(hass, VerifiedStore(hass, 1, f"{DOMAIN}.notifications"))
    await support.load()
    hass.data[DOMAIN]["support"] = support
