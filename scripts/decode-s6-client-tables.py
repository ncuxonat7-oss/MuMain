#!/usr/bin/env python3
"""Read exact pinned BMD tables without importing or changing game data.

Windows fixed-width structs and record-local Bux XOR match native MuMain
8d18a2b. Skill checksums use ZzzInfomation.h; other tables have no checksum.
QuestProgress keys remain raw until the server packet encoding is proven.
"""
import argparse
import ctypes as c
import hashlib
import json
import struct
from pathlib import Path

U8, U16, U32, I32 = c.c_uint8, c.c_uint16, c.c_uint32, c.c_int32
LEGACY_QUEST_COUNT = 200
LEGACY_REQUIREMENT_CAPACITY = 16
LEGACY_QUEST_SIZE = 744
LEGACY_ITEM_ACTION = 1
LEGACY_MONSTER_ACTION = 2
APPROVED_BLOBS = {
    'Local/Eng/skill_eng.bmd': '30a6894364bf526a336a451aa72f74641ef8c812',
    'Local/mix.bmd': '0a24d6da76e72af82473951bf930e3f9ea9d0633',
    'Local/QuestProgress.bmd': '25049cccb137ad2014cdf184b8f3cc320b3edb81',
    'Local/Eng/Quest_eng.bmd': 'ab9472e9f3bccd074edea7003b7404834e9ac085',
}


def bux(data):
    return bytes(value ^ (0xFC, 0xCF, 0xAB)[index % 3] for index, value in enumerate(data))


