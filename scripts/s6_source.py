"""Read a pinned OpenMU source tree without executing initializers.

Only explicit literals are admitted. Expressions and generated records remain
unmapped; this module never promises a complete C# interpretation.
"""
import re
from pathlib import Path

TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/', re.S)
PIN = 'd067b3c11c23c3145de6e2c76201ab9a93b267c8'
EXCLUDED_MAPS = {34, 45, 46, 47, 48, 49, 50}


def strip_comments(text):
    return TOKEN.sub(lambda m: m[0] if m[0].startswith('"') else '\n' * m[0].count('\n'), text)


def split_args(text):
    parts, start, depth, quoted, escaped = [], 0, 0, False, False
    for i, char in enumerate(text):
        if quoted:
            if char == '"' and not escaped:
                quoted = False
            escaped = char == '\\' and not escaped
            continue
        if char == '"':
            quoted = True
        elif char in '([{':
            depth += 1
        elif char in ')]}':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    return parts + [text[start:].strip()]


def balanced(text, start, opening='(', closing=')'):
    depth, quoted, escaped = 0, False, False
    for i in range(start, len(text)):
        char = text[i]
        if quoted:
            if char == '"' and not escaped:
                quoted = False
            escaped = char == '\\' and not escaped
            continue
        if char == '"':
            quoted = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError('Unbalanced source at ' + str(start))


def calls(text, name):
    for match in re.finditer(r'\b' + re.escape(name) + r'\s*\(', text):
        body, end = balanced(text, text.index('(', match.start()))
        yield split_args(body), match.start(), end


def literal(expression, enums=None):
    expression = expression.strip()
    if expression in ('true', 'false'):
        return expression == 'true'
    if re.fullmatch(r'-?\d+(?:\.\d+)?[fFdDmM]?', expression):
        return float(expression.rstrip('fFdDmM')) if '.' in expression else int(expression.rstrip('fFdDmM'))
    if enums and expression in enums:
        return enums[expression]
    return None


def enum_values(text, name):
    match = re.search(r'\benum\s+' + name + r'\b[^\{]*\{', text)
    if not match:
        return {}
    body, _ = balanced(text, match.end() - 1, '{', '}')
    values, current = {}, -1
    for part in split_args(body):
        fields = part.strip().split('=')
        if not re.fullmatch(r'\w+', fields[0].strip()):
            continue
        current = int(fields[1].strip(), 0) if len(fields) == 2 else current + 1
        values[name + '.' + fields[0].strip()] = current
    return values


def record(category, key, fields, path, text, position=0, **extra):
    return dict(category=category, key=str(key), fields=fields,
                source=str(path), line=text[:position].count('\n') + 1,
                line_basis='EXTRACTED_CONTEXT', **extra)


def load_sources(root):
    return {str(p.relative_to(root)): strip_comments(p.read_text(encoding='utf-8-sig'))
            for p in Path(root).rglob('*.cs')}


def classes(sources):
    result = {}
    for path, text in sources.items():
        namespace = re.search(r'namespace\s+([\w.]+)', text)
        match = re.search(r'\bclass\s+(\w+)\s*:\s*([\w.]+)', text)
        if namespace and match:
            result[namespace[1] + '.' + match[1]] = (path, text, match[2])
    return result


def resolve_class(name, namespace, index):
    candidates = [namespace + '.' + name,
                  'MUnique.OpenMU.Persistence.Initialization.' + name]
    found = [key for key in candidates if key in index]
    if found:
        return found[0]
    found = [key for key in index if key.endswith('.' + name)]
    return found[0] if len(found) == 1 else None


def ancestry(name, index):
    chain = []
    while name and name not in chain:
        chain.append(name)
        parent = index[name][2]
        name = resolve_class(parent, name.rsplit('.', 1)[0], index)
    return chain


