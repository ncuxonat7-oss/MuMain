"""New small-fixture integrity checks; no .NET/PowerShell/DB execution."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/package-windows-candidate.py'
spec = importlib.util.spec_from_file_location('candidate', SCRIPT)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
WORKSPACE = Path(__file__).resolve().parents[3]


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'fresh'
        self.helper = C.load_helper(WORKSPACE)
        policy = json.dumps({'runtimeGrantStatus': 'BLOCKED_SOURCE_BINARY_ALIGNMENT'})
        policy_hash = hashlib.sha256(policy.encode()).hexdigest()
        files = {'server/A.dll': b'fixture managed bytes',
                 'scripts/windows11/local-session-contract.json': json.dumps({
                     'launchEnabled': False, 'approvedLaunchManifestSha256': None}).encode(),
                 'scripts/windows11/first-setup-policy.json': policy.encode(),
                 'scripts/windows11/FirstSetup.ps1': (
                     policy_hash + "\nthrow 'RUNTIME_GRANTS_UNRESOLVED'\n").encode()}
        rows = []
        for target, content in files.items():
            source = self.root / ('inputs/' + target)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(content)
            rows.append({'source': 'inputs/' + target, 'target': target,
                         'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
        self.contract = {'files': rows, 'serverCount': 1, 'sourceSnapshotCount': 3}

    def stage(self):
        return C.stage(self.root, self.output, self.contract, self.helper)

    def test_verified_stage_is_disabled(self):
        result = self.stage()
        self.assertEqual(result['result'], 'PASS_INTEGRITY_ONLY')
        self.assertIs(result['launchEnabled'], False)
        self.assertIsNone(result['approvedLaunchManifestSha256'])
        self.assertEqual(result['windowsAcceptance'], 'NOT_RUN')

    def test_same_size_corruption_is_rejected(self):
        self.stage()
        p = self.output / 'server/A.dll'
        p.write_bytes(b'x' * p.stat().st_size)
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            C.verify(self.output, self.contract)

    def test_missing_file_is_rejected(self):
        self.stage()
        (self.output / 'server/A.dll').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or extra'):
            C.verify(self.output, self.contract)

    def test_extra_file_is_rejected(self):
        self.stage()
        (self.output / 'server/extra.dll').write_bytes(b'x')
        with self.assertRaisesRegex(ValueError, 'Missing or extra'):
            C.verify(self.output, self.contract)

    def test_existing_output_is_not_overwritten(self):
        self.stage()
        before = C.digest(self.output / C.CONTRACT)
        with self.assertRaisesRegex(ValueError, 'overwrite refused'):
            self.stage()
        self.assertEqual(before, C.digest(self.output / C.CONTRACT))

    def test_corrupt_source_preserves_incomplete_output(self):
        p = self.root / self.contract['files'][0]['source']
        p.write_bytes(b'x' * p.stat().st_size)
        with self.assertRaisesRegex(ValueError, 'size/hash mismatch'):
            self.stage()
        self.assertEqual(json.loads((self.output / C.STATUS).read_text()), C.disabled_status())
        with self.assertRaisesRegex(ValueError, 'overwrite refused'):
            self.stage()

    def test_missing_source_refuses_before_output_claim(self):
        (self.root / self.contract['files'][0]['source']).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing regular'):
            self.stage()
        self.assertFalse(self.output.exists())

    def test_symlink_source_refused(self):
        p = self.root / self.contract['files'][0]['source']
        other = self.root / 'other'
        other.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.stage()

    def test_symlink_target_parent_refused(self):
        real = self.root / 'real'
        real.mkdir()
        link = self.root / 'link'
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            C.stage(self.root, link / 'fresh', self.contract, self.helper)

    def test_symlink_member_refused(self):
        self.stage()
        p = self.output / 'server/A.dll'
        p.unlink()
        p.symlink_to(self.root / self.contract['files'][0]['source'])
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            C.verify(self.output, self.contract)

    def test_unsafe_paths(self):
        for name in ('../a', '/a', 'a/../b', 'a//b', 'C:/a', 'a\\b', 'a/NUL.txt', 'a/x.', 'a/COM1'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                C.safe_relative(name)

    def test_collision_refused(self):
        rows = copy.deepcopy(self.contract['files'])
        rows.append(dict(rows[0], target='server/a.DLL'))
        with self.assertRaisesRegex(ValueError, 'collision'):
            C.check_rows(rows)

    def test_native_apphosts_refused(self):
        for name in C.EXCLUDED | {n + '.exe' for n in C.EXCLUDED}:
            row = dict(self.contract['files'][0], target='server/' + name)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'apphost'):
                C.check_rows([row])

    def test_manifest_self_tampering_cannot_repin_payload(self):
        self.stage()
        record = copy.deepcopy(self.contract)
        record['files'][0]['sha256'] = '0' * 64
        (self.output / C.CONTRACT).write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'pinned source'):
            C.verify(self.output, self.contract)

    def test_incomplete_status_denies_acceptance(self):
        self.stage()
        (self.output / C.STATUS).write_text(json.dumps(C.disabled_status()))
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            C.assert_launch_allowed(self.output, self.contract)

    def test_valid_component_always_denies_launch(self):
        self.stage()
        with self.assertRaisesRegex(ValueError, 'LAUNCH_DENIED'):
            C.assert_launch_allowed(self.output, self.contract)

    def test_editing_windows_acceptance_does_not_enable_launch(self):
        self.stage()
        status = C.disabled_status(True)
        status['windowsAcceptance'] = 'PASSED'
        status['launchEnabled'] = True
        (self.output / C.STATUS).write_text(json.dumps(status))
        with self.assertRaisesRegex(ValueError, 'status changed'):
            C.assert_launch_allowed(self.output, self.contract)

    def test_real_pinned_plan_has_only_approved_set(self):
        contract = C.load_contract(WORKSPACE)
        self.assertEqual(contract['serverCount'], 183)
        self.assertEqual(contract['sourceSnapshotCount'], 12)
        self.assertEqual((contract['unchanged'], contract['replacements']), (93, 90))
        self.assertEqual(sum(r.get('blockedPortability', False) for r in contract['files']), 5)

    def test_wrong_input_pin_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Pinned input'):
            C.pinned_json(WORKSPACE, C.PLAN, '0' * 64)

    def test_source_bytes_preserved(self):
        before = {r['source']: C.digest(self.root / r['source']) for r in self.contract['files']}
        self.stage()
        self.assertEqual(before, {r['source']: C.digest(self.root / r['source']) for r in self.contract['files']})


if __name__ == '__main__':
    unittest.main(verbosity=2)
