#!/usr/bin/env python3
"""Generate a read-only semantic diff; never connect to or write a database.

Extract a partial literal reference with --source-root, or compare a previously
generated --reference JSON. Every incomplete adapter is explicit in the report.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

from s6_source import EXCLUDED_MAPS, PIN, extract

DATA_TREE = '77f7830f542d106fc519c8821832d49a3dd8ae3a'
TABLES = {'maps': 'GameMapDefinition', 'enter_gates': 'EnterGate', 'exit_gates': 'ExitGate',
          'warps': 'WarpInfo', 'monsters': 'MonsterDefinition', 'spawns': 'MonsterSpawnArea',
          'items': 'ItemDefinition', 'sets': 'ItemSetGroup', 'skills': 'Skill',
          'quests': 'QuestDefinition', 'crafting': 'ItemCrafting', 'drops': 'DropItemGroup',
          'events': 'MiniGameDefinition', 'shops': 'MonsterDefinition', 'npcs': 'MonsterDefinition'}
STATUSES = ['MATCH', 'CURRENT EXTRA', 'REFERENCE EXTRA', 'VALUE MISMATCH',
            'CLIENT RESOURCE MISSING', 'SERVER IMPLEMENTATION MISSING',
            'FORMAT MAPPING REQUIRED', 'UNKNOWN']
SPAWN_FIELDS = ('Map', 'Monster', 'X1', 'X2', 'Y1', 'Y2', 'Quantity', 'Direction', 'SpawnTrigger', 'WaveNumber')
EXIT_FIELDS = ('Map', 'X1', 'Y1', 'X2', 'Y2', 'Direction')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tables(path):
    tables = collections.defaultdict(list)
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        tables[row['table']].append(row['row'])
    return tables


def join_key(row, fields):
    return ':'.join(str(row.get(field)) for field in fields)


def delay_ms(value):
    if not isinstance(value, str):
        return None
    hours, minutes, seconds = value.split(':')
    return (float(hours) * 3600 + float(minutes) * 60 + float(seconds)) * 1000


def current_records(tables, stats):
    maps = {r['Id']: f"{r['Number']}:{r['Discriminator']}" for r in tables['GameMapDefinition']}
    monsters = {r['Id']: r['Number'] for r in tables['MonsterDefinition']}
    classes = {r['Id']: r['Number'] for r in tables['CharacterClass']}
    skills = {r['Id']: r['Number'] for r in tables['Skill']}
    master = {r['Id']: r for r in tables['MasterSkillDefinition']}
    exits = {r['Id']: join_key(dict(r, Map=maps.get(r['MapId'])), EXIT_FIELDS) for r in tables['ExitGate']}
    attributes = collections.defaultdict(dict)
    for row in tables['MonsterAttribute']:
        attributes[row['MonsterDefinitionId']][row['AttributeDefinitionId']] = row['Value']
    requirements = collections.defaultdict(dict)
    for row in tables['AttributeRequirement']:
        if row.get('SkillId1'):
            requirements[row['SkillId1']][row['AttributeId']] = row['MinimumValue']
    result = collections.defaultdict(list)
    for category, table in TABLES.items():
        for original in tables[table]:
            row = dict(original)
            key = normalize_record(category, row, maps, monsters, classes, exits)
            if key is None:
                continue
            if category in ('monsters', 'npcs'):
                row.update({'Stats.' + name: attributes[row['Id']][uuid] for name, uuid in stats.items() if uuid in attributes[row['Id']]})
                for field in ('MoveDelay', 'AttackDelay', 'RespawnDelay'):
                    row[field + 'Ms'] = delay_ms(row.get(field))
            if category in ('monsters', 'npcs', 'shops'):
                row['HasMerchantStore'] = row.get('MerchantStoreId') is not None
            if category == 'events':
                for field in ('EnterDuration', 'GameDuration', 'ExitDuration'):
                    row[field + 'Ms'] = delay_ms(row.get(field))
            if category == 'skills':
                row.update({'Requirements.' + name: requirements[row['Id']].get(uuid, 0) for name, uuid in stats.items()})
                definition = master.get(row.get('MasterDefinitionId'), {})
                row['MasterReplacedSkill'] = skills.get(definition.get('ReplacedSkillId'))
            if scoped(category, row, key):
                result[category].append(dict(key=key, fields=row))
    return result


def normalize_record(category, row, maps, monsters, classes, exits):
    if category == 'maps':
        return f"{row['Number']}:{row['Discriminator']}"
    if category == 'exit_gates':
        row['Map'] = maps.get(row['MapId'])
        return join_key(row, EXIT_FIELDS)
    if category == 'enter_gates':
        row.update(Map=maps.get(row['GameMapDefinitionId']), Target=exits.get(row['TargetGateId']))
    if category == 'warps':
        row['Gate'] = exits.get(row['GateId'])
        return str(row['Index'])
    if category == 'items':
        return f"{row['Group']}:{row['Number']}"
    if category == 'spawns':
        row.update(Map=maps.get(row['GameMapId']), Monster=monsters.get(row['MonsterDefinitionId']))
        return join_key(row, SPAWN_FIELDS)
    if category == 'quests':
        return f"{row['Group']}:{row['Number']}:{monsters.get(row['QuestGiverId'])}:{classes.get(row['QualifiedCharacterId'])}"
    if category == 'sets':
        return row['Id']
    if category == 'drops':
        return row['Id']
    if category == 'npcs' and row['ObjectKind'] not in (1, 7):
        return None
    if category == 'shops' and not row.get('MerchantStoreId'):
        return None
    if category == 'events':
        return f"{row['Type']}:{row['GameLevel']}"
    if category == 'crafting':
        row['Handler'] = (row.get('ItemCraftingHandlerClassName') or '').rsplit('.', 1)[-1]
    return str(row.get('Number', row['Id']))


def scoped(category, row, key):
    map_key = key if category == 'maps' else row.get('Map')
    if map_key and int(map_key.split(':')[0]) in EXCLUDED_MAPS:
        return False
    if category == 'crafting' and 'illusion' in row.get('Name', '').lower():
        return False
    return True


def make_reference(root):
    records, stats, sources = extract(root)
    records = [r for r in records if scoped(r['category'], r['fields'], r['key'])]
    hashes = {path: hashlib.sha256((Path(root) / path).read_bytes()).hexdigest() for path in sorted(sources)}
    return dict(source='MUnique/OpenMU', pin=PIN, completeness='PARTIAL_LITERAL_PROJECTION',
                records=records, stats=stats, source_sha256=hashes,
                excluded_maps=sorted(EXCLUDED_MAPS), authoritative_for='Mapped pinned S6 declarations; not official Webzen completeness')


def world_number(number):
    if 11 <= number <= 17 or number == 52:
        return 12
    if 18 <= number <= 23 or number == 53:
        return 19
    if 24 <= number <= 29 or number == 36:
        return 25
    return 10 if number == 32 else number + 1


def client_check(category, key, row, manifest, prior_client):
    paths = {p.casefold() for p in manifest['paths']}
    if category == 'items':
        group, number = map(int, key.split(':'))
        old = next((x for x in prior_client['item_findings'] if (x['group'], x['number']) == (group, number)), None)
        if row is None:
            return dict(status='UNKNOWN', reason='Reference-only item requires metadata/model/handling admission')
        return dict(status='UNKNOWN' if old else 'METADATA_AND_MODEL_PATH_PRESENT', issues=old['issues'] if old else [], evidence='Reused client-final.json; no repeated dimension checks; rendering/handling not proved')
    if category in ('maps', 'spawns', 'enter_gates', 'exit_gates', 'warps'):
        map_key = key if category == 'maps' else (row or {}).get('Map')
        if not map_key:
            return dict(status='UNKNOWN', reason='Destination/variant must be mapped')
        world = world_number(int(map_key.split(':')[0]))
        required = [f'world{world}/encterrain{world}.{ext}' for ext in ('map', 'att')]
        missing = [p for p in required if p not in paths]
        return dict(status='CLIENT RESOURCE MISSING' if missing else 'TERRAIN_FILES_PRESENT', files=required, missing=missing,
                    limitation='Objects, spawn walkability and rendering not proved')
    if category in ('skills', 'quests', 'crafting'):
        required = {'skills': 'local/eng/skill_eng.bmd', 'quests': 'local/eng/quest_eng.bmd', 'crafting': 'local/mix.bmd'}[category]
        return dict(status='FORMAT MAPPING REQUIRED' if required in paths else 'CLIENT RESOURCE MISSING', file=required,
                    reason='Pinned BMD exists; per-ID binary decoding/checksum/handler compatibility not yet proved')
    return dict(status='UNKNOWN', reason='Explicit model/AI/UI mapping required; resource filenames do not equal server IDs')


def compare_category(category, references, current, manifest, prior_client):
    by_key = collections.defaultdict(list)
    for row in current:
        by_key[row['key']].append(row)
    consumed, findings = collections.Counter(), []
    for ref in references:
        key, candidates = ref['key'], by_key[ref['key']]
        index = consumed[key]
        row = candidates[index]['fields'] if index < len(candidates) else None
        consumed[key] += 1
        mismatches = {field: dict(reference=value, current=row.get(field)) for field, value in ref['fields'].items() if row is not None and row.get(field) != value}
        status = 'REFERENCE EXTRA' if row is None else 'VALUE MISMATCH' if mismatches else 'MATCH'
        finding = dict(category=category, key=key, classification=status, fields=mismatches,
                       source=ref['source'], line=ref['line'],
                       line_basis=ref.get('line_basis', 'EXTRACTED_CONTEXT'), compared_fields=len(ref['fields']))
        if status != 'MATCH':
            client_row = row if category == 'items' else row or ref['fields']
            finding['client'] = client_check(category, key, client_row, manifest, prior_client)
            finding['automation'] = 'AUTO WITH MAPPING' if status == 'VALUE MISMATCH' else 'MANUAL REVIEW REQUIRED'
            finding['safe_to_import'] = False
        findings.append(finding)
    for key, candidates in by_key.items():
        for row in candidates[consumed[key]:]:
            # A partial reference cannot establish CURRENT EXTRA.
            findings.append(dict(category=category, key=key, classification='UNKNOWN',
                                 reason='Current record has no literal reference projection; may be inherited/generated/update-added'))
    return findings


def build_report(reference, tables, manifest, prior_client):
    current = current_records(tables, reference['stats'])
    refs = collections.defaultdict(list)
    for record in reference['records']:
        refs[record['category']].append(record)
    findings, summary = [], {}
    for category in TABLES:
        compared = compare_category(category, refs[category], current[category], manifest, prior_client)
        if not refs[category]:
            for row in compared:
                row['classification'] = 'FORMAT MAPPING REQUIRED'
        findings.extend(compared)
        counts = dict(collections.Counter(row['classification'] for row in compared))
        summary[category] = dict(current=len(current[category]), reference=len(refs[category]), counts=counts)
    measured = sum(x['reference'] for x in summary.values())
    matched = sum(x['counts'].get('MATCH', 0) for x in summary.values())
    present = measured - sum(x['counts'].get('REFERENCE EXTRA', 0) for x in summary.values())
    denominator = sum(x['current'] for x in summary.values())
    return dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], summary=summary, findings=findings,
                metrics=dict(reference_records=measured, reference_keys_present=present,
                             reference_presence_percent=round(100 * present / measured, 2) if measured else None,
                             projected_fields_match_percent=round(100 * matched / measured, 2) if measured else None,
                             selected_current_records=denominator,
                             current_records_with_reference_projection_percent=round(100 * min(present, denominator) / denominator, 2) if denominator else None),
                limitations=['Presence is not complete standard S6 readiness', 'MATCH applies only to compared fields',
                             'Partial source projection; no C# execution, no update replay', 'No automatic import admission without complete semantics and both sides'],
                previous_readiness=65.5, current_readiness=65.5, readiness_gain=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source-root', type=Path)
    group.add_argument('--reference', type=Path)
    parser.add_argument('--client-manifest', required=True, type=Path)
    parser.add_argument('--client-evidence', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    reference = make_reference(args.source_root) if args.source_root else json.loads(args.reference.read_text())
    if reference['pin'] != PIN:
        raise ValueError('Unsupported OpenMU pin; review mappings before changing it')
    manifest = json.loads(args.client_manifest.read_text())
    client = json.loads(args.client_evidence.read_text())
    if manifest.get('truncated') or manifest['tree'] != DATA_TREE or client['data_tree'] != DATA_TREE:
        raise ValueError('Require exact complete approved Data manifest and prior client evidence')
    report = build_report(reference, read_tables(args.baseline), manifest, client)
    report['inputs'] = {key: dict(path=str(path), sha256=digest(path)) for key, path in [('baseline', args.baseline), ('client_manifest', args.client_manifest), ('client_evidence', args.client_evidence)]}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'reference.json').write_text(json.dumps(reference, indent=2) + '\n')
    (args.out / 'diff.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(summary=report['summary'], metrics=report['metrics'], baseline_writes=0), indent=2))


if __name__ == '__main__':
    main()
