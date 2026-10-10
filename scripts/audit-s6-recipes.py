#!/usr/bin/env python3
"""Dry-run semantic projection of the preserved S6 recipes; never imports data.

Reuse decoded pinned tables. MATCH is field-scoped, not whole-recipe proof.
Upgrade scenarios model the pinned native first-match order and server additions.
"""
import argparse
import collections
import importlib.util
import hashlib
import json
from pathlib import Path

NATIVE_PIN = '8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5'
BASELINE_SHA = '8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a'
APPROVED_MIX_PROJECTION = 'be4f559f9a1ccad2deb55f3c410167b0d29949e569f5a1eac71d6a3948fa64e0'
ITEM_STRIDE = 512
OUT_OF_SCOPE_MIX = 37
UPGRADE_IDS = {3: 10, 4: 11, 22: 12, 23: 13, 49: 14, 50: 15}
# MixMgr.h, NOT wire NPC talk values nor OpenMU NpcWindow enum values.
WINDOW_CATEGORIES = {5: {0, 1, 2}, 8: {4}, 11: {7}, 12: {5}, 13: {6},
                     16: {9}, 17: {10, 11}, 18: {12, 13}}
TOKEN_NAMES = {0: 'NUMBER', 1: '+', 2: '-', 3: '*', 4: '/', 5: '(', 6: ')',
               7: 'INT', 32: 'CAP', 33: 'ITEM_VALUE', 34: 'WING_VALUE',
               35: 'EXCELLENT_VALUE', 36: 'EQUIPMENT_VALUE', 37: 'SET_VALUE',
               38: 'FIRST_LEVEL', 39: 'NONJEWEL_VALUE', 64: 'LUCK_25'}
SPECIAL_ADDITIONS = {1: 'SuccessPercentageAdditionForExcellentItem',
                     2: 'SuccessPercentageAdditionForGuardianItem',
                     4: 'SuccessPercentageAdditionForAncientItem',
                     16: 'SuccessPercentageAdditionForSocketItem'}
SCENARIO_MASKS = (0, 1, 2, 4, 16, 3, 5, 17)
PAIR_MASKS = {3, 5, 17}


