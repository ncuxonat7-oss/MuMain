"""Targeted regressions for audit classification and costly false positives."""
import importlib.util
import unittest
from pathlib import Path

from s6_source import calls, strip_comments, finalize_skills

SCRIPT = Path(__file__).with_name('diff-baseline-s6.py')
SPEC = importlib.util.spec_from_file_location('s6diff', SCRIPT)
DIFF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIFF)


class DiffTests(unittest.TestCase):
    def compare(self, refs, rows):
        return DIFF.compare_category('skills', refs, rows, {'paths': ['Local/Eng/skill_eng.bmd']}, {'item_findings': []})

    def test_comments_cannot_create_reference_records(self):
        text = '// this.CreateSkill(999);\nthis.CreateSkill(1, "Name // text");'
        result = list(calls(strip_comments(text), 'CreateSkill'))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0][0], '1')

    def test_semantic_mismatch_never_admits_import(self):
        refs = [dict(key='1', fields={'Range': 6}, source='source.cs', line=1)]
        rows = [dict(key='1', fields={'Range': 5})]
        finding = self.compare(refs, rows)[0]
        self.assertEqual(finding['classification'], 'VALUE MISMATCH')
        self.assertFalse(finding['safe_to_import'])
        self.assertEqual(finding['client']['status'], 'FORMAT MAPPING REQUIRED')

    def test_partial_reference_cannot_establish_current_extra(self):
        finding = self.compare([], [dict(key='900', fields={})])[0]
        self.assertEqual(finding['classification'], 'UNKNOWN')

    def test_reference_extra_is_candidate_not_confirmed_missing(self):
        finding = self.compare([dict(key='1', fields={}, source='source.cs', line=1)], [])[0]
        self.assertEqual(finding['classification'], 'REFERENCE EXTRA')
        self.assertFalse(finding['safe_to_import'])

    def test_duplicate_spawns_preserve_multiplicity(self):
        ref = dict(key='same', fields={'Quantity': 1}, source='map.cs', line=1)
        rows = [dict(key='same', fields={'Quantity': 1})]
        result = self.compare([ref, ref], rows)
        self.assertEqual([x['classification'] for x in result], ['MATCH', 'REFERENCE EXTRA'])

    def test_master_damage_follows_ordered_replacement_chain(self):
        rows = [dict(key='1', fields={'AttackDamage': 100}), dict(key='2', fields={'AttackDamage': 22}), dict(key='3', fields={'AttackDamage': 1})]
        source = 'private void InitializeMasterSkillData() { this.AddMasterSkillDefinition(SkillNumber.A,0,0,2,2,SkillNumber.Base,20,"f"); this.AddMasterSkillDefinition(SkillNumber.B,0,0,2,3,SkillNumber.A,20,"f"); }'
        result = finalize_skills(rows, 'source.cs', source, {'SkillNumber.Base': 1, 'SkillNumber.A': 2, 'SkillNumber.B': 3})
        self.assertEqual(result[-1]['fields']['AttackDamage'], 100)

    def test_missing_client_file_is_not_safe(self):
        result = DIFF.client_check('skills', '1', {}, {'paths': []}, {})
        self.assertEqual(result['status'], 'CLIENT RESOURCE MISSING')


if __name__ == '__main__':
    unittest.main()
