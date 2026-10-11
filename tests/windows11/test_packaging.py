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



# New runtime-stage checks are runnable separately from preserved historical tests.
import io
import json
import tarfile
import zipfile
from unittest.mock import patch


class RuntimePackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / 'output'

    def row(self, source, area, data=b'payload'):
        return {'source': source, 'destination': area + '/' + source.removeprefix('./'),
                'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

    def tar(self, entries):
        path = self.root / 'client.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, data, kind in entries:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.size = len(data) if kind == tarfile.REGTYPE else 0
                member.linkname = '../outside' if kind == tarfile.SYMTYPE else ''
                archive.addfile(member, io.BytesIO(data) if member.isfile() else None)
        return path

    def zip(self, entries, name='server.zip'):
        path = self.root / name
        with zipfile.ZipFile(path, 'w') as archive:
            for key, data in entries:
                archive.writestr(key, data)
        return path

    def test_authoritative_inventory_36_and_186(self):
        client, server = PACKAGE.load_runtime_inventory(ROOT)
        self.assertEqual((len(client), len(server)), (36, 186))
        self.assertTrue({'./Main.exe', './MUnique.Client.Library.dll'} <= set(client))
        self.assertFalse(PACKAGE.CLIENT_EXCLUDED & {k.removeprefix('./') for k in client})
        self.assertTrue(any(k.startswith('runtimes/') for k in server))
        self.assertTrue(any(k.endswith('staticwebassets.runtime.json') for k in server))

    def test_client_payload_and_build_file_exclusions(self):
        rows = {'./Main.exe': self.row('./Main.exe', 'client')}
        entries = [('./Main.exe', b'payload', tarfile.REGTYPE)]
        entries += [('./' + name, b'build-only', tarfile.REGTYPE) for name in PACKAGE.CLIENT_EXCLUDED]
        inventory = {}
        PACKAGE.stage_client(self.tar(entries), rows, self.destination, inventory)
        self.assertEqual(set(inventory), {'client/Main.exe'})
        self.assertEqual([p.name for p in (self.destination / 'client').iterdir()], ['Main.exe'])

    def test_missing_required_shader_rejected(self):
        rows = {'./shader.spv': self.row('./shader.spv', 'client')}
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            PACKAGE.stage_client(self.tar([]), rows, self.destination, {})

    def test_corrupt_required_dll_rejected(self):
        row = self.row('./bridge.dll', 'client')
        archive = self.tar([('./bridge.dll', b'corrupt', tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            PACKAGE.stage_client(archive, {'./bridge.dll': row}, self.destination, {})

    def test_client_size_mismatch_rejected(self):
        row = self.row('./Main.exe', 'client')
        archive = self.tar([('./Main.exe', b'x', tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError, 'size mismatch'):
            PACKAGE.stage_client(archive, {'./Main.exe': row}, self.destination, {})

    def test_tar_traversal_links_and_collision_rejected(self):
        cases = [[('../escape', b'x', tarfile.REGTYPE)],
                 [('./link', b'', tarfile.SYMTYPE)],
                 [('./folder', b'', tarfile.DIRTYPE), ('./FOLDER', b'', tarfile.DIRTYPE)]]
        for entries in cases:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                PACKAGE.stage_client(self.tar(entries), {}, self.destination, {})
        self.assertFalse((self.root / 'escape').exists())

    def test_full_server_tree_retains_locale_and_web_metadata(self):
        names = ['Startup.dll', 'ru/messages.dll', 'Startup.staticwebassets.runtime.json']
        rows = {name: self.row(name, 'server') for name in names}
        inventory = {}
        PACKAGE.stage_server(self.zip([(name, b'payload') for name in names]), rows, self.destination, inventory)
        self.assertEqual(set(inventory), {'server/' + name for name in names})

    def test_missing_and_extra_server_file_rejected(self):
        rows = {'Startup.dll': self.row('Startup.dll', 'server')}
        for entries in ([], [('Startup.dll', b'payload'), ('extra.dll', b'payload')]):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                PACKAGE.stage_server(self.zip(entries), rows, self.destination, {})

    def test_corrupt_server_file_rejected(self):
        rows = {'Startup.dll': self.row('Startup.dll', 'server')}
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            PACKAGE.stage_server(self.zip([('Startup.dll', b'corrupt')]), rows, self.destination, {})

    def test_zip_unsafe_and_case_collision_rejected(self):
        for names in (['../escape'], ['C:/escape'], ['a\\b'], ['A', 'a'], ['NUL.txt']):
            with self.subTest(names=names), zipfile.ZipFile(self.zip([(n, b'x') for n in names])) as archive:
                with self.assertRaises(ValueError):
                    PACKAGE.checked_zip(archive)

    def test_zip_symlink_rejected(self):
        path = self.root / 'link.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            entry = zipfile.ZipInfo('link')
            entry.create_system = 3
            entry.external_attr = 0o120777 << 16
            archive.writestr(entry, '../outside')
        with zipfile.ZipFile(path) as archive, self.assertRaises(ValueError):
            PACKAGE.checked_zip(archive)

    def test_map_unsafe_or_misdirected_path_rejected(self):
        for source, target in [('x', '../x'), ('../x', 'server/../x'), ('x', 'client/x')]:
            row = self.row(source, 'server')
            row['destination'] = target
            with self.subTest(target=target), self.assertRaises(ValueError):
                PACKAGE.checked_map([row], 'server', 1)

    def test_outer_and_inner_identity_fail_closed(self):
        outer = self.zip([('inner', b'inner bytes')], 'outer.zip')
        pin = {'sha256': '0' * 64, 'inner': 'inner', 'inner_bytes': 11, 'inner_sha256': '0' * 64}
        with patch.object(PACKAGE, 'stage_server') as stage:
            with self.assertRaisesRegex(ValueError, 'Outer archive hash'):
                PACKAGE.stage_archive(outer, pin, {}, self.destination, {}, stage)
            pin['sha256'] = PACKAGE.hash_file(outer)
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                PACKAGE.stage_archive(outer, pin, {}, self.destination, {}, stage)
            stage.assert_not_called()

    def test_modified_inventory_and_overlay_rejected_before_execution(self):
        for relative, blob in [('docs/windows11-runtime-inventory.json', PACKAGE.INVENTORY_BLOB),
                               *PACKAGE.OVERLAY_BLOBS.items()]:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'raise RuntimeError("must not run")')
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, 'pinned Git blob'):
                PACKAGE.pinned_file(target, blob)
        with self.assertRaisesRegex(ValueError, 'pinned Git blob'):
            PACKAGE.apply_overlay(self.root, self.destination, {})

    def test_runtime_only_success_still_cannot_enable_launch(self):
        with patch.object(PACKAGE, 'stage_runtimes'):
            result = PACKAGE.package(ROOT, self.destination, Path('client.zip'), Path('server.zip'), True)
        status = json.loads((self.destination / 'packaging-status.json').read_text())
        self.assertFalse(result['launchEnabled'])
        self.assertFalse(status['launchEnabled'])
        self.assertIsNone(status['approvedLaunchManifestSha256'])
        self.assertEqual(status['status'], 'INCOMPLETE_NOT_RUNNABLE')
        self.assertTrue({'pinned Data', 'pinned fonts', 'pinned disabled launcher'} <= set(status['missing']))
        self.assertIsNone(json.loads((self.destination / 'windows11-launch-manifest.draft.json').read_text())['database'])
        self.assertFalse((self.destination / 'windows11-launch-manifest.json').exists())

    def test_failed_staging_leaves_disabled_status(self):
        with patch.object(PACKAGE, 'stage_runtimes', side_effect=ValueError('missing')):
            with self.assertRaises(ValueError):
                PACKAGE.package(ROOT, self.destination, Path('client.zip'), Path('server.zip'), True)
        status = json.loads((self.destination / 'packaging-status.json').read_text())
        self.assertEqual(status['status'], 'INCOMPLETE_STAGING')
        self.assertFalse(status['launchEnabled'])
        self.assertIsNone(status['approvedLaunchManifestSha256'])

    def test_runtime_stage_existing_output_and_symlink_never_overwritten(self):
        self.destination.mkdir()
        marker = self.destination / 'keep'
        marker.write_bytes(b'preserve')
        alias = self.root / 'alias'
        alias.symlink_to(self.destination, target_is_directory=True)
        for destination in (self.destination, alias):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                PACKAGE.package(ROOT, destination, Path('client.zip'), Path('server.zip'), True)
        self.assertEqual(marker.read_bytes(), b'preserve')

    def test_full_mode_preserves_asset_and_launcher_gates(self):
        def copy_area(repo, destination, area, target, inventory):
            if area == 'scripts/windows11':
                PACKAGE.save(destination / target / 'local-session-contract.json',
                             {'launchEnabled': True, 'approvedLaunchManifestSha256': 'a' * 64})
        pins = [value.encode() for value in PACKAGE.TREES.values()]
        with patch.object(PACKAGE, 'git', side_effect=pins), \
             patch.object(PACKAGE, 'copy_git_area', side_effect=copy_area) as copy, \
             patch.object(PACKAGE, 'apply_overlay'), \
             patch.object(PACKAGE, 'stage_runtimes') as runtime:
            with self.assertRaisesRegex(ValueError, 'Launcher must remain disabled'):
                PACKAGE.package(ROOT, self.destination, Path('client.zip'), Path('server.zip'))
            self.assertEqual(copy.call_count, 3)
            runtime.assert_not_called()
        status = json.loads((self.destination / 'packaging-status.json').read_text())
        self.assertFalse(status['launchEnabled'])
        self.assertIsNone(status['approvedLaunchManifestSha256'])

    def test_full_mode_refuses_unpinned_data_before_creating_output(self):
        with patch.object(PACKAGE, 'git', return_value=b'wrong tree'):
            with self.assertRaisesRegex(ValueError, 'Unexpected baseline tree'):
                PACKAGE.package(ROOT, self.destination)
        self.assertFalse(self.destination.exists())

    def test_both_archive_paths_required(self):
        with self.assertRaisesRegex(ValueError, 'Both runtime'):
            PACKAGE.package(ROOT, self.destination, Path('client.zip'), None, True)
        self.assertFalse(self.destination.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
