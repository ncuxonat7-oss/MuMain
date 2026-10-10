#!/usr/bin/env python3
"""Apply a hash-guarded, idempotent metadata correction to pinned client Data."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def corrected_bytes(original, specification):
    document = json.loads(original)
    entries = {item['number']: item for item in document['items']}
    if len(entries) != len(document['items']) or document['group'] != specification['group']:
        raise ValueError('Duplicate identities or unexpected item group')
    for item in specification['add']:
        if item['number'] in entries:
            raise ValueError('Expected missing item already exists')
        document['items'].append(item)
    for change in specification['update']:
        item = entries[change['number']]
        for field in change['remove']:
            item.pop(field, None)
        item.update(change['set'])
    document['items'].sort(key=lambda item: item['number'])
    return (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def apply(data_directory, specification):
    target = data_directory / specification['path']
    original = target.read_bytes()
    actual = sha256(original)
    if actual == specification['after_sha256']:
        return {'status': 'ALREADY_APPLIED', 'sha256': actual}
    if actual != specification['before_sha256']:
        raise ValueError(
            f'Unrecognized client metadata; refusing overwrite: actual_sha256={actual}; '
            f'expected_before_sha256={specification["before_sha256"]}; '
            f'expected_after_sha256={specification["after_sha256"]}; byte_count={len(original)}'
        )
    corrected = corrected_bytes(original, specification)
    if sha256(corrected) != specification['after_sha256']:
        raise ValueError('Correction output hash differs from reviewed overlay')
    backup = target.with_suffix(target.suffix + '.baseline-backup')
    if backup.exists() and backup.read_bytes() != original:
        raise ValueError('Existing backup differs; refusing overwrite')
    backup.write_bytes(original)
    temporary = target.with_suffix(target.suffix + '.baseline-tmp')
    temporary.write_bytes(corrected)
    temporary.replace(target)
    return {'status': 'APPLIED', 'sha256': sha256(corrected)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--overlay', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.data, json.loads(args.overlay.read_text(encoding='utf-8')))))
