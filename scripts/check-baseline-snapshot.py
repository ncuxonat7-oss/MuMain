#!/usr/bin/env python3
"""Read-only bulk integrity check of existing gameplay evidence; no builds or server writes."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def run(evidence, output):
    snapshot = evidence / 'final-database.jsonl'
    rows = [json.loads(line) for line in snapshot.read_text(encoding='utf-8-sig').splitlines() if line.strip().startswith('{')]
    schemas = {}
    for row in rows:
        if 'table_schema' in row and 'column_name' in row:
            key = (row['table_schema'], row['table_name'])
            schemas.setdefault(key, set()).add(row['column_name'])
    tables = {}
    for key, columns in schemas.items():
        tables[key] = [row for row in rows if set(row) == columns]
    items = tables.get(('data', 'Item'), [])
    stores = tables.get(('data', 'ItemStorage'), [])
    attributes = tables.get(('data', 'StatAttribute'), [])
    definitions = tables.get(('config', 'AttributeDefinition'), [])
    characters = tables.get(('data', 'Character'), [])
    checks = []

    def record(name, problems, count, scope):
        checks.append({'check': name, 'status': 'FAIL' if problems else 'PASS', 'records': count, 'scope': scope, 'problems': problems[:25], 'problem_count': len(problems)})

    for name, data in [('Items', items), ('ItemStorage', stores), ('StatAttribute', attributes), ('AttributeDefinition', definitions)]:
        if not data:
            record(name + ' captured', ['Required table missing or empty in snapshot'], 0, 'snapshot coverage')
        ids = Counter(row['Id'] for row in data)
        record(name + ' unique IDs', [key for key, count in ids.items() if count > 1], len(data), 'all captured rows')
    store_ids = {row['Id'] for row in stores}
    definition_ids = {row['Id'] for row in definitions}
    record('Item storage references', [row['Id'] for row in items if row.get('ItemStorageId') and row['ItemStorageId'] not in store_ids], len(items), 'all captured items; unowned items excluded')
    occupied = Counter((row['ItemStorageId'], row['ItemSlot']) for row in items if row.get('ItemStorageId'))
    record('Unique occupied anchor slots', [list(key) for key, count in occupied.items() if count > 1], len(items), 'anchor slots only; multi-cell geometry not captured')
    record('Nonnegative item durability', [row['Id'] for row in items if row.get('Durability', 0) < 0], len(items), 'all captured items')
    record('Attribute definition references', [row['Id'] for row in attributes if row['DefinitionId'] not in definition_ids], len(attributes), 'all captured stat attributes')
    owners = Counter((row.get('CharacterId'), row.get('AccountId'), row['DefinitionId']) for row in attributes if row.get('CharacterId') or row.get('AccountId'))
    record('Unique attributes per owner', [list(key) for key, count in owners.items() if count > 1], len(attributes), 'all captured account/character-owned attributes')
    record('Captured character inventories', [row['Name'] for row in characters if row.get('InventoryId') and row['InventoryId'] not in store_ids], len(characters), 'only characters selected by snapshot SQL')
    expected = [('Main.exe SHA256', 'client-binary-hashes.txt', '9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5'),
                ('Client library SHA256', 'client-binary-hashes.txt', '9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7'),
                ('Approved resource archive SHA256', 'resources.txt', '8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d')]
    for label, filename, digest in expected:
        text = (evidence / filename).read_text(encoding='utf-8-sig') if (evidence / filename).exists() else ''
        record(label, [] if digest.lower() in text.lower() else ['Expected frozen checksum absent'], 1, 'runtime package provenance; not every asset rendering')
    verification = evidence / 'verification.json'
    if verification.exists():
        results = json.loads(verification.read_text(encoding='utf-8-sig'))
        record('Real-client persisted gameplay smoke', [key for key, value in results.items() if value is not True], len(results), 'existing runtime assertions plus authentic screenshots')
    else:
        checks.append({'check': 'Real-client persisted gameplay smoke', 'status': 'NOT_CHECKED', 'records': 0, 'scope': 'verification.json absent', 'problems': []})
    not_checked = ['Maps/gates/spawn/shop/item-definition/drop/skill/quest configuration references: not exported by this snapshot; retain existing baseline audit.',
                   'Client BMD tables, all models/textures/animations and item footprint overlap: this checker does not inspect or render them.',
                   'Party/trade/guild/events/crafting and load: not exercised by these integrity checks.',
                   'A PASS here is not a percentage of total MU content completion. Existing 423 tests were not rerun.']
    result = {'snapshot_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(), 'checks': checks, 'not_checked': not_checked}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'baseline-snapshot-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    lines = ['# Bulk baseline snapshot integrity check', '', 'Read-only verification of captured database records and frozen runtime packages. No game configuration changes, rebuilds or repeated GUI tests.', '', '| Check | Result | Records | Scope |', '|---|---|---:|---|']
    lines += [f"| {r['check']} | {r['status']} | {r['records']} | {r['scope']} |" for r in checks]
    lines += ['', '## Explicitly not checked', ''] + ['- ' + item for item in not_checked]
    lines += ['', '## Reuse', '', '```sh', 'python3 scripts/check-baseline-snapshot.py --evidence PATH_TO_EXTRACTED_GAMEPLAY_ARTIFACT --out docs/generated-baseline-check', '```', '', 'Keep genuine client screenshots and the database backup as runtime evidence. Do not substitute these static checks for feature-level runtime proof.']
    (output / 'baseline-snapshot-check.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'checks': len(checks), 'failed': [r['check'] for r in checks if r['status']=='FAIL'], 'items': len(items), 'stores': len(stores), 'attributes': len(attributes), 'definitions': len(definitions), 'characters_in_snapshot': len(characters)}))
    return int(any(row['status'] == 'FAIL' for row in checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(run(args.evidence, args.out))
