#!/usr/bin/env python3
"""Bulk semantic validation of actual OpenMU export; no mutations or imports."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

GRID_COLUMNS = 8
SHOP_ROWS = 15
EXCLUDED_MAPS = {34, *range(45, 51)}


def load_tables(path):
    tables = defaultdict(list)
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        record = json.loads(line)
        tables[record['table']].append(record['row'])
    return tables


def invalid_ranges(rows, minimum, maximum, zero_unbounded=False):
    return [row['Id'] for row in rows if (row[minimum] is not None and row[minimum] < 0) or
            (row[minimum] is not None and row[maximum] is not None and row[maximum] < row[minimum]
             and not (zero_unbounded and row[maximum] == 0))]


def rectangle_cells(slot, width, height):
    x, y = slot % GRID_COLUMNS, slot // GRID_COLUMNS
    if slot < 0 or width <= 0 or height <= 0 or x + width > GRID_COLUMNS or y + height > SHOP_ROWS:
        raise ValueError('Item rectangle outside shop grid')
    return {(xx, yy) for yy in range(y, y + height) for xx in range(x, x + width)}


def validate_shops(tables):
    definitions = {row['Id']: row for row in tables['ItemDefinition']}
    shops = {row['MerchantStoreId']: row for row in tables['MonsterDefinition'] if row['MerchantStoreId']}
    stock = defaultdict(list)
    for item in tables['Item']:
        stock[item['ItemStorageId']].append(item)
    findings = []
    for storage_id, npc in shops.items():
        occupied = {}
        for item in sorted(stock[storage_id], key=lambda row: (row['ItemSlot'], row['Id'])):
            definition = definitions[item['DefinitionId']]
            try:
                cells = rectangle_cells(item['ItemSlot'], definition['Width'], definition['Height'])
            except ValueError:
                findings.append({'npc': npc['Number'], 'item': item['Id'], 'issue': 'OUTSIDE_GRID'})
                continue
            overlaps = sorted({occupied[cell] for cell in cells if cell in occupied})
            if overlaps:
                findings.append({'npc': npc['Number'], 'item': item['Id'], 'slot': item['ItemSlot'],
                                 'issue': 'OVERLAPPING_RECTANGLE', 'other_items': overlaps})
            occupied.update({cell: item['Id'] for cell in cells})
    return {'stores': len(shops), 'stock_items': sum(len(stock[s]) for s in shops), 'findings': findings}


def validate(tables):
    maps = {row['Id']: row for row in tables['GameMapDefinition']}
    required_spawns = [row for row in tables['MonsterSpawnArea']
                       if maps.get(row['GameMapId'], {}).get('Number') not in EXCLUDED_MAPS]
    # Reversed spawn rectangles are warnings: runtime treats ranges as endpoint bounds.
    reversed_spawns = [row['Id'] for row in required_spawns if row['X1'] > row['X2'] or row['Y1'] > row['Y2']]
    checks = {
        'item_dimensions': [r['Id'] for r in tables['ItemDefinition'] if not (0 < r['Width'] <= GRID_COLUMNS and 0 < r['Height'] <= SHOP_ROWS)],
        'drop_probability': [r['Id'] for r in tables['DropItemGroup'] if not 0 <= r['Chance'] <= 1],
        'drop_level_ranges': invalid_ranges(tables['DropItemGroup'], 'MinimumMonsterLevel', 'MaximumMonsterLevel', True),
        'quest_level_ranges': invalid_ranges(tables['QuestDefinition'], 'MinimumCharacterLevel', 'MaximumCharacterLevel', True),
        'quest_item_amount': [r['Id'] for r in tables['QuestItemRequirement'] if r['MinimumNumber'] <= 0],
        'quest_kill_amount': [r['Id'] for r in tables['QuestMonsterKillRequirement'] if r['MinimumNumber'] <= 0],
        'craft_input_amount': invalid_ranges(tables['ItemCraftingRequiredItem'], 'MinimumAmount', 'MaximumAmount', True),
        'craft_input_levels': invalid_ranges(tables['ItemCraftingRequiredItem'], 'MinimumItemLevel', 'MaximumItemLevel'),
        'craft_output_levels': invalid_ranges(tables['ItemCraftingResultItem'], 'RandomMinimumLevel', 'RandomMaximumLevel'),
        'craft_probability': [r['Id'] for r in tables['SimpleCraftingSettings']
                              if not 0 <= r['SuccessPercent'] <= 100 or not 0 <= r['MaximumSuccessPercent'] <= 100],
        'master_skill_levels': invalid_ranges(tables['MasterSkillDefinition'], 'MinimumLevel', 'MaximumLevel'),
        'spawn_quantities': [r['Id'] for r in required_spawns if r['Quantity'] <= 0],
        'installed_update_state': [r['Id'] for r in tables['ConfigurationUpdate'] if not r['InstalledAt'] or r['Version'] <= 0],
    }
    return {'counts': {name: len(rows) for name, rows in tables.items()}, 'checks': checks,
            'shops': validate_shops(tables), 'warnings': {'reversed_required_spawn_rectangles': reversed_spawns},
            'scope': {'excluded_or_deferred_maps': sorted(EXCLUDED_MAPS), 'required_spawn_records': len(required_spawns)},
            'limits': ['No runtime proof, terrain walkability, balance, AI, texture/animation or binary skill/quest mapping.',
                       'Installed update state is checked; pinned source key/version completeness comparison remains pending.',
                       'Shared drop probabilities are independent selectors; they are not summed across unrelated groups.']}


def validate_updates(tables, manifest):
    source = {plugin['key'].lower(): plugin for plugin in manifest['plugins']}
    installed = {row['Key'].lower(): row for row in tables['ConfigurationUpdate']}
    return {'source_commit': manifest['commit'], 'source_files': manifest['source_files'],
            'season6_plugins': sum(plugin['s6'] for plugin in source.values()),
            'installed': len(installed), 'unknown_keys': sorted(set(installed) - set(source)),
            'outdated': [key for key, row in installed.items()
                         if key in source and row['Version'] < source[key]['version']],
            'missing_season6': [key for key, plugin in source.items() if plugin['s6'] and key not in installed]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--updates', type=Path)
    args = parser.parse_args()
    tables = load_tables(args.export)
    report = validate(tables)
    if args.updates:
        report['updates'] = validate_updates(tables, json.loads(args.updates.read_text()))
        report['limits'].remove('Installed update state is checked; pinned source key/version completeness comparison remains pending.')
    report['export_sha256'] = hashlib.sha256(args.export.read_bytes()).hexdigest()
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'rows': sum(report['counts'].values()), 'check_findings': {k: len(v) for k, v in report['checks'].items()},
                      'shops': report['shops'], 'warnings': {k: len(v) for k, v in report['warnings'].items()}}))
