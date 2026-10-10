#!/usr/bin/env python3
"""Offline tests for use-only fixture, restoration and harness contracts."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('use_only', ROOT / 'scripts/check-skill41-use.py')
USE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(USE)
HELPER = USE.helpers()


def fixture(directory):
    skill = {'character_id': HELPER.ACTOR_ID, 'actor_exists': True, 'skill_count': 1,
             'skills': [{'Id': USE.ENTRY_ID, 'SkillId': HELPER.SKILL_ID,
                         'CharacterId': HELPER.ACTOR_ID, 'Level': 0}]}
    rows = [{'Name': HELPER.ACTOR, 'Id': HELPER.ACTOR_ID, 'InventoryId': 'actor-store'},
            {'Id': 'actor-store', 'Money': 9996100},
            {'Name': 'test0Dk', 'Id': 'core', 'InventoryId': 'core-store'},
            {'Id': 'core-store', 'Money': 10}]
    for stage in ('ready', 'final'):
        (directory / f'{stage}-skill41.json').write_text(json.dumps(skill))
        (directory / f'{stage}-database.jsonl').write_text('\n'.join(map(json.dumps, rows)))
    return skill, rows


class UseOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.skill, self.rows = fixture(self.directory)

    def test_ready_and_final_cli_never_claim_accepted_use(self):
        for extra, expected in ((['--ready'], 'READY_FOR_USE'), ([], 'FIXTURE_PRESERVED')):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/check-skill41-use.py'),
                                     '--evidence', str(self.directory), *extra], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data['status'], expected)
            self.assertEqual(data['accepted_use_effect_cost'], 'UNKNOWN')

    def test_wrong_or_missing_known_skill_fails_closed(self):
        cases = []
        empty = copy.deepcopy(self.skill); empty.update(skill_count=0, skills=[]); cases.append(empty)
        for key, value in (('Id', 'other'), ('Level', 1), ('CharacterId', 'other'), ('SkillId', 'skill22')):
            changed = copy.deepcopy(self.skill); changed['skills'][0][key] = value; cases.append(changed)
        duplicate = copy.deepcopy(self.skill); duplicate['skills'] *= 2; duplicate['skill_count'] = 2; cases.append(duplicate)
        for data in cases:
            with self.subTest(data=data):
                (self.directory / 'ready-skill41.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError): USE.assess(self.directory, True)

    def test_wrong_actor_and_reappearing_orb_rejected(self):
        for rows in ([dict(self.rows[0], Id='other'), *self.rows[1:]],
                     [*self.rows, {'Id': HELPER.ORB_ID, 'ItemStorageId': 'other-store'}]):
            (self.directory / 'ready-database.jsonl').write_text('\n'.join(map(json.dumps, rows)))
            with self.assertRaises(ValueError): USE.assess(self.directory, True)

    def test_final_missing_or_corrupted_is_not_success(self):
        (self.directory / 'final-skill41.json').unlink()
        with self.assertRaises(OSError): USE.assess(self.directory)

    def test_final_money_and_core_changes_fail(self):
        for index in (1, 3):
            rows = copy.deepcopy(self.rows); rows[index]['Money'] += 1
            (self.directory / 'final-database.jsonl').write_text('\n'.join(map(json.dumps, rows)))
            result = USE.assess(self.directory)
            self.assertEqual(result['status'], 'FAIL')
            self.assertEqual(result['accepted_use_effect_cost'], 'UNKNOWN')

    def test_archive_hash_rejected_before_destination_write(self):
        archive = self.directory / 'bad.zip'; archive.write_bytes(b'wrong')
        destination = self.directory / 'restore'
        with self.assertRaises(ValueError): USE.restore_archive(archive, destination)
        self.assertFalse(destination.exists())

    def test_archive_extracts_only_fixed_dump(self):
        archive = self.directory / 'synthetic.zip'
        with zipfile.ZipFile(archive, 'w') as out:
            out.writestr('gameplay-test-db.dump', b'PGDMPsynthetic')
            out.writestr('../unwanted', b'never extract')
        destination = self.directory / 'restore'
        with patch.object(USE, 'RUN16_ZIP_SHA256', hashlib.sha256(archive.read_bytes()).hexdigest()):
            USE.restore_archive(archive, destination)
        self.assertEqual([p.name for p in destination.iterdir()], ['gameplay-test-db.dump'])
        self.assertFalse((self.directory / 'unwanted').exists())

    def test_scenario_and_fast_capture_contracts(self):
        workflow = (ROOT / '.github/workflows/standard-gameplay.yml').read_text()
        ps = json.loads(re.search(r'const psSource = (".*");', workflow).group(1))
        capture = (ROOT / 'scripts/capture-skill41.ps1').read_text()
        fast = (ROOT / 'scripts/capture-skill41-use.ps1').read_text()
        self.assertIn('options: [trade, skill41, skill41-use]', workflow)
        self.assertIn("inputs.scenario != 'skill41-use'", workflow)
        self.assertIn('run-id: 38005996341', workflow)
        self.assertIn('artifact_id:11680250531', workflow)
        self.assertIn('artifact.data.workflow_run.id !== 38078397211', workflow)
        self.assertIn("if (!$UseOnly -and $Stage -eq 'ready'", capture)
        self.assertIn('--ready', capture)
        self.assertIn("['skill41','skill41-use'].includes(process.env.GAMEPLAY_SCENARIO)?context.ref:'main'", workflow)
        self.assertIn('[int]$postClickMilliseconds=2000', ps)
        self.assertIn('Start-Sleep -Milliseconds $postClickMilliseconds', ps)
        self.assertIn("'skill41-cast' { Invoke-Skill41Cast", ps)
        self.assertIn("$env:GAMEPLAY_SCENARIO -ne 'skill41-use' -or $script:skill41CastAttempted", fast)
        self.assertLess(fast.index("Capture-Stage 'skill41-use-before'"), fast.index('Click-Client $X $Y $true 0'))
        self.assertLess(fast.index('Click-Client $X $Y $true 0'), fast.index("Capture-Stage 'skill41-use-immediate'"))
        self.assertLess(fast.index("Capture-Stage 'skill41-use-immediate'"), fast.index('Start-Sleep -Milliseconds 100'))
        self.assertIn('skill41-use-timing.json', workflow)
        self.assertIn("'accepted_use_effect_cost': 'UNKNOWN'", (ROOT / 'scripts/check-skill41-use.py').read_text())


if __name__ == '__main__':
    unittest.main()