def method_body(text, name):
    pattern = r'(?:protected|private|public|internal)\s+(?:(?:override|virtual|static)\s+)*[\w<>?,]+\s+' + name + r'\s*\('
    match = re.search(pattern, text)
    if not match:
        return None
    _, end = balanced(text, text.index('(', match.start()))
    start = text.find('{', end)
    if start < 0 or '=>' in text[end:start]:
        return None
    return balanced(text, start, '{', '}')[0]


def effective_bodies(chain, index, method):
    for name in chain:
        path, text, _ = index[name]
        body = method_body(text, method)
        if body is None:
            continue
        yield path, body
        if 'base.' + method + '(' not in body:
            return


def map_identity(chain, index):
    number, discriminator = None, 0
    for name in chain:
        text = index[name][1]
        match = re.search(r'\bMapNumber\s*=>\s*(\d+|Number)\s*;', text)
        if number is None and match:
            value = match[1]
            constant = re.search(r'(?:const|static readonly)\s+byte\s+Number\s*=\s*(\d+)', text)
            number = int(constant[1]) if value == 'Number' and constant else literal(value)
        match = re.search(r'\bDiscriminator\s*=>\s*(\d+)', text)
        if match:
            discriminator = int(match[1])
            break
    return number, discriminator


def monster_records(path, text, enums=None):
    starts = list(re.finditer(r'var\s+(\w+)\s*=\s*this\.Context\.CreateNew<MonsterDefinition>\(\)', text))
    for i, match in enumerate(starts):
        body = text[match.end():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        var = match[1]
        assignments = dict(re.findall(r'\b' + var + r'\.(\w+)\s*=\s*([^;]+);', body))
        number = literal(assignments.get('Number', ''))
        if number is None:
            continue
        fields = {field: value for field, expr in assignments.items()
                  if (value := literal(expr, enums)) is not None and field != 'Number'}
        if 'MerchantStore' in assignments:
            fields['HasMerchantStore'] = True
        for field in ('MoveDelay', 'AttackDelay', 'RespawnDelay'):
            delay = re.fullmatch(r'new TimeSpan\((\d+) \* TimeSpan.TicksPer(Millisecond|Second)\)', assignments.get(field, ''))
            if delay:
                fields[field + 'Ms'] = int(delay[1]) * (1000 if delay[2] == 'Second' else 1)
        stats = re.findall(r'\{\s*Stats\.(\w+),\s*([\d.]+f?)\s*\}', body)
        fields.update({'Stats.' + key: literal(value) for key, value in stats})
        yield record('monsters', number, fields, path, text, match.start())


def selected_maps(sources, index):
    path = next(p for p in sources if p.endswith('VersionSeasonSix/GameMapsInitializer.cs'))
    text = sources[path]
    namespace = 'MUnique.OpenMU.Persistence.Initialization.VersionSeasonSix.Maps'
    for type_name in re.findall(r'yield return typeof\(([\w.]+)\)', text):
        name = resolve_class(type_name, namespace, index)
        if name:
            chain = ancestry(name, index)
            number, discriminator = map_identity(chain, index)
            if number is not None:
                yield number, discriminator, chain


def spawn_records(path, body, map_key, enums):
    for args, pos, _ in calls(body, 'CreateMonsterSpawn'):
        if len(args) < 4 or not re.fullmatch(r'this.NpcDictionary\[\d+\]', args[1]):
            continue
        monster = int(re.search(r'\[(\d+)\]', args[1])[1])
        values = [literal(arg, enums) for arg in args[2:]]
        if len(args) >= 6 and all(literal(arg) is not None for arg in args[2:6]):
            x1, x2, y1, y2 = values[:4]
            quantity = values[4] if len(values) > 4 else 1
            direction = values[5] if len(values) > 5 else 0
            trigger = values[6] if len(values) > 6 else 0
            wave = values[7] if len(values) > 7 else 0
        else:
            x1 = x2 = values[0]
            y1 = y2 = values[1]
            quantity, wave = 1, 0
            direction = values[2] if len(values) > 2 else 0
            trigger = values[3] if len(values) > 3 else 0
        fields = dict(Map=map_key, Monster=monster, X1=x1, X2=x2, Y1=y1, Y2=y2,
                      Quantity=quantity, Direction=direction, SpawnTrigger=trigger, WaveNumber=wave)
        if any(value is None for value in fields.values()):
            continue
        key = ':'.join(str(fields[k]) for k in fields)
        yield record('spawns', key, fields, path, body, pos)


def gate_records(path, text):
    exits = {}
    pattern = r'targetGates.Add\((\d+), this.CreateExitGate\(maps\[(\d+)\], ([^;]+)\)\);'
    for match in re.finditer(pattern, text):
        args = split_args(match[3])
        fields = dict(zip(('X1', 'Y1', 'X2', 'Y2', 'Direction'), map(literal, args[:5])))
        fields.update(Map=match[2] + ':0', IsSpawnGate=literal(args[5]) if len(args) > 5 else False)
        key = ':'.join(str(fields[k]) for k in ('Map', 'X1', 'Y1', 'X2', 'Y2', 'Direction'))
        exits[int(match[1])] = key
        yield record('exit_gates', key, fields, path, text, match.start())
    pattern = r'maps\[(\d+)\].EnterGates.Add\(this.CreateEnterGate\((\d+), targetGates\[(\d+)\], ([^;]+)\)\);'
    for match in re.finditer(pattern, text):
        fields = dict(zip(('X1', 'Y1', 'X2', 'Y2', 'LevelRequirement'), map(literal, split_args(match[4]))))
        fields.update(Map=match[1] + ':0', Target=exits.get(int(match[3])))
        yield record('enter_gates', match[2], fields, path, text, match.start())
    for args, pos, _ in calls(text, 'CreateWarpInfo'):
        if literal(args[0]) is None or len(args) != 5:
            continue
        target = re.fullmatch(r'gates\[(\d+)\]', args[4])
        if target:
            fields = dict(Costs=literal(args[2]), LevelRequirement=literal(args[3]), Gate=exits.get(int(target[1])))
            yield record('warps', literal(args[0]), fields, path, text, pos)


def skill_records(path, text, enums):
    parameters = ['number', 'name', 'classes', 'damageType', 'damage', 'distance', 'abilityConsumption', 'manaConsumption', 'levelRequirement', 'energyRequirement', 'leadershipRequirement']
    for args, pos, _ in calls(text, 'CreateSkill'):
        values = {}
        for i, arg in enumerate(args):
            named = re.match(r'(\w+):\s*(.*)', arg, re.S)
            key = named[1] if named else parameters[i] if i < len(parameters) else None
            if key:
                values[key] = literal(named[2] if named else arg, enums)
        number = values.get('number')
        if number is None:
            continue
        fields = {'AttackDamage': values.get('damage') or 0, 'Range': values.get('distance') or 0}
        for arg, field in [('movesToTarget', 'MovesToTarget'), ('movesTarget', 'MovesTarget'), ('hitsPerAttack', 'NumberOfHitsPerAttack')]:
            if arg in values and values[arg] is not None:
                fields[field] = values[arg]
        for arg, stat in [('energyRequirement', 'TotalEnergy'), ('levelRequirement', 'Level'), ('leadershipRequirement', 'TotalLeadership')]:
            if values.get(arg) is not None:
                fields['Requirements.' + stat] = values[arg]
        yield record('skills', number, fields, path, text, pos)


def item_records(path, text):
    for name in ('CreateWeapon', 'CreateArmor'):
        for args, pos, _ in calls(text, name):
            if literal(args[0]) is None:
                continue
            if name == 'CreateWeapon':
                group, number = literal(args[0]), literal(args[1])
                fields = {key: literal(args[i]) for key, i in [('Width', 4), ('Height', 5), ('DropLevel', 8), ('DropsFromMonsters', 6)]}
            else:
                number, slot = literal(args[0]), literal(args[1])
                if slot is None:
                    continue
                group = slot + 5
                fields = {key: literal(args[i]) for key, i in [('Width', 2), ('Height', 3), ('DropLevel', 5)]}
            yield record('items', f'{group}:{number}', fields, path, text, pos)
    for name, group in [('CreateGloves', 10), ('CreateBoots', 11)]:
        for args, pos, _ in calls(text, name):
            number = literal(args[0])
            if number is not None and len(args) > 3 and args[1].startswith('LocalizedString'):
                yield record('items', f'{group}:{number}', {'DropLevel': literal(args[2])}, path, text, pos)
    starts = list(re.finditer(r'var\s+(\w+)\s*=\s*this.Context.CreateNew<ItemDefinition>\(\)', text))
    for i, match in enumerate(starts):
        body = text[match.end():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        assignments = dict(re.findall(r'\b' + match[1] + r'\.(\w+)\s*=\s*([^;]+);', body))
        group, number = literal(assignments.get('Group', '')), literal(assignments.get('Number', ''))
        if group is None or number is None:
            continue
        fields = {field: value for field, expr in assignments.items() if field not in ('Group', 'Number') and (value := literal(expr)) is not None}
        yield record('items', f'{group}:{number}', fields, path, text, match.start())


def quest_records(path, text, enums):
    for args, pos, _ in calls(text, 'CreateQuest'):
        if len(args) < 8 or literal(args[1]) is None:
            continue
        values = [literal(arg, enums) for arg in args[1:]]
        group, start, number, refuse, minimum, maximum, giver = values[:7]
        character = values[7] if len(values) > 7 else None
        key = f'{group}:{number}:{giver}:{character}'
        fields = dict(StartingNumber=start, RefuseNumber=refuse, MinimumCharacterLevel=minimum, MaximumCharacterLevel=maximum)
        yield record('quests', key, fields, path, text, pos)


def set_records(path, text):
    for args, pos, end in calls(text, 'AddAncientSet'):
        prefix = text[max(0, pos - 70):pos]
        var = re.search(r'var\s+(\w+)\s*=\s*this\.\s*$', prefix)
        if not var:
            continue
        match = re.search(r'\b' + var[1] + r'\.SetGuid\((\d+),\s*(\d+)\)', text[end:])
        if not match:
            continue
        # GuidHelper.cs maps ItemSetGroup to type 0x92 and two short key parts.
        key = f'00000092-{int(match[1]):04x}-{int(match[2]):04x}-0000-000000000000'
        fields = dict(CountDistinct=True, MinimumItemCount=2)
        yield record('sets', key, fields, path, text, pos)


def crafting_records(path, text):
    initializer = method_body(text, 'Initialize') or ''
    for method in re.findall(r'\.ItemCraftings.Add\(this\.(\w+)\(', initializer):
        if 'IllusionTemple' in method:
            continue
        body = method_body(text, method)
        if not body:
            continue
        match = re.search(r'crafting.Number\s*=\s*(\d+)', body)
        if not match:
            continue
        fields = {}
        handler = re.search(r'crafting.ItemCraftingHandlerClassName = typeof\((\w+)\)', body)
        if handler:
            fields['Handler'] = handler[1]
        yield record('crafting', match[1], fields, path, text, text.index(body))
    for args, pos, _ in calls(initializer, 'ItemLevelUpgradeCrafting'):
        if literal(args[0]) is not None:
            yield record('crafting', literal(args[0]), {}, path, initializer, pos)


def finalize_skills(records, path, text, enums):
    by_number = {int(r['key']): r for r in records}
    body = method_body(text, 'InitializeMasterSkillData') or ''
    for args, pos, _ in calls(body, 'AddMasterSkillDefinition'):
        if len(args) < 7:
            continue
        skill_number, replaced_number = literal(args[0], enums), literal(args[5], enums)
        if skill_number not in by_number or replaced_number not in by_number:
            continue
        record = by_number[skill_number]
        previous = record['fields']['AttackDamage']
        record['fields']['AttackDamage'] = by_number[replaced_number]['fields']['AttackDamage']
        record['fields']['MasterReplacedSkill'] = replaced_number
        if previous != record['fields']['AttackDamage']:
            record['transformation'] = dict(rule='AddMasterSkillDefinition copies replaced skill AttackDamage',
                                            initial=previous, replaced_skill=replaced_number)
    return records


def explicit_object_records(path, text, type_name, category, type_id, enums):
    starts = list(re.finditer(r'var\s+(\w+)\s*=\s*this.Context.CreateNew<' + type_name + r'>\(\)', text))
    for i, match in enumerate(starts):
        body = text[match.end():starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        var = match[1]
        guid = re.search(r'\b' + var + r'\.SetGuid\((\d+)(?:,\s*(\d+))?\)', body)
        if not guid:
            continue
        fields = {}
        for field, expression in re.findall(r'\b' + var + r'\.(\w+)\s*=\s*([^;]+);', body):
            value = literal(expression, enums)
            if value is not None:
                fields[field] = value
        parent, number = int(guid[1]), int(guid[2] or 0)
        key = f'{type_id:08x}-{parent:04x}-{number:04x}-0000-000000000000'
        yield record(category, key, fields, path, text, match.start())


def event_fields(body, enums):
    fields = {}
    for field, expression in re.findall(r'\b\w+\.(\w+)\s*=\s*([^;]+);', body):
        value = literal(expression, enums)
        if value is not None:
            fields[field] = value
        duration = re.fullmatch(r'TimeSpan.From(Minutes|Seconds)\((\d+)\)', expression)
        if duration:
            fields[field + 'Ms'] = int(duration[2]) * (60000 if duration[1] == 'Minutes' else 1000)
    return fields


def event_records(sources, index, enums):
    namespace = 'MUnique.OpenMU.Persistence.Initialization.VersionSeasonSix.Events'
    for name in ('BloodCastle', 'ChaosCastle', 'DevilSquare'):
        cls = resolve_class(name + 'Initializer', namespace, index)
        chain = ancestry(cls, index)
        method = 'Create' + name + 'Definition'
        template = next(((path, body) for path, body in effective_bodies(chain, index, method)), None)
        if not template:
            continue
        fields = event_fields(template[1], enums)
        for path, body in effective_bodies(chain, index, 'Initialize'):
            for args, pos, _ in calls(body, method):
                level = literal(args[0])
                if level is not None:
                    yield record('events', f"{fields['Type']}:{level}", dict(fields, GameLevel=level), path, body, pos)
    for name in ('Doppelganger', 'Kanturu', 'ImperialGuardian'):
        cls = resolve_class(name + 'Initializer', namespace, index)
        if not cls:
            continue
        path, text, _ = index[cls]
        method = 'CreateMiniGameDefinitions' if name == 'ImperialGuardian' else 'Initialize'
        body = method_body(text, method) or ''
        fields = event_fields(body, enums)
        if 'Type' not in fields:
            continue
        if name == 'Doppelganger':
            match = re.search(r'MapNumbers = \[([^\]]+)\]', text)
            levels = range(1, len(split_args(match[1])) + 1)
        elif name == 'ImperialGuardian':
            levels = range(1, len(re.findall(r'\(ImperialGuardianDay\.\w+,', text)) + 1)
        else:
            levels = [fields.get('GameLevel', 1)]
        for level in levels:
            yield record('events', f"{fields['Type']}:{level}", dict(fields, GameLevel=level), path, text)


def finalize_reward_chests(records, sources, enums):
    path = next(p for p in sources if p.endswith('/Events/DoppelgangerMonsters.cs'))
    text = sources[path]
    constants = {name: int(value) for name, value in re.findall(r'const short (\w+) = (\d+)', text)}
    body = method_body(text, 'ConfigureRewardChests') or ''
    changes = {}
    for args, _, _ in calls(body, 'ConfigureRewardChest'):
        number = constants.get(args[0])
        if number is not None:
            changes[str(number)] = dict(ObjectKind=enums['NpcObjectKind.Destructible'], NumberOfMaximumItemDrops=literal(args[1]), RespawnDelayMs=0)
    for row in records:
        if row['category'] in ('monsters', 'npcs') and row['key'] in changes:
            row['fields'].update(changes[row['key']])
            row['transformation'] = dict(rule='ConfigureRewardChests: passive declarations become attackable rewards', source=path,
                                         update='8E4D2B17-6A3F-4C95-9D02-B7E15A6C3F48')
    return records


def extract(root):
    sources, records = load_sources(root), []
    index, enums = classes(sources), {}
    for text in sources.values():
        for enum in ('SkillNumber', 'Direction', 'CharacterClassNumber', 'SpawnTrigger', 'ItemGroups', 'NpcObjectKind', 'NpcWindow', 'MiniGameType', 'MiniGameMapCreationPolicy'):
            enums.update(enum_values(text, enum))
    for number, discriminator, chain in selected_maps(sources, index):
        if number in EXCLUDED_MAPS:
            continue
        map_key = f'{number}:{discriminator}'
        path = index[chain[0]][0]
        records.append(record('maps', map_key, {'Number': number, 'Discriminator': discriminator}, path, index[chain[0]][1]))
        for method in ('CreateMonsters', 'CreateNpcSpawns', 'CreateMonsterSpawns'):
            for source, body in effective_bodies(chain, index, method):
                if method == 'CreateMonsters':
                    records.extend(monster_records(source, body, enums))
                else:
                    records.extend(spawn_records(source, body, map_key, enums))
    npc = resolve_class('NpcInitialization', 'MUnique.OpenMU.Persistence.Initialization.VersionSeasonSix', index)
    for path, body in effective_bodies(ancestry(npc, index), index, 'Initialize'):
        npcs = list(monster_records(path, body, enums))
        records.extend(npcs)
        records.extend(dict(r, category='npcs') for r in npcs if r['fields'].get('ObjectKind') == 1)
        records.extend(dict(r, category='shops', fields={'HasMerchantStore': True}) for r in npcs if r['fields'].get('HasMerchantStore'))
    for path, text in sources.items():
        if path.endswith('/GameConfigurationInitializerBase.cs'):
            records.extend(explicit_object_records(path, text, 'DropItemGroup', 'drops', 0x200, enums))
        if 'VersionSeasonSix/' not in path:
            continue
        if path.endswith('/Gates.cs'):
            records.extend(gate_records(path, text))
        elif path.endswith('/SkillsInitializer.cs'):
            skills = list(skill_records(path, method_body(text, 'Initialize') or '', enums))
            records.extend(finalize_skills(skills, path, text, enums))
        elif '/Items/' in path:
            records.extend(item_records(path, text))
            if path.endswith('/AncientSets.cs'):
                records.extend(set_records(path, text))
        elif path.endswith('/Quests.cs'):
            records.extend(quest_records(path, text, enums))
        elif path.endswith('/ChaosMixes.cs'):
            records.extend(crafting_records(path, text))
        if '/Items/' in path or path.endswith('/GameConfigurationInitializerBase.cs'):
            records.extend(explicit_object_records(path, text, 'DropItemGroup', 'drops', 0x200, enums))
    records.extend(event_records(sources, index, enums))
    records = finalize_reward_chests(records, sources, enums)
    stats_path = next(p for p in sources if p.endswith('/Attributes/Stats.cs'))
    stats = dict(re.findall(r'AttributeDefinition (\w+) \{ get; \} = new\(new Guid\("([\w-]+)"\)', sources[stats_path]))
    return records, {name: value.lower() for name, value in stats.items()}, sources
