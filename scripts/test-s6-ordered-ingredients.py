#!/usr/bin/env python3
"""New ordered-predicate boundaries/mutations; no old rate or runtime tests."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('ordered',
    Path(__file__).with_name('map-s6-ordered-ingredients.py'))
ordered = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ordered)
TARGET = 0
JEWEL = 7181


def source(key=TARGET, mask=0):
    return dict(TypeMin=key, TypeMax=key, LevelMin=9, LevelMax=9,
        OptionMin=0, OptionMax=255, DurabilityMin=0, DurabilityMax=255,
        SpecialItem=mask, CountMin=1, CountMax=1)


def variant(index, mask=0):
    return dict(MixIndex=index, Sources=[source(mask=mask)])


def item():
    return dict(id=TARGET, level=9, option=0, durability=100, mask=1)


class OrderedTests(unittest.TestCase):
    def setUp(self):
        self.mapper = ordered.load_mapper()
        self.items = {TARGET: dict(Group=0, Number=0, MaximumItemLevel=15,
            Durability=100, ItemSlotId='weapon')}

    def test_positive_mask_allows_additional_flags(self):
        # Synthetic CheckItem boundary only; no real combined-flag eligibility claim.
        state = item()
        state['mask'] = 1 | 8
        self.assertTrue(ordered.check_item(source(mask=1), state))

    def test_missing_required_flag_rejected(self):
        self.assertFalse(ordered.check_item(source(mask=4), item()))

    def test_order_mutation_changes_first_match(self):
        variants = [variant(7, 1), variant(8, 0)]
        self.assertEqual(ordered.first_source_variant(variants, item()), 7)
        self.assertEqual(ordered.first_source_variant(variants[::-1], item()), 8)

    def test_regions_retain_file_order_not_index_sort(self):
        result = ordered.ordered_regions([variant(9), variant(3)])
        self.assertEqual(result[1]['excluded_prior_variants'], [9])

    def test_option_minimum_boundary(self):
        row = source()
        row['OptionMin'] = 4
        state = item()
        state['option'] = 3
        self.assertFalse(ordered.check_item(row, state))
        state['option'] = 4
        self.assertTrue(ordered.check_item(row, state))

    def test_option_maximum_mutation(self):
        state = item()
        state['option'] = 8
        row = source()
        row['OptionMax'] = 7
        self.assertFalse(ordered.check_item(row, state))

    def test_level_and_item_mutations(self):
        for field, value in [('id', 1), ('level', 10)]:
            state = item()
            state[field] = value
            self.assertFalse(ordered.check_item(source(), state))

    def test_durability_mutation(self):
        row = source()
        row['DurabilityMin'] = 101
        self.assertFalse(ordered.check_item(row, item()))

    def test_unknown_flag_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Unknown native'):
            ordered.client_predicate(source(mask=32), self.items, self.mapper)

    def test_compaction_does_not_fill_definition_holes(self):
        self.assertEqual(ordered.compact_states([(0, 9), (1, 9), (3, 9)]),
                         [[0, 1, 9, 9], [3, 3, 9, 9]])

    def test_count_mutation_detected(self):
        client = ordered.client_predicate(source(), self.items, self.mapper)
        server = dict(states=[(TARGET, 9)], count=[2, 2])
        result = ordered.amount_comparison([server], [[client]], self.mapper)
        self.assertEqual(result['per_variant'], ['VALUE MISMATCH'])

    def test_overlap_stays_unknown(self):
        client = ordered.client_predicate(source(), self.items, self.mapper)
        server = dict(states=[(TARGET, 9)], count=[1, 1])
        result = ordered.amount_comparison([server, server], [[client]], self.mapper)
        self.assertEqual(result['classification'], ordered.UNKNOWN)
        self.assertIn('Overlapping', result['reason'])

    def test_custom_handler_not_overridden_by_settings(self):
        recipe = dict(Number=3, ItemCraftingHandlerClassName='Custom')
        result = ordered.map_ordered(recipe, {'settings': {'present': True}}, [], self.items, self.mapper)
        self.assertEqual(result['classification'], ordered.UNKNOWN)

    def test_domain_mismatch_is_not_whole_recipe_proof(self):
        server = dict(states=[(TARGET, 9), (JEWEL, 9)], count=[1, 1])
        client = ordered.client_predicate(source(), self.items, self.mapper)
        result = ordered.domain_delta([server], [[client]])
        self.assertEqual(result['server_only'], [[JEWEL, JEWEL, 9, 9]])
        self.assertIn('only', result['limit'])

    def test_target_amount_mutation_detected(self):
        target = dict(states=[(TARGET, 9)], count=[2, 2], reference=1)
        client = ordered.client_predicate(source(), self.items, self.mapper)
        result = ordered.upgrade_amounts([target], [[client]], self.mapper)
        self.assertEqual(result['target_amounts'], 'VALUE MISMATCH')

    def test_positive_server_options_preserved_without_equivalence(self):
        projection = dict(settings={'present': True}, required=[dict(
            MinimumItemLevel=9, MaximumItemLevel=9, MinimumAmount=1, MaximumAmount=1,
            possible_items=[{'client_id': TARGET}], required_options=['Option'], Reference=1)])
        recipe = dict(Number=3, ItemCraftingHandlerClassName=None)
        variants = [dict(**variant(7, 1), category=0, MixOption=69),
                    dict(**variant(8), category=0, MixOption=69)]
        result = ordered.map_ordered(recipe, projection, variants, self.items, self.mapper)
        self.assertEqual(result['server'][0]['required_positive_option_types'], ['Option'])
        self.assertEqual(result['native_option_to_server_option_equivalence'], ordered.UNKNOWN)
        self.assertFalse(result['safe_to_import'])


if __name__ == '__main__':
    unittest.main()
