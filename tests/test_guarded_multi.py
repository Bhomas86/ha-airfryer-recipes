"""Own final HTTP-boundary guard, with actual pinned controller transport methods.

No real HA/controller/cloud. HTTP is AsyncMock; tokens are fake constants.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, patch

from custom_components.airfryer_recipes.beta_send import BetaSender, BetaTestBlocked
from custom_components.airfryer_recipes.const import DOMAIN
from custom_components.airfryer_recipes.guarded_multi import MultiSender, safe_report, build_payload, GuardedTransport
from custom_components.airfryer_recipes.recipe_model import CookingPhase

PHASES = {'1': CookingPhase(program='airfry',temperature_c=180,duration_minutes=7),
          '2': CookingPhase(program='roast',temperature_c=190,duration_minutes=10)}

def load_api():
    env = {'AirfryerError':type('UpstreamError',(Exception,),{}),'AirfryerAuthError':type('AuthError',(Exception,),{}),
           'AirfryerDeviceOffline':type('Offline',(Exception,),{}), 'AUTH_ERROR_CODES':{-11001000},
           'CODE_OK':0,'CODE_DEVICE_OFFLINE':9999,'CODE_DEVICE_TIMEOUT':9998,
           'APP_VERSION_FULL':'test','PHONE_BRAND':'test','PHONE_OS':'test'}
    source = (Path(__file__).parent/'fixtures/controller_103_transport.py.txt').read_text()
    exec(compile('from __future__ import annotations\n'+source,'actual-controller-transport','exec'),env)
    return env['ReviewedAPI']


def api_instance():
    api=load_api()()
    for k,v in {'_lang':'en','_account_id':'fake','account_id':'fake','_current_region':'US',
                '_time_zone':'UTC','_token':'fake','_country_code':'US','base_url':'https://example.invalid'}.items():
        setattr(api,k,v)
    api._trace=lambda:'fake'
    api._ensure_login=AsyncMock()
    api._post=AsyncMock(return_value={'code':0,'result':{'code':0}})
    return api


def fryer():
    return NS(model='CAF-DC111S-AEU',online=True,last_error=None,last_report=datetime.now(timezone.utc),revision=1,
        state=NS(active=False,status='bereit',temp_unit='celsius',sync_type=0,
                 zones={1:NS(active=False,status='bereit'),2:NS(active=False,status='bereit')}))


class ReportTests(unittest.TestCase):
    def test_missing_unknown_busy_and_malformed_reports_rejected(self):
        mutations=[lambda f:f.state.zones.pop(2), lambda f:setattr(f.state.zones[1],'status','unbekannt'),
                   lambda f:setattr(f.state.zones[1],'active',True),lambda f:setattr(f,'last_error','failure'),
                   lambda f:setattr(f,'online',False),lambda f:setattr(f.state,'active',None),
                   lambda f:setattr(f.state,'sync_type',True),lambda f:setattr(f,'revision',True),
                   lambda f:setattr(f,'last_report',datetime.now(timezone.utc)-timedelta(seconds=16)),
                   lambda f:setattr(f,'last_report',datetime.now()),lambda f:setattr(f.state,'temp_unit','fahrenheit')]
        for mutate in mutations:
            f=fryer(); mutate(f)
            with self.assertRaises(BetaTestBlocked): safe_report(f)

    def test_exact_prepare_only_payload_matches_reviewed_app_form(self):
        p=build_payload('sync',PHASES,'fake')
        self.assertIs(p['readyStart'],True)
        self.assertEqual(p['syncType'],2)
        self.assertEqual(p['workChamber'],4)
        self.assertEqual([c['mode'] for c in p['cookConfigs']],['AirFry','Roast'])
        self.assertEqual([c['holdTime'] for c in p['cookConfigs']],[180,0])
        p=build_payload('match',{'1':PHASES['1'],'2':PHASES['1']},'fake')
        self.assertEqual(p['syncType'],1)
        self.assertTrue(all('holdTime' not in c for c in p['cookConfigs']))


class MultiSenderTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.hass=NS(data={DOMAIN:{}},is_stopping=False)
        self.parent=BetaSender(self.hass);self.hass.data[DOMAIN]['beta_sender']=self.parent
        self.sender=MultiSender(self.hass,self.parent)
        self.sender.authorize=AsyncMock(return_value=('grant',1))
        self.connection=NS(user=NS(id='user'),subscriptions={})
        self.api=api_instance();self.f=fryer()
        self.binding=NS(api=self.api,info={'cid':'fake-device'},fingerprint=safe_report(self.f))
        def check():
            require=safe_report(self.f)
            if require != self.binding.fingerprint: raise BetaTestBlocked('state_changed')
            return require
        self.binding.check=check
        self.bind=AsyncMock(return_value=self.binding)
        self.read_patch=patch('custom_components.airfryer_recipes.guarded_multi.bind',self.bind)
        self.read_patch.start();self.addCleanup(self.read_patch.stop)
        self.resolve=patch('custom_components.airfryer_recipes.guarded_multi.resolve_sources',AsyncMock(return_value=(PHASES,[])))
        self.resolve.start();self.addCleanup(self.resolve.stop)

    async def prepare(self,dry=False):
        return await self.sender.prepare(self.connection,'device','sync',{},dry)

    async def test_dry_run_is_enforced_server_side_and_allocates_no_permit(self):
        result=await self.prepare(True)
        self.assertNotIn('token',result);self.assertFalse(result['transmitted'])
        self.assertEqual(self.sender.pending,{})
        self.api._post.assert_not_called()

    async def test_exact_one_http_write_with_confirmation_and_no_controller_mutation(self):
        before=dict(self.api.__dict__)
        token=(await self.prepare())['token']
        result=await self.sender.confirm(self.connection,token,True)
        self.assertEqual(result['outcome'],'accepted')
        self.assertFalse(result['confirmed_on_device'])
        self.api._post.assert_awaited_once()
        self.assertEqual(self.api.__dict__,before)
        body=self.api._post.call_args.args[1]
        self.assertEqual(body['payload']['method'],'startMultiCook')
        self.assertIs(body['payload']['data']['readyStart'],True)
        self.assertEqual(self.connection.subscriptions,{})
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.assertEqual(self.api._post.await_count,1)

    async def test_missing_zone_after_login_is_blocked_at_http_boundary(self):
        token=(await self.prepare())['token']
        async def login(): self.f.state.zones.pop(2)
        self.api._ensure_login.side_effect=login
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()
        self.assertNotIn('device',self.parent.uncertain)

    async def test_unknown_after_login_is_also_blocked(self):
        token=(await self.prepare())['token']
        async def login(): self.f.state.zones[2].status='unbekannt'
        self.api._ensure_login.side_effect=login
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()

    async def test_auth_revocation_during_login_is_checked_again(self):
        token=(await self.prepare())['token']
        async def login(): self.sender.authorize.return_value=('grant',2)
        self.api._ensure_login.side_effect=login
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()

    async def test_disconnect_during_login_cancels_inflight_permit(self):
        token=(await self.prepare())['token']
        async def login():
            for cleanup in tuple(self.connection.subscriptions.values()): cleanup()
        self.api._ensure_login.side_effect=login
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()

    async def test_expired_token_wrong_connection_and_device_lock_do_not_send(self):
        token=(await self.prepare())['token']
        other=NS(user=NS(id='user'),subscriptions={})
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(other,token,True)
        self.sender.pending[token]['expires']=0
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        token=(await self.prepare())['token'];self.parent.busy.add('device')
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()

    async def test_unknown_write_never_retries_and_latch_survives_reload(self):
        token=(await self.prepare())['token']
        self.api._post.side_effect=OSError('PRIVATE RAW ERROR')
        result=await self.sender.confirm(self.connection,token,True)
        self.assertEqual(result['outcome'],'unknown')
        self.assertNotIn('PRIVATE',str(result))
        self.api._post.assert_awaited_once()
        self.assertIn('device',self.parent.uncertain)
        with self.assertRaises(BetaTestBlocked): await self.prepare()
        self.assertIn('device',BetaSender(self.hass).uncertain)

    async def test_history_failure_after_acceptance_does_not_repeat(self):
        self.hass.data[DOMAIN]['sent_settings']=NS(record=AsyncMock(side_effect=OSError('storage')))
        token=(await self.prepare())['token']
        result=await self.sender.confirm(self.connection,token,True)
        self.assertEqual(result['outcome'],'accepted');self.assertFalse(result['history_saved'])
        self.api._post.assert_awaited_once()

    async def test_recovery_requires_ack_and_fresh_safe_read_and_sends_nothing(self):
        self.parent.uncertain.add('device')
        with self.assertRaises(BetaTestBlocked): await self.sender.recover(self.connection,'device',False)
        await self.sender.recover(self.connection,'device',True)
        self.assertNotIn('device',self.parent.uncertain)
        self.api._post.assert_not_called()

    async def test_repeated_post_even_within_transport_is_blocked(self):
        checks=AsyncMock();mark=lambda:None
        transport=GuardedTransport(self.api,{'cid':'fake'},build_payload('sync',PHASES,'fake'),checks,mark)
        await transport.send()
        with self.assertRaises(BetaTestBlocked): await transport.send()
        self.api._post.assert_awaited_once()

    async def test_login_failure_before_device_write_is_sanitized(self):
        token=(await self.prepare())['token']
        self.api._ensure_login.side_effect=OSError('PRIVATE LOGIN FAILURE')
        with self.assertRaisesRegex(BetaTestBlocked,'adapter_data'):
            await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()
        self.assertNotIn('device',self.parent.uncertain)

    async def test_auth_error_and_malformed_success_never_retry_or_clear_latch(self):
        for code in (-11001000, False):
            self.parent.uncertain.clear()
            self.api._post.reset_mock()
            self.api._post.return_value={'code':code}
            token=(await self.prepare())['token']
            result=await self.sender.confirm(self.connection,token,True)
            self.assertEqual(result['outcome'],'unknown')
            self.assertIn('device',self.parent.uncertain)
            self.api._post.assert_awaited_once()

    async def test_cancel_and_unload_before_write_do_not_reach_http(self):
        token=(await self.prepare())['token']
        await self.sender.cancel(self.connection,token)
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        token=(await self.prepare())['token']
        async def login():
            self.parent.closed=True
            self.sender.close()
        self.api._ensure_login.side_effect=login
        with self.assertRaises(BetaTestBlocked): await self.sender.confirm(self.connection,token,True)
        self.api._post.assert_not_called()


class BindingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import sys
        self.sys=sys
        self.f=fryer();self.f.info={'cid':'fake'}
        self.api=api_instance()
        self.runtime=NS(api=self.api,fryers={'fake':self.f})
        async def refresh(): self.f.last_report=datetime.now(timezone.utc)
        self.runtime.async_refresh=AsyncMock(side_effect=refresh)
        self.entry=NS(entry_id='entry',runtime_data=self.runtime)
        self.device=NS(disabled_by=None,model='CAF-DC111S-AEU',identifiers={('airfryer_control','fake')},config_entries={'entry'})
        self.registry=NS(async_get=lambda _:self.device)
        loader=NS(async_get_integration=AsyncMock(return_value=NS(version='1.0.3')))
        helpers=NS(device_registry=NS(async_get=lambda _:self.registry))
        self.patch=patch.dict(sys.modules,{'homeassistant.helpers':helpers,'homeassistant.loader':loader})
        self.patch.start();self.addCleanup(self.patch.stop)
        async def capabilities(*args,**kwargs):
            return {'programme':{p:{'temperatur':[120,230],'minuten':[1,60],'temperatur_schritt':5} for p in ('airfry','roast')},
                    'verbindung':'ok','revision':self.f.revision,'letzte_meldung':self.f.last_report.isoformat()}
        self.hass=NS(is_stopping=False,config_entries=NS(async_loaded_entries=lambda _:[self.entry]),
                     services=NS(async_call=AsyncMock(side_effect=capabilities)))

    async def test_real_binding_refreshes_only_reads_and_rechecks_runtime_identity(self):
        from custom_components.airfryer_recipes.guarded_multi import bind
        binding=await bind(self.hass,'device',PHASES,True)
        binding.check()
        self.runtime.async_refresh.assert_awaited_once()
        self.assertEqual(self.hass.services.async_call.call_args.args[:2],('airfryer_control','faehigkeiten'))
        self.runtime.api=api_instance()
        with self.assertRaises(BetaTestBlocked): binding.check()
        self.api._post.assert_not_called()

    async def test_missing_zone_after_actual_refresh_is_blocked(self):
        from custom_components.airfryer_recipes.guarded_multi import bind
        async def refresh():
            self.f.last_report=datetime.now(timezone.utc)
            self.f.state.zones.pop(2)
        self.runtime.async_refresh.side_effect=refresh
        with self.assertRaises(BetaTestBlocked): await bind(self.hass,'device',PHASES,True)
        self.hass.services.async_call.assert_not_called()
        self.api._post.assert_not_called()

    async def test_unchanged_old_refresh_cannot_fabricate_freshness(self):
        from custom_components.airfryer_recipes.guarded_multi import bind
        self.runtime.async_refresh.side_effect=None
        with self.assertRaises(BetaTestBlocked): await bind(self.hass,'device',PHASES,True)
        self.api._post.assert_not_called()
