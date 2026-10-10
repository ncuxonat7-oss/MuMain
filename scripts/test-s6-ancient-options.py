#!/usr/bin/env python3
"""Targeted set/bonus join checks, not gameplay simulation."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('ancient',
    Path(__file__).with_name('audit-s6-ancient-options.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BonusJoinTests(unittest.TestCase):
    def classify(self, discriminator=1, bonus='bonus', options=None, types=None):
        return audit.classify_set(dict(AncientSetDiscriminator=discriminator, BonusOptionId=bonus),
            {'bonus': {'OptionTypeId': 'type'}} if options is None else options,
            {'type': {'Name': 'Ancient Bonus Option||translation'}} if types is None else types)

    def test_nonancient_bonus_does_not_imply_set(self):
        self.assertEqual(self.classify(discriminator=0), 'NOT_ANCIENT')

    def test_bonusless_ancient_is_retained(self):
        self.assertEqual(self.classify(bonus=None), 'SET_WITHOUT_BONUS')

    def test_bonus_capability_is_not_presence(self):
        self.assertEqual(self.classify(), 'BONUS_CAPABLE_SET')

    def test_missing_option_fails_closed(self):
        self.assertEqual(self.classify(options={}), 'UNKNOWN')

    def test_missing_type_fails_closed(self):
        self.assertEqual(self.classify(types={}), 'UNKNOWN')

    def test_other_bonus_type_not_equivalent(self):
        self.assertEqual(self.classify(types={'type': {'Name': 'Option'}}), 'SET_WITH_OTHER_BONUS')


if __name__ == '__main__':
    unittest.main()
