#!/usr/bin/env python3
"""Stage pinned local assets/runtime archives; never download, install or activate."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import stat
import tarfile
import tempfile
import zipfile

LAUNCHER = '7f5b44a930a501dfc7ea4f522584cb59a22c9499'
TREES = {'Data': '77f7830f542d106fc519c8821832d49a3dd8ae3a',
         'fonts': '149f928e2547aa6658977c3f41c63abccfa471ed'}
RUNTIME = {'library_file_id': 'PRIVATE_BACKUP_REFERENCE_OMITTED',
           'name': 'openmu-money-local-bind-38104421623.zip', 'artifact': '11689365514',
           'sha256': '505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c',
           'inner_sha256': '4b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec'}
CLIENT = {'library_file_id': 'PRIVATE_BACKUP_REFERENCE_OMITTED',
          'name': 'validated-mumain-native-build.zip', 'artifact': '11567737809',
          'sha256': 'eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e'}

CLIENT.update(inner='MuMain-windows-native-x64-release-editor-off-no-data.tar.gz',
              inner_bytes=258774906,
              inner_sha256='ccfcfc6c8d199d3a192a5abf22551926de35aaa88ebeea7c5ef6f905f695e66a')
RUNTIME.update(inner='downloads/openmu-money-local-bind-runtime.zip', inner_bytes=22966886)
INVENTORY_BLOB = 'f8e36cfe1f8167094a77e26009df314589197a39'
OVERLAY_BLOBS = {'scripts/apply-client-overlay.py': '287c4f7cb980b0ac13ded1a231f03c1e92653f46',
                 'patches/client-socket-metadata.json': 'ccb1a945603be57f7f3d7001adf690dde56e6e43'}
CHUNK = 1024 * 1024
MAX_ENTRIES = 1024
MAX_CLIENT_MEMBER = 32 * CHUNK
MAX_SERVER_MEMBER = 64 * CHUNK
CLIENT_EXCLUDED = {'MuClient.lib', 'Main.map', 'Main.pdb'}


def pinned_file(path, blob):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Pinned input must be a regular file')
    data = path.read_bytes()
    verify_blob(data, blob)
    return data


def hash_file(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Archive must be a regular file')
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked_zip(archive, max_entries=MAX_ENTRIES):
    entries = archive.infolist()
    if len(entries) > max_entries:
        raise ValueError('Too many archive entries')
    seen = set()
    for entry in entries:
        name = entry.filename[:-1] if entry.is_dir() else entry.filename
        safe_path(name)
        mode = entry.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in (0, stat.S_IFDIR if entry.is_dir() else stat.S_IFREG):
            raise ValueError('Nonregular ZIP member')
        if name.casefold() in seen or entry.flag_bits & 1:
            raise ValueError('Duplicate or encrypted ZIP member')
        seen.add(name.casefold())
    return {entry.filename: entry for entry in entries if not entry.is_dir()}


def checked_map(rows, area, count):
    if len(rows) != count:
        raise ValueError('Unexpected runtime inventory count')
    sources, destinations = set(), set()
    for row in rows:
        source = row['source']
        clean = source[2:] if area == 'client' and source.startswith('./') else source
        safe_path(clean)
        safe_path(row['destination'])
        if row['destination'] != area + '/' + clean:
            raise ValueError('Unexpected runtime destination')
        if clean.casefold() in sources or row['destination'].casefold() in destinations:
            raise ValueError('Colliding runtime inventory')
        if type(row['bytes']) is not int or row['bytes'] <= 0 or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid runtime identity')
        if area == 'client' and clean in CLIENT_EXCLUDED:
            raise ValueError('Build-only payload is forbidden')
        sources.add(clean.casefold())
        destinations.add(row['destination'].casefold())
    return {row['source']: row for row in rows}


def load_runtime_inventory(repo):
    data = pinned_file(repo / 'docs/windows11-runtime-inventory.json', INVENTORY_BLOB)
    document = json.loads(data)
    return (checked_map(document['client_files'], 'client', 36),
            checked_map(document['server_files'], 'server', 186))


def copy_checked(stream, output, size, digest):
    actual, total = hashlib.sha256(), 0
    with output.open('xb') as target:
        while chunk := stream.read(min(CHUNK, size - total + 1)):
            total += len(chunk)
            if total > size:
                raise ValueError('Archive member exceeds pinned size')
            actual.update(chunk)
            target.write(chunk)
    if total != size or actual.hexdigest() != digest:
        raise ValueError('Archive member size/hash mismatch')


def stage_member(stream, row, destination, inventory):
    relative = str(safe_path(row['destination']))
    if relative.casefold() in {key.casefold() for key in inventory}:
        raise ValueError('Package destination collision')
    output = destination / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    copy_checked(stream, output, row['bytes'], row['sha256'])
    inventory[relative] = {key: row[key] for key in ('bytes', 'sha256')}
    inventory[relative]['source_archive_member'] = row['source']


def stage_client(inner, rows, destination, inventory):
    found, seen = set(), set()
    with tarfile.open(inner, 'r|gz') as archive:
        for index, member in enumerate(archive):
            if index >= MAX_ENTRIES:
                raise ValueError('Too many TAR entries')
            name = member.name[2:] if member.name.startswith('./') else member.name
            if name == '.' and member.isdir():
                continue
            safe_path(name)
            if not (member.isfile() or member.isdir()) or name.casefold() in seen:
                raise ValueError('Nonregular or colliding TAR entry')
            seen.add(name.casefold())
            if member.isdir():
                continue
            if member.name not in rows:
                if name not in CLIENT_EXCLUDED:
                    raise ValueError('Unexpected client payload')
                continue
            row = rows[member.name]
            if member.size != row['bytes'] or member.size > MAX_CLIENT_MEMBER:
                raise ValueError('Client member size mismatch')
            with archive.extractfile(member) as stream:
                stage_member(stream, row, destination, inventory)
            found.add(member.name)
    if found != set(rows):
        raise ValueError('Missing required client file')


def stage_server(inner, rows, destination, inventory):
    with zipfile.ZipFile(inner) as archive:
        members = checked_zip(archive)
        if set(members) != set(rows):
            raise ValueError('Server tree must match full pinned inventory')
        for name, row in rows.items():
            if members[name].file_size != row['bytes'] or row['bytes'] > MAX_SERVER_MEMBER:
                raise ValueError('Server member size mismatch')
            with archive.open(name) as stream:
                stage_member(stream, row, destination, inventory)


def stage_archive(path, pin, rows, destination, inventory, stage):
    if hash_file(path) != pin['sha256']:
        raise ValueError('Outer archive hash mismatch')
    with tempfile.TemporaryDirectory(prefix='mumain-stage-') as temporary:
        inner = Path(temporary) / 'inner'
        with zipfile.ZipFile(path) as archive:
            members = checked_zip(archive)
            entry = members.get(pin['inner'])
            if entry is None or entry.file_size != pin['inner_bytes']:
                raise ValueError('Missing or incorrect inner archive')
            with archive.open(entry) as stream:
                copy_checked(stream, inner, pin['inner_bytes'], pin['inner_sha256'])
        stage(inner, rows, destination, inventory)
    if pin is RUNTIME:
        row = {'source': path.name, 'destination': 'inputs/' + RUNTIME['name'],
               'bytes': path.stat().st_size, 'sha256': pin['sha256']}
        with path.open('rb') as stream:
            stage_member(stream, row, destination, inventory)


def stage_runtimes(repo, destination, inventory, client_archive, server_archive):
    client, server = load_runtime_inventory(repo)
    stage_archive(client_archive, CLIENT, client, destination, inventory, stage_client)
    stage_archive(server_archive, RUNTIME, server, destination, inventory, stage_server)


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
    helper = pinned_file(repo / 'scripts/apply-client-overlay.py',
                         OVERLAY_BLOBS['scripts/apply-client-overlay.py'])
    overlay_path = repo / 'patches/client-socket-metadata.json'
    overlay = json.loads(pinned_file(overlay_path, OVERLAY_BLOBS['patches/client-socket-metadata.json']))
    safe_path(overlay['path'])
    namespace = {'__name__': 'client_overlay'}
    exec(compile(helper, 'pinned-client-overlay', 'exec'), namespace)
    result = namespace['apply'](destination / 'client/Data', overlay)
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


def write_package_status(destination, inventory, overlay, runtimes, assets):
    save(destination / 'package-inventory.json', inventory)
    save(destination / 'windows11-launch-manifest.draft.json', draft_manifest(inventory))
    missing = ['Windows .NET/ASP.NET runtime', 'Windows PostgreSQL tools',
               'PowerShell Windows dependency', 'approved persistent DB/setup',
               'independently reconciled migration/configuration IDs',
               'dependency provenance and redistribution notices']
    if not assets:
        missing += ['pinned Data', 'pinned fonts', 'pinned disabled launcher']
    if not runtimes:
        missing += ['server runtime', 'client binary/DLL/shaders bundle']
    status = {'status': 'INCOMPLETE_NOT_RUNNABLE', 'launchEnabled': False,
              'approvedLaunchManifestSha256': None, 'launcher_commit': LAUNCHER,
              'source_trees': TREES, 'verified_files': len(inventory), 'overlay': overlay,
              'runtime': dict(RUNTIME, status='INCLUDED' if runtimes else 'NOT_INCLUDED'),
              'client_binary': dict(CLIENT, status='INCLUDED' if runtimes else 'NOT_INCLUDED'),
              'missing': missing, 'assets_staged': assets,
              'web_ui': 'UNVERIFIED_PORTABLE_ASSETS_NOT_ESTABLISHED',
              'database': 'NOT_SELECTED_NOT_PROVISIONED', 'windows_acceptance': 'NOT_RUN',
              'credentials': 'NOT_CONFIGURED', 'component_incompatibility': 'NOT_ESTABLISHED'}
    save(destination / 'packaging-status.json', status)
    return status


def package(repo, destination, client_archive=None, server_archive=None, runtime_only=False):
    if destination.exists() or destination.is_symlink():
        raise ValueError('Fresh package destination required; no overwrite')
    if bool(client_archive) != bool(server_archive) or runtime_only and not client_archive:
        raise ValueError('Both runtime archive paths are required')
    if not runtime_only:
        for name, expected in TREES.items():
            if git(repo, 'rev-parse', f'{LAUNCHER}:src/bin/{name}').decode().strip() != expected:
                raise ValueError('Unexpected baseline tree')
    destination.mkdir(parents=True)
    save(destination / 'packaging-status.json', {'status': 'INCOMPLETE_STAGING',
         'launchEnabled': False, 'approvedLaunchManifestSha256': None})
    inventory, overlay = {}, None
    if not runtime_only:
        for name in TREES:
            copy_git_area(repo, destination, 'src/bin/' + name, 'client/' + name, inventory)
        copy_git_area(repo, destination, 'scripts/windows11', 'scripts/windows11', inventory)
        overlay = apply_overlay(repo, destination, inventory)
        contract = json.loads((destination / 'scripts/windows11/local-session-contract.json').read_text())
        if contract['launchEnabled'] is not False or contract['approvedLaunchManifestSha256'] is not None:
            raise ValueError('Launcher must remain disabled')
    if client_archive:
        stage_runtimes(repo, destination, inventory, client_archive, server_archive)
    write_package_status(destination, inventory, overlay, bool(client_archive), not runtime_only)
    return {'verified_files': len(inventory), 'bytes': sum(row['bytes'] for row in inventory.values()),
            'overlay': overlay, 'launchEnabled': False, 'approvedLaunchManifestSha256': None}


DEPENDENCY_MANIFEST_SHA256 = 'a5f0e64145763509a43100afd05a38ed27fbbc870e35a091e320c8be387038c6'
MAX_DEPENDENCY_ENTRIES = 50000
MAX_DEPENDENCY_EXPANDED = 2 * 1024 * CHUNK
MAX_DEPENDENCY_MEMBER = 128 * CHUNK
DEPENDENCY_AREAS = {'dotnet', 'postgres', 'powershell'}


def load_dependencies(path):
    if hash_file(path) != DEPENDENCY_MANIFEST_SHA256:
        raise ValueError('Dependency specification identity mismatch')
    specification = json.loads(path.read_text(encoding='utf-8'))
    if specification['launchEnabled'] is not False or specification['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Dependencies cannot enable launch')
    return specification


def dependency_rows(component):
    rows, destinations = {}, set()
    for row in component['files']:
        safe_path(row['source'])
        path = safe_path(row['destination'])
        if path.parts[0] not in DEPENDENCY_AREAS:
            raise ValueError('Unexpected dependency destination')
        if row['source'] in rows or row['destination'].casefold() in destinations:
            raise ValueError('Duplicate dependency file')
        if type(row['bytes']) is not int or not 0 <= row['bytes'] <= MAX_DEPENDENCY_MEMBER:
            raise ValueError('Dependency member size limit')
        if not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid dependency digest')
        rows[row['source']] = row
        destinations.add(row['destination'].casefold())
    return rows


def stage_dependency(component, archives, destination, inventory):
    safe_path(component['name'])
    path = archives / component['name']
    if hash_file(path) != component['sha256'] or path.stat().st_size != component['bytes']:
        raise ValueError('Dependency archive identity mismatch')
    rows = dependency_rows(component)
    with zipfile.ZipFile(path) as archive:
        members = checked_zip(archive, MAX_DEPENDENCY_ENTRIES)
        if sum(member.file_size for member in members.values()) > MAX_DEPENDENCY_EXPANDED:
            raise ValueError('Dependency archive expanded size limit')
        if not set(rows) <= set(members):
            raise ValueError('Missing required dependency member')
        for name, row in rows.items():
            if members[name].file_size != row['bytes']:
                raise ValueError('Dependency member size mismatch')
            with archive.open(name) as stream:
                stage_member(stream, row, destination, inventory)
            inventory[row['destination']]['dependency_archive_sha256'] = component['sha256']


def regular_control_file(base, relative):
    path = base / safe_path(relative)
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError('Symlink in base control input')
        if parent == base:
            break
    if not path.is_file():
        raise ValueError('Missing base control input')
    return path


def copy_existing_control(base, destination, specification):
    inventory_path = regular_control_file(base, 'package-inventory.json')
    if hash_file(inventory_path) != specification['base_inventory_sha256']:
        raise ValueError('Base inventory identity mismatch')
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    if len(inventory) != specification['base_verified_files']:
        raise ValueError('Base inventory count mismatch')
    contract = json.loads(regular_control_file(base, 'scripts/windows11/local-session-contract.json').read_text())
    if contract['launchEnabled'] is not False or contract['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Base launcher must remain disabled')
    for relative, row in inventory.items():
        source = regular_control_file(base, relative)
        if source.is_symlink() or not source.is_file() or source.stat().st_size != row['bytes']:
            raise ValueError('Base component changed or missing')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as origin, target.open('xb') as output:
            shutil.copyfileobj(origin, output, CHUNK)
    for relative in ('evidence/original-Group12_Wing.json', 'evidence/client-socket-metadata.json',
                     'evidence/overlay-result.json'):
        source = regular_control_file(base, relative)
        if source.is_symlink() or not source.is_file():
            raise ValueError('Missing original overlay evidence')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open('rb') as origin, target.open('xb') as output:
            shutil.copyfileobj(origin, output, CHUNK)
    return inventory


def finish_dependencies(destination, inventory, specification, base_count):
    if not set(specification['required_files']) <= set(inventory):
        raise ValueError('Required dependency payload or notices missing')
    for area, version in (('dotnet', '10.0.11'), ('postgres', '17.11-3'), ('powershell', '7.4.20')):
        if not any(row['version'] == version and any(file['destination'].startswith(area + '/')
                   for file in row['files']) for row in specification['archives']):
            raise ValueError('Unexpected dependency version')
    overlay = json.loads((destination / 'evidence/overlay-result.json').read_text())
    status = write_package_status(destination, inventory, overlay, True, True)
    status.update(missing=specification['missing'], dependency_archives=[
        {key: component[key] for key in ('id', 'version', 'name', 'sha256', 'url')}
        for component in specification['archives']],
        powershell='powershell/pwsh.exe', prerequisite=specification['prerequisite'],
        base_files_reused=base_count, base_hashes='PRIOR_VERIFIED_NOT_REHASHED',
        new_dependency_files_verified=len(inventory) - base_count,
        dependency_manifest_sha256=DEPENDENCY_MANIFEST_SHA256)
    save(destination / 'packaging-status.json', status)
    return status


def package_dependencies(base, destination, archives, specification_path):
    if destination.exists() or destination.is_symlink():
        raise ValueError('Fresh package destination required; no overwrite')
    specification = load_dependencies(specification_path)
    destination.mkdir(parents=True)
    save(destination / 'packaging-status.json', {'status': 'INCOMPLETE_STAGING',
         'launchEnabled': False, 'approvedLaunchManifestSha256': None})
    inventory = copy_existing_control(base, destination, specification)
    base_count = len(inventory)
    for component in specification['archives']:
        stage_dependency(component, archives, destination, inventory)
    prerequisite = specification['prerequisite']
    source = archives / safe_path(prerequisite['name'])
    if hash_file(source) != prerequisite['sha256']:
        raise ValueError('Prerequisite identity mismatch')
    with source.open('rb') as stream:
        stage_member(stream, dict(prerequisite, source=prerequisite['name']), destination, inventory)
    return finish_dependencies(destination, inventory, specification, base_count)


# Bounded continuation: exactly the reviewed two-context guard overlay. This is
# not an installer, DB setup operation or generic overlay/plugin framework.
DATABASE_GUARD_BASE_INVENTORY = '22c4c3d6649dda053cc8bb606735ee615c4d1c35a60f23735edeb48beb0d7955'
DATABASE_GUARD_BASE_STATUS = '4c59d8681a126a52948a4c355d445d60f9d7e06d7ac5b014f9e4b9de9ce8539d'
DATABASE_GUARD_FILES = {'scripts/windows11/Database.ps1': 'c8089453f95413cb178d03cd351ddea6140c188eb4ba2405e7c36ddbcc010b1d', 'scripts/windows11/Guards.ps1': '8e95e68479ea364c022fd16823a8afc25ef00d0544138f019e18f9b9a2966ac6', 'scripts/windows11/database-source-contract.json': '0718c51ba1367d476a5d3fff7a46e55b16f334688ecbb650af7148b836c2cac6'}


def package_database_guards(base, destination):
    if destination.exists() or destination.is_symlink():
        raise ValueError('Fresh package destination required; no overwrite')
    source_root = Path(__file__).resolve().parents[1]
    replacement = {}
    for relative, expected in DATABASE_GUARD_FILES.items():
        source = regular_control_file(source_root, relative)
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Reviewed database guard source changed')
        replacement[relative] = data
    contract = json.loads(replacement['scripts/windows11/database-source-contract.json'])
    status_path = regular_control_file(base, 'packaging-status.json')
    if hash_file(status_path) != DATABASE_GUARD_BASE_STATUS:
        raise ValueError('Dependency base status changed')
    status = json.loads(status_path.read_text())
    if status['launchEnabled'] is not False or status['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Dependency base must remain disabled')
    destination.mkdir(parents=True)
    save(destination / 'packaging-status.json', {'status': 'INCOMPLETE_STAGING',
         'launchEnabled': False, 'approvedLaunchManifestSha256': None})
    inventory = copy_existing_control(base, destination, {
        'base_inventory_sha256': DATABASE_GUARD_BASE_INVENTORY, 'base_verified_files': 16160})
    for relative, data in replacement.items():
        target = destination / safe_path(relative)
        previous = inventory.get(relative)
        if (relative.endswith('/database-source-contract.json') and (previous is not None or target.exists())):
            raise ValueError('Unexpected preexisting database source contract')
        if not relative.endswith('/database-source-contract.json') and previous is None:
            raise ValueError('Missing original guard to replace')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('wb' if previous else 'xb') as output:
            output.write(data)
        if hash_file(target) != DATABASE_GUARD_FILES[relative]:
            raise ValueError('Staged database guard hash mismatch')
        inventory[relative] = {'bytes': len(data), 'sha256': DATABASE_GUARD_FILES[relative],
            'source': 'reviewed-local-two-context-database-guards',
            'replaces_sha256': previous['sha256'] if previous else None}
    # Fill only independently established expectations; host-owned/private facts
    # stay null. This is a draft only; no approved manifest is written.
    draft = draft_manifest(inventory)
    draft['schema'] = 2
    draft['database'] = {'name': 'openmu', 'queryUser': None, 'pgPassFile': None,
        'systemIdentifier': None, 'migrationHistories': contract['migrationHistories'],
        'runtimeRoles': None, 'configurationIds': contract['configurationIds']}
    draft['endpoints'] = contract['endpoints']
    save(destination / 'package-inventory.json', inventory)
    save(destination / 'windows11-launch-manifest.draft.json', draft)
    status.update(verified_files=len(inventory), base_files_reused=16158,
        base_hashes='PRIOR_VERIFIED_NOT_REHASHED',
        database_guard_files_verified=3, database_guard_pins=DATABASE_GUARD_FILES,
        database_guard_base_inventory_sha256=DATABASE_GUARD_BASE_INVENTORY,
        database_guard_manifest_schema=2, database='BASELINE_IDENTIFIED_NOT_PROVISIONED',
        database_source_contract='PINNED_SOURCE_AND_COMPILED_METADATA_RECONCILED',
        database_setup_implementation='NOT_IMPLEMENTED',
        launcher_overlay='reviewed-local-two-context-database-guards',
        launchEnabled=False, approvedLaunchManifestSha256=None)
    status['missing'] = [item for item in status['missing']
                         if item != 'independently reconciled migration/configuration IDs']
    status['missing'] += ['actual DB history/schema and restricted-role acceptance',
                         'explicit persistent AutoUpdateSchema=false and ReadConsoleInput=true setup approval']
    save(destination / 'packaging-status.json', status)
    return status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--client-archive', type=Path)
    parser.add_argument('--server-archive', type=Path)
    parser.add_argument('--runtime-only', action='store_true',
                        help='Control staging only; Data/fonts/launcher stay mandatory and missing')
    parser.add_argument('--base-package', type=Path)
    parser.add_argument('--dependency-archives', type=Path)
    parser.add_argument('--database-guards', action='store_true', help='Only the pinned two-context guard overlay on the dependency control')
    args = parser.parse_args()
    if args.database_guards:
        if not args.base_package or args.dependency_archives or args.repo or args.client_archive or args.server_archive or args.runtime_only:
            parser.error('Database guard continuation requires only base-package, database-guards and destination')
        result = package_database_guards(args.base_package.absolute(), args.destination.absolute())
    elif args.base_package:
        if not args.dependency_archives or args.repo or args.client_archive or args.server_archive or args.runtime_only:
            parser.error('Dependency continuation requires only base-package, dependency-archives and destination')
        specification = Path(__file__).resolve().parents[1] / 'docs/windows11-dependencies.json'
        result = package_dependencies(args.base_package, args.destination.absolute(), args.dependency_archives, specification)
    else:
        if not args.repo or args.dependency_archives:
            parser.error('Asset/runtime mode requires repo and no dependency-archives')
        result = package(args.repo.resolve(), args.destination.absolute(), args.client_archive,
                         args.server_archive, args.runtime_only)
    print(json.dumps(result))
