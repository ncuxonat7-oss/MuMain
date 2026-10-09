#!/usr/bin/env python3
"""Recalculate the frozen owner-weighted baseline acceptance score."""
import argparse
import json
from pathlib import Path

EXPECTED_WEIGHTS = [15, 10, 10, 10, 10, 10, 10, 10, 5, 10]
CRITERIA_PER_SUBSYSTEM = 5
ALLOWED_VALUES = (0, 0.5, 1)


def calculate(document):
    systems = document['subsystems']
    if document['model_version'] != '1.0' or [system['weight'] for system in systems] != EXPECTED_WEIGHTS:
        raise ValueError('Model/weights changed: document a comparable migration before recalculating.')
    scores = {}
    for system in systems:
        criteria = system['criteria']
        if len(criteria) != CRITERIA_PER_SUBSYSTEM or any(item['value'] not in ALLOWED_VALUES for item in criteria):
            raise ValueError('Invalid frozen acceptance checklist or criterion value.')
        for item in criteria:
            if item['value'] and item['evidence_type'] not in ('RUNTIME_VERIFIED', 'AUTOMATICALLY_VALIDATED'):
                raise ValueError('Presence/inference cannot earn acceptance points.')
        scores[system['name']] = sum(item['value'] for item in criteria) / CRITERIA_PER_SUBSYSTEM * 100
    score = sum(system['weight'] * scores[system['name']] / 100 for system in systems)
    return {'model': document['model_version'], 'readiness': score, 'confidence': document['confidence'],
            'subsystem_scores': scores, 'coverage': document['weighted_acceptance_evidence_coverage'],
            'critical_red_blockers': document['critical_red_blockers'], 'decision': document['readiness_decision']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    args = parser.parse_args()
    print(json.dumps(calculate(json.loads(args.ledger.read_text())), indent=2))
