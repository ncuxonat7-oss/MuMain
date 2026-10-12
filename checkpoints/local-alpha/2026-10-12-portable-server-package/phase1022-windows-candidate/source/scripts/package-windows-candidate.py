#!/usr/bin/env python3
"""Stage/check one pinned disabled server candidate; never install or launch."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

PLAN = 'phase1015-windows-candidate-plan/proposed-overlay-inventory.json'
PLAN_HASH = '08dea6de7a5fcc67bda71b6e68d9f72d1a64b5366f804766cb9a4537164f1d59'
HELPER = 'phase2104-admin-availability/source/scripts/package-windows11-local.py'
HELPER_HASH = 'c700e0ed3a0fe2a6bbd77de0f0bd5c60f814ca4dd49852cf15734473a53459e7'
SOURCE_PINS = 'phase1022-windows-candidate/source/docs/disabled-launcher-source-pins.json'
SOURCE_PINS_HASH = 'e0afe98d38fd9bc60de21938b375016020f3e33c0f5883db3638a4df565f2670'
BASE = 'phase2027-powershell-check/control-database-guards-20261011'
BASE_STATUS_HASH = '35013e776fee1e0e967157dbcb653a3237605cf62f996c61e31f84a7abde57d6'
MAX_FILE = 64 * 1024 * 1024
CONTRACT = 'candidate-integrity.json'
STATUS = 'candidate-status.json'
EXCLUDED = {'MUnique.OpenMU.Startup', 'MUnique.OpenMU.Web.AdminPanel', 'MUnique.OpenMU.Web.Map'}
BLOCKERS = ['NOT_WINDOWS_ACCEPTED', 'RUNTIME_GRANTS_UNRESOLVED',
            'STATIC_WEB_ASSET_LINUX_PATHS', 'COMPONENT_ONLY_NOT_FULL_PACKAGE',
            'LEGACY_LAUNCHER_RUNTIME_CONTRACT_NOT_ALIGNED']


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Unsafe path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Unsafe path')
    for part in path.parts:
        stem = part.split('.')[0].upper()
        if part.endswith((' ', '.')) or stem in {'CON', 'PRN', 'AUX', 'NUL'} or re.fullmatch(r'(COM|LPT)[1-9]', stem):
            raise ValueError('Unsafe Windows path')
    return path


def no_links(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('Symlink path forbidden')


def regular(root, relative):
    path = root / safe_relative(relative)
    no_links(path)
    if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('Missing regular file')
    return path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def pinned_json(root, name, expected):
    path = regular(root, name)
    if digest(path) != expected:
        raise ValueError('Pinned input hash mismatch')
    return json.loads(path.read_text())


def load_helper(root):
    path = regular(root, HELPER)
    if digest(path) != HELPER_HASH:
        raise ValueError('Packager helper pin mismatch')
    spec = importlib.util.spec_from_file_location('preserved_packager', path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def check_rows(rows):
    seen = set()
    for row in rows:
        path = safe_relative(row['target'])
        safe_relative(row['source'])
        if path.parts[0] not in ('server', 'scripts') or len(path.parts) < 2:
            raise ValueError('Unexpected target area')
        if row['target'].casefold() in seen:
            raise ValueError('Case-insensitive target collision')
        seen.add(row['target'].casefold())
        if type(row['bytes']) is not int or not 0 < row['bytes'] <= MAX_FILE:
            raise ValueError('Invalid file size')
        if not re.fullmatch('[0-9a-f]{64}', row['sha256']):
            raise ValueError('Invalid hash')
        if path.parts[0] == 'server' and (path.name in EXCLUDED or path.name in {n + '.exe' for n in EXCLUDED}):
            raise ValueError('Native apphost excluded')


def disabled_status(complete=False):
    return {'status': 'VERIFIED_COMPONENT_NOT_RUNNABLE' if complete else 'INCOMPLETE_NOT_RUNNABLE',
            'launchEnabled': False, 'approvedLaunchManifestSha256': None,
            'windowsAcceptance': 'NOT_RUN', 'setupExecution': 'BLOCKED',
            'runtimeGrantStatus': 'RUNTIME_GRANTS_UNRESOLVED', 'blockers': BLOCKERS}


def make_contract(plan, source_pins):
    rows = plan['serverRows'] + source_pins['files']
    check_rows(rows)
    return {'schema': 1, 'kind': 'DISABLED_SERVER_COMPONENT_ONLY',
            'planSha256': PLAN_HASH, 'sourcePinsSha256': SOURCE_PINS_HASH,
            'basePackage': BASE, 'baseInventorySha256': plan['baseInventorySha256'],
            'originalRuntimeArchivePreservedInBase': True,
            'historicalRuntimePinsCertifyCandidate': False,
            'serverCount': len(plan['serverRows']), 'sourceSnapshotCount': len(source_pins['files']),
            'unchanged': 93, 'replacements': 90, 'files': rows,
            'nativeApphostExclusions': plan['nativeApphostExclusions'],
            'launchEnabled': False, 'approvedLaunchManifestSha256': None,
            'blockers': BLOCKERS}


def load_contract(root):
    plan = pinned_json(root, PLAN, PLAN_HASH)
    sources = pinned_json(root, SOURCE_PINS, SOURCE_PINS_HASH)
    pinned_json(root, BASE + '/package-inventory.json', plan['baseInventorySha256'])
    status = pinned_json(root, BASE + '/packaging-status.json', BASE_STATUS_HASH)
    pinned_json(root, 'phase2129-csharp-build/server-build-inventory.json', plan['phase2129InventorySha256'])
    pinned_json(root, 'phase2129-csharp-build/binary-json-candidate/manifest.json', plan['binaryJsonManifestSha256'])
    if status['launchEnabled'] is not False or status['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Baseline must remain disabled')
    counts = {kind: sum(r['action'] == kind for r in plan['serverRows'])
              for kind in ('REPLACE', 'REUSE_IDENTICAL_BASE')}
    if len(plan['serverRows']) != 183 or counts != {'REPLACE': 90, 'REUSE_IDENTICAL_BASE': 93}:
        raise ValueError('Unexpected candidate set')
    return make_contract(plan, sources)


def save_new(path, document):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(document, stream, indent=2)
        stream.write('\n')


def check_exact_tree(destination, expected):
    no_links(destination)
    actual = set()
    for path in destination.rglob('*'):
        no_links(path)
        mode = path.stat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError('Nonregular candidate member')
        actual.add(path.relative_to(destination).as_posix())
    if actual != expected:
        raise ValueError('Missing or extra candidate file')


def verify_payload(destination, contract):
    check_rows(contract['files'])
    expected = {row['target'] for row in contract['files']} | {CONTRACT, STATUS}
    check_exact_tree(destination, expected)
    for row in contract['files']:
        path = regular(destination, row['target'])
        if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('Candidate file identity mismatch')
    recorded = json.loads(regular(destination, CONTRACT).read_text())
    if recorded != contract:
        raise ValueError('Candidate contract differs from pinned source')


def verify_guards(destination):
    directory = destination / 'scripts/windows11'
    contract = json.loads((directory / 'local-session-contract.json').read_text())
    if contract['launchEnabled'] is not False or contract['approvedLaunchManifestSha256'] is not None:
        raise ValueError('Launcher unexpectedly enabled')
    policy_path = directory / 'first-setup-policy.json'
    policy = json.loads(policy_path.read_text())
    setup = (directory / 'FirstSetup.ps1').read_text()
    if policy['runtimeGrantStatus'] == 'APPROVED_FOR_DEPLOYMENT':
        raise ValueError('Setup unexpectedly approved')
    if digest(policy_path) not in setup or "throw 'RUNTIME_GRANTS_UNRESOLVED'" not in setup:
        raise ValueError('Unresolved setup fence missing')


def verify(destination, contract):
    verify_payload(destination, contract)
    if json.loads(regular(destination, STATUS).read_text()) != disabled_status(True):
        raise ValueError('Candidate incomplete or status changed')
    verify_guards(destination)
    return {'result': 'PASS_INTEGRITY_ONLY', 'serverFiles': contract['serverCount'],
            'sourceSnapshots': contract['sourceSnapshotCount'],
            'verifiedBytes': sum(r['bytes'] for r in contract['files']),
            'launchEnabled': False, 'approvedLaunchManifestSha256': None,
            'windowsAcceptance': 'NOT_RUN', 'blockers': BLOCKERS}


def assert_launch_allowed(destination, contract):
    verify(destination, contract)
    # This command is a denial check, not a launcher. No status edit grants launch.
    raise ValueError('LAUNCH_DENIED: incomplete package; Windows acceptance and setup unresolved')


def stage(root, destination, contract, helper):
    no_links(destination)
    if destination.exists():
        raise ValueError('Fresh destination required; overwrite refused')
    # Verify existence/type/size before claiming output; hash during checked copy.
    for row in contract['files']:
        path = regular(root, row['source'])
        if path.stat().st_size != row['bytes']:
            raise ValueError('Source size mismatch')
    destination.mkdir(parents=True, exist_ok=False)
    save_new(destination / STATUS, disabled_status())
    for row in contract['files']:
        target = destination / safe_relative(row['target'])
        target.parent.mkdir(parents=True, exist_ok=True)
        with regular(root, row['source']).open('rb') as stream:
            helper.copy_checked(stream, target, row['bytes'], row['sha256'])
    save_new(destination / CONTRACT, contract)
    verify_payload(destination, contract)
    verify_guards(destination)
    # A failed partial output is preserved with INCOMPLETE status, never reused.
    (destination / STATUS).write_text(json.dumps(disabled_status(True), indent=2) + '\n')
    return verify(destination, contract)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('stage', 'verify', 'launch-check'))
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    root = args.workspace.absolute()
    no_links(root)
    destination = args.destination.absolute()
    contract = load_contract(root)
    if args.action == 'stage':
        result = stage(root, destination, contract, load_helper(root))
    elif args.action == 'verify':
        result = verify(destination, contract)
    else:
        assert_launch_allowed(destination, contract)
        return
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
