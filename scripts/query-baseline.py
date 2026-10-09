#!/usr/bin/env python3
"""Locate objects in a preserved configuration export; no database or game writes."""
import argparse
from collections import defaultdict
import json
from pathlib import Path


def read_tables(path):
    tables = defaultdict(list)
    for line in path.read_text().splitlines():
        record = json.loads(line)
        tables[record['table']].append(record['row'])
    return tables


def compact(row):
    return {key: value for key, value in row.items()
            if key != 'TerrainData' and not isinstance(value, (dict, list))
            and (not isinstance(value, str) or len(value) < 500)}


def lookup(tables, args):
    if args.map_number is not None:
        maps = [row for row in tables['GameMapDefinition'] if row['Number'] == args.map_number]
        map_ids = {row['Id'] for row in maps}
        spawns = [row for row in tables['MonsterSpawnArea'] if row['GameMapId'] in map_ids]
        if args.x is not None and args.y is not None:
            spawns = [row for row in spawns if min(row['X1'], row['X2']) <= args.x <= max(row['X1'], row['X2'])
                      and min(row['Y1'], row['Y2']) <= args.y <= max(row['Y1'], row['Y2'])]
        monster_ids = {row['MonsterDefinitionId'] for row in spawns}
        monsters = [row for row in tables['MonsterDefinition'] if row['Id'] in monster_ids]
        return {'maps': maps, 'spawns': spawns, 'monsters_or_npcs': monsters}
    if args.item:
        group, number = map(int, args.item.split(':'))
        items = [row for row in tables['ItemDefinition'] if (row['Group'], row['Number']) == (group, number)]
        ids = {row['Id'] for row in items}
        references = {name: [row for row in rows if any(value in ids for value in row.values() if isinstance(value, str))]
                      for name, rows in tables.items() if name != 'ItemDefinition'}
        return {'items': items, **{name: rows for name, rows in references.items() if rows}}
    names = {'skill': 'Skill', 'npc': 'MonsterDefinition'}
    for option, table in names.items():
        number = getattr(args, option)
        if number is not None:
            return {table: [row for row in tables[table] if row.get('Number') == number]}
    return {'matches': [dict(table=table, **compact(row)) for table, rows in tables.items() for row in rows
                        if args.search.casefold() in ' '.join(str(row.get(field, '')) for field in ('Name', 'Designation', 'Description')).casefold()]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', required=True, type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--map-number', type=int)
    selection.add_argument('--item', help='group:number')
    selection.add_argument('--skill', type=int)
    selection.add_argument('--npc', type=int)
    selection.add_argument('--search')
    parser.add_argument('--x', type=int)
    parser.add_argument('--y', type=int)
    args = parser.parse_args()
    result = lookup(read_tables(args.export), args)
    print(json.dumps({table: [compact(row) for row in rows] for table, rows in result.items()}, indent=2, ensure_ascii=False))
