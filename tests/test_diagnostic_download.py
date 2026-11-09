"""Immutable bounded diagnostic previews, with expiration and user isolation."""
import json
import unittest
from unittest.mock import patch
from custom_components.airfryer_recipes.diagnostic_download import DiagnosticDownloads
from custom_components.airfryer_recipes.recipe_repository import RecipePreviewExpiredError

class DiagnosticPreviewTests(unittest.TestCase):
    def test_exact_snapshot_survives_original_mutation(self):
        cache=DiagnosticDownloads();value={'flag':True,'count':1}
        token=cache.create('owner',value);value['count']=99
        self.assertEqual(json.loads(cache.read('owner',token)),{'flag':True,'count':1})
        with self.assertRaises(RecipePreviewExpiredError):cache.read('other',token)

    def test_expiry_and_replacement_invalidate_old_preview(self):
        cache=DiagnosticDownloads()
        with patch('custom_components.airfryer_recipes.diagnostic_download.time.monotonic',return_value=0):
            first=cache.create('owner',{})
            second=cache.create('owner',{'new':True})
        with self.assertRaises(RecipePreviewExpiredError):cache.read('owner',first)
        with patch('custom_components.airfryer_recipes.diagnostic_download.time.monotonic',return_value=601):
            with self.assertRaises(RecipePreviewExpiredError):cache.read('owner',second)

    def test_cache_capacity_is_bounded_and_expired_entries_are_pruned(self):
        cache=DiagnosticDownloads()
        with patch('custom_components.airfryer_recipes.diagnostic_download.time.monotonic',return_value=0):
            for i in range(128):cache.create(str(i),{})
            with self.assertRaises(OSError):cache.create('extra',{})
        with patch('custom_components.airfryer_recipes.diagnostic_download.time.monotonic',return_value=601):
            cache.create('extra',{})
        self.assertEqual(len(cache.snapshots),1)