def load_module():
    path = Path(__file__).with_name('crosscheck-s6-client-ids.py')
    spec = importlib.util.spec_from_file_location('client_ids', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_item(item):
    return dict(group=item['Group'], number=item['Number'],
                client_id=item['Group'] * ITEM_STRIDE + item['Number'])


def server_projection(tables, recipe):
    items = {r['Id']: r for r in tables['ItemDefinition']}
    options = {r['Id']: r['Name'].split('||')[0] for r in tables['ItemOptionType']}
    settings = next((r for r in tables['SimpleCraftingSettings']
                     if r['Id'] == recipe['SimpleCraftingSettingsId']), None)
    required, outcomes = [], []
    if settings is None:
        return dict(settings=None, required=[], outcomes=[])
    for row in tables['ItemCraftingRequiredItem']:
        if row['SimpleCraftingSettingsId'] != settings['Id']:
            continue
        entry = {k: v for k, v in row.items() if k not in ('Id', 'SimpleCraftingSettingsId')}
        entry['possible_items'] = sorted((semantic_item(items[link['ItemDefinitionId']])
            for link in tables['ItemCraftingRequiredItemItemDefinition']
            if link['ItemCraftingRequiredItemId'] == row['Id']), key=lambda r: r['client_id'])
        entry['required_options'] = sorted(options[link['ItemOptionTypeId']]
            for link in tables['ItemCraftingRequiredItemItemOptionType']
            if link['ItemCraftingRequiredItemId'] == row['Id'])
        required.append(entry)
    for row in tables['ItemCraftingResultItem']:
        if row['SimpleCraftingSettingsId'] == settings['Id']:
            entry = {k: v for k, v in row.items()
                     if k not in ('Id', 'ItemDefinitionId', 'SimpleCraftingSettingsId')}
            entry['item'] = semantic_item(items[row['ItemDefinitionId']]) if row['ItemDefinitionId'] else None
            outcomes.append(entry)
    return dict(settings={k: v for k, v in settings.items() if k != 'Id'},
                required=required, outcomes=outcomes)


def source_projection(source, items):
    result = dict(source)
    result['known_current_item_ids'] = sorted(r['Group'] * ITEM_STRIDE + r['Number']
        for r in items if source['TypeMin'] <= r['Group'] * ITEM_STRIDE + r['Number'] <= source['TypeMax'])
    result['resource_support'] = 'UNKNOWN: definition presence is not model/icon proof'
    return result


def client_projection(row, items):
    result = {k: v for k, v in row.items() if k not in ('Sources', 'RateTokens')}
    result['Sources'] = [source_projection(s, items) for s in row['Sources']]
    result['rate_expression'] = [dict(op=TOKEN_NAMES[t['Op']], value=t['Value']) for t in row['RateTokens']]
    result['zen_rule'] = {65: 'FIXED', 66: 'FINAL_RATE_MULTIPLIER', 67: 'FIXED_DISPLAY',
                          68: 'HARMONY_TABLE_LOOKUP'}.get(row['RequiredZenType'], 'UNKNOWN')
    return result


def constant_rate(settings, requirements, variants, custom_handler):
    if not settings or custom_handler:
        return dict(classification='UNKNOWN', reason='Custom handler must be mapped, not overridden by settings')
    dynamic = ['NpcPriceDivisor', *SPECIAL_ADDITIONS.values(), 'SuccessPercentageAdditionForLuck']
    if any(settings[k] for k in dynamic) or any(r['AddPercentage'] or r['NpcPriceDivisor'] for r in requirements):
        return dict(classification='FORMAT MAPPING REQUIRED', reason='Inventory-dependent rate')
    if any(v['RateTokens'] != [{'Op': 32, 'Value': 0.0}] for v in variants):
        return dict(classification='FORMAT MAPPING REQUIRED', reason='Client expression is inventory-dependent')
    server_rate = min(100, settings['SuccessPercent'])
    if settings['MaximumSuccessPercent']:
        server_rate = min(server_rate, settings['MaximumSuccessPercent'])
    client_rates = [v['SuccessRate'] for v in variants]
    return dict(classification='MATCH' if all(r == server_rate for r in client_rates) else 'VALUE MISMATCH',
                server=server_rate, client=client_rates, limit='No charms, eligible standard ingredients only')


def price_rule(settings, variants, custom_handler):
    if not settings or custom_handler:
        return dict(classification='UNKNOWN', reason='Custom GetPrice can override settings')
    rules = [(v['RequiredZenType'], v['RequiredZen']) for v in variants]
    expected = (66, settings['MoneyPerFinalSuccessPercentage']) if settings['MoneyPerFinalSuccessPercentage'] else (65, settings['Money'])
    match = all((kind, value) == expected or (kind == 67 and expected == (65, value)) for kind, value in rules)
    if settings['Money'] and settings['MoneyPerFinalSuccessPercentage']:
        return dict(classification='FORMAT MAPPING REQUIRED', reason='Combined fixed plus percentage price')
    return dict(classification='MATCH' if match else 'VALUE MISMATCH', server=expected, client=rules,
                limit='Base cost formula, before castle tax or discounts; not outcome proof')


def upgrade_rate(settings, variants, mask, luck):
    # Pinned CheckItem checks positive flags; CheckRecipe stops at the first match.
    chosen = next(v for v in variants if v['Sources'][0]['SpecialItem'] & mask == v['Sources'][0]['SpecialItem'])
    tokens = chosen['RateTokens']
    if [t['Op'] for t in tokens] != [0, 1, 64]:
        raise ValueError('Unmapped upgrade rate formula')
    client = min(chosen['SuccessRate'], int(tokens[0]['Value']) + (25 if luck else 0))
    server = settings['SuccessPercent']
    for flag, field in SPECIAL_ADDITIONS.items():
        if mask & flag:
            server = (server + settings[field]) & 255  # explicit C# byte casts
    if luck:
        server = (server + settings['SuccessPercentageAdditionForLuck']) & 255
    if settings['MaximumSuccessPercent']:
        server = min(server, settings['MaximumSuccessPercent'])
    return dict(mask=mask, luck=luck, client_variant=chosen['MixIndex'], client_rate=client,
                server_rate=min(100, server), classification='MATCH' if client == min(100, server) else 'VALUE MISMATCH',
                reachability='UNPROVEN: combined special flags require exact item eligibility' if mask in PAIR_MASKS
                else 'Representative single-condition scenario; not a runtime test')


def upgrade_checks(recipe, projection, variants):
    if recipe['Number'] not in UPGRADE_IDS:
        return []
    return [upgrade_rate(projection['settings'], variants, mask, luck)
            for mask in SCENARIO_MASKS for luck in (False, True)]


def audit(tables, client):
    result = dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], recipes=[])
    monsters = {r['Id']: r for r in tables['MonsterDefinition']}
    for recipe in sorted(tables['ItemCrafting'], key=lambda r: r['Number']):
        if recipe['Number'] == OUT_OF_SCOPE_MIX:
            continue
        variants = [v for v in client['tables']['crafting'] if v['MixID'] == recipe['Number']]
        if not variants:
            raise ValueError('Previously verified MixID disappeared')
        monster = monsters[recipe['MonsterDefinitionId']]
        projection = server_projection(tables, recipe)
        categories = {v['category'] for v in variants}
        dispatch = categories <= WINDOW_CATEGORIES.get(monster['NpcWindow'], set())
        checks = dict(category_binding=dict(classification='MATCH' if dispatch else 'FORMAT MAPPING REQUIRED',
                      server_npc=monster['Number'], server_window=monster['NpcWindow'],
                      client_categories=sorted(categories), limit='Mapped enum/category; wire dialog/submenu path still requires verification'),
                      cost=price_rule(projection['settings'], variants, recipe['ItemCraftingHandlerClassName']),
                      rate=constant_rate(projection['settings'], projection['required'], variants, recipe['ItemCraftingHandlerClassName']),
                      ingredients=dict(classification='FORMAT MAPPING REQUIRED', reason='Projected ranges/options/counts; no full inventory matcher yet'),
                      outcomes=dict(classification='UNKNOWN', reason='mix.bmd has no result-item table; compare native handling/text plus server handlers'))
        result['recipes'].append(dict(id=recipe['Number'], name=recipe['Name'],
            handler=recipe['ItemCraftingHandlerClassName'] or 'SimpleItemCraftingHandler',
            server=projection, client=[client_projection(v, tables['ItemDefinition']) for v in variants],
            checks=checks, upgrade_scenarios=upgrade_checks(recipe, projection, variants), safe_to_import=False))
    result['summary'] = dict(recipes=len(result['recipes']), client_variants=sum(len(r['client']) for r in result['recipes']),
        dimensions={key: dict(collections.Counter(r['checks'][key]['classification'] for r in result['recipes']))
                    for key in ('category_binding', 'cost', 'rate', 'ingredients', 'outcomes')},
        upgrade_scenarios=dict(collections.Counter(s['classification'] for r in result['recipes'] for s in r['upgrade_scenarios'])))
    result['limitations'] = ['Pair-flag counterexamples are not confirmed reachable gameplay defects',
        'No whole-recipe MATCH or safe import; charms/tax/matcher/custom outcomes remain unmapped',
        'No item resource missing inferred from numeric range gaps', 'IT omitted; Crywolf not evaluated']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--client-tables', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    baseline_hash = hashlib.sha256(args.baseline.read_bytes()).hexdigest()
    if baseline_hash != BASELINE_SHA:
        raise ValueError('Baseline differs from confirmed export')
    client = json.loads(args.client_tables.read_text())
    if client['native_pin'] != NATIVE_PIN:
        raise ValueError('Unsupported native pin')
    if client['inputs']['crafting']['git_blob'] != '0a24d6da76e72af82473951bf930e3f9ea9d0633':
        raise ValueError('Unapproved mix projection')
    projection_hash = hashlib.sha256(json.dumps(client['tables']['crafting'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if projection_hash != APPROVED_MIX_PROJECTION:
        raise ValueError('Mix semantic projection differs from approved decoded data')
    result = audit(load_module().load_tables(args.baseline), client)
    result['inputs'] = dict(baseline_sha256=baseline_hash, native_pin=NATIVE_PIN,
                           client_projection_sha256=hashlib.sha256(args.client_tables.read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
