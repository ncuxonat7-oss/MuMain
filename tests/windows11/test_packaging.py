"""Focused static checks for the partial local packaging recipe; no runtime."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('package_mu', ROOT / 'scripts/package-windows11-local.py')
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class PackagingTests(unittest.TestCase):
    def test_windows_safe_path(self):
        self.assertEqual(str(PACKAGE.safe_path('Data/Items/Group12_Wing.json')), 'Data/Items/Group12_Wing.json')

    def test_unsafe_paths_rejected(self):
        for value in ('../escape', '/absolute', 'C:/escape', 'Data\\file', 'Data/NUL.txt',
                      'Data/x. ', 'Data//file', 'Data/./file', 'Data/a*', 'Data/a\n'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PACKAGE.safe_path(value)

    def test_changed_bytes_do_not_inherit_git_provenance(self):
        data = b'pinned bytes'
        blob = hashlib.sha1(b'blob 12\0' + data).hexdigest()
        PACKAGE.verify_blob(data, blob)
        with self.assertRaises(ValueError):
            PACKAGE.verify_blob(data + b'changed', blob)

    def test_draft_leaves_setup_and_endpoints_unknown(self):
        draft = PACKAGE.draft_manifest({'client/Data/file': {'sha256': 'a' * 64}})
        self.assertIsNone(draft['database'])
        self.assertIsNone(draft['endpoints'])
        self.assertEqual(draft['hashes'], {'client/Data/file': 'a' * 64})
        self.assertNotIn('approvedLaunchManifestSha256', draft)

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            marker = path / 'keep'
            marker.write_bytes(b'preserve')
            with self.assertRaises(ValueError):
                PACKAGE.package(ROOT, path)
            self.assertEqual(marker.read_bytes(), b'preserve')


if __name__ == '__main__':
    unittest.main(verbosity=2)
