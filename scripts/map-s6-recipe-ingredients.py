#!/usr/bin/env python3
"""Read-only ingredient predicate comparison; field matches are not recipe proof."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

BYTE_MAX = 255
PLAIN_MIX_OPTION = 65
MIX_BLOB = '0a24d6da76e72af82473951bf930e3f9ea9d0633'
# Exact CMixItem::SetItem switch at native 8d18a2b, not general stackability.
CLIENT_STACK_KEYS = {(14, n) for n in (3, 38, 39, 53, 88, 89, 90, 100)}
MAPPING = 'FORMAT MAPPING REQUIRED'


def load_audit():
    spec = importlib.util.spec_from_file_location('recipe_audit',
        Path(__file__).with_name('audit-s6-recipes.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def item_index(tables, stride):
    return {r['Group'] * stride + r['Number']: r for r in tables['ItemDefinition']}


def server_stackable(item):
    return item['ItemSlotId'] is None and item['Durability'] > 1


def states(ids, low, high, items):
    return sorted((key, level) for key in ids
        for level in range(max(0, low), min(high, items[key]['MaximumItemLevel']) + 1))


def requirement(row, items):
    ids = [r['client_id'] for r in row['possible_items']] or sorted(items)
    return dict(states=states(ids, row['MinimumItemLevel'], row['MaximumItemLevel'], items),
                count=[row['MinimumAmount'], row['MaximumAmount'] or None])


def source(row, items):
    ids = sorted(key for key in items if row['TypeMin'] <= key <= row['TypeMax'])
    result = dict(states=states(ids, row['LevelMin'], row['LevelMax'], items),
                  count=[row['CountMin'], row['CountMax']], packaging=[])
    scales = set()
    for key in ids:
        item = items[key]
        client_stack = (item['Group'], item['Number']) in CLIENT_STACK_KEYS
        if client_stack == server_stackable(item):
            scales.add(1)
        elif server_stackable(item) and row['DurabilityMin'] == row['DurabilityMax']:
            scales.add(row['DurabilityMin'])
            result['packaging'].append(dict(item_id=key, container_units=row['DurabilityMin']))
        else:
            raise ValueError('Unmapped client/server count units')
    if len(scales) != 1:
        raise ValueError('Empty source or mixed count units')
    scale = scales.pop()
    result['count'] = [value * scale for value in result['count']]
    if (row['DurabilityMin'], row['DurabilityMax']) != (0, BYTE_MAX):
        result['packaging'].append(dict(durability_bounds=[row['DurabilityMin'], row['DurabilityMax']]))
    return result


def unsupported(recipe, projection, variants):
    if recipe['ItemCraftingHandlerClassName'] or not projection['settings']:
        return 'Custom handler: settings alone do not establish eligibility'
    if len(variants) != 1:
        return 'Multiple variants: native ordered selection remains unmapped'
    if variants[0]['MixOption'] != PLAIN_MIX_OPTION:
        return 'Special native mix option'
    if any(r['required_options'] for r in projection['required']):
        return 'Required server options need semantic mapping'
    if any(r['SpecialItem'] or (r['OptionMin'], r['OptionMax']) != (0, BYTE_MAX)
           for r in variants[0]['Sources']):
        return 'Client special flags/options need semantic mapping'
    return None


def disjoint(rows):
    seen = set()
    for row in rows:
        current = set(map(tuple, row['states']))
        if not current or current & seen:
            return False
        seen.update(current)
    return True


def signature(rows, include_count):
    return collections.Counter((tuple(map(tuple, r['states'])), tuple(r['count']) if include_count else ())
                               for r in rows)


def compare(requirements, sources):
    if not disjoint(requirements) or not disjoint(sources):
        return dict(classification=MAPPING, reason='Empty/overlapping domains: allocator order not mapped')
    domains_match = signature(requirements, False) == signature(sources, False)
    counts_match = signature(requirements, True) == signature(sources, True)
    packaging = any(r['packaging'] for r in sources)
    classification = 'MATCH' if counts_match and not packaging else MAPPING
    if not domains_match or not counts_match:
        classification = 'VALUE MISMATCH'
    return dict(classification=classification,
        item_level_domains='MATCH' if domains_match else 'VALUE MISMATCH',
        normalized_counts='MATCH' if counts_match else 'VALUE MISMATCH',
        packaging=MAPPING if packaging else 'No additional client durability predicate',
        server=requirements, client=sources,
        limit='Configured legal item levels only; capacity, UI, consumption and outcomes not proved')


def map_recipe(tables, recipe, variants, items, audit):
    projection = audit.server_projection(tables, recipe)
    reason = unsupported(recipe, projection, variants)
    if reason:
        return dict(classification=MAPPING, reason=reason)
    try:
        requirements = [requirement(r, items) for r in projection['required']]
        sources = [source(r, items) for r in variants[0]['Sources']]
    except ValueError as error:
        return dict(classification=MAPPING, reason=str(error))
    return compare(requirements, sources)


def run(tables, client, audit):
    items = item_index(tables, audit.ITEM_STRIDE)
    rows = []
    for recipe in sorted(tables['ItemCrafting'], key=lambda r: r['Number']):
        if recipe['Number'] == audit.OUT_OF_SCOPE_MIX:
            continue
        variants = [v for v in client['tables']['crafting'] if v['MixID'] == recipe['Number']]
        rows.append(dict(id=recipe['Number'], name=recipe['Name'],
            ingredients=map_recipe(tables, recipe, variants, items, audit),
            outcomes='UNKNOWN', safe_to_import=False))
    return dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], recipes=rows,
        summary=dict(recipes=len(rows), classifications=dict(collections.Counter(
            r['ingredients']['classification'] for r in rows)),
            normalized_recipes=sum('server' in r['ingredients'] for r in rows)),
        limitations=['Field-scoped comparison, not full inventory matcher or whole-recipe equivalence',
            'Unbounded server amounts versus finite client amounts need inventory-capacity proof',
            'Current definition universe is not an independent S6 completeness oracle',
            'No client resource missing inferred from range holes; IT excluded, Crywolf deferred'])


def validate_inputs(baseline, client, audit):
    digest = hashlib.sha256(baseline.read_bytes()).hexdigest()
    if digest != audit.BASELINE_SHA:
        raise ValueError('Baseline differs from confirmed export')
    if client['native_pin'] != audit.NATIVE_PIN or client['inputs']['crafting']['git_blob'] != MIX_BLOB:
        raise ValueError('Unsupported native/mix pin')
    payload = json.dumps(client['tables']['crafting'], sort_keys=True, separators=(',', ':')).encode()
    if hashlib.sha256(payload).hexdigest() != audit.APPROVED_MIX_PROJECTION:
        raise ValueError('Unapproved crafting projection')
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--client-tables', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    audit = load_audit()
    client = json.loads(args.client_tables.read_text())
    digest = validate_inputs(args.baseline, client, audit)
    result = run(audit.load_module().load_tables(args.baseline), client, audit)
    result['inputs'] = dict(baseline_sha256=digest, native_pin=audit.NATIVE_PIN,
        mix_blob=MIX_BLOB, client_projection_sha256=hashlib.sha256(args.client_tables.read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
