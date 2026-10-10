#!/usr/bin/env python3
"""Dry-run capacity and packaging witnesses for four disjoint plain S6 mixes.

This models ingredient acceptance only. No crafting execution or import mode.
"""
import argparse
import importlib.util
import json
from pathlib import Path

GRID_COLUMNS = 8
GRID_ROWS = 4
SCOPED_IDS = (15, 16, 25, 26)


def load_mapper():
    spec = importlib.util.spec_from_file_location('ingredients',
        Path(__file__).with_name('map-s6-recipe-ingredients.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def server_accepts(required, inventory, items, mapper):
    remaining = list(inventory)
    for row in sorted(required, key=lambda r: r['MinimumAmount'], reverse=True):
        ids = {r['client_id'] for r in row['possible_items']}
        found = [i for i in remaining if i['id'] in ids
            and row['MinimumItemLevel'] <= i['level'] <= row['MaximumItemLevel']]
        count = sum(i['durability'] if mapper.server_stackable(items[i['id']]) else 1
                    for i in found)
        if count < row['MinimumAmount'] or (row['MaximumAmount'] and count > row['MaximumAmount']):
            return False
        remaining = [i for i in remaining if i not in found]
    return not remaining


def client_source_matches(source, item):
    return (source['TypeMin'] <= item['id'] <= source['TypeMax']
        and source['LevelMin'] <= item['level'] <= source['LevelMax']
        and source['DurabilityMin'] <= item['durability'] <= source['DurabilityMax'])


def client_accepts(sources, inventory, items, mapper):
    # Restricted to disjoint plain domains. The native grouping/allocation then
    # reduces to these totals; do not use this for overlapping or flagged mixes.
    remaining = list(inventory)
    for source in sources:
        found = [i for i in remaining if client_source_matches(source, i)]
        count = sum(i['durability'] if (items[i['id']]['Group'],
            items[i['id']]['Number']) in mapper.CLIENT_STACK_KEYS else 1 for i in found)
        if not source['CountMin'] <= count <= source['CountMax']:
            return False
        remaining = [i for i in remaining if i not in found]
    return not remaining


def place(inventory, items):
    occupied = set()
    slots = []
    for item in inventory:
        definition = items[item['id']]
        width, height = definition['Width'], definition['Height']
        if width <= 0 or height <= 0:
            raise ValueError('Invalid item footprint')
        slot = next((s for s in range(GRID_COLUMNS * GRID_ROWS)
            if s % GRID_COLUMNS + width <= GRID_COLUMNS
            and s // GRID_COLUMNS + height <= GRID_ROWS
            and not footprint(s, width, height) & occupied), None)
        if slot is None:
            return None
        occupied.update(footprint(slot, width, height))
        slots.append(slot)
    return slots


def footprint(slot, width, height):
    return {slot + x + y * GRID_COLUMNS for y in range(height) for x in range(width)}


def inventory_item(key, durability=1):
    return dict(id=key, level=0, durability=durability)


def witnesses(recipe, projection):
    if recipe['Number'] in (15, 16):
        key = projection['required'][0]['possible_items'][0]['client_id']
        return [(str(count) + '_jewels', [inventory_item(key) for _ in range(count)])
                for count in (25, 26, 32, 33)]
    full = []
    for row in projection['required']:
        key = row['possible_items'][0]['client_id']
        amount = row['MinimumAmount']
        if key in (6688, 6689, 6690):
            full.append(inventory_item(key, amount))
        else:
            full.extend(inventory_item(key) for _ in range(amount))
    split = []
    changed = False
    for item in full:
        if item['durability'] > 1 and not changed:
            amount = item['durability']
            split.extend([inventory_item(item['id'], amount // 2),
                          inventory_item(item['id'], amount - amount // 2)])
            changed = True
        else:
            split.append(item.copy())
    return [('full_containers', full), ('fragmented_equal_total', split)]


def audit_recipe(recipe, tables, client, items, mapper, audit):
    variants = [v for v in client['tables']['crafting'] if v['MixID'] == recipe['Number']]
    projection = audit.server_projection(tables, recipe)
    reason = mapper.unsupported(recipe, projection, variants)
    if reason:
        raise ValueError(reason)
    required = [mapper.requirement(r, items) for r in projection['required']]
    sources = [mapper.source(r, items) for r in variants[0]['Sources']]
    if not mapper.disjoint(required) or not mapper.disjoint(sources):
        raise ValueError('Unsupported overlapping ingredient domains')
    if any(len(r['possible_items']) != 1 for r in projection['required']):
        raise ValueError('Witness builder requires exact item IDs')
    rows = []
    for label, inventory in witnesses(recipe, projection):
        slots = place(inventory, items)
        server = server_accepts(projection['required'], inventory, items, mapper)
        native = client_accepts(variants[0]['Sources'], inventory, items, mapper)
        entry = all(any(client_source_matches(s, i) for s in variants[0]['Sources'])
                    for i in inventory)
        rows.append(dict(name=label, inventory=inventory, slots=slots,
            grid_fits=slots is not None, native_entry_predicate=entry,
            native_recipe_accepts=native, server_ingredient_accepts=server,
            classification='VALUE MISMATCH' if server != native else 'MATCH',
            evidence='STATIC_SOURCE_MODEL', runtime_verified=False))
    return dict(id=recipe['Number'], witnesses=rows, safe_to_import=False,
        disposition='MANUAL REVIEW REQUIRED',
        limit='Ingredient predicates only; UI state, money, character level and outcome not executed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--client-tables', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    mapper = load_mapper()
    audit = mapper.load_audit()
    client = json.loads(args.client_tables.read_text())
    digest = mapper.validate_inputs(args.baseline, client, audit)
    tables = audit.load_module().load_tables(args.baseline)
    items = mapper.item_index(tables, audit.ITEM_STRIDE)
    result = dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[],
        inputs=dict(baseline_sha256=digest, native_pin=audit.NATIVE_PIN),
        grid=dict(columns=GRID_COLUMNS, rows=GRID_ROWS),
        recipes=[audit_recipe(r, tables, client, items, mapper, audit)
            for r in sorted(tables['ItemCrafting'], key=lambda r: r['Number'])
            if r['Number'] in SCOPED_IDS], readiness=65.5,
        limits=['Static policy differences are not runtime failures',
                'Fragmented Fenrir stacks fail native entry; modified-client reachability not tested',
                'No full-recipe equivalence, import permission or score credit'])
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(recipes=len(result['recipes']), baseline_writes=0)))


if __name__ == '__main__':
    main()
