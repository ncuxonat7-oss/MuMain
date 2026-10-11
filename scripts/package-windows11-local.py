#!/usr/bin/env python3
"""Assemble pinned local launcher/assets only; never download, install or activate."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

LAUNCHER = '7f5b44a930a501dfc7ea4f522584cb59a22c9499'
TREES = {'Data': '77f7830f542d106fc519c8821832d49a3dd8ae3a',
         'fonts': '149f928e2547aa6658977c3f41c63abccfa471ed'}
RUNTIME = {'library_file_id': 'libfile_b1e2679ae4088191859d97f0bbd4903c',
           'name': 'openmu-money-local-bind-38104421623.zip', 'artifact': '11689365514',
           'sha256': '505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c',
           'inner_sha256': '4b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec'}
CLIENT = {'library_file_id': 'libfile_1174bdeb6c048191ad0be1ac163fdad5',
          'name': 'validated-mumain-native-build.zip', 'artifact': '11567737809',
          'sha256': 'eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e'}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def safe_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or '\\' in value or ':' in value or not path.parts:
        raise ValueError('Unsafe package path')
    for part in value.split('/'):
        if not part or part in ('.', '..') or part != part.rstrip(' .'):
            raise ValueError('Unsafe package path component')
        if re.search(r'[\x00-\x1f<>"|?*]', part) or re.fullmatch(r'(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?', part):
            raise ValueError('Unsafe Windows path component')
    return path


def verify_blob(data, expected):
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual != expected:
        raise ValueError('Local input differs from pinned Git blob')


def record(data, blob=None):
    result = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if blob:
        result['source_git_blob'] = blob
    return result


def copy_git_area(repo, destination, area, target, inventory):
    entries = git(repo, 'ls-tree', '-rz', LAUNCHER, '--', area).split(b'\0')
    seen = set()
    for entry in filter(None, entries):
        metadata, name = entry.decode('utf-8').split('\t', 1)
        mode, kind, blob = metadata.split()
        relative = name[len(area):].lstrip('/')
        output = str(PurePosixPath(target) / safe_path(relative))
        if mode != '100644' or kind != 'blob' or output.casefold() in seen:
            raise ValueError('Nonregular or colliding input')
        seen.add(output.casefold())
        source = repo / name
        if source.is_symlink() or not source.is_file():
            raise ValueError('Input is not a regular local file')
        data = source.read_bytes()
        verify_blob(data, blob)
        if target.startswith('client/') and PurePosixPath(output).suffix.lower() in ('.exe', '.dll', '.ps1', '.bat', '.cmd', '.so'):
            raise ValueError('Executable in asset area')
        path = destination / output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        inventory[output] = record(data, blob)


def apply_overlay(repo, destination, inventory):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('client_overlay', repo / 'scripts/apply-client-overlay.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    overlay_path = repo / 'patches/client-socket-metadata.json'
    overlay = json.loads(overlay_path.read_text(encoding='utf-8'))
    result = module.apply(destination / 'client/Data', overlay)
    key = 'client/Data/' + overlay['path']
    original_blob = inventory[key]['source_git_blob']
    inventory[key] = record((destination / key).read_bytes(), original_blob)
    inventory[key]['transformation'] = 'reviewed-client-socket-overlay'
    backup = (destination / key).with_suffix('.json.baseline-backup')
    evidence = destination / 'evidence/original-Group12_Wing.json'
    evidence.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(backup, evidence)
    shutil.copyfile(overlay_path, destination / 'evidence/client-socket-metadata.json')
    save(destination / 'evidence/overlay-result.json', result)
    return result


def draft_manifest(inventory):
    return {'schema': 1, 'runtimeArchive': 'inputs/' + RUNTIME['name'],
            'server': 'server', 'clientDirectory': 'client', 'pgDirectory': 'postgres',
            'dotnetDirectory': 'dotnet', 'pgData': 'database/cluster',
            'dotnet': 'dotnet/dotnet.exe', 'postgres': 'postgres/bin/postgres.exe',
            'pgCtl': 'postgres/bin/pg_ctl.exe', 'pgControlData': 'postgres/bin/pg_controldata.exe',
            'psql': 'postgres/bin/psql.exe', 'client': 'client/Main.exe',
            'hashes': {name: row['sha256'] for name, row in sorted(inventory.items())},
            'database': None, 'endpoints': None, 'versions': {'dotnet': '10.0.11', 'postgres': '17.11'}}


def package(repo, destination):
    if destination.exists():
        raise ValueError('Fresh package destination required; no overwrite')
    for name, expected in TREES.items():
        if git(repo, 'rev-parse', f'{LAUNCHER}:src/bin/{name}').decode().strip() != expected:
            raise ValueError('Unexpected baseline tree')
    destination.mkdir(parents=True)
    inventory = {}
    for name in TREES:
        copy_git_area(repo, destination, 'src/bin/' + name, 'client/' + name, inventory)
    copy_git_area(repo, destination, 'scripts/windows11', 'scripts/windows11', inventory)
    overlay = apply_overlay(repo, destination, inventory)
    contract = json.loads((destination / 'scripts/windows11/local-session-contract.json').read_text())
    if contract['launchEnabled'] is not False or contract['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Launcher must remain disabled')
    save(destination / 'package-inventory.json', inventory)
    save(destination / 'windows11-launch-manifest.draft.json', draft_manifest(inventory))
    save(destination / 'packaging-status.json', {
        'status': 'INCOMPLETE_NOT_RUNNABLE', 'launchEnabled': False, 'launcher_commit': LAUNCHER,
        'source_trees': TREES, 'verified_files': len(inventory), 'overlay': overlay,
        'runtime': dict(RUNTIME, status='NOT_INCLUDED'),
        'client_binary': dict(CLIENT, status='NOT_INCLUDED'),
        'missing': ['server runtime', 'client binary/DLL/shaders bundle', 'Windows .NET/ASP.NET runtime',
                    'Windows PostgreSQL tools', 'PowerShell Windows dependency', 'approved persistent DB/setup',
                    'independently verified migration IDs'],
        'database': 'NOT_SELECTED_NOT_PROVISIONED', 'windows_acceptance': 'NOT_RUN',
        'credentials': 'NOT_READ_NOT_CONFIGURED', 'component_incompatibility': 'NOT_ESTABLISHED'})
    return {'verified_files': len(inventory), 'bytes': sum(row['bytes'] for row in inventory.values()), 'overlay': overlay}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.repo.resolve(), args.destination.resolve())))