def checksum(data, key=0x5A18):
    if len(data) < 4:
        raise ValueError('Checksum input too short')
    result = key << 9
    for offset in range(0, len(data) - 3, 4):
        value = struct.unpack_from('<I', data, offset)[0]
        result = (result + value) & 0xFFFFFFFF if (offset // 4 + key) % 2 else result ^ value
        if offset % 16 == 0:
            result ^= ((key + result) & 0xFFFFFFFF) >> ((offset // 4) % 8 + 1)
    return result


class Skill(c.LittleEndianStructure):
    _fields_ = [('Name', c.c_char * 50), ('Level', U16), ('Damage', U16), ('Mana', U16),
                ('AbilityGuage', U16), ('Distance', U32), ('Delay', I32), ('Energy', I32),
                ('Charisma', U16), ('MasteryType', U8), ('SkillUseType', U8), ('SkillBrand', U32),
                ('KillCount', U8), ('RequireDutyClass', U8 * 3), ('RequireClass', U8 * 7),
                ('SkillRank', U8), ('Magic_Icon', U16), ('TypeSkill', U8), ('Strength', I32),
                ('Dexterity', I32), ('ItemSkill', U8), ('IsDamage', U8), ('Effect', U16)]


class MixItem(c.LittleEndianStructure):
    _fields_ = [('TypeMin', c.c_int16), ('TypeMax', c.c_int16)] + [
        (name, I32) for name in ('LevelMin', 'LevelMax', 'OptionMin', 'OptionMax',
                              'DurabilityMin', 'DurabilityMax', 'CountMin', 'CountMax')
    ] + [('SpecialItem', U32)]


class RateToken(c.LittleEndianStructure):
    _fields_ = [('Op', I32), ('Value', c.c_float)]


class Mix(c.LittleEndianStructure):
    _fields_ = [('MixIndex', I32), ('MixID', I32), ('MixName', I32 * 3), ('MixDesc', I32 * 3),
                ('MixAdvice', I32 * 3), ('Width', I32), ('Height', I32), ('RequiredLevel', I32),
                ('RequiredZenType', U8), ('RequiredZen', U32), ('NumRateData', I32),
                ('RateTokens', RateToken * 32), ('SuccessRate', I32), ('MixOption', U8),
                ('CharmOption', U8), ('ChaosCharmOption', U8), ('Sources', MixItem * 8),
                ('NumSources', I32)]


class LegacyAct(c.LittleEndianStructure):
    _fields_ = [('Live', U8), ('Type', U8), ('ItemType', U16), ('ItemSubType', U8),
                ('ItemLevel', U8), ('ItemCount', U8), ('RequestType', U8),
                ('Classes', U8 * 7), ('Texts', c.c_int16 * 4)]


class LegacyRequest(c.LittleEndianStructure):
    _fields_ = [('Live', U8), ('Type', U8), ('CompleteQuest', U16), ('LevelMin', U16),
                ('LevelMax', U16), ('Strength', U16), ('Zen', U32), ('ErrorText', c.c_int16)]


class LegacyQuest(c.LittleEndianStructure):
    _fields_ = [('ActCount', c.c_int16), ('RequestCount', c.c_int16), ('Npc', U16),
                ('Name', c.c_char * 32), ('Acts', LegacyAct * LEGACY_REQUIREMENT_CAPACITY),
                ('Requests', LegacyRequest * LEGACY_REQUIREMENT_CAPACITY)]


def fields(value):
    result = {}
    for name, _ in value._fields_:
        item = getattr(value, name)
        if isinstance(item, bytes):
            item = item.split(b'\0')[0].decode('utf-8', errors='strict')
        elif isinstance(item, c.Array):
            item = [fields(v) if isinstance(v, c.Structure) else v for v in item]
        result[name] = item
    return result


def decode_skills(data):
    size = c.sizeof(Skill)
    if size != 108 or len(data) != size * 650 + 4:
        raise ValueError('Unsupported skill layout; require 650 current 108-byte records')
    expected = struct.unpack_from('<I', data, len(data) - 4)[0]
    if checksum(data[:-4]) != expected:
        raise ValueError('Skill checksum mismatch')
    return [dict(id=i, **fields(Skill.from_buffer_copy(bux(data[i * size:(i + 1) * size])))) for i in range(650)]


def decode_mixes(data):
    if len(data) < 56:
        raise ValueError('Mix header truncated')
    counts = struct.unpack('<14i', bux(data[:56]))
    size = c.sizeof(Mix)
    if any(n < 0 or n > 1000 for n in counts) or len(data) != 56 + sum(counts) * size:
        raise ValueError('Mix counts/layout/length mismatch')
    result, offset = [], 56
    for category, count in enumerate(counts):
        for _ in range(count):
            row = fields(Mix.from_buffer_copy(bux(data[offset:offset + size])))
            if not 0 <= row['NumSources'] <= 8 or not 0 <= row['NumRateData'] <= 32:
                raise ValueError('Invalid mix source/rate count')
            row['Sources'] = row['Sources'][:row['NumSources']]
            row['RateTokens'] = row['RateTokens'][:row['NumRateData']]
            result.append(dict(category=category, **row))
            offset += size
    return result


def decode_quest_progress(data):
    # QuestMng.h packs SQuestProgress to 1; DWORD key + BYTE UI + nine int32s.
    size = 41
    if len(data) % size:
        raise ValueError('QuestProgress has a partial record')
    result = []
    for offset in range(0, len(data), size):
        values = struct.unpack('<IB9i', bux(data[offset:offset + size]))
        result.append(dict(raw_key=values[0], ui_type=values[1], words=list(values[2:])))
    keys = [row['raw_key'] for row in result]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate QuestProgress key')
    return result


def decode_legacy_quests(data):
    if c.sizeof(LegacyQuest) != LEGACY_QUEST_SIZE or len(data) != LEGACY_QUEST_COUNT * LEGACY_QUEST_SIZE:
        raise ValueError('Unsupported legacy quest layout/length')
    result = []
    for index in range(LEGACY_QUEST_COUNT):
        offset = index * LEGACY_QUEST_SIZE
        row = fields(LegacyQuest.from_buffer_copy(bux(data[offset:offset + LEGACY_QUEST_SIZE])))
        if any(not 0 <= row[key] <= LEGACY_REQUIREMENT_CAPACITY for key in ('ActCount', 'RequestCount')):
            raise ValueError('Invalid legacy quest act/request count')
        row['Acts'] = row['Acts'][:row['ActCount']]
        row['Requests'] = row['Requests'][:row['RequestCount']]
        if any(act['Type'] not in (LEGACY_ITEM_ACTION, LEGACY_MONSTER_ACTION) for act in row['Acts']):
            raise ValueError('Unmapped legacy quest action type')
        result.append(dict(id=index, **row))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    paths = {'skills': 'Local/Eng/skill_eng.bmd', 'crafting': 'Local/mix.bmd',
             'quest_progress': 'Local/QuestProgress.bmd', 'legacy_quests': 'Local/Eng/Quest_eng.bmd'}
    decoders = {'skills': decode_skills, 'crafting': decode_mixes,
                'quest_progress': decode_quest_progress, 'legacy_quests': decode_legacy_quests}
    result = dict(mode='READ_ONLY', baseline_writes=0, native_pin='8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5', tables={}, inputs={})
    for category, relative in paths.items():
        data = (args.data / relative).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != APPROVED_BLOBS[relative]:
            raise ValueError('Client input differs from approved pinned Git blob: ' + relative)
        result['tables'][category] = decoders[category](data)
        result['inputs'][category] = dict(path=relative, git_blob=blob, sha256=hashlib.sha256(data).hexdigest(), size=len(data))
    result['limitations'] = ['Metadata is not rendering/animation or gameplay proof',
                             'QuestProgress raw keys require verified server packet mapping',
                             'MixID differs from UI MixIndex; ingredients/outcomes require semantic mapping',
                             'Legacy quest names/NPC/actions decoded; inherited levels, prerequisites, item levels and rewards need semantic mapping']
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({name: len(rows) for name, rows in result['tables'].items()}))


if __name__ == '__main__':
    main()
