"""Simulated guided runs: no appliance/network access."""
import unittest
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch
from custom_components.airfryer_recipes.beta_send import BetaSender, BetaTestBlocked, Target, REVIEWED_PROGRAM_LIMITS
from custom_components.airfryer_recipes.beta_batch import BatchRunner
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.device_discovery import normalize_capabilities


class BatchTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass = NS(services=NS(async_call=AsyncMock()), data={DOMAIN: {}}, auth=NS(async_get_user=AsyncMock(return_value=NS(is_admin=True,is_active=True))))
        self.sender = BetaSender(self.hass)
        self.hass.data[DOMAIN]['beta_sender'] = self.sender
        payload = json.loads((Path(__file__).parent/'fixtures/airfryer_control_1_0_3_beta_3.json').read_text())['capabilities']
        programs = normalize_capabilities(payload)['programs']
        metadata = tuple((p['id'],p['temperature_c']['min'],p['temperature_c']['max'],
                          p['duration_minutes']['min'],p['duration_minutes']['max'],
                          p['limits_status'],p['send_status'],p['temperature_step_c']) for p in programs)
        self.target = Target('Fixture', ('entry',1,2,'time',1,((1,'idle'),(2,'idle')),metadata,'model','version'))
        self.sender._read = AsyncMock(return_value=self.target)
        self.sender.send_once = AsyncMock(return_value={'outcome':'accepted'})
        self.batch = BatchRunner(self.sender)
        self.owner = NS(subscriptions={})
        reset = patch("custom_components.airfryer_recipes.beta_batch.zone_switch",
                      side_effect=lambda h, d, e, z: f"switch.fixture_zone_{z}")
        self.resolve_reset = reset.start()
        self.addCleanup(reset.stop)

    async def start(self):
        self.plan = await self.batch.prepare('u', self.owner, 'device', 'context')
        return await self.batch.start('u', self.owner, self.plan['token'], True)

    async def step(self, run):
        result = await self.batch.next('u',self.owner,run['run_id'],run['next_token'],'context')
        run['next_token'] = result['next_token']
        return result

    async def test_full_44_step_run_covers_temperature_bounds_and_proof_without_start(self):
        run = await self.start()
        self.assertEqual(len(self.plan['steps']),44)
        self.assertEqual([step for step in self.plan['steps'] if step['settings']['program'] == 'dry'],
                         [{'zone_id': zone, 'settings': {'program': 'dry', 'temperature_c': temp,
                                                        'duration_minutes': 360}} for temp in (35,55,95) for zone in (1, 2)])
        self.sender.send_once.assert_not_awaited()
        for i in range(44):
            result = await self.step(run)
            self.assertEqual(result['completed'],i+1)
            self.assertEqual(result['done'],i==43)
            self.assertTrue(result['reported_values_match'])
        self.assertEqual(self.sender.send_once.await_count,44)
        actual=[(c.args[1],c.args[2].program,c.args[2].temperature_c) for c in self.sender.send_once.await_args_list]
        self.assertEqual(len(set(actual)),44)
        for program,(low,high,_) in REVIEWED_PROGRAM_LIMITS.items():
            for zone in (1,2):
                self.assertIn((zone,program,low),actual)
                self.assertIn((zone,program,high),actual)
        for zone in (1,2): self.assertIn((zone,'proof',31),actual)
        self.assertNotIn('device',self.sender.batch_devices)
        self.assertEqual(self.sender._read.await_count,131)
        calls = self.hass.services.async_call.await_args_list
        self.assertEqual(len(calls), 42)  # End both zones before each of 21 setting changes.
        self.assertEqual([c.args[2]["entity_id"] for c in calls],
                         ["switch.fixture_zone_1", "switch.fixture_zone_2"] * 21)
        self.assertTrue(all(c.args[:2] == ("switch", "turn_off") for c in calls))
        self.assertEqual([(c.args[1], c.args[2].temperature_c, c.args[2].duration_minutes)
                          for c in self.sender.send_once.await_args_list if c.args[2].program == 'dry'],
                         [(z, t, 360) for t in (35,55,95) for z in (1,2)])

    async def test_missing_program_is_explicitly_skipped_without_substitution(self):
        f=list(self.target.fingerprint);f[6]=tuple(p for p in f[6] if p[0]!='dry')
        self.sender._read.return_value=Target('Fixture',tuple(f))
        run=await self.start()
        self.assertEqual(run['total'],38)
        self.assertEqual(self.plan['skipped'],['dry'])

    async def test_old_temperature_report_skips_whole_program_not_just_its_new_upper_bound(self):
        f=list(self.target.fingerprint)
        f[6]=tuple((p[:2]+(205,)+p[3:]) if p[0]=='airfry' else p for p in f[6])
        self.sender._read.return_value=Target('Fixture',tuple(f))
        run=await self.start()
        self.assertEqual(run['total'],38)
        self.assertEqual(self.plan['skipped'],['airfry'])
        self.assertFalse(any(s['settings']['program']=='airfry' for s in self.plan['steps']))

    async def test_proof_only_plan_still_requires_resets_between_temperature_pairs(self):
        f=list(self.target.fingerprint);f[6]=tuple(p for p in f[6] if p[0]=='proof')
        self.sender._read.return_value=Target('Fixture',tuple(f))
        run=await self.start()
        self.assertEqual(run['total'],8)
        self.assertTrue(self.plan['resets_between_settings'])
        self.assertFalse(self.plan['resets_between_programs'])
        await self.step(run);await self.step(run);await self.step(run)
        self.assertEqual(self.hass.services.async_call.await_count,2)
        self.assertEqual(self.sender.send_once.await_args.args[2].temperature_c,31)

    async def test_proof_missing_one_degree_metadata_is_explicitly_skipped(self):
        f=list(self.target.fingerprint);f[6]=tuple(p[:7]+(5,) if p[0]=='proof' else p for p in f[6])
        self.sender._read.return_value=Target('Fixture',tuple(f))
        run=await self.start()
        self.assertEqual(run['total'],36)
        self.assertEqual(self.plan['skipped'],['proof'])

    async def test_false_ack_replay_and_other_connection_cannot_start_or_resume(self):
        plan=await self.batch.prepare('u',self.owner,'device','context')
        with self.assertRaisesRegex(BetaTestBlocked,'acknowledgement'):
            await self.batch.start('u',self.owner,plan['token'],False)
        run=await self.batch.start('u',self.owner,plan['token'],True)
        old=run['next_token']
        await self.step(run)
        with self.assertRaisesRegex(BetaTestBlocked,'confirmation'):
            await self.batch.next('u',self.owner,run['run_id'],old,'context')
        with self.assertRaisesRegex(BetaTestBlocked,'batch_connection'):
            await self.batch.next('u',NS(),run['run_id'],run['next_token'],'context')
        self.assertEqual(self.sender.send_once.await_count,1)

    async def test_stopping_during_read_prevents_control(self):
        run=await self.start()
        async def read(*a,**k):
            self.batch.stop(self.batch.runs[run['run_id']])
            return self.target
        self.sender._read.side_effect=read
        with self.assertRaises(BetaTestBlocked):await self.step(run)
        self.sender.send_once.assert_not_awaited()
        self.assertNotIn('device',self.sender.uncertain)

    async def test_stop_during_send_cannot_recall_command_but_blocks_following_steps(self):
        run=await self.start()
        async def send(*a,**k):
            self.batch.stop(self.batch.runs[run['run_id']])
            return {'outcome':'accepted'}
        self.sender.send_once.side_effect=send
        with self.assertRaisesRegex(BetaTestBlocked,'batch_stopped'):await self.step(run)
        self.assertIn('device',self.sender.uncertain)
        self.assertEqual(self.sender.send_once.await_count,1)

    async def test_unknown_transport_or_failed_readback_latches_and_never_retries(self):
        run=await self.start()
        self.sender.send_once.return_value={'outcome':'unknown'}
        with self.assertRaisesRegex(BetaTestBlocked,'outcome_unknown'):await self.step(run)
        self.assertEqual(self.sender.send_once.await_count,1)
        self.assertIn('device',self.sender.uncertain)

    async def test_readback_failure_does_not_offer_next_token(self):
        run=await self.start()
        self.sender._read.side_effect=[self.target,BetaTestBlocked('zones')]
        with self.assertRaisesRegex(BetaTestBlocked,'zones'):await self.step(run)
        self.assertIn('device',self.sender.uncertain)
        self.assertTrue(self.batch.runs[run['run_id']].stopped)
        self.assertIsNone(self.batch.runs[run['run_id']].nonce)

    async def test_active_batch_blocks_individual_sends_and_expired_pending_plan_cannot_unlock_it(self):
        old=await self.batch.prepare('u',self.owner,'device','context')
        run=await self.start()
        self.batch.stop(self.batch.runs[old['token']])
        self.assertEqual(self.sender.batch_devices['device'],run['run_id'])
        with self.assertRaisesRegex(BetaTestBlocked,'busy'):
            await self.sender.prepare('u','device',1,True,'context')
        self.sender.send_once.assert_not_awaited()

    async def test_lost_admin_or_adapter_change_stops_without_control(self):
        run=await self.start()
        f=list(self.target.fingerprint);f[1]=999
        self.sender._read.return_value=Target('Fixture',tuple(f))
        with self.assertRaisesRegex(BetaTestBlocked,'state_changed'):await self.step(run)
        self.sender.send_once.assert_not_awaited()

    async def test_unload_and_expired_run_cannot_continue(self):
        run=await self.start()
        self.batch.runs[run['run_id']].expires=0
        with self.assertRaisesRegex(BetaTestBlocked,'confirmation'):await self.step(run)
        self.sender.send_once.assert_not_awaited()

    async def test_rejection_reports_exact_failed_step_without_retry(self):
        run = await self.start()
        await self.step(run)
        await self.step(run)
        self.sender.send_once.return_value = {'outcome': 'rejected', 'error_code': 11912000}
        result = await self.step(run)
        self.assertTrue(result['stopped'])
        self.assertEqual(result['failed_step'], 3)
        self.assertEqual(result['settings']['program'], 'airfry')
        self.assertEqual(result['settings']['temperature_c'], 180)
        self.assertEqual(result['zone_id'], 1)
        self.assertEqual(result['error_code'], 11912000)
        self.assertEqual(self.sender.send_once.await_count, 3)

    async def test_reset_failure_stops_before_third_setting_and_does_not_retry(self):
        run = await self.start()
        await self.step(run); await self.step(run)
        self.hass.services.async_call.side_effect = TimeoutError('private')
        with self.assertRaisesRegex(BetaTestBlocked, 'reset_failed'):
            await self.step(run)
        self.assertEqual(self.sender.send_once.await_count, 2)
        self.hass.services.async_call.assert_awaited_once()
        self.assertIn('device', self.sender.uncertain)

    async def test_failed_reset_readback_stops_before_second_reset_or_setting(self):
        run = await self.start()
        await self.step(run); await self.step(run)
        self.sender._read.side_effect = [self.target, BetaTestBlocked('zones')]
        with self.assertRaisesRegex(BetaTestBlocked, 'zones'):
            await self.step(run)
        self.assertEqual(self.sender.send_once.await_count, 2)
        self.hass.services.async_call.assert_awaited_once()
        self.assertIn('device', self.sender.uncertain)

    async def test_stop_during_first_reset_prevents_second_reset_and_new_program(self):
        run = await self.start()
        await self.step(run); await self.step(run)
        async def reset(*args, **kwargs):
            self.batch.stop(self.batch.runs[run['run_id']])
        self.hass.services.async_call.side_effect = reset
        with self.assertRaisesRegex(BetaTestBlocked, 'batch_stopped'):
            await self.step(run)
        self.assertEqual(self.sender.send_once.await_count, 2)
        self.hass.services.async_call.assert_awaited_once()

    async def test_missing_zone_switch_prevents_offering_an_automatic_reset_plan(self):
        self.resolve_reset.side_effect = BetaTestBlocked('reset_unavailable')
        with self.assertRaisesRegex(BetaTestBlocked, 'reset_unavailable'):
            await self.start()
        self.assertEqual(self.batch.runs, {})
        self.sender.send_once.assert_not_awaited()
