#!/usr/bin/env python3
"""Focused regression tests for recipe mapping and false-positive boundaries."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('recipes', Path(__file__).with_name('audit-s6-recipes.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def settings():
    return dict(SuccessPercent=60, MaximumSuccessPercent=0, Money=2000000,
                MoneyPerFinalSuccessPercentage=0, NpcPriceDivisor=0,
                SuccessPercentageAdditionForLuck=25, SuccessPercentageAdditionForExcellentItem=-10,
                SuccessPercentageAdditionForGuardianItem=-10, SuccessPercentageAdditionForAncientItem=-10,
                SuccessPercentageAdditionForSocketItem=-20)


def variants():
    return [dict(MixIndex=index, Sources=[dict(SpecialItem=mask)],
                 RateTokens=[dict(Op=0, Value=value), dict(Op=1, Value=0), dict(Op=64, Value=0)],
                 SuccessRate=value+25, RequiredZenType=65, RequiredZen=2000000)
            for index, (mask, value) in enumerate([(1, 50), (4, 50), (2, 50), (16, 40), (0, 60)])]


class RecipeTests(unittest.TestCase):
    def test_item_id_is_group_stride_not_decimal_concat(self):
        self.assertEqual(module.semantic_item(dict(Group=12, Number=15))['client_id'], 6159)

    def test_normal_and_luck_upgrade(self):
        for luck, rate in [(False, 60), (True, 85)]:
            actual = module.upgrade_rate(settings(), variants(), 0, luck)
            self.assertEqual((actual['classification'], actual['client_rate']), ('MATCH', rate))

    def test_single_conditions_match(self):
        for flag in [1, 2, 4, 16]:
            for luck in [False, True]:
                self.assertEqual(module.upgrade_rate(settings(), variants(), flag, luck)['classification'], 'MATCH')

    def test_combined_conditions_expose_counterexample_without_reachability_claim(self):
        actual = module.upgrade_rate(settings(), variants(), 3, False)
        self.assertEqual((actual['client_rate'], actual['server_rate']), (50, 40))
        self.assertTrue(actual['reachability'].startswith('UNPROVEN'))

    def test_client_first_variant_order_is_preserved(self):
        rows = variants()
        rows[-1]['RateTokens'][0]['Value'] = 61
        actual = module.upgrade_rate(settings(), rows[-1:] + rows[:-1], 1, False)
        self.assertEqual(actual['client_rate'], 61)

    def test_changed_rate_is_reported(self):
        rows = variants()
        rows[0]['RateTokens'][0]['Value'] = 49
        self.assertEqual(module.upgrade_rate(settings(), rows, 1, False)['classification'], 'VALUE MISMATCH')

    def test_cap_applies_after_luck(self):
        rows = variants()
        rows[-1]['SuccessRate'] = 70
        self.assertEqual(module.upgrade_rate(settings(), rows, 0, True)['client_rate'], 70)

    def test_unknown_formula_fails_closed(self):
        rows = variants()
        rows[-1]['RateTokens'][0]['Op'] = 999
        with self.assertRaises(ValueError):
            module.upgrade_rate(settings(), rows, 0, False)

    def test_custom_price_is_unknown(self):
        self.assertEqual(module.price_rule(settings(), variants(), 'RefineStoneCrafting')['classification'], 'UNKNOWN')

    def test_changed_fixed_price_is_detected(self):
        rows = variants()
        rows[0]['RequiredZen'] += 1
        self.assertEqual(module.price_rule(settings(), rows, '')['classification'], 'VALUE MISMATCH')

    def test_variable_price_requires_mapping(self):
        config = settings()
        config['MoneyPerFinalSuccessPercentage'] = 10000
        self.assertEqual(module.price_rule(config, variants(), '')['classification'], 'FORMAT MAPPING REQUIRED')

    def test_custom_rate_not_compared_to_raw_success_percent(self):
        self.assertEqual(module.constant_rate(settings(), [], variants(), 'RefineStoneCrafting')['classification'], 'UNKNOWN')

    def test_fixed_rate_discrepancy_is_detected(self):
        config = settings()
        for field in module.SPECIAL_ADDITIONS.values():
            config[field] = 0
        config['SuccessPercentageAdditionForLuck'] = 0
        rows = variants()
        for row in rows:
            row['RateTokens'] = [dict(Op=32, Value=0.0)]
            row['SuccessRate'] = 60
        self.assertEqual(module.constant_rate(config, [], rows, '')['classification'], 'MATCH')
        rows[0]['SuccessRate'] = 59
        self.assertEqual(module.constant_rate(config, [], rows, '')['classification'], 'VALUE MISMATCH')


if __name__ == '__main__':
    unittest.main()
