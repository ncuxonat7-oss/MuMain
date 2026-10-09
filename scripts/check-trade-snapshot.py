#!/usr/bin/env python3
"""Verify an observed finite trade from saved PostgreSQL snapshots, not UI guesses."""
import argparse
import json
from pathlib import Path

DONOR = 'testgmDk'
RECIPIENT = 'test300Dk'
BASELINE = 'test0Dk'


def read_rows(path):
    rows = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def character_state(rows, name):
    character = next(row for row in rows if row.get('Name') == name and 'InventoryId' in row)
    storage = next(row for row in rows if row.get('Id') == character['InventoryId'] and 'Money' in row)
    attributes = {row['DefinitionId']: row['Value'] for row in rows if row.get('CharacterId') == character['Id'] and 'Value' in row}
    items = {row['Id']: row for row in rows if row.get('ItemStorageId') == character['InventoryId']}
    return {'id': character['Id'], 'money': storage['Money'], 'attributes': attributes, 'items': items}


def compare(before_rows, after_rows, amount, item_uuid):
    before = {name: character_state(before_rows, name) for name in (DONOR, RECIPIENT, BASELINE)}
    after = {name: character_state(after_rows, name) for name in before}
    donor_delta = after[DONOR]['money'] - before[DONOR]['money']
    recipient_delta = after[RECIPIENT]['money'] - before[RECIPIENT]['money']
    assertions = {
        'donor_debited_expected_zen': donor_delta == -amount,
        'recipient_credited_expected_zen': recipient_delta == amount,
        'zen_conserved': donor_delta + recipient_delta == 0,
        'same_character_identities': all(before[name]['id'] == after[name]['id'] for name in before),
        'baseline_dk_stats_unchanged': before[BASELINE]['attributes'] == after[BASELINE]['attributes'],
        'baseline_dk_items_unchanged': before[BASELINE]['items'] == after[BASELINE]['items'],
    }
    prior = before[DONOR]['items'].get(item_uuid)
    received = after[RECIPIENT]['items'].get(item_uuid)
    assertions['same_item_uuid_transferred'] = prior is not None and received is not None and item_uuid not in after[DONOR]['items']
    fields = ('DefinitionId', 'Durability', 'Level', 'HasSkill', 'SocketCount', 'PetExperience')
    assertions['item_identity_quantity_options_preserved'] = bool(prior and received) and all(prior.get(key) == received.get(key) for key in fields)
    before_items = set(before[DONOR]['items']) | set(before[RECIPIENT]['items'])
    after_items = set(after[DONOR]['items']) | set(after[RECIPIENT]['items'])
    assertions['two_inventories_item_ids_conserved'] = before_items == after_items
    return {'assertions': assertions, 'donor_zen_delta': donor_delta, 'recipient_zen_delta': recipient_delta,
            'item_uuid': item_uuid, 'pass': all(assertions.values()), 'limit': 'Saved observed item/Zen transfer and untouched DK; party/GUI/cancel/crash safety not proven by DB alone.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--zen', type=int, required=True)
    parser.add_argument('--item-uuid', required=True)
    args = parser.parse_args()
    if args.zen <= 0:
        parser.error('Expected observed trade amount must be positive.')
    result = compare(read_rows(args.before), read_rows(args.after), args.zen, args.item_uuid)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['pass'] else 1)
