"""Contract regressions and offline execution of pinned upstream functions."""
import ast
import copy
from datetime import datetime, timedelta, timezone
import pathlib
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, patch

from custom_components.airfryer_recipes.multi_contract import build_request, normalize_response, snapshot_blockers, describe_contract
from custom_components.airfryer_recipes.recipe_model import CookingPhase

ROOT = pathlib.Path(__file__).resolve().parents[1]
PHASES = {'1': CookingPhase(program='airfry', temperature_c=180, duration_minutes=7),
          '2': CookingPhase(program='roast', temperature_c=190, duration_minutes=10)}


class ContractTests(unittest.IsolatedAsyncioTestCase):
    def test_exact_request_cannot_reset_retry_or_use_implicit_values(self):
        request = build_request('device', 'sync', PHASES)
        self.assertEqual(request['service'], 'sync_senden')
        self.assertIs(request['data']['einmal'], True)
        self.assertIs(request['data']['streng'], True)
        self.assertIs(request['data']['zuruecksetzen'], False)
        self.assertEqual(request['data']['zone2'], {'programm':'roast','temperatur':190,'minuten':10})
        request['data']['zone1']['temperatur'] = 200
        self.assertEqual(PHASES['1'].temperature_c, 180)
        with self.assertRaises(ValueError): build_request('device', 'match', PHASES)
        match = build_request('device','match',{'1':PHASES['1'],'2':PHASES['1']})
        self.assertEqual(match['data']['zone1'],match['data']['zone2'])
        self.assertEqual(match['data']['quelle'],1)

    def test_response_accepts_only_consistent_exact_echo_and_never_returns_errors(self):
        request = build_request('device','sync',PHASES)
        response = {'art':'sync','revision_vorher':1,'ok':True,'ergebnis':'angenommen',
                    'gesendet':{k:request['data'][k] for k in ('zone1','zone2')}}
        self.assertEqual(normalize_response(response,request,'sync'),'accepted')
        mutations=[{'ok':False},{'art':'match'},{'revision_vorher':True},{'revision_vorher':-1},
                   {'ergebnis':'unbekannt'},{'gesendet':None}]
        for values in mutations:
            self.assertEqual(normalize_response({**response,**values},request,'sync'),'unknown')
        bad=copy.deepcopy(response);bad['gesendet']['zone1']['minuten']=7.0
        self.assertEqual(normalize_response(bad,request,'sync'),'unknown')
        self.assertEqual(normalize_response({'art':'sync','revision_vorher':1,'ok':False,
            'ergebnis':'abgelehnt','fehler':'PRIVATE ERROR'},request,'sync'),'rejected')

    def test_snapshot_rejects_missing_unknown_duplicate_stale_and_future_zones(self):
        now=datetime.now(timezone.utc)
        device={'model':'CAF-DC111S-AEU','connectivity':'reported_online','reported_at':now.isoformat(),
                'revision':1,'zones':[{'zone_id':1,'status':'idle'},{'zone_id':2,'status':'off'}]}
        self.assertEqual(snapshot_blockers(device,now),[])
        for zones in (device['zones'][:1], [device['zones'][0]]*2,
                      [{'zone_id':1,'status':'unknown'},device['zones'][1]]):
            self.assertTrue(snapshot_blockers({**device,'zones':zones},now))
        for stamp in (now-timedelta(seconds=16),now+timedelta(seconds=1),now.replace(tzinfo=None)):
            self.assertIn('freshness_unverified',snapshot_blockers({**device,'reported_at':stamp.isoformat()},now))
        self.assertIn('freshness_unverified',snapshot_blockers({**device,'revision':True},now))

    async def test_only_reviewed_versions_identified_and_none_enable_live(self):
        loader=NS(async_get_integration=AsyncMock())
        with patch.dict(sys.modules, {'homeassistant.loader':loader}):
            for version,expected in [('1.0.3',True),('1.0.4-beta.1',True),('future',False),('1.0.3-beta.3',False)]:
                loader.async_get_integration.return_value=NS(version=version)
                result=await describe_contract(NS())
                self.assertEqual(result['explicit_values'],expected)
                self.assertFalse(result['live_send_enabled'])
            loader.async_get_integration.side_effect=OSError('private')
            self.assertIsNone((await describe_contract(NS()))['reviewed_version'])


