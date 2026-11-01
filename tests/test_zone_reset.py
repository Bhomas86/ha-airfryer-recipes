"""Registry-only resolution of reviewed zone-ending switches; no controls."""
import sys
import types
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
from custom_components.airfryer_recipes.zone_reset import zone_switch
from custom_components.airfryer_recipes.beta_send import BetaTestBlocked


class ZoneResetTests(unittest.TestCase):
    def setUp(self):
        self.device = NS(disabled_by=None, config_entries={'entry'}, identifiers={('airfryer_control','private-fixture')})
        self.entries = [NS(entity_id=f'switch.fixture_{zone}', platform='airfryer_control',
            unique_id=f'private-fixture_zone{zone}_gart', config_entry_id='entry', disabled_by=None) for zone in (1,2)]
        self.hass = NS(states=NS(get=Mock(return_value=NS(state='on'))), services=NS(has_service=Mock(return_value=True)))
        helpers = types.ModuleType('homeassistant.helpers')
        dr = types.ModuleType('homeassistant.helpers.device_registry')
        er = types.ModuleType('homeassistant.helpers.entity_registry')
        dr.async_get = lambda hass: NS(async_get=lambda device: self.device)
        er.async_get = lambda hass: 'registry'
        er.async_entries_for_device = lambda registry, device: self.entries
        helpers.device_registry, helpers.entity_registry = dr, er
        p = patch.dict(sys.modules, {'homeassistant.helpers':helpers,
            'homeassistant.helpers.device_registry':dr, 'homeassistant.helpers.entity_registry':er})
        p.start();self.addCleanup(p.stop)

    def test_both_zones_resolve_without_using_entity_names_or_global_button(self):
        for z in (1,2):self.assertEqual(zone_switch(self.hass,'device','entry',z),f'switch.fixture_{z}')
        self.entries[0].entity_id = 'switch.renamed_by_owner'
        self.assertEqual(zone_switch(self.hass,'device','entry',1),'switch.renamed_by_owner')

    def test_unknown_zone_wrong_entry_and_other_platform_are_blocked(self):
        for z in (True,0,3):
            with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',z)
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','other-entry',1)
        self.entries[0].platform = 'other'
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',1)

    def test_disabled_unloaded_unavailable_or_ambiguous_switches_are_blocked(self):
        self.entries[0].disabled_by = 'user'
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',1)
        self.entries[0].disabled_by = None
        self.hass.states.get.return_value = None
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',1)
        self.hass.states.get.return_value = NS(state='unavailable')
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',1)
        self.hass.states.get.return_value = NS(state='on')
        self.entries.append(self.entries[0])
        with self.assertRaises(BetaTestBlocked):zone_switch(self.hass,'device','entry',1)
