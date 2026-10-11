#!/usr/bin/env python3
"""Stage the approved one-run Windows smoke; never starts a server or edits a DB.

Usage: python scripts/prepare-local-bind-smoke.py inputs|source|runtime|evidence
Run only from the checked-out repository root in the manual Windows workflow.
"""
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

PIN = 'd067b3c11c23c3145de6e2c76201ab9a93b267c8'
SDK = '10.0.109'
RESOURCE = 'MuMain-data-4b0ab29c58b27fc4.tar.gz'
RESOURCE_SHA = '8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d'
DUMP_SHA = '0a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478'
CLIENT_HASHES = {
    'Main.exe': '9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5',
    'MUnique.Client.Library.dll': '9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7',
}
MAX_UNPACKED = 3 * 1024**3


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    checksum = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(chunk)
    return checksum.hexdigest()


def save_json(name, value):
    Path('evidence').mkdir(exist_ok=True)
    Path('evidence', name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def extract_one(archive, basename, destination):
    with zipfile.ZipFile(archive) as source:
        members = [m for m in source.infolist() if PurePosixPath(m.filename).name == basename]
        require(len(members) == 1, 'Expected exactly one input: ' + basename)
        require(members[0].file_size < MAX_UNPACKED, 'Input exceeds bound')
        with source.open(members[0]) as src, Path(destination).open('wb') as dst:
            shutil.copyfileobj(src, dst)


def extract_tar(archive, destination):
    root = Path(destination).resolve()
    with tarfile.open(archive, 'r:gz') as source:
        members = source.getmembers()
        require(sum(m.size for m in members) < MAX_UNPACKED, 'Archive exceeds bound')
        for member in members:
            name = PurePosixPath(member.name)
            require(not name.is_absolute() and '..' not in name.parts and ':' not in member.name
                    and '\\' not in member.name, 'Unsafe archive path')
            require(member.isdir() or member.isfile(), 'Archive links/devices are not allowed')
            target = root.joinpath(*name.parts)
            require(target == root or root in target.parents, 'Archive escaped destination')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as src, target.open('wb') as dst:
                    shutil.copyfileobj(src, dst)


def inputs():
    require(not Path('client').exists() and not Path('saved-gameplay').exists(), 'Fresh input directories required')
    Path('saved-gameplay').mkdir()
    dump = Path('saved-gameplay/gameplay-test-db.dump')
    extract_one('downloads/database.zip', dump.name, dump)
    require(digest(dump) == DUMP_SHA, 'Pinned DB dump mismatch')
    archive = Path('downloads/client.tar.gz')
    extract_one('downloads/client.zip', 'MuMain-windows-native-x64-release-editor-off-no-data.tar.gz', archive)
    extract_tar(archive, 'client')
    for name, expected in CLIENT_HASHES.items():
        require(digest(Path('client', name)) == expected, 'Client binary mismatch: ' + name)
    resource = Path('downloads', RESOURCE)
    url = 'https://github.com/sven-n/MuMain/releases/download/data-4b0ab29c58b27fc4/' + RESOURCE
    with urllib.request.urlopen(url, timeout=120) as src, resource.open('wb') as dst:
        shutil.copyfileobj(src, dst)
    require(digest(resource) == RESOURCE_SHA, 'Frozen Data/fonts archive mismatch')
    extract_tar(resource, 'client')
    subprocess.run([sys.executable, 'scripts/apply-client-overlay.py', '--data', 'client/Data',
                    '--overlay', 'patches/client-socket-metadata.json'], check=True)
    require(Path('client/fonts').is_dir() and Path('client/shaders').is_dir(), 'Incomplete client assets')
    Path('client/config.ini').write_text(
        '[LOGIN]\nRememberMe=0\nLanguage=Eng\n[Window]\nWidth=1024\nHeight=768\nWindowed=1\n'
        '[Audio]\nSoundVolume=0\nMusicVolume=0\n[CONNECTION SETTINGS]\nServerIP=127.0.0.1\n'
        'ServerPort=44406\n[UI]\nLocale=en\n[Render]\nVSync=0\n', encoding='utf-8')
    save_json('staged-inputs.json', {'dump_sha256': DUMP_SHA, 'client': CLIENT_HASHES,
                                  'resources_sha256': RESOURCE_SHA, 'source': url})


def source():
    server = Path('server-source').resolve()
    head = subprocess.check_output(['git', '-C', str(server), 'rev-parse', 'HEAD'], text=True).strip()
    require(head == PIN, 'Wrong OpenMU revision')
    require(not subprocess.check_output(['git', '-C', str(server), 'status', '--porcelain']), 'Dirty server checkout')
    names = ['patches/openmu-trade-money.patch', 'patches/openmu-local-only-bind.patch',
             'patches/openmu-local-only-bind-provenance.json']
    # Obtain canonical Git bytes rather than Windows checkout line endings.
    for name in names:
        Path(name).write_bytes(subprocess.check_output(['git', 'show', 'HEAD:' + name]))
    require(digest(names[0]) == '85d8428452a25fef598c19ef2cda8d0ab94b2d5c13296481445ae84b7fad197d', 'Money patch identity changed')
    require(digest(names[1]) == 'd0ee9ada196913fdeaa8036cc57c7712ac77817117a6dd5d19e926965cf6a1a9', 'Reviewed bind patch identity changed')
    subprocess.run([sys.executable, 'scripts/check-local-bind-source.py', str(server)], check=True)
    for name in names[:2]:
        patch = str(Path(name).resolve())
        subprocess.run(['git', 'apply', '--check', patch], cwd=server, check=True)
        subprocess.run(['git', 'apply', patch], cwd=server, check=True)
    require(digest(server / 'src/Network/Listener.cs') ==
            '7f887ef3e58ee009beee04c6632ffe6b4f290669ae098f39ff72778c6561f2a3', 'Patched Listener mismatch')
    for name in names[:2]:
        subprocess.run(['git', 'apply', '--reverse', '--check', str(Path(name).resolve())], cwd=server, check=True)
    save_json('source-provenance.json', {
        'openmu': head, 'sdk': SDK, 'workflow_commit': os.environ['GITHUB_SHA'],
        'patches': {name: digest(name) for name in names},
        'helper_sha256': digest(server / 'src/Network/LocalOnlyBinding.cs'),
        'limit': 'Build candidate; integration status is separate from source applicability.'})
    (server / 'global.json').write_text(json.dumps({'sdk': {
        'version': SDK, 'rollForward': 'disable', 'allowPrerelease': False}}), encoding='utf-8')


def runtime():
    root = Path('server-source/src/Startup/bin/Release')
    for name in ('MUnique.OpenMU.Startup.dll', 'MUnique.OpenMU.GameLogic.dll',
                 'MUnique.OpenMU.Network.dll', 'MUnique.OpenMU.Startup.deps.json',
                 'MUnique.OpenMU.Startup.runtimeconfig.json', 'ConnectionSettings.xml'):
        require((root / name).is_file(), 'Missing new runtime file: ' + name)
    files = sorted(p for p in root.rglob('*') if p.is_file())
    require(files and sum(p.stat().st_size for p in files) < MAX_UNPACKED, 'Runtime exceeds bound')
    save_json('runtime-manifest.json', {p.relative_to(root).as_posix(): digest(p) for p in files})
    # Require appsettings and DB settings to match tracked files at the pinned source.
    tracked = subprocess.check_output(['git', '-C', 'server-source', 'ls-files'], text=True).splitlines()
    for config in list(root.rglob('appsettings*')) + [root / 'ConnectionSettings.xml']:
        if not config.is_file():
            continue
        candidates = [name for name in tracked if Path(name).name == config.name]
        require(any(subprocess.check_output(['git', '-C', 'server-source', 'show', 'HEAD:' + name])
                    == config.read_bytes() for name in candidates), 'Unpinned application/DB settings output')
    # Package BEFORE starting server: no generated DB, logs, or session secrets.
    with zipfile.ZipFile('downloads/openmu-money-local-bind-runtime.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    save_json('runtime-archive.json', {'sha256': digest('downloads/openmu-money-local-bind-runtime.zip')})


def evidence():
    Path('evidence').mkdir(exist_ok=True)
    save_json('job-status.json', {'status': os.environ.get('SMOKE_JOB_STATUS', 'unknown'),
                                'runtime_success_requires': 'persistedState PASS plus separate native screenshot review; no aggregate PASS'})
    result = Path('evidence/smoke-result.json')
    status = json.loads(result.read_text(encoding='utf-8-sig'))['status'] if result.exists() else 'NOT_RUN'
    Path('evidence/result.txt').write_text(status + '\n', encoding='utf-8')
    log = Path('private-logs/build.txt')
    if log.exists():
        tail = log.read_text(encoding='utf-8', errors='replace')[-200_000:]
        Path('evidence/build-tail.txt').write_text(tail, encoding='utf-8')
    events = {}
    for path in Path('private-logs').glob('*-server.*'):
        text = path.read_text(encoding='utf-8', errors='replace')[-1_000_000:]
        events[path.name] = {
            'bytes': path.stat().st_size,
            'exception_types': sorted(set(re.findall(r'\b(?:System|Microsoft|Npgsql|MUnique)\.[A-Za-z0-9_.]*Exception\b', text))),
            'saving_sessions_seen': 'Saving all open sessions' in text,
            'actor_enabled_seen': 'Actor control endpoint enabled' in text,
            'error_markers': len(re.findall(r'(?im)\b(?:ERR|FTL|Error|Fatal)\b|Unhandled exception|Exception:', text)),
        }
    save_json('server-log-summary.json', events)
    total = sum(p.stat().st_size for p in Path('evidence').rglob('*') if p.is_file())
    require(total < 20 * 1024**2, 'Evidence exceeded 20 MiB bound')


if __name__ == '__main__':
    require(len(sys.argv) == 2 and sys.argv[1] in ('inputs', 'source', 'runtime', 'evidence'), 'Invalid stage')
    globals()[sys.argv[1]]()
