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


def cancel_progress(state, name, mutable_attributes, item_uuid):
    if name == BASELINE:
        return state
    progress = dict(state)
    progress['attributes'] = {key: value for key, value in state['attributes'].items() if key not in mutable_attributes}
    progress['items'] = {}
    for key, item in state['items'].items():
        stable_item = dict(item)
        if key != item_uuid and 0 <= item.get('ItemSlot', -1) <= 11:
            stable_item.pop('Durability', None)
        progress['items'][key] = stable_item
    return progress


def compare_cancel(before_rows, after_rows, item_uuid):
    names = (DONOR, RECIPIENT, BASELINE)
    before = {name: character_state(before_rows, name) for name in names}
    after = {name: character_state(after_rows, name) for name in names}
    assertions = {'offered_item_present_in_original_inventory': item_uuid in before[DONOR]['items']}
    assertions['offered_item_exactly_restored'] = (item_uuid in before[DONOR]['items']
                                                 and before[DONOR]['items'][item_uuid] == after[DONOR]['items'].get(item_uuid))
    mutable_attributes = {row['Id'] for row in before_rows if row.get('Designation') == 'Current Ability'}
    for name in names:
        before_progress = cancel_progress(before[name], name, mutable_attributes, item_uuid)
        after_progress = cancel_progress(after[name], name, mutable_attributes, item_uuid)
        for field in ('id', 'money', 'attributes', 'items'):
            assertions[f'{name}_{field}_unchanged'] = before_progress[field] == after_progress[field]
    return {'assertions': assertions, 'pass': all(assertions.values()), 'outcome': 'cancel',
            'item_uuid': item_uuid, 'limit': 'Native offer/cancel/relog evidence required. Ignores Current Ability regeneration and other equipped-item wear, never offered-item quantity/slot/options. Core DK exact. Hard server-crash safety unproven.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--zen', type=int)
    parser.add_argument('--outcome', choices=('complete', 'cancel'), default='complete')
    parser.add_argument('--item-uuid', required=True)
    args = parser.parse_args()
    if args.outcome == 'complete' and (args.zen is None or args.zen <= 0):
        parser.error('Expected observed trade amount must be positive.')
    before_rows, after_rows = read_rows(args.before), read_rows(args.after)
    result = (compare_cancel(before_rows, after_rows, args.item_uuid) if args.outcome == 'cancel'
              else compare(before_rows, after_rows, args.zen, args.item_uuid))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['pass'] else 1)
