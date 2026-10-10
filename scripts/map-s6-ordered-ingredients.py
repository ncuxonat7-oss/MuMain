#!/usr/bin/env python3
"""Dry-run ordered ingredient projection; no inventory, runtime or outcome proof."""
import argparse
import collections
import importlib.util
import json
from pathlib import Path

ORDERED_IDS = {3, 4, 22, 23, 38, 49, 50}
KNOWN_FLAGS = 1 | 2 | 4 | 8 | 16
UNKNOWN = 'UNKNOWN'


def load_mapper():
    spec = importlib.util.spec_from_file_location('ingredients',
        Path(__file__).with_name('map-s6-recipe-ingredients.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compact_states(states):
    """Coalesce only adjacent current IDs with exactly the same legal levels."""
    levels = collections.defaultdict(list)
    for key, level in sorted(set(states)):
        levels[key].append(level)
    result = []
    for key, values in sorted(levels.items()):
        low, high = min(values), max(values)
        if values != list(range(low, high + 1)):
            raise ValueError('Non-contiguous legal levels')
        if result and result[-1][1] + 1 == key and result[-1][2:] == [low, high]:
            result[-1][1] = key
        else:
            result.append([key, key, low, high])
    return result


def client_predicate(row, items, mapper):
    if row['SpecialItem'] & ~KNOWN_FLAGS:
        raise ValueError('Unknown native special flag')
    ids = [key for key in items if row['TypeMin'] <= key <= row['TypeMax']]
    states = mapper.states(ids, row['LevelMin'], row['LevelMax'], items)
    # Preserve counts as native units; do not silently convert broad wildcard stacks.
    return dict(states=states, count=[row['CountMin'], row['CountMax']],
        option_bounds=[row['OptionMin'], row['OptionMax']],
        durability_bounds=[row['DurabilityMin'], row['DurabilityMax']],
        required_positive_mask=row['SpecialItem'],
        native_stack_item_ids=sorted(key for key, _ in set(states)
            if (items[key]['Group'], items[key]['Number']) in mapper.CLIENT_STACK_KEYS))


def public_predicate(row):
    return {**{k: v for k, v in row.items() if k != 'states'},
            'current_definition_ranges': compact_states(row['states'])}


def check_item(row, item):
    """Native CheckItem only; caller supplies already-derived native attributes."""
    if row['SpecialItem'] & ~KNOWN_FLAGS:
        raise ValueError('Unknown native special flag')
    return (row['TypeMin'] <= item['id'] <= row['TypeMax']
        and row['LevelMin'] <= item['level'] <= row['LevelMax']
        and row['OptionMin'] <= item['option'] <= row['OptionMax']
        and row['DurabilityMin'] <= item['durability'] <= row['DurabilityMax']
        and item['mask'] & row['SpecialItem'] == row['SpecialItem'])


def first_source_variant(variants, item):
    """Single target selector for disjoint upgrade recipes, NOT CheckRecipeSub."""
    return next((v['MixIndex'] for v in variants if check_item(v['Sources'][0], item)), None)


def ordered_regions(variants):
    # Order is decoded file order, not numeric sorting or exclusive flag equality.
    previous = []
    result = []
    for row in variants:
        source = row['Sources'][0]
        result.append(dict(mix_index=row['MixIndex'],
            positive_mask=source['SpecialItem'],
            excluded_prior_variants=list(previous)))
        previous.append(row['MixIndex'])
    return result


def domain_delta(required, sources):
    server = set(state for row in required for state in row['states'])
    client = set(state for variant in sources for row in variant for state in row['states'])
    return dict(classification='MATCH' if server == client else 'VALUE MISMATCH',
        server_only=compact_states(server - client), client_only=compact_states(client - server),
        limit='Item/level union only; positive flags/options and allocation not erased from report')


def amount_comparison(required, variants, mapper):
    # Restrict alignment to disjoint rows and identical item/level domains.
    if not mapper.disjoint(required) or any(not mapper.disjoint(rows) for rows in variants):
        return dict(classification=UNKNOWN, reason='Overlapping allocator domains')
    results = []
    for rows in variants:
        if mapper.signature(required, False) != mapper.signature(rows, False):
            results.append('UNKNOWN: item/level roles differ')
        elif any(row['native_stack_item_ids'] for row in rows):
            results.append('UNKNOWN: stack units')
        else:
            results.append('MATCH' if mapper.signature(required, True) == mapper.signature(rows, True)
                           else 'VALUE MISMATCH')
    return dict(classification='MATCH' if set(results) == {'MATCH'} else UNKNOWN,
                per_variant=results)


def upgrade_amounts(required, sources, mapper):
    target = [r for r in required if r['reference'] == 1]
    other = [r for r in required if r['reference'] != 1]
    if len(target) != 1 or not mapper.disjoint(required):
        return dict(classification=UNKNOWN, reason='Upgrade roles/overlap unproved')
    targets = [rows[0]['count'] == target[0]['count'] for rows in sources]
    rest = amount_comparison(other, [rows[1:] for rows in sources], mapper)
    return dict(target_amounts='MATCH' if all(targets) else 'VALUE MISMATCH',
                other_ingredients=rest,
                limit='Target amount comparison independent of its item eligibility; no whole match')


def map_ordered(recipe, projection, variants, items, mapper):
    if recipe['ItemCraftingHandlerClassName'] or not projection['settings']:
        return dict(classification=UNKNOWN, reason='Custom handler owns ingredient eligibility')
    if recipe['Number'] not in ORDERED_IDS or len(variants) < 2:
        return dict(classification=UNKNOWN, reason='Outside seven ordered simple recipes')
    try:
        required = [{**mapper.requirement(row, items),
            'required_positive_option_types': row['required_options'], 'reference': row['Reference']}
            for row in projection['required']]
        sources = [[client_predicate(row, items, mapper) for row in v['Sources']] for v in variants]
    except ValueError as error:
        return dict(classification=UNKNOWN, reason=str(error))
    upgrade = recipe['Number'] in mapper.load_audit().UPGRADE_IDS
    return dict(classification='PARTIAL STATIC MAPPING',
        server_order='Descending MinimumAmount; tie order not established',
        server=[public_predicate(row) for row in required],
        client=[dict(category=v['category'], mix_index=v['MixIndex'], mix_option=v['MixOption'],
            sources=[public_predicate(row) for row in rows]) for v, rows in zip(variants, sources)],
        item_level_union=domain_delta(required, sources),
        amounts=upgrade_amounts(required, sources, mapper) if upgrade
                else amount_comparison(required, sources, mapper),
        selection=ordered_regions(variants) if upgrade else dict(classification=UNKNOWN,
            reason='Positive options plus overlapping server domains need full ordered allocation'),
        native_entry='UNKNOWN: MixOption E equipment/wing gate' if upgrade
                     else 'MixOption A; option value and flag construction still unproved',
        native_flag_eligibility=UNKNOWN, native_option_to_server_option_equivalence=UNKNOWN,
        full_inventory_acceptance=UNKNOWN, outcomes=UNKNOWN, safe_to_import=False)


def run(tables, client, mapper):
    audit = mapper.load_audit()
    items = mapper.item_index(tables, audit.ITEM_STRIDE)
    rows = []
    for recipe in sorted(tables['ItemCrafting'], key=lambda row: row['Number']):
        if recipe['Number'] == audit.OUT_OF_SCOPE_MIX:
            continue
        variants = [v for v in client['tables']['crafting'] if v['MixID'] == recipe['Number']]
        if recipe['Number'] not in ORDERED_IDS:
            reason = 'Custom handler owns eligibility' if recipe['ItemCraftingHandlerClassName'] else 'Prior plain/option audit retained'
            rows.append(dict(id=recipe['Number'], classification=UNKNOWN, reason=reason))
            continue
        projection = audit.server_projection(tables, recipe)
        rows.append(dict(id=recipe['Number'], name=recipe['Name'],
                         **map_ordered(recipe, projection, variants, items, mapper)))
    mapped = [row for row in rows if row['classification'] == 'PARTIAL STATIC MAPPING']
    return dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], recipes=rows,
        summary=dict(scoped_recipes=len(rows), ordered_recipes=len(mapped),
            ordered_variants=sum(len(row['client']) for row in mapped),
            item_level_union=dict(collections.Counter(row['item_level_union']['classification'] for row in mapped)),
            whole_recipe_matches=0),
        limitations=['Current configured legal levels, not acquisition/runtime reachability',
            'Positive native masks and required server option types are retained, not declared equivalent',
            'Native first-match order retained; allocator overlap fails closed',
            'No new rate scenarios, charms, full inventory matcher, imports or baseline changes'])


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
    result = run(audit.load_module().load_tables(args.baseline), client, mapper)
    result['inputs'] = dict(baseline_sha256=digest, native_pin=audit.NATIVE_PIN,
        mix_blob=mapper.MIX_BLOB, approved_mix_projection_sha256=audit.APPROVED_MIX_PROJECTION,
        sources='patches/s6-recipe-source-provenance.json')
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
