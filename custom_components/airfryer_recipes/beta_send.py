"""Supervised, single-shot commissioning; never used by the dry-run API.

Only the reviewed public Airfryer Control service is called. This beta test is
not a compatibility approval: the administrator must observe the appliance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import asyncio
from datetime import datetime, timezone
import secrets
import time
from typing import Any, Callable

from .const import DOMAIN
from .device_discovery import normalize_capabilities
from .recipe_model import CookingPhase, Recipe
from .recipe_repository import RecipeNotFoundError

UPSTREAM = "airfryer_control"
MODEL = "CAF-DC111S-AEU"
VERSION = "1.0.2-beta.1"
TTL_SECONDS = 15
MAX_REPORT_AGE = 15
MODE_NAMES = {"airfry": "airfry", "roast": "roast", "bake": "bake", "grill": "grill", "reheat": "reheat", "dry": "dry"}

TEST_SETTINGS = {"program": "airfry", "temperature_c": 170, "duration_minutes": 1}
# Reviewed upstream contract bounds, NOT verified CAF-DC111S-AEU capabilities.
# Recipe schema v1 caps duration at 1440 minutes, including manual beta input.
REVIEWED_PROGRAM_LIMITS = {
    "airfry": (120, 205, 60), "roast": (120, 205, 240),
    "bake": (80, 205, 240), "grill": (205, 240, 30),
    "reheat": (40, 205, 60), "dry": (34, 95, 1440),
}


def validate_settings(phase: CookingPhase) -> None:
    """Bound supervised commissioning; these are not verified model limits."""
    require(phase.program in REVIEWED_PROGRAM_LIMITS, "program_unsupported")
    low, high, minutes = REVIEWED_PROGRAM_LIMITS[phase.program]
    require(low <= phase.temperature_c <= high and 1 <= phase.duration_minutes <= minutes,
            "test_range")


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
    settings: CookingPhase | None = None, prepared_zones: dict[int, CookingPhase] | None = None,
    wait_for_report: bool = False,
) -> Target:
    """Read a coherent idle snapshot; optionally request a read-only refresh.

    The report timestamp is part of the confirmation binding. Even an identical
    new report invalidates a prepared test, as does a different adapter instance.
    """
    from homeassistant.helpers import device_registry as dr
    from homeassistant.loader import async_get_integration

    phase = settings or CookingPhase(**TEST_SETTINGS)
    validate_settings(phase)
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
                if wait_for_report:
                    # HA may debounce the public refresh. Wait only for reads;
                    # never repeat a control command or fabricate freshness.
                    while True:
                        current = getattr(fryer, "last_report", None)
                        if (isinstance(current, datetime) and current.tzinfo is not None
                                and current >= requested_at
                                and (not isinstance(before, datetime) or before.tzinfo is None or current > before)):
                            break
                        await asyncio.sleep(0.25)
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
    expected = dict(prepared_zones or {})
    state = fryer.state
    def safe_zones() -> bool:
        if set(state.zones) != {1, 2} or any(type(z) is not int for z in state.zones):
            return False
        for z, item in state.zones.items():
            if item.active is not False:
                return False
            if z in expected:
                wanted = expected[z]
                if not (item.status == "wartet_auf_start" and isinstance(item.mode, str)
                        and item.mode.lower() == MODE_NAMES[wanted.program]
                        and item.set_temp == wanted.temperature_c
                        and item.set_time_s == wanted.duration_minutes * 60):
                    return False
            elif item.status not in ("aus", "bereit"):
                return False
        return True
    safe_statuses = ("aus", "bereit", "wartet_auf_start") if expected else ("aus", "bereit")
    require(type(state.sync_type) is int and state.sync_type == 0, "zones")
    require(state.temp_unit == "celsius", "zones")
    require(state.status in safe_statuses and state.active is False, "zones")
    require(set(state.zones) == {1, 2} and all(type(z) is int for z in state.zones), "zones")
    statuses = tuple((z, state.zones[z].status) for z in (1, 2))
    require(safe_zones(), "zones")
    program = next((p for p in caps["programs"] if p["id"] == phase.program), None)
    require(program is not None and program["limits_status"] in ("confirmed", "estimated")
            and program["send_status"] in ("confirmed", "unverified"), "capabilities")
    require(program["temperature_c"]["min"] <= phase.temperature_c <= program["temperature_c"]["max"]
            and program["duration_minutes"]["min"] <= phase.duration_minutes <= program["duration_minutes"]["max"], "capabilities")
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
            and state.status in safe_statuses and state.active is False
            and type(state.sync_type) is int and state.sync_type == 0
            and state.temp_unit == "celsius" and set(state.zones) == {1, 2}
            and tuple((z, state.zones[z].status) for z in (1, 2)) == statuses
            and safe_zones()
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
    phase: CookingPhase
    recipe: Recipe | None
    repository: Any
    variable: bool


class BetaSender:
    """Volatile confirmations and fail-fast per-device locks, never a queue."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.pending: dict[str, Confirmation] = {}
        state = hass.data[DOMAIN]
        # Survive integration reload, including old service calls still in flight.
        self.busy: set[str] = state.setdefault("beta_busy", set())
        self.uncertain: set[str] = state.setdefault("beta_uncertain", set())
        self.batch_devices: dict[str, str] = {}
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
        *, source: dict | None = None,
    ) -> dict:
        require(acknowledge is True, "acknowledgement")
        await self._authorized(user_id)
        require(device_id not in self.busy and device_id not in self.batch_devices, "busy")
        require(device_id not in self.uncertain, "outcome_unknown")
        self.busy.add(device_id)
        try:
            # Starting a fresh preparation invalidates older confirmations for
            # this user even when the refresh subsequently fails.
            self.pending = {k: v for k, v in self.pending.items() if v.user_id != user_id}
            recipe, repository = None, None
            phase = CookingPhase(**TEST_SETTINGS)
            if source is not None:
                require(isinstance(source, dict), "source")
                if set(source) == {"recipe_id"}:
                    recipe_id = source["recipe_id"]
                    require(isinstance(recipe_id, str) and 0 < len(recipe_id) <= 128, "source")
                    repository = self.hass.data[DOMAIN]["repository"]
                    try:
                        recipe = await repository.async_get(recipe_id)
                    except RecipeNotFoundError:
                        raise BetaTestBlocked("recipe_changed") from None
                    require(len(recipe.phases) == 1, "source")
                    phase = recipe.phases[0]
                else:
                    require(set(source) == {"settings"} and isinstance(source["settings"], dict), "source")
                    raw = source["settings"]
                    require(set(raw) == {"program", "temperature_c", "duration_minutes"}, "source")
                    phase = CookingPhase(**raw)
                    require(phase.program == raw["program"], "source")
                validate_settings(phase)
            await self._authorized(user_id)
            extra = {"settings": phase} if source is not None else {}
            target = await self._read(device_id, zone_id, refresh=True, context=context, **extra)
            await self._authorized(user_id)
            if recipe is not None:
                require(repository.matches_snapshot(recipe), "recipe_changed")
            now = time.monotonic()
            self.pending = {k: v for k, v in self.pending.items() if v.expires > now}
            require(len(self.pending) < 32, "busy")
            token = secrets.token_urlsafe(32)
            self.pending[token] = Confirmation(user_id, device_id, zone_id, target, now + TTL_SECONDS,
                                               phase, recipe, repository, source is not None)
            return {"mode": "supervised_beta_test", "token": token, "expires_seconds": TTL_SECONDS,
                    "device_id": device_id, "device_name": target.name, "zone_id": zone_id,
                    "settings": asdict(phase), "recipe_name": recipe.name if recipe else None,
                    "transmitted": False,
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
        require(device_id not in self.busy and device_id not in self.batch_devices, "busy")
        require(device_id not in self.uncertain, "outcome_unknown")
        self.busy.add(device_id)
        try:
            extra = {"settings": prepared.phase} if prepared.variable else {}
            target = await self._read(device_id, prepared.zone_id, **extra)
            require(target.fingerprint == prepared.target.fingerprint, "state_changed")
            await self._authorized(user_id)
            require(time.monotonic() < prepared.expires, "confirmation")
            if prepared.recipe is not None:
                require(self.hass.data[DOMAIN].get("repository") is prepared.repository
                        and prepared.repository.matches_snapshot(prepared.recipe), "recipe_changed")
            phase = prepared.phase
            validate_settings(phase)
            try:
                unchanged = target.unchanged()
            except Exception:
                unchanged = False
            require(unchanged, "state_changed")
            return await self.send_once(device_id, prepared.zone_id, phase, context)
        finally:
            self.busy.discard(device_id)

    async def send_once(self, device_id: str, zone_id: int, phase: CookingPhase, context: Any) -> dict:
        """One public transport attempt; caller owns validation and per-device lock."""
        # This is the only control call. Never invoke raw, SYNC/MATCH or a
        # start-capable service, and never trust upstream cached confirmation.
        try:
            self.uncertain.add(device_id)
            result = await self.hass.services.async_call(
                UPSTREAM, "programm_senden",
                {"geraet": device_id, "zone": zone_id, "programm": phase.program,
                 "temperatur": phase.temperature_c, "minuten": phase.duration_minutes, "variante": "multi_app",
                 "einmal": True, "streng": True, "bestaetigen": False},
                blocking=True, return_response=True, context=context,
            )
        except asyncio.CancelledError:
            raise  # Uncertain latch remains set; never permit a replay.
        except Exception:
            return self._result("unknown")
        # Only accept a complete, exact response contract. Nothing from the
        # upstream response (including error strings or raw data) is exposed.
        exact = {"programm": phase.program, "temperatur": phase.temperature_c,
                 "minuten": phase.duration_minutes, "zone": zone_id}
        if (isinstance(result, dict) and result.get("ok") is True
                and result.get("ergebnis") == "angenommen"
                and type(result.get("versuche")) is int and result["versuche"] == 1
                and result.get("variante") == "multi_app" and result.get("gesendet") == exact
                and all(type(result["gesendet"][k]) is type(v) for k, v in exact.items())):
            self.uncertain.discard(device_id)
            return self._result("accepted")
        return self._result("unknown")

    @staticmethod
    def _result(outcome: str) -> dict:
        return {"mode": "supervised_beta_test", "attempted": True, "outcome": outcome,
                "accepted_by_adapter": outcome == "accepted", "confirmed_on_device": False,
                "compatibility_verified": False, "automatic_retry": False}
