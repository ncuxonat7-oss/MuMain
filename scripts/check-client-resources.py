#!/usr/bin/env python3
"""Read-only cross-check of exported OpenMU definitions and pinned MuMain metadata."""
import argparse
import json
from pathlib import Path


def world_number(number):
    if number in range(11, 18) or number == 52:
        return 12
    if number in range(18, 24) or number == 53:
        return 19
    if number in range(24, 30) or number == 36:
        return 25
    if number in range(45, 51):
        return 47
    if number == 32:
        return 10
    return number + 1


def load_groups(directory, field):
    result = {}
    for path in sorted(directory.glob('Group*.json')):
        group = json.loads(path.read_text())
        result.update({(group['group'], item['number']): item for item in group[field]})
    return result


def validate_item(item, entries, models, shared, paths):
    identity = (item['Group'], item['Number'])
    result = {'id': item['Id'], 'group': identity[0], 'number': identity[1],
              'name': item['Name'].split('||')[0], 'issues': []}
    entry = entries.get(identity)
    if entry is None:
        result['issues'].append('MISSING_CLIENT_ITEM_ENTRY')
    else:
        # ItemJsonFormat.cpp explicitly defaults omitted dimensions to zero.
        dimensions = (entry.get('width', 0), entry.get('height', 0))
        if dimensions != (item['Width'], item['Height']):
            result['issues'].append('CLIENT_DIMENSIONS_DIFFER')
            result['client_dimensions'] = list(dimensions)
            result['server_dimensions'] = [item['Width'], item['Height']]
    model = models.get(identity)
    if model is None:
        result['issues'].append('MODEL_MAPPING_UNKNOWN')
        return result
    if model.get('model'):
        definition = shared.get(model['model'])
        if definition is None:
            result['issues'].append('MISSING_SHARED_MODEL_DEFINITION')
            return result
        model = definition
    filename = model.get('file', '').removeprefix('Data/')
    result['model_file'] = filename
    if filename and filename.casefold() not in paths:
        result['issues'].append('MISSING_MODEL_FILE')
    return result


def run(evidence, metadata, manifest_path, output):
    records = [json.loads(line) for line in (evidence / 'baseline-config.jsonl').read_text().splitlines()]
    items = [record['row'] for record in records if record['table'] == 'ItemDefinition']
    maps = [record['row'] for record in records if record['table'] == 'GameMapDefinition']
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('truncated') or manifest['tree'] != '77f7830f542d106fc519c8821832d49a3dd8ae3a':
        raise ValueError('Require complete approved pinned Data tree manifest.')
    paths = {path.casefold() for path in manifest['paths']}
    entries = load_groups(metadata / 'Items', 'items')
    models = load_groups(metadata / 'Items/Models', 'models')
    shared_data = json.loads((metadata / 'Items/Models/SharedModels.json').read_text())
    shared = {model['name']: model for model in shared_data['models']}
    checked = [validate_item(item, entries, models, shared, paths) for item in items]
    missing_maps = []
    for game_map in maps:
        world = world_number(game_map['Number'])
        for extension in ('map', 'att', 'obj'):
            filename = f'World{world}/EncTerrain{world}.{extension}'
            if filename.casefold() not in paths:
                missing_maps.append({'map': game_map['Number'], 'name': game_map['Name'].split('||')[0], 'file': filename})
    result = {'data_tree': manifest['tree'], 'file_count': len(paths), 'server_items': len(items),
              'client_entries': len(entries), 'client_model_entries': len(models), 'server_maps': len(maps),
              'distinct_map_numbers': len({game_map['Number'] for game_map in maps}),
              'item_findings': [item for item in checked if item['issues']], 'map_findings': missing_maps,
              'scope': 'Metadata IDs, loader-default dimensions, resolved model paths and aliased terrain triplets only. No binary decoding, textures, animations or runtime proof.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ('item_findings', 'scope')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--metadata', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    run(args.evidence, args.metadata, args.manifest, args.out)
