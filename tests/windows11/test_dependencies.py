"""New dependency-only checks; never execute bundled Windows binaries."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('package_mu', ROOT / 'scripts/package-windows11-local.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'output'

    def component(self, entries=None):
        if entries is None:
            entries = [('dotnet.exe', b'runtime')]
        path = self.root / 'runtime.zip'
        with zipfile.ZipFile(path, 'w') as z:
            for name, data in entries:
                z.writestr(name, data)
        rows = [{'source': name, 'destination': 'dotnet/' + name, 'bytes': len(data),
                 'sha256': hashlib.sha256(data).hexdigest()} for name, data in entries]
        return {'id': 'runtime', 'version': '10.0.11', 'name': path.name, 'url': 'https://official.example/runtime.zip',
                'bytes': path.stat().st_size, 'sha256': P.hash_file(path), 'files': rows}

    def test_real_pinned_manifest_and_versions(self):
        document = P.load_dependencies(ROOT / 'docs/windows11-dependencies.json')
        self.assertEqual([(x['id'], x['version']) for x in document['archives']],
                         [('aspnetcore-runtime', '10.0.11'), ('powershell', '7.4.20'), ('postgres', '17.11-3')])
        self.assertFalse(document['launchEnabled'])
        self.assertIsNone(document['approvedLaunchManifestSha256'])
        self.assertEqual(sum(len(x['files']) for x in document['archives']), 2727)

    def test_selected_payload_and_notices_are_copied(self):
        component = self.component([('dotnet.exe', b'run'), ('LICENSE.txt', b'notice')])
        inventory = {}
        P.stage_dependency(component, self.root, self.output, inventory)
        self.assertEqual(set(inventory), {'dotnet/dotnet.exe', 'dotnet/LICENSE.txt'})
        self.assertEqual((self.output / 'dotnet/LICENSE.txt').read_bytes(), b'notice')

    def test_corrupt_archive_rejected_before_extraction(self):
        component = self.component()
        with (self.root / component['name']).open('ab') as f:
            f.write(b'corruption')
        with self.assertRaisesRegex(ValueError, 'archive identity'):
            P.stage_dependency(component, self.root, self.output, {})
        self.assertFalse(self.output.exists())

    def test_missing_archive_rejected(self):
        component = self.component()
        component['name'] = 'absent.zip'
        with self.assertRaises(ValueError):
            P.stage_dependency(component, self.root, self.output, {})

    def test_missing_required_member_rejected(self):
        component = self.component()
        component['files'][0]['source'] = 'missing.dll'
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            P.stage_dependency(component, self.root, self.output, {})

    def test_corrupt_member_digest_rejected(self):
        component = self.component()
        component['files'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            P.stage_dependency(component, self.root, self.output, {})

    def test_unsafe_map_destinations_and_duplicate_case_rejected(self):
        for target in ('../escape', 'dotnet/../escape', 'server/extra.dll', 'dotnet/CON.txt'):
            component = self.component()
            component['files'][0]['destination'] = target
            with self.subTest(target=target), self.assertRaises(ValueError):
                P.dependency_rows(component)
        component = self.component([('A', b'a'), ('a', b'a')])
        with self.assertRaises(ValueError):
            P.dependency_rows(component)

    def test_unsafe_unselected_archive_member_rejected(self):
        component = self.component([('dotnet.exe', b'run'), ('../outside', b'bad')])
        component['files'] = component['files'][:1]
        with self.assertRaises(ValueError):
            P.stage_dependency(component, self.root, self.output, {})
        self.assertFalse((self.root / 'outside').exists())

    def test_symlink_archive_member_rejected(self):
        component = self.component()
        path = self.root / component['name']
        with zipfile.ZipFile(path, 'a') as z:
            entry = zipfile.ZipInfo('link');entry.create_system = 3;entry.external_attr = 0o120777 << 16
            z.writestr(entry, '../outside')
        component.update(sha256=P.hash_file(path), bytes=path.stat().st_size)
        with self.assertRaises(ValueError):
            P.stage_dependency(component, self.root, self.output, {})

    def test_manifest_changed_or_enabled_rejected(self):
        path = self.root / 'spec.json'
        path.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'specification identity'):
            P.load_dependencies(path)
        path.write_text(json.dumps({'launchEnabled': True, 'approvedLaunchManifestSha256': None}))
        with patch.object(P, 'DEPENDENCY_MANIFEST_SHA256', P.hash_file(path)), self.assertRaisesRegex(ValueError, 'cannot enable'):
            P.load_dependencies(path)

    def test_missing_notices_cannot_finish(self):
        with self.assertRaisesRegex(ValueError, 'notices missing'):
            P.finish_dependencies(self.output, {}, {'required_files': ['dotnet/LICENSE.txt']}, 0)

    def test_wrong_version_cannot_finish(self):
        spec = {'required_files': [], 'archives': [{'version': '10.0.12', 'files': [{'destination': 'dotnet/a'}]}]}
        with self.assertRaisesRegex(ValueError, 'version'):
            P.finish_dependencies(self.output, {}, spec, 0)

    def test_existing_destination_preserved(self):
        self.output.mkdir();marker=self.output/'keep';marker.write_bytes(b'preserve')
        with self.assertRaisesRegex(ValueError, 'no overwrite'):
            P.package_dependencies(self.root, self.output, self.root, self.root/'absent')
        self.assertEqual(marker.read_bytes(), b'preserve')

    def test_changed_base_inventory_rejected(self):
        base = self.root / 'base';base.mkdir()
        (base/'package-inventory.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Base inventory identity'):
            P.copy_existing_control(base, self.output, {'base_inventory_sha256': '0'*64})

    def test_dependency_collision_never_overwrites(self):
        component=self.component();inventory={'dotnet/dotnet.exe': {'sha256':'a'*64}}
        with self.assertRaisesRegex(ValueError, 'collision'):
            P.stage_dependency(component,self.root,self.output,inventory)

    def test_symlink_parent_in_base_refused(self):
        base = self.root / 'base';base.mkdir()
        external = self.root / 'external';external.mkdir()
        (external / 'file').write_bytes(b'content')
        (base / 'alias').symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            P.regular_control_file(base, 'alias/file')

    def test_archive_size_bounds(self):
        component=self.component()
        with patch.object(P,'MAX_DEPENDENCY_EXPANDED',1),self.assertRaisesRegex(ValueError,'expanded size'):
            P.stage_dependency(component,self.root,self.output,{})

    def test_failure_status_remains_disabled(self):
        document=P.load_dependencies(ROOT/'docs/windows11-dependencies.json')
        with patch.object(P,'load_dependencies',return_value=document), \
             patch.object(P,'copy_existing_control',side_effect=ValueError('missing')):
            with self.assertRaises(ValueError):
                P.package_dependencies(self.root,self.output,self.root,self.root/'spec')
        status=json.loads((self.output/'packaging-status.json').read_text())
        self.assertFalse(status['launchEnabled']);self.assertIsNone(status['approvedLaunchManifestSha256'])
        self.assertEqual(status['status'],'INCOMPLETE_STAGING')


if __name__ == '__main__':
    unittest.main(verbosity=2)
