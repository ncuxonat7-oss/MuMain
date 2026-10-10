#!/usr/bin/env python3
"""Join preserved server IDs with decoded pinned client tables, read-only.

Quest key = (Group << 16) | StepNumber per native ReceiveQuestQSSelSentence.
Crafting uses protocol MixID, never UI MixIndex. Presence does not admit import.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

CLIENT_BASE_CLASS_COUNT = 7
OPENMU_CLASS_STRIDE = 4
LEGACY_ITEM_ACTION = 1
UNIVERSAL_REQUEST_TYPE = 255


def load_tables(path):
    result = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        result.setdefault(row['table'], []).append(row['row'])
    return result


def quest_key(group, number):
    return ((group & 0xFFFF) << 16) | (number & 0xFFFF)


def legacy_requirements(tables, quest):
    items = {row['Id']: row for row in tables.get('ItemDefinition', [])}
    monsters = {row['Id']: row for row in tables.get('MonsterDefinition', [])}
    result = []
    for row in tables.get('QuestItemRequirement', []):
        if row['QuestDefinitionId'] == quest['Id']:
            item = items[row['ItemId']]
            result.append(('item', item['Group'], item['Number'], row['MinimumNumber']))
    for row in tables.get('QuestMonsterKillRequirement', []):
        if row['QuestDefinitionId'] == quest['Id']:
            result.append(('monster', monsters[row['MonsterId']]['Number'], row['MinimumNumber']))
    return sorted(result)


def legacy_class_check(client, class_index, expected):
    acts = [act for act in client['Acts'] if act['Classes'][class_index] >= 1]
    requirements = [('item', a['ItemType'], a['ItemSubType'], a['ItemCount']) if a['Type'] == LEGACY_ITEM_ACTION
                    else ('monster', a['ItemType'], a['ItemCount']) for a in acts]
    request_types = {a['RequestType'] for a in acts}
    money = {r['Zen'] for r in client['Requests'] if r['Zen'] and (r['Type'] == UNIVERSAL_REQUEST_TYPE or r['Type'] in request_types)}
    return dict(class_index=class_index, requirements=sorted(requirements),
                requirements_match=collections.Counter(requirements) == collections.Counter(expected), money=sorted(money))


def crosscheck_legacy(tables, quest, clients):
    client = clients.get(quest['Number'])
    if client is None:
        return dict(group=0, number=quest['Number'], classification='CLIENT RESOURCE MISSING', safe_to_import=False)
    # Pinned OpenMU class enum: low two bits are generation, base index is Number // 4.
    classes = {row['Id']: row['Number'] for row in tables.get('CharacterClass', [])}
    qualified = classes.get(quest['QualifiedCharacterId'])
    if quest['QualifiedCharacterId'] is not None and qualified is None:
        return dict(group=0, number=quest['Number'], classification='UNKNOWN', safe_to_import=False,
                    reason='Qualified server class was not mapped')
    indexes = [qualified // OPENMU_CLASS_STRIDE] if qualified is not None else list(range(CLIENT_BASE_CLASS_COUNT))
    expected = legacy_requirements(tables, quest)
    checks = [legacy_class_check(client, index, expected) for index in indexes]
    monsters = {r['Id']: r['Number'] for r in tables.get('MonsterDefinition', [])}
    npc_matches = client['Npc'] == monsters.get(quest['QuestGiverId'])
    money_matches = all(not r['money'] or r['money'] == [quest['RequiredStartMoney']] for r in checks)
    matched = npc_matches and money_matches and all(r['requirements_match'] for r in checks)
    return dict(group=0, number=quest['Number'], qualified_class=qualified,
                classification='MATCH' if matched else 'VALUE MISMATCH', npc_match=npc_matches,
                money_match=money_matches, server_requirements=expected, class_checks=checks, safe_to_import=False,
                limit='Only NPC, item/monster IDs/counts and unambiguous positive Zen. Class generation eligibility, inherited levels, prerequisites, item levels/rewards/dialogs remain UNKNOWN')


def recipe_mapping_scope(tables, client):
    variants = collections.defaultdict(list)
    for row in client['tables']['crafting']:
        variants[row['MixID']].append(row)
    result = []
    for row in tables['ItemCrafting']:
        if row['Number'] == 37:
            continue
        matches = variants[row['Number']]
        result.append(dict(id=row['Number'], client_variants=len(matches),
                           categories=sorted({m['category'] for m in matches}),
                           simple_settings=row['SimpleCraftingSettingsId'] is not None,
                           custom_handler=row['ItemCraftingHandlerClassName'],
                           classification='FORMAT MAPPING REQUIRED', safe_to_import=False,
                           limit='IDs present; variants, condition masks, formulas, dispatch, ingredients and outcomes need semantic equivalence'))
    return result


def crosscheck(tables, client):
    skills = {row['id']: row for row in client['tables']['skills']}
    mixes = {row['MixID'] for row in client['tables']['crafting']}
    quests = {row['raw_key'] for row in client['tables']['quest_progress']}
    legacy = {row['id']: row for row in client['tables'].get('legacy_quests', [])}
    result = dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], skills=[], crafting=[], quests=[])
    for row in tables['Skill']:
        match = skills.get(row['Number'])
        name = match.get('Name') if match else None
        result['skills'].append(dict(id=row['Number'], client_name=name,
                                     classification='MATCH' if name else 'UNKNOWN', safe_to_import=False,
                                     limit='Metadata name present, not full display/effect/handler proof' if name else
                                     'Blank metadata name is not missing implementation; Nova start and monster-internal skills require handling mapping'))
    for row in tables['ItemCrafting']:
        if row['Number'] == 37:
            continue  # Owner excludes Illusion Temple.
        result['crafting'].append(dict(id=row['Number'], classification='MATCH' if row['Number'] in mixes else 'CLIENT RESOURCE MISSING',
                                       safe_to_import=False, limit='MixID only; category, source ranges, rates and outcomes still need mapping'))
    for row in tables['QuestDefinition']:
        if row['Group'] == 0:
            if not legacy:
                result['quests'].append(dict(group=0, number=row['Number'], classification='FORMAT MAPPING REQUIRED',
                                            reason='Legacy Quest_eng.bmd is a different format, not QuestProgress'))
            else:
                result['quests'].append(crosscheck_legacy(tables, row, legacy))
            continue
        steps = {field: dict(number=row[field], raw_key=quest_key(row['Group'], row[field]),
                             present=quest_key(row['Group'], row[field]) in quests)
                 for field in ('Number', 'StartingNumber', 'RefuseNumber')}
        result['quests'].append(dict(group=row['Group'], number=row['Number'], steps=steps,
                                     classification='MATCH' if all(s['present'] for s in steps.values()) else 'CLIENT RESOURCE MISSING',
                                     safe_to_import=False, limit='Step keys present; words, requirements/rewards and runtime chain not proved'))
    current_mix = {row['Number'] for row in tables['ItemCrafting']}
    result['client_only_mix_ids'] = sorted(mixes - current_mix)
    result['client_only_policy'] = 'MANUAL REVIEW REQUIRED; no missing server content inferred from client-only IDs'
    result['recipe_mapping_scope'] = recipe_mapping_scope(tables, client)
    result['summary'] = {category: {status: sum(r['classification'] == status for r in result[category])
                                   for status in sorted({r['classification'] for r in result[category]})}
                         for category in ('skills', 'crafting', 'quests')}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--client-tables', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    client = json.loads(args.client_tables.read_text())
    if client['native_pin'] != '8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5':
        raise ValueError('Unsupported native pin')
    report = crosscheck(load_tables(args.baseline), client)
    report['inputs'] = dict(baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
                           client_tables_sha256=hashlib.sha256(args.client_tables.read_bytes()).hexdigest())
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(summary=report['summary'], client_only_mix_ids=report['client_only_mix_ids'])))


if __name__ == '__main__':
    main()
