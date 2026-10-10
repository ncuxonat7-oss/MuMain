#!/usr/bin/env python3
"""Targeted mutation tests for ingredient normalization, not runtime gameplay."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('mapper',
    Path(__file__).with_name('map-s6-recipe-ingredients.py'))
mapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapper)
ITEM_ID = 7181
STACK_ID = 6688


def item(group=14, number=13, durability=1, level=0):
    return dict(Group=group, Number=number, Durability=durability,
                MaximumItemLevel=level, ItemSlotId=None)


def source_row(key=ITEM_ID):
    return dict(TypeMin=key, TypeMax=key, LevelMin=0, LevelMax=255,
                CountMin=1, CountMax=1, DurabilityMin=0, DurabilityMax=255)


def predicate(key=ITEM_ID, count=None):
    return dict(states=[(key, 0)], count=count or [1, 1])


class IngredientTests(unittest.TestCase):
    def setUp(self):
        self.items = {ITEM_ID: item(), STACK_ID: item(13, 32, 20)}

    def check(self, required, client):
        return mapper.compare(required, client)['classification']

    def test_plain_match(self):
        source = mapper.source(source_row(), self.items)
        self.assertEqual(self.check([predicate()], [source]), 'MATCH')

    def test_item_mutation_detected(self):
        source = mapper.source(source_row(), self.items)
        self.assertEqual(self.check([predicate(STACK_ID)], [source]), 'VALUE MISMATCH')

    def test_amount_mutation_detected(self):
        source = mapper.source(source_row(), self.items)
        self.assertEqual(self.check([predicate(count=[2, 2])], [source]), 'VALUE MISMATCH')

    def test_level_mutation_detected(self):
        source = mapper.source(source_row(), self.items)
        required = predicate()
        required['states'] = [(ITEM_ID, 1)]
        self.assertEqual(self.check([required], [source]), 'VALUE MISMATCH')

    def test_range_padding_not_missing_resource(self):
        row = source_row()
        row.update(TypeMin=ITEM_ID - 1, TypeMax=ITEM_ID + 1)
        self.assertEqual(mapper.source(row, self.items)['states'], [(ITEM_ID, 0)])

    def test_unbounded_server_not_finite_client(self):
        source = mapper.source(source_row(), self.items)
        self.assertEqual(self.check([predicate(count=[1, None])], [source]), 'VALUE MISMATCH')

    def test_optional_zero_preserved(self):
        row = source_row()
        row.update(CountMin=0)
        self.assertEqual(self.check([predicate(count=[0, 1])], [mapper.source(row, self.items)]), 'MATCH')

    def test_fixed_container_normalizes_without_full_match(self):
        row = source_row(STACK_ID)
        row.update(DurabilityMin=20, DurabilityMax=20)
        source = mapper.source(row, self.items)
        result = mapper.compare([predicate(STACK_ID, [20, 20])], [source])
        self.assertEqual(result['normalized_counts'], 'MATCH')
        self.assertEqual(result['classification'], mapper.MAPPING)

    def test_unknown_unit_mismatch_stays_unmapped(self):
        with self.assertRaisesRegex(ValueError, 'count units'):
            mapper.source(source_row(STACK_ID), self.items)

    def test_native_stack_list_counts_units(self):
        key = 14 * 512 + 3
        self.items[key] = item(14, 3, 3, 1)
        self.assertEqual(mapper.source(source_row(key), self.items)['count'], [1, 1])

    def test_overlapping_predicates_not_claimed_equal(self):
        source = mapper.source(source_row(), self.items)
        self.assertEqual(self.check([predicate(), predicate()], [source, source]), mapper.MAPPING)

    def test_custom_handler_and_flags_excluded(self):
        recipe = {'ItemCraftingHandlerClassName': 'Custom'}
        projection = {'settings': {}, 'required': []}
        self.assertIn('Custom', mapper.unsupported(recipe, projection, []))
        recipe['ItemCraftingHandlerClassName'] = None
        projection['settings'] = {'present': True}
        variants = [{'MixOption': 65, 'Sources': [{'SpecialItem': 1, 'OptionMin': 0, 'OptionMax': 255}]}]
        self.assertIn('flags', mapper.unsupported(recipe, projection, variants))


if __name__ == '__main__':
    unittest.main()
