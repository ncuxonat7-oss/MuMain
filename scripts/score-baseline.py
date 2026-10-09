#!/usr/bin/env python3
"""Recalculate readiness with the versioned owner-defined baseline scope."""
import argparse
import json
from pathlib import Path

EXPECTED_WEIGHTS = [15, 10, 10, 10, 10, 10, 10, 10, 5, 10]
LEGACY_CRITERIA_COUNT = 5
ALLOWED_VALUES = (0, 0.5, 1)
EXCLUDED_CRITERION = 'Required Crywolf and Illusion Temple lifecycle completeness'
EVENT_SUBSYSTEM = 'Quests/events/Chaos Machine/crafting'
ACCEPTED_EVIDENCE = ('RUNTIME_VERIFIED', 'AUTOMATICALLY_VALIDATED')


def required_criteria(system, version):
    criteria = system['criteria']
    if len(criteria) != LEGACY_CRITERIA_COUNT:
        raise ValueError('Original checklist must remain preserved.')
    excluded = [item for item in criteria if item.get('scope') == 'excluded']
    expected = [EXCLUDED_CRITERION] if version == '1.1' and system['name'] == EVENT_SUBSYSTEM else []
    if [item['criterion'] for item in excluded] != expected:
        raise ValueError('Unexpected scope migration; record owner authorization first.')
    return [item for item in criteria if item not in excluded]


def subsystem_score(system, version):
    criteria = required_criteria(system, version)
    for item in criteria:
        if item['value'] not in ALLOWED_VALUES:
            raise ValueError('Invalid acceptance evidence value.')
        if item['value'] and item['evidence_type'] not in ACCEPTED_EVIDENCE:
            raise ValueError('Presence/inference cannot earn acceptance points.')
    return sum(item['value'] for item in criteria) / len(criteria) * 100


def evidence_coverage(systems, version):
    coverage = {kind: 0.0 for kind in (*ACCEPTED_EVIDENCE, 'STATICALLY_CONFIRMED', 'UNKNOWN', 'BROKEN_MISSING')}
    for system in systems:
        criteria = required_criteria(system, version)
        weight = system['weight'] / len(criteria)
        for item in criteria:
            kind = item['evidence_type']
            if kind in ACCEPTED_EVIDENCE:
                coverage[kind] += weight * item['value']
                coverage['UNKNOWN'] += weight * (1 - item['value'])
            else:
                coverage[kind] += weight
    return coverage


def calculate(document):
    systems = document['subsystems']
    version = document['model_version']
    if version not in ('1.0', '1.1') or [system['weight'] for system in systems] != EXPECTED_WEIGHTS:
        raise ValueError('Unsupported model/weights migration.')
    scores = {system['name']: subsystem_score(system, version) for system in systems}
    score = sum(system['weight'] * scores[system['name']] / 100 for system in systems)
    return {'model': version, 'readiness': score, 'confidence': document['confidence'],
            'subsystem_scores': scores, 'coverage': evidence_coverage(systems, version),
            'critical_red_blockers': document['critical_red_blockers'], 'decision': document['readiness_decision']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    args = parser.parse_args()
    print(json.dumps(calculate(json.loads(args.ledger.read_text())), indent=2))
