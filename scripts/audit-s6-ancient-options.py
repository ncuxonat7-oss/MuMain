#!/usr/bin/env python3
"""Dry-run configured ancient-set/bonus correspondence for mix 38."""
import argparse
import importlib.util
import json
from pathlib import Path

MIX_ID = 38
ANCIENT_FLAG = 4
ANCIENT_BONUS_TYPE = 'Ancient Bonus Option'


def load_mapper():
    spec = importlib.util.spec_from_file_location('ingredients',
        Path(__file__).with_name('map-s6-recipe-ingredients.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify_set(row, options, types):
    if not row['AncientSetDiscriminator']:
        return 'NOT_ANCIENT'
    bonus = row['BonusOptionId']
    if bonus is None:
        return 'SET_WITHOUT_BONUS'
    option = options.get(bonus)
    if option is None or option['OptionTypeId'] not in types:
        return 'UNKNOWN'
    name = types[option['OptionTypeId']]['Name'].split('||')[0]
    return 'BONUS_CAPABLE_SET' if name == ANCIENT_BONUS_TYPE else 'SET_WITH_OTHER_BONUS'


def run(tables, client, stride):
    options = {r['Id']: r for r in tables['IncreasableItemOption']}
    types = {r['Id']: r for r in tables['ItemOptionType']}
    items = {r['Id']: r for r in tables['ItemDefinition']}
    sources = [s for v in client['tables']['crafting'] if v['MixID'] == MIX_ID
               for s in v['Sources'] if s['SpecialItem'] & ANCIENT_FLAG]
    results = []
    for row in tables['ItemOfItemSet']:
        classification = classify_set(row, options, types)
        if classification == 'NOT_ANCIENT':
            continue
        item = items[row['ItemDefinitionId']]
        key = item['Group'] * stride + item['Number']
        levels = sorted({level for s in sources if s['TypeMin'] <= key <= s['TypeMax']
            for level in range(max(0, s['LevelMin']),
                min(item['MaximumItemLevel'], s['LevelMax']) + 1)})
        results.append(dict(set_item_id=row['Id'], group=item['Group'], number=item['Number'],
            discriminator=row['AncientSetDiscriminator'], classification=classification,
            native_item_level_candidate_levels=levels,
            eligibility='UNKNOWN: actual options, generation, full allocation and runtime'))
    counts = {name: sum(r['classification'] == name for r in results)
              for name in sorted({r['classification'] for r in results})}
    return dict(mode='DRY_RUN', baseline_writes=0, safe_import_plan=[], mix_id=MIX_ID,
        summary=dict(ancient_set_links=len(results), classifications=counts), links=results,
        limits=['Bonus-capable definition is not a generated bonus option',
            'Client SET uses discriminator; server requires Ancient Bonus Option presence',
            'Native item/level candidates exclude no option, durability or allocation states',
            'No full-recipe equivalence, runtime defect or readiness credit'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--client-tables', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    mapper = load_mapper()
    audit = mapper.load_audit()
    client = json.loads(args.client_tables.read_text())
    digest = mapper.validate_inputs(args.baseline, client, audit)
    result = run(audit.load_module().load_tables(args.baseline), client, audit.ITEM_STRIDE)
    result['inputs'] = dict(baseline_sha256=digest, native_pin=audit.NATIVE_PIN,
        sources='patches/s6-option-source-provenance.json')
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
