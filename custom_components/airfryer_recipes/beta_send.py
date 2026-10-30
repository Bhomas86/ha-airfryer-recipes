"""Supervised, single-shot commissioning; never used by the dry-run API.

Only the reviewed public Airfryer Control service is called. This beta test is
not a compatibility approval: the administrator must observe the appliance.
"""

from __future__ import annotations

from dataclasses import dataclass
import asyncio
from datetime import datetime, timezone
import secrets
import time
from typing import Any, Callable

from .const import DOMAIN
from .device_discovery import normalize_capabilities

UPSTREAM = "airfryer_control"
MODEL = "CAF-DC111S-AEU"
VERSION = "1.0.2-beta.1"
TTL_SECONDS = 15
MAX_REPORT_AGE = 15
TEST_SETTINGS = {"program": "airfry", "temperature_c": 170, "duration_minutes": 1}


class BetaTestBlocked(ValueError):
    """A public, allowlisted reason; never contains upstream exceptions."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise BetaTestBlocked(reason)


@dataclass(frozen=True)
class Target:
    name: str
    fingerprint: tuple
    unchanged: Callable[[], bool] = lambda: True


async def read_target(
    hass: Any, device_id: str, zone_id: int, *, refresh: bool = False, context: Any = None,
) -> Target:
    """Read a coherent idle snapshot; optionally request a read-only refresh.

    The report timestamp is part of the confirmation binding. Even an identical
    new report invalidates a prepared test, as does a different adapter instance.
    """
    from homeassistant.helpers import device_registry as dr
    from homeassistant.loader import async_get_integration

    require(isinstance(device_id, str) and 0 < len(device_id) <= 128, "target")
    require(type(zone_id) is int and zone_id in (1, 2), "target")
    integration = await async_get_integration(hass, UPSTREAM)
    require(integration.version == VERSION, "adapter_version")
    require(hass.services.has_service(UPSTREAM, "programm_senden"), "adapter_version")
    device = dr.async_get(hass).async_get(device_id)
    require(device is not None and device.disabled_by is None, "target")
    require(device.model == MODEL, "model")
    identities = [v for d, v in device.identifiers if d == UPSTREAM]
    require(len(identities) == 1, "target")
    matches = []
    for entry in hass.config_entries.async_loaded_entries(UPSTREAM):
        runtime = getattr(entry, "runtime_data", None)
        fryers = getattr(runtime, "fryers", {})
        if entry.entry_id in device.config_entries and isinstance(fryers, dict):
            if identities[0] in fryers:
                matches.append((entry, runtime, fryers[identities[0]]))
    require(len(matches) == 1, "target")
    entry, runtime, fryer = matches[0]
    if refresh:
        from homeassistant.helpers import entity_registry as er

        require(context is not None, "unauthorized")
        require(hass.services.has_service("homeassistant", "update_entity"), "refresh_unavailable")
        registry = er.async_get(hass)
        # All sensors of the reviewed upstream use CoordinatorEntity. Updating
        # one loaded sensor requests a coordinator read, never a control action.
        sensors = sorted(
            entity.entity_id
            for entity in er.async_entries_for_device(registry, device_id)
            if entity.platform == UPSTREAM and entity.config_entry_id == entry.entry_id
            and entity.disabled_by is None and entity.entity_id.startswith("sensor.")
            and hass.states.get(entity.entity_id) is not None
        )
        require(bool(sensors), "refresh_unavailable")
        before = getattr(fryer, "last_report", None)
        requested_at = datetime.now(timezone.utc)
        try:
            async with asyncio.timeout(20):
                await hass.services.async_call(
                    "homeassistant", "update_entity", {"entity_id": [sensors[0]]},
                    blocking=True, context=context,
                )
        except Exception:
            raise BetaTestBlocked("refresh_failed") from None
        after = getattr(fryer, "last_report", None)
        require(isinstance(after, datetime) and after.tzinfo is not None, "refresh_failed")
        require(after >= requested_at, "refresh_failed")
        if isinstance(before, datetime) and before.tzinfo is not None:
            require(after > before, "refresh_failed")
    payload = await hass.services.async_call(
        UPSTREAM, "faehigkeiten", {"geraet": device_id},
        blocking=True, return_response=True,
    )
    caps = normalize_capabilities(payload)
    require(caps is not None, "capabilities")
    require(getattr(fryer, "model", None) == MODEL, "model")
    require(fryer.online is True and not fryer.last_error and caps["connection"] == "ok", "connection")
    reported = getattr(fryer, "last_report", None)
    require(isinstance(reported, datetime) and reported.tzinfo is not None, "freshness")
    require(0 <= (datetime.now(timezone.utc) - reported).total_seconds() <= MAX_REPORT_AGE, "freshness")
    require(caps["reported_at"] == reported.isoformat(), "freshness")
    revision = getattr(fryer, "revision", None)
    require(type(revision) is int and revision >= 0 and caps["revision"] == revision, "freshness")
    state = fryer.state
    require(type(state.sync_type) is int and state.sync_type == 0, "zones")
    require(state.temp_unit == "celsius", "zones")
    require(state.status in ("aus", "bereit") and state.active is False, "zones")
    require(set(state.zones) == {1, 2} and all(type(z) is int for z in state.zones), "zones")
    statuses = tuple((z, state.zones[z].status) for z in (1, 2))
    require(all(s in ("aus", "bereit") and state.zones[z].active is False for z, s in statuses), "zones")
    program = next((p for p in caps["programs"] if p["id"] == "airfry"), None)
    require(program is not None and program["limits_status"] in ("confirmed", "estimated"), "capabilities")
    require(program["temperature_c"]["min"] <= 170 <= program["temperature_c"]["max"]
            and program["duration_minutes"]["min"] <= 1 <= program["duration_minutes"]["max"], "capabilities")
    programs = tuple((p["id"], p["temperature_c"]["min"], p["temperature_c"]["max"],
                      p["duration_minutes"]["min"], p["duration_minutes"]["max"],
                      p["limits_status"], p["send_status"]) for p in caps["programs"])

    def unchanged() -> bool:
        current = dr.async_get(hass).async_get(device_id)
        return (
            current is device and current.disabled_by is None and current.model == MODEL
            and entry.runtime_data is runtime and runtime.fryers.get(identities[0]) is fryer
            and entry in hass.config_entries.async_loaded_entries(UPSTREAM)
            and fryer.state is state and fryer.online is True and not fryer.last_error
            and fryer.last_report == reported and fryer.revision == revision
            and state.status in ("aus", "bereit") and state.active is False
            and type(state.sync_type) is int and state.sync_type == 0
            and state.temp_unit == "celsius" and set(state.zones) == {1, 2}
            and tuple((z, state.zones[z].status) for z in (1, 2)) == statuses
            and all(state.zones[z].active is False for z in (1, 2))
            and 0 <= (datetime.now(timezone.utc) - reported).total_seconds() <= MAX_REPORT_AGE
        )

    return Target(device.name_by_user or device.name or "Airfryer",
                  (entry.entry_id, id(runtime), id(fryer), reported.isoformat(), revision,
                   statuses, programs, MODEL, VERSION), unchanged)


@dataclass(frozen=True)
class Confirmation:
    user_id: str
    device_id: str
    zone_id: int
    target: Target
    expires: float


class BetaSender:
    """Volatile confirmations and fail-fast per-device locks, never a queue."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.pending: dict[str, Confirmation] = {}
        state = hass.data[DOMAIN]
        # Survive integration reload, including old service calls still in flight.
        self.busy: set[str] = state.setdefault("beta_busy", set())
        self.uncertain: set[str] = state.setdefault("beta_uncertain", set())
        self.closed = False

    def close(self) -> None:
        self.closed = True
        self.pending.clear()

    async def _authorized(self, user_id: str) -> None:
        user = await self.hass.auth.async_get_user(user_id)
        require(user is not None and user.is_admin and user.is_active, "unauthorized")
        require(not self.closed and self.hass.data.get(DOMAIN, {}).get("beta_sender") is self,
                "not_configured")

    async def _read(self, device_id: str, zone_id: int, **kwargs: Any) -> Target:
        try:
            return await read_target(self.hass, device_id, zone_id, **kwargs)
        except BetaTestBlocked:
            raise
        except Exception:
            raise BetaTestBlocked("adapter_data") from None

    async def prepare(
        self, user_id: str, device_id: str, zone_id: int, acknowledge: bool, context: Any,
    ) -> dict:
        require(acknowledge is True, "acknowledgement")
        await self._authorized(user_id)
        require(device_id not in self.busy, "busy")
        require(device_id not in self.uncertain, "outcome_unknown")
        self.busy.add(device_id)
        try:
            # Starting a fresh preparation invalidates older confirmations for
            # this user even when the refresh subsequently fails.
            self.pending = {k: v for k, v in self.pending.items() if v.user_id != user_id}
            target = await self._read(device_id, zone_id, refresh=True, context=context)
            await self._authorized(user_id)
            now = time.monotonic()
            self.pending = {k: v for k, v in self.pending.items() if v.expires > now}
            require(len(self.pending) < 32, "busy")
            token = secrets.token_urlsafe(32)
            self.pending[token] = Confirmation(user_id, device_id, zone_id, target, now + TTL_SECONDS)
            return {"mode": "supervised_beta_test", "token": token, "expires_seconds": TTL_SECONDS,
                    "device_id": device_id, "device_name": target.name, "zone_id": zone_id,
                    "settings": dict(TEST_SETTINGS), "transmitted": False,
                    "compatibility_verified": False}
        finally:
            self.busy.discard(device_id)

    async def confirm(self, user_id: str, token: str, acknowledge: bool, context: Any) -> dict:
        require(acknowledge is True, "acknowledgement")
        await self._authorized(user_id)
        require(isinstance(token, str) and 0 < len(token) <= 128, "confirmation")
        prepared = self.pending.get(token)
        require(prepared is not None and prepared.user_id == user_id, "confirmation")
        self.pending.pop(token)  # Consume before any await, including failed validation.
        require(time.monotonic() < prepared.expires, "confirmation")
        device_id = prepared.device_id
        require(device_id not in self.busy, "busy")
        require(device_id not in self.uncertain, "outcome_unknown")
        self.busy.add(device_id)
        try:
            target = await self._read(device_id, prepared.zone_id)
            require(target.fingerprint == prepared.target.fingerprint, "state_changed")
            await self._authorized(user_id)
            require(time.monotonic() < prepared.expires, "confirmation")
            try:
                unchanged = target.unchanged()
            except Exception:
                unchanged = False
            require(unchanged, "state_changed")
            # This is the only control call. Never invoke raw, SYNC/MATCH or a
            # start-capable service, and never trust upstream cached confirmation.
            try:
                self.uncertain.add(device_id)
                result = await self.hass.services.async_call(
                    UPSTREAM, "programm_senden",
                    {"geraet": device_id, "zone": prepared.zone_id, "programm": "airfry",
                     "temperatur": 170, "minuten": 1, "variante": "multi_app",
                     "einmal": True, "streng": True, "bestaetigen": False},
                    blocking=True, return_response=True, context=context,
                )
            except asyncio.CancelledError:
                raise  # Uncertain latch remains set; never permit a replay.
            except Exception:
                return self._result("unknown")
            # Only accept a complete, exact response contract. Nothing from the
            # upstream response (including error strings or raw data) is exposed.
            exact = {"programm": "airfry", "temperatur": 170, "minuten": 1, "zone": prepared.zone_id}
            if (isinstance(result, dict) and result.get("ok") is True
                    and result.get("ergebnis") == "angenommen"
                    and type(result.get("versuche")) is int and result["versuche"] == 1
                    and result.get("variante") == "multi_app" and result.get("gesendet") == exact
                    and all(type(result["gesendet"][k]) is type(v) for k, v in exact.items())):
                self.uncertain.discard(device_id)
                return self._result("accepted")
            return self._result("unknown")
        finally:
            self.busy.discard(device_id)

    @staticmethod
    def _result(outcome: str) -> dict:
        return {"mode": "supervised_beta_test", "attempted": True, "outcome": outcome,
                "accepted_by_adapter": outcome == "accepted", "confirmed_on_device": False,
                "compatibility_verified": False, "automatic_retry": False}
