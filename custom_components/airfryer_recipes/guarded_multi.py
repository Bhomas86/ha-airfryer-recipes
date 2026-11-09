"""Our own prepare-only SYNC/MATCH coordinator; controller stays unmodified.

The reviewed controller transport is composed through a per-call delegate. Its
HTTP submission is guarded AFTER any login awaits. No service interception,
monkey-patching, credential storage, reset, refresh-after-check or retry.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import secrets
import time

from .beta_send import BetaTestBlocked, SendPermit, require, validate_settings
from .const import DOMAIN
from .device_access import authorize_device, AccessDenied
from .device_discovery import normalize_capabilities
from .model_profiles import TURBO_TOWER_MODEL
from .multi_contract import REVIEWED_VERSIONS
from .multi_zone import resolve_sources


def _safe_report(fryer):
    now = datetime.now(timezone.utc)
    report = getattr(fryer, "last_report", None)
    require(isinstance(report, datetime) and report.tzinfo is not None
            and 0 <= (now - report).total_seconds() <= 15, "freshness")
    require(fryer.online is True and not fryer.last_error and fryer.model == TURBO_TOWER_MODEL, "connection")
    require(type(fryer.revision) is int and fryer.revision >= 0, "freshness")
    state = fryer.state
    require(state.active is False and state.status in ("bereit", "aus")
            and state.temp_unit == "celsius" and type(state.sync_type) is int and state.sync_type == 0, "zones")
    require(isinstance(state.zones, dict) and len(state.zones) == 2 and set(state.zones) == {1, 2}
            and all(type(z) is int for z in state.zones), "zones")
    require(all(z.active is False and z.status in ("bereit", "aus") for z in state.zones.values()), "zones")
    return (id(state), report, fryer.revision, tuple((i, state.zones[i].status) for i in (1, 2)))


def safe_report(fryer):
    try:
        return _safe_report(fryer)
    except (AttributeError, TypeError, ValueError) as err:
        if isinstance(err, BetaTestBlocked):
            raise
        raise BetaTestBlocked("zones") from None


def validate_phases(caps, phases):
    require(caps is not None and caps["connection"] == "ok", "capabilities")
    for phase in phases.values():
        validate_settings(phase)
        program = next((p for p in caps["programs"] if p["id"] == phase.program), None)
        require(program is not None, "capabilities")
        for key, value in (("temperature_c", phase.temperature_c), ("duration_minutes", phase.duration_minutes)):
            require(program[key]["min"] <= value <= program[key]["max"], "test_range")
        step = program.get("temperature_step_c")
        require(type(step) is int and step > 0
                and (phase.temperature_c - program["temperature_c"]["min"]) % step == 0, "test_range")


class Binding:
    def __init__(self, hass, device_id, device, entry, runtime, fryer, version):
        self.hass, self.device_id, self.device = hass, device_id, device
        self.entry, self.runtime, self.fryer, self.version = entry, runtime, fryer, version
        self.api = runtime.api
        self.account_id = self.api.account_id
        require(isinstance(self.account_id, str) and bool(self.account_id), "adapter_data")
        self.info = deepcopy(fryer.info)
        self.identity = next(v for d, v in device.identifiers if d == "airfryer_control")
        self.fingerprint = None

    def check(self):
        from homeassistant.helpers import device_registry as dr
        require(dr.async_get(self.hass).async_get(self.device_id) is self.device
                and self.device.disabled_by is None and self.device.model == TURBO_TOWER_MODEL
                and [v for d, v in self.device.identifiers if d == "airfryer_control"] == [self.identity]
                and self.entry.entry_id in self.device.config_entries
                and self.entry in self.hass.config_entries.async_loaded_entries("airfryer_control")
                and self.entry.runtime_data is self.runtime and self.runtime.fryers.get(self.identity) is self.fryer
                and self.runtime.api is self.api and self.api.account_id == self.account_id and self.fryer.info == self.info
                and not getattr(self.hass, "is_stopping", False), "state_changed")
        current = safe_report(self.fryer)
        require(self.fingerprint is None or current == self.fingerprint, "state_changed")
        return current


async def bind(hass, device_id, phases, refresh):
    from homeassistant.helpers import device_registry as dr
    from homeassistant.loader import async_get_integration
    version = (await async_get_integration(hass, "airfryer_control")).version
    require(version in REVIEWED_VERSIONS, "adapter_version")
    device = dr.async_get(hass).async_get(device_id)
    require(device is not None and device.disabled_by is None and device.model == TURBO_TOWER_MODEL, "target")
    identities = [v for d, v in device.identifiers if d == "airfryer_control"]
    require(len(identities) == 1, "target")
    matches = []
    for entry in hass.config_entries.async_loaded_entries("airfryer_control"):
        runtime = entry.runtime_data
        fryers = getattr(runtime, "fryers", {})
        if entry.entry_id in device.config_entries and identities[0] in fryers:
            matches.append((entry, runtime, fryers[identities[0]]))
    require(len(matches) == 1, "target")
    binding = Binding(hass, device_id, device, *matches[0], version)
    if refresh:
        before, requested = binding.fryer.last_report, datetime.now(timezone.utc)
        async with asyncio.timeout(20):
            await binding.runtime.async_refresh()  # read-only coordinator operation
        require(isinstance(binding.fryer.last_report, datetime)
                and binding.fryer.last_report >= requested
                and (before is None or binding.fryer.last_report > before), "refresh_failed")
    binding.check()
    caps = normalize_capabilities(await hass.services.async_call(
        "airfryer_control", "faehigkeiten", {"geraet": device_id}, blocking=True, return_response=True))
    validate_phases(caps, phases)
    require(caps["reported_at"] == binding.fryer.last_report.isoformat()
            and caps["revision"] == binding.fryer.revision, "freshness")
    binding.fingerprint = binding.check()
    return binding


APP_MODES = {"airfry": "AirFry", "roast": "Roast", "bake": "Bake", "grill": "Grill", "reheat": "Reheat", "dry": "Dry", "proof": "Proof"}


def build_payload(operation, phases, account_id):
    configs = []
    longest = max(p.duration_minutes for p in phases.values())
    for zone in (1, 2):
        p = phases[str(zone)]
        config = {"cookSetTime": p.duration_minutes * 60, "cookTemp": p.temperature_c,
                  "mode": APP_MODES[p.program], "chamber": zone, "recipeId": 14,
                  "recipeName": "Air Fry" if p.program == "airfry" else APP_MODES[p.program],
                  "recipeType": 3, "shakeTime": 0}
        if operation == "sync":
            config["holdTime"] = (longest - p.duration_minutes) * 60
        configs.append(config)
    return {"syncType": 2 if operation == "sync" else 1, "workChamber": 4,
            "tempUnit": "c", "accountId": account_id or "", "readyStart": True, "cookConfigs": configs}


class GuardedTransport:
    """Per-call composition; no attribute on the controller/API is replaced."""
    def __init__(self, api, info, payload, final_check, mark_attempt):
        self.api, self.info, self.expected = api, deepcopy(info), deepcopy(payload)
        self.final_check, self.mark_attempt = final_check, mark_attempt
        self.attempted = False

    def __getattr__(self, name):
        return getattr(self.api, name)

    async def _post(self, url, body, headers=None):
        require(not self.attempted and headers is None
                and url == self.api.base_url + "/cloud/v2/deviceManaged/bypassV2"
                and body.get("cid") == self.info.get("cid") and body.get("method") == "bypassV2"
                and isinstance(self.expected.get("accountId"), str) and bool(self.expected["accountId"])
                and body.get("accountID") == self.expected["accountId"]
                and body.get("payload") == {"method": "startMultiCook", "data": self.expected, "source": "APP"}, "adapter_data")
        await self.final_check()
        self.attempted = True
        self.mark_attempt()
        result = await self.api._post(url, body)
        require(isinstance(result, dict) and type(result.get("code")) is int, "adapter_data")
        inner = result.get("result")
        if isinstance(inner, dict) and inner.get("code") is not None:
            require(type(inner["code"]) is int, "adapter_data")
        return result

    async def send(self):
        return await type(self.api).bypass_v2(self, self.info, "startMultiCook", deepcopy(self.expected), retry=False)


class MultiSender:
    def __init__(self, hass, parent):
        self.hass, self.parent = hass, parent
        self.pending = {}
        self.confirming = {}

    async def authorize(self, uid, device):
        permission = await authorize_device(self.hass, uid, device)
        require(not self.parent.closed and self.hass.data.get(DOMAIN, {}).get("beta_sender") is self.parent
                and not getattr(self.hass, "is_stopping", False), "not_configured")
        return permission

    def discard(self, token):
        prepared = self.pending.pop(token, None) or self.confirming.get(token)
        if prepared:
            prepared["permit"].close()

    def close(self):
        for token in tuple(self.pending) + tuple(self.confirming):
            self.discard(token)

    async def cancel(self, connection, token):
        prepared = self.pending.get(token) or self.confirming.get(token)
        if prepared is not None:
            require(prepared["uid"] == connection.user.id and prepared["permit"].owner is connection, "confirmation")
            self.discard(token)
        return {"discarded": prepared is not None}

    async def prepare(self, connection, device_id, mode, sources, dry_run):
        require(type(dry_run) is bool, "source")
        uid = connection.user.id
        permission = await self.authorize(uid, device_id)
        require(device_id not in self.parent.busy and device_id not in self.parent.batch_devices, "busy")
        require(device_id not in self.parent.uncertain, "outcome_unknown")
        self.parent.busy.add(device_id)
        try:
            for token, old in tuple(self.pending.items()):
                if old["uid"] == uid or old["expires"] <= time.monotonic():
                    self.discard(token)
            require(len(self.pending) < 128, "busy")
            phases, references = await resolve_sources(self.hass, mode, sources)
            binding = await bind(self.hass, device_id, phases, refresh=True)
            require(await self.authorize(uid, device_id) == permission, "unauthorized")
            binding.check()
            for repo, recipe in references:
                require(self.hass.data[DOMAIN].get("repository") is repo and repo.matches_snapshot(recipe), "recipe_changed")
            result = {"mode": "dry_run" if dry_run else "supervised_beta_test", "transmitted": False,
                      "operation": mode, "zones": [{"zone_id": int(z), "settings": asdict(p)} for z, p in sorted(phases.items())]}
            if not dry_run:
                token = secrets.token_urlsafe(24)
                permit = SendPermit(owner=connection)
                subscription = "airfryer_recipes_multi_" + token
                connection.subscriptions[subscription] = lambda: self.discard(token)
                permit.cleanup = lambda: connection.subscriptions.pop(subscription, None)
                self.pending[token] = dict(uid=uid, device_id=device_id, phases=phases, references=references,
                    binding=binding, permission=permission, permit=permit, expires=time.monotonic()+15, operation=mode)
                result["token"] = token
            return result
        finally:
            self.parent.busy.discard(device_id)

    async def confirm(self, connection, token, ack):
        require(ack is True and isinstance(token, str) and 0 < len(token) <= 128, "confirmation")
        prepared = self.pending.get(token)
        require(prepared is not None and prepared["uid"] == connection.user.id
                and prepared["permit"].owner is connection, "confirmation")
        self.pending.pop(token)
        self.confirming[token] = prepared
        device = prepared["device_id"]
        transport = None
        locked = False
        async def final_check():
            require(await self.authorize(prepared["uid"], device) == prepared["permission"], "unauthorized")
            require(prepared["permit"].active and time.monotonic() < prepared["expires"], "confirmation")
            require(device not in self.parent.uncertain and device not in self.parent.batch_devices, "outcome_unknown")
            for repo, recipe in prepared["references"]:
                require(self.hass.data[DOMAIN].get("repository") is repo and repo.matches_snapshot(recipe), "recipe_changed")
            prepared["binding"].check()
        try:
            require(device not in self.parent.busy, "busy")
            self.parent.busy.add(device); locked = True
            await final_check()
            binding = prepared["binding"]
            payload = build_payload(prepared["operation"], prepared["phases"], binding.api.account_id)
            transport = GuardedTransport(binding.api, binding.info, payload, final_check,
                                         lambda: self.parent.uncertain.add(device))
            await transport.send()
            require(transport.attempted, "adapter_data")
            self.parent.uncertain.discard(device)
            history_saved = True
            history = self.hass.data[DOMAIN].get("sent_settings")
            if history:
                for zone, phase in prepared["phases"].items():
                    try:
                        await history.record(device, int(zone), phase)
                    except Exception:
                        history_saved = False
            return {"outcome": "accepted", "attempted": True, "confirmed_on_device": False,
                    "history_saved": history_saved, "automatic_retry": False}
        except Exception as err:
            if transport is not None and transport.attempted:
                return {"outcome": "unknown", "attempted": True, "automatic_retry": False}
            if isinstance(err, (BetaTestBlocked, AccessDenied)):
                raise
            raise BetaTestBlocked("adapter_data") from None
        finally:
            self.confirming.pop(token, None)
            prepared["permit"].close()
            if locked:
                self.parent.busy.discard(device)

    async def recover(self, connection, device_id, acknowledge):
        require(acknowledge is True, "acknowledgement")
        permission = await self.authorize(connection.user.id, device_id)
        require(device_id not in self.parent.busy and device_id not in self.parent.batch_devices, "busy")
        self.parent.busy.add(device_id)
        try:
            from .recipe_model import CookingPhase
            phase = CookingPhase(program="airfry", temperature_c=180, duration_minutes=7)
            binding = await bind(self.hass, device_id, {"1": phase, "2": phase}, refresh=True)
            require(await self.authorize(connection.user.id, device_id) == permission, "unauthorized")
            binding.check()
            for token, old in tuple(self.pending.items()):
                if old["device_id"] == device_id:
                    self.discard(token)
            self.parent.uncertain.discard(device_id)
            return {"rearmed": True, "transmitted": False}
        finally:
            self.parent.busy.discard(device_id)


def manager(hass):
    parent = hass.data[DOMAIN].get("beta_sender")
    require(parent is not None and not parent.closed, "not_configured")
    current = hass.data[DOMAIN].get("multi_sender")
    if current is None or current.parent is not parent:
        if current is not None:
            current.close()
        current = hass.data[DOMAIN]["multi_sender"] = MultiSender(hass, parent)
    return current
