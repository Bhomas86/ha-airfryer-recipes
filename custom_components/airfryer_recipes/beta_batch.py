"""Bounded, connection-bound commissioning sequence; no background queue."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import secrets
import time
from typing import Any

from .beta_send import BetaSender, BetaTestBlocked, Target, require
from .recipe_model import CookingPhase

SAMPLES = (("airfry", 180, 7), ("roast", 190, 10), ("bake", 180, 6),
           ("grill", 205, 1), ("reheat", 70, 5), ("dry", 55, 10))


def identity(target: Target) -> tuple:
    # Fresh report time/revision and owned prepared states change during a run.
    # Adapter identity, capabilities, model and contract must remain identical.
    f = target.fingerprint
    return (*f[:3], *f[6:])


@dataclass
class Run:
    token: str
    user: str
    owner: Any
    device: str
    name: str
    signature: tuple
    steps: tuple[tuple[int, CookingPhase], ...]
    skipped: tuple[str, ...]
    expires: float
    index: int = 0
    nonce: str | None = None
    expected: dict[int, CookingPhase] = field(default_factory=dict)
    stopped: bool = False
    started: bool = False
    inflight: bool = False
    cleanup: Any = None


class BatchRunner:
    def __init__(self, sender: BetaSender) -> None:
        self.sender = sender
        self.runs: dict[str, Run] = {}

    def stop(self, run: Run, *, disconnected: bool = False) -> None:
        run.stopped = True
        run.nonce = None
        if not run.inflight:
            if self.sender.batch_devices.get(run.device) == run.token:
                self.sender.batch_devices.pop(run.device, None)
        if run.cleanup and not disconnected:
            run.cleanup()
            run.cleanup = None

    async def prepare(self, user: str, owner: Any, device: str, context: Any) -> dict:
        await self.sender._authorized(user)
        for key, old in list(self.runs.items()):
            if old.expires <= time.monotonic() or old.stopped:
                self.stop(old)
                if not old.inflight:
                    self.runs.pop(key)
        require(len(self.runs) < 16, "busy")
        require(device not in self.sender.busy and device not in self.sender.batch_devices, "busy")
        require(device not in self.sender.uncertain, "outcome_unknown")
        self.sender.busy.add(device)
        try:
            target = await self.sender._read(device, 1, refresh=True, context=context, wait_for_report=True)
            await self.sender._authorized(user)
            metadata = {p[0]: p for p in target.fingerprint[6]}
            steps, skipped = [], []
            for program, temp, minutes in SAMPLES:
                p = metadata.get(program)
                if (p is None or p[5] not in ("estimated", "confirmed")
                        or p[6] not in ("unverified", "confirmed")
                        or not (p[1] <= temp <= p[2] and p[3] <= minutes <= p[4])):
                    skipped.append(program)
                    continue
                steps.extend((zone, CookingPhase(program, temp, minutes)) for zone in (1, 2))
            require(bool(steps), "capabilities")
            token = secrets.token_urlsafe(32)
            self.runs[token] = Run(token, user, owner, device, target.name, identity(target),
                                   tuple(steps), tuple(skipped), time.monotonic() + 60)
            return {"token": token, "device_name": target.name, "expires_seconds": 60,
                    "steps": [{"zone_id": z, "settings": asdict(p)} for z, p in steps],
                    "skipped": skipped, "transmitted": False}
        finally:
            self.sender.busy.discard(device)

    def owned(self, user: str, owner: Any, token: str) -> Run:
        require(isinstance(token, str) and len(token) <= 128, "confirmation")
        run = self.runs.get(token)
        require(run is not None and run.user == user, "confirmation")
        if run.owner is not owner:
            self.stop(run)
            raise BetaTestBlocked("batch_connection")
        if run.stopped or time.monotonic() >= run.expires:
            self.stop(run)
            raise BetaTestBlocked("confirmation")
        return run

    async def start(self, user: str, owner: Any, token: str, ack: bool) -> dict:
        require(ack is True, "acknowledgement")
        await self.sender._authorized(user)
        run = self.owned(user, owner, token)
        require(not run.started and run.device not in self.sender.busy
                and run.device not in self.sender.batch_devices, "busy")
        require(run.device not in self.sender.uncertain, "outcome_unknown")
        run.started = True
        run.expires = time.monotonic() + 600
        run.nonce = secrets.token_urlsafe(32)
        self.sender.batch_devices[run.device] = token
        return {"run_id": token, "next_token": run.nonce, "total": len(run.steps)}

    async def next(self, user: str, owner: Any, token: str, nonce: str, context: Any) -> dict:
        await self.sender._authorized(user)
        run = self.owned(user, owner, token)
        require(run.started and run.nonce is not None and nonce == run.nonce, "confirmation")
        require(not run.inflight and run.device not in self.sender.busy, "busy")
        require(run.device not in self.sender.uncertain, "outcome_unknown")
        run.nonce = None  # Never replay a step after an exception or lost response.
        run.inflight = True
        self.sender.busy.add(run.device)
        attempted = False
        try:
            zone, phase = run.steps[run.index]
            target = await self.sender._read(run.device, zone, refresh=True, context=context, wait_for_report=True,
                                              settings=phase, prepared_zones=run.expected)
            await self.sender._authorized(user)
            require(not run.stopped and time.monotonic() < run.expires, "confirmation")
            require(identity(target) == run.signature and target.unchanged(), "state_changed")
            attempted = True
            result = await self.sender.send_once(run.device, zone, phase, context)
            require(result["outcome"] == "accepted", "outcome_unknown")
            require(not run.stopped, "batch_stopped")
            run.expected[zone] = phase
            # Fresh telemetry must confirm both owned prepared zones and no heat
            # before another control command can be offered to the client.
            observed = await self.sender._read(run.device, zone, refresh=True, context=context, wait_for_report=True,
                                                settings=phase, prepared_zones=run.expected)
            await self.sender._authorized(user)
            require(not run.stopped and identity(observed) == run.signature
                    and observed.unchanged(), "state_changed")
            run.index += 1
            done = run.index == len(run.steps)
            if done:
                self.stop(run)
            else:
                run.nonce = secrets.token_urlsafe(32)
            return {"completed": run.index, "total": len(run.steps), "done": done,
                    "next_token": run.nonce, "zone_id": zone, "settings": asdict(phase),
                    "reported_values_match": True, "compatibility_verified": False}
        except BaseException:
            if attempted:
                self.sender.uncertain.add(run.device)
            self.stop(run)
            raise
        finally:
            run.inflight = False
            self.sender.busy.discard(run.device)
            if run.stopped and self.sender.batch_devices.get(run.device) == run.token:
                self.sender.batch_devices.pop(run.device, None)
