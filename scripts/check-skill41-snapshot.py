#!/usr/bin/env python3
"""Assess fixed skill-41 persistence evidence; never infer accepted use from animation."""
import argparse
import importlib.util
import json
from pathlib import Path

ACTOR = 'test300Dk'
ACTOR_ID = '511da101-0000-7171-e6b7-6ed8654174ee'
SKILL_ID = '00000400-0029-0000-0000-000000000000'
ORB_ID = '511da101-0000-780d-d7a9-a661c1e70ec8'
ORB_DEFINITION = '00000080-000c-0007-0000-000000000000'


def snapshot_helpers():
    spec = importlib.util.spec_from_file_location(
        'trade_snapshot', Path(__file__).with_name('check-trade-snapshot.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_skills(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    skills = data['skills']
    if (data['character_id'] != ACTOR_ID or not data['actor_exists']
            or data['skill_count'] != len(skills)
            or any(row['CharacterId'] != ACTOR_ID for row in skills)):
        raise ValueError('Skill capture actor/count mismatch')
    ids = [row['SkillId'] for row in skills]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate learned skill identity')
    return set(ids)


def scoped_state_assertions(helpers, before, after):
    old = helpers.character_state(before, ACTOR)
    new = helpers.character_state(after, ACTOR)
    return {
        'actor_identity': old['id'] == new['id'] == ACTOR_ID,
        'orb_consumed': not any(row.get('Id') == ORB_ID for row in after),
        'other_actor_item_ids_preserved': set(new['items']) == set(old['items']) - {ORB_ID},
        'actor_money_unchanged': old['money'] == new['money'],
        'core_dk_unchanged': helpers.character_state(before, 'test0Dk')
                             == helpers.character_state(after, 'test0Dk'),
    }


def compare_persistence(directory, before_skills):
    helpers = snapshot_helpers()
    before = helpers.read_rows(directory / 'ready-database.jsonl')
    after = helpers.read_rows(directory / 'skill41-relog-database.jsonl')
    final = helpers.read_rows(directory / 'final-database.jsonl')
    old = helpers.character_state(before, ACTOR)
    after_skills = read_skills(directory / 'skill41-relog-skill41.json')
    final_skills = read_skills(directory / 'final-skill41.json')
    orb = old['items'].get(ORB_ID)
    assertions = {
        'orb_initially_present': bool(orb and orb['DefinitionId'] == ORB_DEFINITION
                                     and orb['Durability'] == 1),
        'only_target_skill_added_after_relog': after_skills == before_skills | {SKILL_ID},
        'skill_persists_after_client_exit': final_skills == after_skills,
    }
    for stage, rows in (('relog', after), ('final', final)):
        assertions.update({f'{stage}_{key}': value
                           for key, value in scoped_state_assertions(helpers, before, rows).items()})
    return {key: 'PASS' if value else 'FAIL' for key, value in assertions.items()}


def assess(directory):
    before = read_skills(directory / 'ready-skill41.json')
    if SKILL_ID in before:
        return {'status': 'BLOCKED_ALREADY_LEARNED', 'skill_absence': 'FAIL'}
    assertions = compare_persistence(directory, before)
    return {
        'status': 'PERSISTENCE_PASS' if all(v == 'PASS' for v in assertions.values()) else 'FAIL',
        'skill_absence': 'PASS',
        'assertions': assertions,
        'accepted_use_effect_cost': 'UNKNOWN',
        'full_learn_use_relog_proof': 'UNKNOWN',
        'limits': 'Requires reviewed native learn/relog sequence and independent accepted-use '
                  'effect/cost evidence. A named snapshot is not proof of relog; DB state or '
                  'animation alone cannot prove use. Final capture follows client exit, not '
                  'server/PostgreSQL restart. No baseline promotion/readiness credit.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = assess(args.evidence)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        result = {'status': 'UNKNOWN', 'reason': str(error),
                  'full_learn_use_relog_proof': 'UNKNOWN'}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PERSISTENCE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