def controller_functions(patched):
    original=(ROOT/'tests/fixtures/controller_103_sync_functions.py.txt').read_text()
    if patched:
        # Apply the exact reviewed helper/hook additions from our proposed diff.
        lines=(ROOT/'docs/upstream/controller-sync-state-guard.patch').read_text().splitlines()
        added='\n'.join(l[1:] for l in lines if l.startswith('+') and not l.startswith('+++'))
        helper_text='\n'.join(l for l in added.splitlines() if not l.lstrip().startswith('_require_sync_report(fryer,'))
        module=ast.parse(helper_text)
        helper=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='_require_sync_report')
        original=ast.unparse(helper)+'\n\n'+original
        original=original.replace('    todo = [z for z in zones if states[z] in PREPARED]',
            '    _require_sync_report(fryer, allow_prepared=True)\n    todo = [z for z in zones if states[z] in PREPARED]')
        original=original.replace('    answer = await coordinator.api.bypass_v2(fryer.info, "startMultiCook", payload, **extra)',
            '    _require_sync_report(fryer, allow_prepared=False)\n    answer = await coordinator.api.bypass_v2(fryer.info, "startMultiCook", payload, **extra)')
    env={'AirfryerError':type('AirfryerError',(Exception,),{}),'AirfryerDeviceOffline':type('Offline',(Exception,),{}),
         'BUSY':{'vorheizen','gart','pausiert','schublade_offen'},'PREPARED':{'wartet_auf_start','wartet_auf_sync'},
         'modelle':NS(ALL_MODES={'airfry':'airfry'}),'redact':lambda v:v}
    exec(compile('from __future__ import annotations\n'+original,'upstream-fixture','exec'),env)
    return env


class ControllerPatchTests(unittest.IsolatedAsyncioTestCase):
    async def attempt(self,statuses,patched,age=0,after_refresh=None):
        env=controller_functions(patched)
        api=NS(account_id='dummy',bypass_v2=AsyncMock(return_value={}))
        fryer=NS(online=True,last_error=None,last_report=datetime.now(timezone.utc)-timedelta(seconds=age),
                 state=NS(active=False,zones={k:NS(status=v,active=False) for k,v in statuses.items()}),info={})
        async def refresh():
            if after_refresh: after_refresh(fryer)
        coordinator=NS(api=api,async_refresh=refresh,async_request_fast_refresh=AsyncMock())
        try:
            await env['async_send_sync'](coordinator,fryer,2,plans=(('airfry',180,7),('airfry',180,10)),once=True,reset=False)
            blocked=False
        except env['SyncBlocked']:
            blocked=True
        return blocked,api.bypass_v2

    async def test_original_missing_and_unknown_zone_defect_is_reproduced(self):
        for statuses in ({1:'bereit'},{1:'unbekannt',2:'bereit'}):
            blocked,write=await self.attempt(statuses,False)
            self.assertFalse(blocked);write.assert_awaited_once()

    async def test_patch_blocks_missing_unknown_stale_and_refresh_race(self):
        for statuses in ({1:'bereit'},{1:'unbekannt',2:'bereit'},{1:'gart',2:'bereit'},
                         {1:'wartet_auf_start',2:'bereit'}):
            blocked,write=await self.attempt(statuses,True)
            self.assertTrue(blocked);write.assert_not_called()
        blocked,write=await self.attempt({1:'bereit',2:'bereit'},True,age=16)
        self.assertTrue(blocked);write.assert_not_called()
        blocked,write=await self.attempt({1:'bereit',2:'bereit'},True,
            after_refresh=lambda fryer:fryer.state.zones.pop(2))
        self.assertTrue(blocked);write.assert_not_called()

    async def test_patch_still_allows_exactly_one_prepare_only_idle_write(self):
        blocked,write=await self.attempt({1:'bereit',2:'bereit'},True)
        self.assertFalse(blocked);write.assert_awaited_once()
        self.assertIs(write.call_args.kwargs['retry'],False)
        self.assertIs(write.call_args.args[2]['readyStart'],True)
