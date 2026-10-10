#!/usr/bin/env python3
"""Join preserved server IDs with decoded pinned client tables, read-only.

Quest key = (Group << 16) | StepNumber per native ReceiveQuestQSSelSentence.
Crafting uses protocol MixID, never UI MixIndex. Presence does not admit import.
"""
import argparse
import hashlib
import json
from pathlib import Path


def load_tables(path):
    result = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        result.setdefault(row['table'], []).append(row['row'])
    return result


def quest_key(group, number):
    return ((group & 0xFFFF) << 16) | (number & 0xFFFF)


def crosscheck(tables, client):
    skills = {row['id']: row for row in client['tables']['skills']}
    mixes = {row['MixID'] for row in client['tables']['crafting']}
    quests = {row['raw_key'] for row in client['tables']['quest_progress']}
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
            result['quests'].append(dict(group=0, number=row['Number'], classification='FORMAT MAPPING REQUIRED',
                                        reason='Legacy Quest_eng.bmd is a different format, not QuestProgress'))
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
