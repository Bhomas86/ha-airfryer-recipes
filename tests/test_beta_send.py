"""Commissioning safety tests; fake public services only, no appliance access."""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS, ModuleType
import sys
import unittest
from unittest.mock import AsyncMock, Mock, patch

from custom_components.airfryer_recipes.beta_send import (
    BetaSender, BetaTestBlocked, SendPermit, Target, read_target, TEST_SETTINGS,
)
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.recipe_model import CookingPhase, create_recipe, RecipeValidationError
from custom_components.airfryer_recipes.recipe_repository import RecipeRepository
from dataclasses import replace


class SenderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = NS(data={DOMAIN: {}}, auth=NS(async_get_user=AsyncMock(
            return_value=NS(is_admin=True, is_active=True))),
            services=NS(async_call=AsyncMock(return_value={
                "ok": True, "ergebnis": "angenommen", "versuche": 1, "variante": "multi_app",
                "gesendet": {"programm": "airfry", "temperatur": 170, "minuten": 1, "zone": 1},
                "raw": "secret", "bestaetigt": True,
            })))
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        self.read = AsyncMock(return_value=Target("Kitchen", ("same",)))
        p = patch("custom_components.airfryer_recipes.beta_send.read_target", self.read)
        p.start()
        self.addCleanup(p.stop)

    async def prepare(self, user="u1", device="device", zone=1):
        return await self.sender.prepare(user, device, zone, True, "user-context")

    async def confirm(self, token, user="u1"):
        return await self.sender.confirm(user, token, True, "user-context")

    async def test_prepare_never_sends_and_result_does_not_claim_confirmation(self):
        prepared = await self.prepare()
        self.assertEqual(prepared["settings"], TEST_SETTINGS)
        self.assertFalse(prepared["transmitted"])
        self.hass.services.async_call.assert_not_awaited()
        self.read.assert_awaited_once_with(self.hass, "device", 1, refresh=True, context="user-context")
        result = await self.confirm(prepared["token"])
        self.assertEqual(self.read.await_args.kwargs, {})  # Confirmation never refreshes again.
        self.assertEqual(result["outcome"], "accepted")
        self.assertFalse(result["confirmed_on_device"])
        self.assertNotIn("secret", str(result))
        self.hass.services.async_call.assert_awaited_once_with(
            "airfryer_control", "programm_senden",
            {"geraet": "device", "zone": 1, "programm": "airfry", "temperatur": 170,
             "minuten": 1, "variante": "multi_app", "einmal": True,
             "streng": True, "bestaetigen": False},
            blocking=True, return_response=True, context="user-context")
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(prepared["token"])

    async def test_acknowledgements_must_be_true_and_admin_is_rechecked(self):
        for value in (False, 1, "true", None):
            with self.assertRaisesRegex(BetaTestBlocked, "acknowledgement"):
                await self.sender.prepare("u1", "device", 1, value, "user-context")
        token = (await self.prepare())["token"]
        self.hass.auth.async_get_user.return_value.is_admin = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_tokens_are_user_bound_and_new_prepare_invalidates_old(self):
        first = (await self.prepare())["token"]
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(first, "u2")
        second = (await self.prepare())["token"]
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(first)
        await self.confirm(second)

    async def test_expired_confirmation_never_sends(self):
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=1):
            token = (await self.prepare())["token"]
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=20):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_state_or_session_changes_consume_confirmation(self):
        token = (await self.prepare())["token"]
        self.read.return_value = Target("Kitchen", ("new session",))
        with self.assertRaisesRegex(BetaTestBlocked, "state_changed"):
            await self.confirm(token)
        self.assertNotIn(token, self.sender.pending)
        self.hass.services.async_call.assert_not_awaited()

    async def test_change_during_final_auth_await_is_blocked(self):
        token = (await self.prepare())["token"]
        self.read.return_value = Target("Kitchen", ("same",), lambda: False)
        with self.assertRaisesRegex(BetaTestBlocked, "state_changed"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_concurrent_confirmation_is_rejected_without_queue(self):
        a = (await self.prepare())["token"]
        b = (await self.prepare(user="u2"))["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def call(*args, **kwargs):
            entered.set()
            await finish.wait()
            return None
        self.hass.services.async_call.side_effect = call
        task = asyncio.create_task(self.confirm(a))
        await entered.wait()
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.confirm(b, "u2")
        finish.set()
        await task
        self.hass.services.async_call.assert_awaited_once()

    async def test_exception_unknown_and_no_retry_even_after_integration_reload(self):
        self.hass.services.async_call.side_effect = TimeoutError("private")
        token = (await self.prepare())["token"]
        self.assertEqual((await self.confirm(token))["outcome"], "unknown")
        self.sender.close()
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        with self.assertRaisesRegex(BetaTestBlocked, "outcome_unknown"):
            await self.prepare()
        self.hass.services.async_call.assert_awaited_once()

    async def test_cancellation_keeps_uncertain_latch_and_clears_busy(self):
        token = (await self.prepare())["token"]
        self.hass.services.async_call.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await self.confirm(token)
        self.assertIn("device", self.sender.uncertain)
        self.assertNotIn("device", self.sender.busy)

    async def test_unload_while_reading_prevents_send(self):
        token = (await self.prepare())["token"]
        async def read(*args):
            self.sender.close()
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        with self.assertRaisesRegex(BetaTestBlocked, "not_configured"):
            await self.confirm(token)
        self.hass.services.async_call.assert_not_awaited()

    async def test_untrusted_upstream_response_never_confirms_or_retries(self):
        for response in (None, {"ok": True, "bestaetigt": True},
                         {"ok": False, "ergebnis": "abgelehnt", "fehler": "private"}):
            self.sender.uncertain.clear()
            token = (await self.prepare())["token"]
            self.hass.services.async_call.return_value = response
            result = await self.confirm(token)
            self.assertEqual(result["outcome"], "rejected" if isinstance(response, dict) and response.get("ergebnis") == "abgelehnt" else "unknown")
            self.assertFalse(result["confirmed_on_device"])
            self.assertNotIn("private", str(result))
        self.assertEqual(self.hass.services.async_call.await_count, 3)

    async def test_expiry_during_revalidation_and_inactive_admin_are_blocked(self):
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=1):
            token = (await self.prepare())["token"]
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", side_effect=[2, 20]):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.confirm(token)
        self.hass.auth.async_get_user.return_value.is_active = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.prepare()
        self.hass.services.async_call.assert_not_awaited()

    async def test_adapter_read_failure_never_leaks_error_or_sends(self):
        self.read.side_effect = RuntimeError("private-cloud-id")
        with self.assertRaisesRegex(BetaTestBlocked, "^adapter_data$"):
            await self.prepare()
        self.hass.services.async_call.assert_not_awaited()

    async def test_active_service_lock_survives_reload(self):
        token = (await self.prepare())["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def call(*args, **kwargs):
            entered.set()
            await finish.wait()
            return None
        self.hass.services.async_call.side_effect = call
        task = asyncio.create_task(self.confirm(token))
        await entered.wait()
        self.sender.close()
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]["beta_sender"] = self.sender
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.prepare()
        finish.set()
        await task

    async def test_parallel_preparation_cannot_queue_refresh_or_send(self):
        entered, finish = asyncio.Event(), asyncio.Event()
        async def read(*args, **kwargs):
            entered.set()
            await finish.wait()
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        task = asyncio.create_task(self.prepare())
        await entered.wait()
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.prepare(user="u2")
        finish.set()
        await task
        self.read.assert_awaited_once()
        self.hass.services.async_call.assert_not_awaited()

    async def test_failed_new_preparation_invalidates_previous_token(self):
        token = (await self.prepare())["token"]
        self.read.side_effect = BetaTestBlocked("refresh_failed")
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_failed"):
            await self.prepare()
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(token)
        self.assertNotIn("device", self.sender.busy)
        self.hass.services.async_call.assert_not_awaited()

    async def test_confirmation_is_connection_bound_and_cleanup_runs_after_send(self):
        owner, other = object(), object()
        cleanup = Mock()
        permit = SendPermit(owner=owner, cleanup=cleanup)
        token = (await self.sender.prepare("u1", "device", 1, True, "context", permit=permit))["token"]
        with self.assertRaisesRegex(BetaTestBlocked, "connection_changed"):
            await self.sender.confirm("u1", token, True, "context", owner=other)
        self.hass.services.async_call.assert_not_awaited()
        self.assertEqual((await self.sender.confirm("u1", token, True, "context", owner=owner))["outcome"], "accepted")
        cleanup.assert_called_once_with()
        self.assertFalse(permit.active)
        self.assertFalse(self.sender.confirming)

    async def test_disconnect_during_preparation_does_not_create_a_late_token(self):
        permit = SendPermit(owner=object())
        async def read(*args, **kwargs):
            self.sender.close_permit(permit, disconnected=True)
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        with self.assertRaisesRegex(BetaTestBlocked, "connection_changed"):
            await self.sender.prepare("u1", "device", 1, True, "context", permit=permit)
        self.assertFalse(self.sender.pending)
        self.assertNotIn("device", self.sender.busy)
        self.hass.services.async_call.assert_not_awaited()

    async def test_disconnect_during_final_validation_prevents_a_device_call(self):
        owner = object()
        permit = SendPermit(owner=owner)
        token = (await self.sender.prepare("u1", "device", 1, True, "context", permit=permit))["token"]
        async def read(*args, **kwargs):
            self.sender.close_permit(permit, disconnected=True)
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        with self.assertRaisesRegex(BetaTestBlocked, "connection_changed"):
            await self.sender.confirm("u1", token, True, "context", owner=owner)
        self.assertFalse(self.sender.pending)
        self.assertFalse(self.sender.confirming)
        self.assertNotIn("device", self.sender.uncertain)
        self.hass.services.async_call.assert_not_awaited()

    async def test_cancel_is_owned_and_discards_a_pending_confirmation_without_control(self):
        owner = object()
        cleanup = Mock()
        permit = SendPermit(owner=owner, cleanup=cleanup)
        token = (await self.sender.prepare("u1", "device", 1, True, "context", permit=permit))["token"]
        for user, connection in (("u2", owner), ("u1", object())):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.sender.cancel(user, token, owner=connection)
        self.assertTrue((await self.sender.cancel("u1", token, owner=owner))["discarded"])
        self.assertFalse((await self.sender.cancel("u1", token, owner=owner))["discarded"])
        cleanup.assert_called_once_with()
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.sender.confirm("u1", token, True, "context", owner=owner)
        self.hass.services.async_call.assert_not_awaited()

    async def test_cancel_while_confirmation_is_validating_prevents_send(self):
        owner = object()
        token = (await self.sender.prepare("u1", "device", 1, True, "context",
                                            permit=SendPermit(owner=owner)))["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def read(*args, **kwargs):
            entered.set()
            await finish.wait()
            return Target("Kitchen", ("same",))
        self.read.side_effect = read
        task = asyncio.create_task(self.sender.confirm("u1", token, True, "context", owner=owner))
        await entered.wait()
        self.assertTrue((await self.sender.cancel("u1", token, owner=owner))["discarded"])
        finish.set()
        with self.assertRaisesRegex(BetaTestBlocked, "connection_changed"):
            await task
        self.assertFalse(self.sender.confirming)
        self.assertNotIn("device", self.sender.busy)
        self.hass.services.async_call.assert_not_awaited()

    async def test_disconnect_after_submission_cannot_recall_or_repeat_the_send(self):
        owner = object()
        permit = SendPermit(owner=owner)
        token = (await self.sender.prepare("u1", "device", 1, True, "context", permit=permit))["token"]
        answer = self.hass.services.async_call.return_value
        async def call(*args, **kwargs):
            self.sender.close_permit(permit, disconnected=True)
            return answer
        self.hass.services.async_call.side_effect = call
        self.assertEqual((await self.sender.confirm("u1", token, True, "context", owner=owner))["outcome"], "accepted")
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.sender.confirm("u1", token, True, "context", owner=object())
        self.hass.services.async_call.assert_awaited_once()

    async def test_cancel_after_submission_keeps_device_locked_until_the_call_finishes(self):
        owner = object()
        token = (await self.sender.prepare("u1", "device", 1, True, "context",
                                            permit=SendPermit(owner=owner)))["token"]
        entered, finish = asyncio.Event(), asyncio.Event()
        async def call(*args, **kwargs):
            entered.set()
            await finish.wait()
            return None
        self.hass.services.async_call.side_effect = call
        sending = asyncio.create_task(self.sender.confirm("u1", token, True, "context", owner=owner))
        await entered.wait()
        try:
            await self.sender.cancel("u1", token, owner=owner)
            with self.assertRaisesRegex(BetaTestBlocked, "busy"):
                await self.sender.recover("u1", "device", True, "context")
            with self.assertRaisesRegex(BetaTestBlocked, "busy"):
                await self.prepare()
            self.hass.services.async_call.assert_awaited_once()
        finally:
            finish.set()
            result = await sending
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("device", self.sender.uncertain)
        self.assertNotIn("device", self.sender.busy)

    async def test_expiry_and_failed_new_preparation_release_connection_cleanup(self):
        first_cleanup, second_cleanup = Mock(), Mock()
        await self.sender.prepare("u1", "device", 1, True, "context", permit=SendPermit(cleanup=first_cleanup))
        self.read.side_effect = BetaTestBlocked("connection")
        with self.assertRaisesRegex(BetaTestBlocked, "connection"):
            await self.sender.prepare("u1", "device", 1, True, "context", permit=SendPermit(cleanup=second_cleanup))
        first_cleanup.assert_called_once_with()
        second_cleanup.assert_called_once_with()
        self.assertFalse(self.sender.pending)
        self.read.side_effect = None
        expiry_cleanup = Mock()
        token = (await self.sender.prepare("u1", "device", 1, True, "context", permit=SendPermit(cleanup=expiry_cleanup)))["token"]
        with patch("custom_components.airfryer_recipes.beta_send.time.monotonic", return_value=10**12):
            with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
                await self.confirm(token)
        expiry_cleanup.assert_called_once_with()
        self.hass.services.async_call.assert_not_awaited()

    async def selected(self, source, zone=1):
        return await self.sender.prepare("u1", "device", zone, True, "user-context", source=source)

    async def library(self):
        repo = RecipeRepository(AsyncMock(return_value=None), AsyncMock())
        await repo.async_load()
        self.hass.data[DOMAIN]["repository"] = repo
        return repo

    async def test_manual_values_are_copied_bound_and_sent_exactly_once(self):
        source = {"settings": {"program": "airfry", "temperature_c": 180, "duration_minutes": 7}}
        prepared = await self.selected(source)
        source["settings"]["temperature_c"] = 200
        self.assertEqual(prepared["settings"]["temperature_c"], 180)
        self.hass.services.async_call.return_value["gesendet"].update(temperatur=180, minuten=7)
        result = await self.confirm(prepared["token"])
        self.assertEqual(result["outcome"], "accepted")
        self.assertEqual(self.hass.services.async_call.await_args.args[2]["temperatur"], 180)
        self.assertEqual(self.hass.services.async_call.await_args.args[2]["minuten"], 7)
        self.assertEqual(self.read.await_args.kwargs["settings"], CookingPhase("airfry", 180, 7))

    async def test_recipe_resolves_server_side_and_is_not_modified(self):
        history = NS(record=AsyncMock())
        self.hass.data[DOMAIN]["sent_settings"] = history
        repo = await self.library()
        recipe = await repo.async_create(create_recipe("Rolls", program="airfry", temperature_c=180, duration_minutes=7))
        prepared = await self.selected({"recipe_id": recipe.id})
        self.assertEqual(prepared["recipe_name"], "Rolls")
        self.assertEqual(prepared["settings"], {"program": "airfry", "temperature_c": 180, "duration_minutes": 7})
        self.hass.services.async_call.return_value["gesendet"].update(temperatur=180, minuten=7)
        await self.confirm(prepared["token"])
        history.record.assert_awaited_once_with("device", 1, recipe.phases[0], recipe.id)
        self.assertEqual(await repo.async_get(recipe.id), recipe)

    async def test_changed_deleted_or_reloaded_recipe_blocks_confirmation(self):
        for change in ("change", "delete", "reload"):
            repo = await self.library()
            recipe = await repo.async_create(create_recipe("Rolls", program="airfry", temperature_c=180, duration_minutes=7))
            prepared = await self.selected({"recipe_id": recipe.id})
            if change == "change":
                await repo.async_update(replace(recipe, phases=(CookingPhase("airfry", 190, 8),)))
            elif change == "delete":
                await repo.async_delete(recipe.id)
            else:
                await self.library()
            with self.assertRaisesRegex(BetaTestBlocked, "recipe_changed"):
                await self.confirm(prepared["token"])
            self.assertNotIn(prepared["token"], self.sender.pending)
        self.hass.services.async_call.assert_not_awaited()

    async def test_invalid_or_forged_sources_are_rejected_before_status_refresh(self):
        for source in ({}, {"recipe_id": "x", "settings": {}}, {"settings": {}, "is_admin": True},
                       {"recipe_id": True}, {"settings": {"program": "airfry", "temperature_c": 180, "duration_minutes": 7, "readyStart": False}}):
            with self.assertRaises(BetaTestBlocked):
                await self.selected(source)
        for settings in ({"program": "airfry", "temperature_c": True, "duration_minutes": 7},
                         {"program": "airfry", "temperature_c": 180, "duration_minutes": 1.5}):
            with self.assertRaises(RecipeValidationError):
                await self.selected({"settings": settings})
        self.read.assert_not_awaited()

    async def test_program_and_test_envelope_are_not_silently_adapted(self):
        for program, temp, minutes in (("proof", 170, 1), ("unknown", 180, 7),
                                       ("airfry", 119, 1), ("airfry", 231, 1), ("airfry", 180, 61)):
            with self.assertRaises(BetaTestBlocked):
                await self.selected({"settings": {"program": program, "temperature_c": temp, "duration_minutes": minutes}})
        self.read.assert_not_awaited()

    async def test_owner_reported_dry_temperature_bounds_reject_outside_values_before_reading(self):
        for temperature in (34, 96, 120):
            with self.subTest(temperature=temperature):
                with self.assertRaisesRegex(BetaTestBlocked, "test_range"):
                    await self.selected({"settings": {"program": "dry", "temperature_c": temperature,
                                                       "duration_minutes": 360}})
        self.read.assert_not_awaited()
        self.hass.services.async_call.assert_not_awaited()

    async def test_owner_reported_dry_endpoints_can_be_prepared_without_sending(self):
        for temperature in (35, 95):
            with self.subTest(temperature=temperature):
                prepared = await self.selected({"settings": {"program": "dry", "temperature_c": temperature,
                                                            "duration_minutes": 360}})
                self.assertEqual(prepared["settings"], {"program": "dry", "temperature_c": temperature,
                                                       "duration_minutes": 360})
        self.hass.services.async_call.assert_not_awaited()

    async def test_model_and_upstream_temperature_intersection_blocks_before_device_read(self):
        for program, temperatures in (("airfry", (119, 231)), ("roast", (120, 174, 231)),
                                      ("bake", (79, 206)), ("grill", (159, 231, 240)),
                                      ("reheat", (39, 206))):
            for temperature in temperatures:
                with self.subTest(program=program, temperature=temperature):
                    with self.assertRaisesRegex(BetaTestBlocked, "test_range"):
                        await self.selected({"settings": {"program": program, "temperature_c": temperature,
                                                           "duration_minutes": 1}})
        for temperature in (29, 46):
            with self.assertRaisesRegex(BetaTestBlocked, "test_range"):
                await self.selected({"settings": {"program": "proof", "temperature_c": temperature,
                                                   "duration_minutes": 1}})
        self.read.assert_not_awaited()
        self.hass.services.async_call.assert_not_awaited()

    async def test_model_and_upstream_common_temperature_endpoints_allow_preparation_only(self):
        for program, temperatures in (("airfry", (120, 230)), ("roast", (175, 230)),
                                      ("bake", (80, 205)), ("grill", (160, 230)), ("reheat", (40, 205)), ("proof", (30, 31, 45))):
            for temperature in temperatures:
                with self.subTest(program=program, temperature=temperature):
                    prepared = await self.selected({"settings": {"program": program, "temperature_c": temperature,
                                                                "duration_minutes": 1}})
                    self.assertEqual(prepared["settings"]["temperature_c"], temperature)
                    self.assertEqual(prepared["settings"]["program"], program)
        self.hass.services.async_call.assert_not_awaited()

    async def test_missing_and_multiphase_recipes_cannot_be_sent(self):
        repo = await self.library()
        with self.assertRaisesRegex(BetaTestBlocked, "recipe_changed"):
            await self.selected({"recipe_id": "missing"})
        recipe = create_recipe("Two steps", program="airfry", temperature_c=170, duration_minutes=1)
        recipe = await repo.async_create(replace(recipe, phases=recipe.phases * 2))
        with self.assertRaisesRegex(BetaTestBlocked, "source"):
            await self.selected({"recipe_id": recipe.id})
        self.read.assert_not_awaited()

    async def test_all_seven_programs_on_both_zones_use_the_same_single_attempt_contract(self):
        for zone in (1, 2):
            for program, temp, minutes in (("airfry", 180, 7), ("roast", 190, 30),
                                           ("bake", 180, 6), ("grill", 205, 1),
                                           ("reheat", 70, 10), ("dry", 55, 10), ("proof", 35, 60)):
                with self.subTest(zone=zone, program=program):
                    prepared = await self.selected({"settings": {"program": program,
                        "temperature_c": temp, "duration_minutes": minutes}}, zone=zone)
                    self.hass.services.async_call.return_value["gesendet"].update(
                        programm=program, temperatur=temp, minuten=minutes, zone=zone)
                    self.assertEqual((await self.confirm(prepared["token"]))["outcome"], "accepted")
                    sent = self.hass.services.async_call.await_args.args[2]
                    self.assertEqual((sent["programm"], sent["zone"], sent["temperatur"], sent["minuten"]),
                                     (program, zone, temp, minutes))
                    self.assertTrue(sent["einmal"])
                    self.assertFalse(sent["bestaetigen"])
        self.assertEqual(self.hass.services.async_call.await_count, 14)

    async def test_recipe_write_in_progress_blocks_confirmation_without_waiting_for_write(self):
        entered, finish = asyncio.Event(), asyncio.Event()
        writing = False
        async def save(data):
            if writing:
                entered.set()
                await finish.wait()
        repo = RecipeRepository(AsyncMock(return_value=None), save)
        await repo.async_load()
        recipe = await repo.async_create(create_recipe("Rolls", program="airfry", temperature_c=180, duration_minutes=7))
        self.hass.data[DOMAIN]["repository"] = repo
        token = (await self.selected({"recipe_id": recipe.id}))["token"]
        writing = True
        task = asyncio.create_task(repo.async_update(replace(recipe, name="Renamed")))
        await entered.wait()
        try:
            with self.assertRaisesRegex(BetaTestBlocked, "recipe_changed"):
                await self.confirm(token)
        finally:
            finish.set()
            await task
        self.hass.services.async_call.assert_not_awaited()

    async def test_explicit_recovery_clears_latch_and_old_tokens_without_sending(self):
        old = (await self.prepare())["token"]
        self.sender.uncertain.add("device")
        result = await self.sender.recover("u1", "device", True, "context")
        self.assertEqual(result, {"rearmed": True, "transmitted": False})
        self.assertNotIn("device", self.sender.uncertain)
        self.assertNotIn(old, self.sender.pending)
        self.read.assert_awaited_with(self.hass, "device", 1, refresh=True, wait_for_report=True, context="context")
        self.hass.services.async_call.assert_not_awaited()
        await self.prepare()
        with self.assertRaisesRegex(BetaTestBlocked, "confirmation"):
            await self.confirm(old)

    async def test_recovery_refuses_inflight_active_batch_or_failed_fresh_read(self):
        self.sender.uncertain.add("device")
        self.sender.busy.add("device")
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.sender.recover("u1", "device", True, "context")
        self.sender.busy.clear()
        self.sender.batch_devices["device"] = "run"
        with self.assertRaisesRegex(BetaTestBlocked, "busy"):
            await self.sender.recover("u1", "device", True, "context")
        self.sender.batch_devices.clear()
        self.read.side_effect = BetaTestBlocked("zones")
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.sender.recover("u1", "device", True, "context")
        self.assertIn("device", self.sender.uncertain)
        self.hass.services.async_call.assert_not_awaited()

    async def test_recovery_requires_explicit_ack_current_admin_and_unchanged_snapshot(self):
        self.sender.uncertain.add("device")
        with self.assertRaisesRegex(BetaTestBlocked, "acknowledgement"):
            await self.sender.recover("u1", "device", False, "context")
        self.hass.auth.async_get_user.return_value.is_admin = False
        with self.assertRaisesRegex(BetaTestBlocked, "unauthorized"):
            await self.sender.recover("u1", "device", True, "context")
        self.hass.auth.async_get_user.return_value.is_admin = True
        self.read.return_value = Target("Kitchen", ("same",), lambda: False)
        with self.assertRaisesRegex(BetaTestBlocked, "state_changed"):
            await self.sender.recover("u1", "device", True, "context")
        self.assertIn("device", self.sender.uncertain)

    async def test_numeric_adapter_rejection_code_is_exposed_without_raw_errors(self):
        token = (await self.prepare())["token"]
        self.hass.services.async_call.return_value = {
            "ok": False, "ergebnis": "abgelehnt", "code": 11912000, "fehler": "private"}
        result = await self.confirm(token)
        self.assertEqual(result["outcome"], "rejected")
        self.assertEqual(result["error_code"], 11912000)
        self.assertNotIn("private", str(result))


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.reported = datetime.now(timezone.utc)
        self.zones = {i: NS(status="bereit", active=False) for i in (1, 2)}
        self.fryer = NS(model="CAF-DC111S-AEU", online=True, last_error=None,
                        last_report=self.reported, revision=7,
                        state=NS(status="bereit", active=False, sync_type=0,
                                 temp_unit="celsius", zones=self.zones))
        self.runtime = NS(fryers={"cloud-private": self.fryer})
        self.entry = NS(entry_id="entry", runtime_data=self.runtime)
        self.device = NS(id="ha-device", name="Kitchen", name_by_user=None,
                         model=self.fryer.model, disabled_by=None,
                         identifiers={("airfryer_control", "cloud-private")}, config_entries={"entry"})
        self.registry = NS(async_get=Mock(return_value=self.device))
        self.integration = NS(version="1.0.3-beta.3")
        self.payload = {"programme": {"airfry": {"temperatur": [120, 205], "minuten": [1, 60],
                        "grenzen": "geschaetzt", "senden": "ungeprueft"}}, "verbindung": "ok",
                        "letzte_meldung": self.reported.isoformat(), "revision": 7}
        self.hass = NS(config_entries=NS(async_loaded_entries=Mock(return_value=[self.entry])),
                       services=NS(has_service=Mock(return_value=True),
                                   async_call=AsyncMock(return_value=self.payload)),
                       states=NS(get=Mock(return_value=NS(state="ready"))))
        helpers = ModuleType("homeassistant.helpers")
        dr = ModuleType("homeassistant.helpers.device_registry")
        dr.async_get = lambda hass: self.registry
        helpers.device_registry = dr
        er = ModuleType("homeassistant.helpers.entity_registry")
        self.entities = [NS(entity_id="sensor.airfryer_status", platform="airfryer_control",
                            config_entry_id="entry", disabled_by=None)]
        er.async_get = lambda hass: "registry"
        er.async_entries_for_device = Mock(side_effect=lambda registry, device_id: self.entities)
        helpers.entity_registry = er
        loader = ModuleType("homeassistant.loader")
        loader.async_get_integration = AsyncMock(return_value=self.integration)
        p = patch.dict(sys.modules, {"homeassistant.helpers": helpers,
                                    "homeassistant.helpers.device_registry": dr,
                                    "homeassistant.helpers.entity_registry": er,
                                    "homeassistant.loader": loader})
        p.start()
        self.addCleanup(p.stop)

    async def read(self, zone=1):
        return await read_target(self.hass, "ha-device", zone)

    async def test_reviewed_beta_owner_limits_and_proof_step_require_exact_current_report(self):
        from custom_components.airfryer_recipes.beta_send import VERSION, REVIEWED_COMMIT
        fixture=json.loads((Path(__file__).parent/'fixtures/airfryer_control_1_0_3_beta_3.json').read_text())
        self.assertEqual(fixture['adapter_version'],VERSION)
        self.assertEqual(fixture['reviewed_commit'],REVIEWED_COMMIT)
        self.payload.update(fixture['capabilities'],letzte_meldung=self.reported.isoformat(),revision=7)
        for zone in (1,2):
            for program,temp in [('airfry',230),('roast',230),('grill',160),('grill',230),('proof',30),('proof',31),('proof',45)]:
                target=await read_target(self.hass,'ha-device',zone,settings=CookingPhase(program,temp,1))
                self.assertTrue(target.unchanged())
        for step in [None,True,5]:
            self.payload['programme']['proof']['temperatur_schritt']=step
            with self.assertRaisesRegex(BetaTestBlocked,'capabilities'):
                await read_target(self.hass,'ha-device',1,settings=CookingPhase('proof',31,1))
        self.assertTrue(all(c.args[1]=='faehigkeiten' for c in self.hass.services.async_call.await_args_list))

    async def test_reviewed_stable_and_beta_keep_single_zone_read_guards(self):
        for version in ('1.0.3','1.0.4-beta.1'):
            self.integration.version=version
            target=await self.read()
            self.assertIn(version,target.fingerprint)
            self.assertTrue(target.unchanged())

    async def test_unreviewed_adapter_releases_are_blocked_before_any_service_call(self):
        for version in ['1.0.2-beta.1','1.0.2','1.0.3-beta.1','1.0.3-beta.2','1.0.4-beta.2','1.0.4']:
            self.integration.version=version
            with self.assertRaisesRegex(BetaTestBlocked,'adapter_version'):await self.read()
        self.hass.services.async_call.assert_not_awaited()

    async def test_complete_temperature_batch_uses_real_sender_and_fresh_state_validation(self):
        from custom_components.airfryer_recipes.beta_batch import BatchRunner
        fixture=json.loads((Path(__file__).parent/'fixtures/airfryer_control_1_0_3_beta_3.json').read_text())
        self.payload.update(fixture['capabilities'],letzte_meldung=self.reported.isoformat(),revision=7)
        self.hass.auth=NS(async_get_user=AsyncMock(return_value=NS(is_admin=True,is_active=True)))
        self.hass.data={DOMAIN:{}}
        transmitted=[]
        async def call(domain,service,data,**kwargs):
            if (domain,service)==('homeassistant','update_entity'):
                self.fryer.last_report=datetime.now(timezone.utc)
                self.fryer.revision+=1
                self.payload.update(letzte_meldung=self.fryer.last_report.isoformat(),revision=self.fryer.revision)
            elif (domain,service)==('airfryer_control','faehigkeiten'):
                return self.payload
            elif (domain,service)==('switch','turn_off'):
                zone=int(data['entity_id'][-1]);self.zones[zone].status='bereit'
                self.fryer.state.status='wartet_auf_start' if any(z.status=='wartet_auf_start' for z in self.zones.values()) else 'bereit'
            elif (domain,service)==('airfryer_control','programm_senden'):
                self.assertTrue(data['einmal']);self.assertTrue(data['streng'])
                self.assertFalse(data['bestaetigen']);self.assertEqual(data['variante'],'multi_app')
                transmitted.append((data['zone'],data['programm'],data['temperatur']))
                zone=self.zones[data['zone']];zone.status='wartet_auf_start'
                zone.mode=data['programm'].capitalize();zone.set_temp=data['temperatur'];zone.set_time_s=data['minuten']*60
                self.fryer.state.status='wartet_auf_start'
                return {'ok':True,'ergebnis':'angenommen','versuche':1,'variante':'multi_app',
                        'gesendet':{k:data[k] for k in ['programm','temperatur','minuten','zone']}}
            else:self.fail('Unexpected service')
        self.hass.services.async_call=AsyncMock(side_effect=call)
        sender=BetaSender(self.hass);self.hass.data[DOMAIN]['beta_sender']=sender
        batch=BatchRunner(sender);owner=object()
        with patch('custom_components.airfryer_recipes.beta_batch.zone_switch',side_effect=lambda h,d,e,z:f'switch.zone{z}'):
            plan=await batch.prepare('admin',owner,'ha-device','context')
            self.assertFalse(transmitted)
            run=await batch.start('admin',owner,plan['token'],True)
            nonce=run['next_token']
            while nonce:
                result=await batch.next('admin',owner,run['run_id'],nonce,'context')
                nonce=result['next_token']
        self.assertEqual(len(transmitted),44)
        self.assertIn((1,'proof',31),transmitted);self.assertIn((2,'grill',160),transmitted)
        self.assertEqual(result['completed'],44);self.assertTrue(result['reported_values_match'])
        self.assertFalse(sender.uncertain)
        self.assertTrue(all(z.active is False for z in self.zones.values()))

    async def test_both_zones_and_no_control_calls(self):
        for zone in (1, 2):
            target = await self.read(zone)
            self.assertTrue(target.unchanged())
            self.assertNotIn("cloud-private", str(target.fingerprint))
        self.assertTrue(all(c.args[1] == "faehigkeiten" for c in self.hass.services.async_call.await_args_list))

    async def test_unverified_program_is_only_allowed_inside_fixed_test_envelope(self):
        await self.read()
        del self.payload["programme"]["airfry"]
        with self.assertRaisesRegex(BetaTestBlocked, "capabilities"):
            await self.read()

    async def test_other_models_versions_and_zones_block(self):
        for zone in (True, 0, 3, "1"):
            with self.assertRaisesRegex(BetaTestBlocked, "target"):
                await self.read(zone)
        self.integration.version = "1.0.1"
        with self.assertRaisesRegex(BetaTestBlocked, "adapter_version"):
            await self.read()
        self.integration.version = "1.0.3-beta.3"
        self.device.model = "Other"
        with self.assertRaisesRegex(BetaTestBlocked, "model"):
            await self.read()

    async def test_stale_future_naive_and_mismatched_report_block(self):
        for stamp in (self.reported - timedelta(seconds=16), self.reported + timedelta(seconds=1),
                      self.reported.replace(tzinfo=None), None):
            self.fryer.last_report = stamp
            with self.assertRaisesRegex(BetaTestBlocked, "freshness"):
                await self.read()
        self.fryer.last_report = self.reported
        self.payload["revision"] = 8
        with self.assertRaisesRegex(BetaTestBlocked, "freshness"):
            await self.read()

    async def test_unknown_connection_and_active_other_zone_block(self):
        self.payload["verbindung"] = "fehler"
        with self.assertRaisesRegex(BetaTestBlocked, "connection"):
            await self.read()
        self.payload["verbindung"] = "ok"
        for status in ("gart", "pausiert", "schublade_offen", "wartet_auf_start", "unknown"):
            self.zones[2].status = status
            with self.assertRaisesRegex(BetaTestBlocked, "zones"):
                await self.read()

    async def test_missing_zones_sync_unknown_and_fahrenheit_block(self):
        self.fryer.state.sync_type = None
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.sync_type = 1
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.sync_type = 0
        self.fryer.state.temp_unit = "fahrenheit"
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()
        self.fryer.state.temp_unit = "celsius"
        del self.zones[2]
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()

    async def test_guard_catches_changes_after_async_read(self):
        target = await self.read()
        self.fryer.last_error = "new error"
        self.assertFalse(target.unchanged())
        self.fryer.last_error = None
        self.fryer.state.zones[2].status = "gart"
        self.assertFalse(target.unchanged())

    async def refreshing_read(self):
        return await read_target(self.hass, "ha-device", 1, refresh=True, context="admin-context")

    async def test_stale_report_is_refreshed_through_one_public_read_only_call(self):
        self.fryer.last_report = self.reported - timedelta(seconds=90)
        async def service(domain, name, data, **kwargs):
            if (domain, name) == ("homeassistant", "update_entity"):
                self.fryer.last_report = datetime.now(timezone.utc)
                self.payload["letzte_meldung"] = self.fryer.last_report.isoformat()
                return None
            return self.payload
        self.hass.services.async_call.side_effect = service
        target = await self.refreshing_read()
        self.assertTrue(target.unchanged())
        calls = self.hass.services.async_call.await_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args, ("homeassistant", "update_entity",
                                       {"entity_id": ["sensor.airfryer_status"]}))
        self.assertEqual(calls[0].kwargs, {"blocking": True, "context": "admin-context"})
        self.assertEqual(calls[1].args[1], "faehigkeiten")
        self.assertFalse(any(c.args[1] == "programm_senden" for c in calls))

    async def test_refresh_returning_without_new_report_is_rejected_even_if_cache_is_recent(self):
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_failed"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_awaited_once()

    async def test_refresh_timeout_does_not_retry_or_expose_exception(self):
        self.hass.services.async_call.side_effect = TimeoutError("private")
        with self.assertRaisesRegex(BetaTestBlocked, "^refresh_failed$"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_awaited_once()

    async def test_refresh_requires_loaded_enabled_upstream_sensor_from_selected_entry(self):
        self.entities[:] = [
            NS(entity_id="button.control", platform="airfryer_control", config_entry_id="entry", disabled_by=None),
            NS(entity_id="sensor.other", platform="other", config_entry_id="entry", disabled_by=None),
            NS(entity_id="sensor.wrong_entry", platform="airfryer_control", config_entry_id="other", disabled_by=None),
            NS(entity_id="sensor.disabled", platform="airfryer_control", config_entry_id="entry", disabled_by="user"),
        ]
        with self.assertRaisesRegex(BetaTestBlocked, "refresh_unavailable"):
            await self.refreshing_read()
        self.hass.services.async_call.assert_not_awaited()

    async def test_read_without_refresh_does_not_invoke_update_service(self):
        await self.read()
        self.hass.services.async_call.assert_awaited_once_with(
            "airfryer_control", "faehigkeiten", {"geraet": "ha-device"},
            blocking=True, return_response=True)

    async def test_selected_values_must_fit_reported_limits_as_well_as_test_envelope(self):
        await read_target(self.hass, "ha-device", 1, settings=CookingPhase("airfry", 180, 7))
        self.payload["programme"]["airfry"]["temperatur"] = [120, 175]
        with self.assertRaisesRegex(BetaTestBlocked, "capabilities"):
            await read_target(self.hass, "ha-device", 1, settings=CookingPhase("airfry", 180, 7))

    async def test_all_program_bounds_require_actual_report_and_known_provenance(self):
        from custom_components.airfryer_recipes.beta_send import REVIEWED_PROGRAM_LIMITS, MODEL_TEMPERATURE_LIMITS
        for program, (low, high, minutes) in REVIEWED_PROGRAM_LIMITS.items():
            self.payload["programme"] = {program: {"temperatur": [low, high], "minuten": [1, minutes],
                "grenzen": "besitzer", "senden": "ungeprueft", "temperatur_schritt": 1 if program == "proof" else 5}}
            model_low, model_high = MODEL_TEMPERATURE_LIMITS[program]
            allowed_low, allowed_high = max(low, model_low), min(high, model_high)
            for zone in (1, 2):
                for temp, duration in ((allowed_low, 1), (allowed_high, minutes)):
                    await read_target(self.hass, "ha-device", zone,
                                      settings=CookingPhase(program, temp, duration))
            self.payload["programme"][program]["grenzen"] = "unknown-source"
            with self.assertRaisesRegex(BetaTestBlocked, "capabilities"):
                await read_target(self.hass, "ha-device", 1, settings=CookingPhase(program, allowed_low, 1))
        self.assertTrue(all(call.args[1] == "faehigkeiten" for call in self.hass.services.async_call.await_args_list))

    async def test_batch_can_only_replace_prepared_values_owned_and_verified_by_that_run(self):
        previous = CookingPhase("airfry", 170, 1)
        self.fryer.state.status = "wartet_auf_start"
        self.zones[1].status = "wartet_auf_start"
        self.zones[1].mode = "AirFry"
        self.zones[1].set_temp = 170
        self.zones[1].set_time_s = 60
        target = await read_target(self.hass, "ha-device", 2, prepared_zones={1: previous})
        self.assertTrue(target.unchanged())
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await self.read()  # Individual sending still blocks prepared zones.
        self.zones[1].set_temp = 180
        self.assertFalse(target.unchanged())
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await read_target(self.hass, "ha-device", 2, prepared_zones={1: previous})
        self.zones[1].set_temp = 170
        self.zones[1].active = True
        with self.assertRaisesRegex(BetaTestBlocked, "zones"):
            await read_target(self.hass, "ha-device", 2, prepared_zones={1: previous})

    async def test_batch_waits_for_debounced_read_without_repeating_service_call(self):
        async def deferred_report(*args):
            self.fryer.last_report = datetime.now(timezone.utc)
            self.payload["letzte_meldung"] = self.fryer.last_report.isoformat()
        with patch("custom_components.airfryer_recipes.beta_send.asyncio.sleep", side_effect=deferred_report) as sleep:
            await read_target(self.hass, "ha-device", 1, refresh=True, context="admin", wait_for_report=True)
        sleep.assert_awaited_once()
        self.assertEqual(self.hass.services.async_call.await_count, 2)  # One update and one capability read.
