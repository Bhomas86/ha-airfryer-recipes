"""Offline tests for recipe data validation and JSON interoperability."""

import json
import unittest

from custom_components.airfryer_recipes.recipe_model import (
    CookingPhase,
    Recipe,
    RecipeValidationError,
    create_recipe,
    export_library_json,
    import_library_json,
    recipe_from_dict,
    recipe_to_dict,
)


class TestRecipeModel(unittest.TestCase):
    def setUp(self):
        self.recipe = create_recipe(
            "Brötchen auftauen",
            program="airfry",
            temperature_c=160,
            duration_minutes=8,
            description="Frozen bread rolls",
            category="Breakfast",
            tags=("Frozen", "Quick"),
        )

    def test_create_device_independent_single_phase(self):
        self.assertEqual(len(self.recipe.phases), 1)
        self.assertEqual(self.recipe.phases[0].temperature_c, 160)
        self.assertNotIn("device_id", recipe_to_dict(self.recipe))
        self.assertNotIn("zone", recipe_to_dict(self.recipe))

    def test_unicode_round_trip(self):
        raw = export_library_json([self.recipe])
        self.assertIn("Brötchen", raw)
        restored = import_library_json(raw)
        self.assertEqual(restored, [self.recipe])
        self.assertEqual(json.loads(raw)["schema_version"], 1)

    def test_favorite_is_backward_compatible_and_validated(self):
        encoded = recipe_to_dict(self.recipe)
        encoded.pop("favorite")
        self.assertFalse(recipe_from_dict(encoded).favorite)
        encoded["favorite"] = True
        self.assertTrue(recipe_from_dict(encoded).favorite)
        encoded["favorite"] = "yes"
        with self.assertRaises(RecipeValidationError):
            recipe_from_dict(encoded)

    def test_empty_collection_is_valid(self):
        self.assertEqual(import_library_json(export_library_json([])), [])

    def test_data_model_allows_future_multiple_phases(self):
        recipe = Recipe(
            id="two-steps",
            name="Two steps",
            phases=(
                CookingPhase("airfry", 120, 4),
                CookingPhase("airfry", 180, 3),
            ),
        )
        self.assertEqual(recipe_from_dict(recipe_to_dict(recipe)), recipe)

    def test_reject_invalid_boolean_temperature(self):
        with self.assertRaises(RecipeValidationError):
            CookingPhase("airfry", True, 8)

    def test_reject_duration_zero(self):
        with self.assertRaises(RecipeValidationError):
            CookingPhase("airfry", 160, 0)

    def test_reject_empty_recipe_name(self):
        with self.assertRaises(RecipeValidationError):
            create_recipe("  ", program="airfry", temperature_c=160, duration_minutes=8)

    def test_reject_duplicate_tags(self):
        with self.assertRaises(RecipeValidationError):
            create_recipe(
                "Bread",
                program="airfry",
                temperature_c=160,
                duration_minutes=8,
                tags=("Quick", "quick"),
            )

    def test_reject_unsupported_schema(self):
        raw = json.loads(export_library_json([self.recipe]))
        raw["schema_version"] = 2
        with self.assertRaises(RecipeValidationError):
            import_library_json(json.dumps(raw))

    def test_reject_duplicate_recipe_ids(self):
        with self.assertRaises(RecipeValidationError):
            import_library_json(export_library_json([self.recipe, self.recipe]))

    def test_reject_unknown_recipe_field(self):
        raw = recipe_to_dict(self.recipe)
        raw["device_id"] = "should-not-be-present"
        with self.assertRaises(RecipeValidationError):
            recipe_from_dict(raw)

    def test_reject_invalid_json(self):
        with self.assertRaises(RecipeValidationError):
            import_library_json("{ not valid JSON }")

    def test_reject_oversized_import(self):
        with self.assertRaises(RecipeValidationError):
            import_library_json(" " * 1_000_001)

    def test_reject_boolean_schema_version(self):
        raw = {"schema_version": True, "recipes": []}
        with self.assertRaises(RecipeValidationError):
            import_library_json(json.dumps(raw))


if __name__ == "__main__":
    unittest.main()
