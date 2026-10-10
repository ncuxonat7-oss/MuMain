#!/usr/bin/env python3
"""Guard the fixed run16 fixture; accepted skill use always needs separate review."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

RUN16_ZIP_SHA256 = '189ba4bf3e9715aef05d53517383d15abda4d1bbcb24e2b3579a8784ff7600f5'
ENTRY_ID = '3a27a101-0000-72c9-8e81-6912c7b14844'


def helpers():
    spec = importlib.util.spec_from_file_location('skill41', Path(__file__).with_name('check-skill41-snapshot.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def known_skill(path, helper):
    if helper.read_skills(path) != {helper.SKILL_ID}:
        raise ValueError('Use-only requires exactly the already learned skill41')
    entry = json.loads(path.read_text(encoding='utf-8-sig'))['skills'][0]
    if entry['Id'] != ENTRY_ID or entry['Level'] != 0:
        raise ValueError('Use-only skill entry differs from run16')


def check_stage(directory, stage, helper):
    known_skill(directory / f'{stage}-skill41.json', helper)
    rows = helper.snapshot_helpers().read_rows(directory / f'{stage}-database.jsonl')
    actor = helper.snapshot_helpers().character_state(rows, helper.ACTOR)
    if actor['id'] != helper.ACTOR_ID:
        raise ValueError('Use-only actor identity differs')
    if any(row.get('Id') == helper.ORB_ID for row in rows):
        raise ValueError('Consumed run16 orb unexpectedly present; do not relearn')
    return rows


def assess(directory, ready_only=False):
    helper = helpers()
    before = check_stage(directory, 'ready', helper)
    if ready_only:
        return {'status': 'READY_FOR_USE', 'accepted_use_effect_cost': 'UNKNOWN'}
    after = check_stage(directory, 'final', helper)
    checks = helper.scoped_state_assertions(helper.snapshot_helpers(), before, after)
    return {
        'status': 'FIXTURE_PRESERVED' if all(checks.values()) else 'FAIL',
        'assertions': checks,
        'accepted_use_effect_cost': 'UNKNOWN',
        'limits': 'Not an accepted-use verdict. Review selected skill41, MP/AG with regeneration, '
                  'target damage/server evidence and timed screenshots. No new learning/relog credit.',
    }


def restore_archive(archive, destination):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != RUN16_ZIP_SHA256:
        raise ValueError('Run16 archive hash mismatch; refusing extraction')
    with zipfile.ZipFile(archive) as source:
        dump = source.read('gameplay-test-db.dump')
    if not dump.startswith(b'PGDMP'):
        raise ValueError('Run16 dump is not PostgreSQL custom format')
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'gameplay-test-db.dump').write_bytes(dump)
    return {'status': 'RESTORED_EXACT_RUN16_ARCHIVE', 'archive_sha256': RUN16_ZIP_SHA256}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--ready', action='store_true')
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    try:
        if args.archive:
            if not args.destination or args.evidence or args.ready:
                raise ValueError('Archive mode requires only archive and destination')
            result = restore_archive(args.archive, args.destination)
        else:
            if not args.evidence or args.destination:
                raise ValueError('Evidence directory required')
            result = assess(args.evidence, args.ready)
    except (OSError, ValueError, KeyError, TypeError, StopIteration, zipfile.BadZipFile) as error:
        result = {'status': 'UNKNOWN', 'reason': str(error), 'accepted_use_effect_cost': 'UNKNOWN'}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] in ('READY_FOR_USE', 'FIXTURE_PRESERVED', 'RESTORED_EXACT_RUN16_ARCHIVE') else 1


if __name__ == '__main__':
    raise SystemExit(main())
