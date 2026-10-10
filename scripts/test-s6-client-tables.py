#!/usr/bin/env python3
"""Targeted fail-closed format tests; no gameplay/baseline test replay."""
import importlib.util
import struct
import unittest
from pathlib import Path


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


decoder = load('decode-s6-client-tables')
crosswalk = load('crosscheck-s6-client-ids')


class Formats(unittest.TestCase):
    def legacy_data(self, mutate=None):
        record = decoder.LegacyQuest()
        record.Name = b'Fixture'
        if mutate:
            mutate(record)
        return decoder.bux(bytes(record)) + decoder.bux(bytes(decoder.LegacyQuest())) * (decoder.LEGACY_QUEST_COUNT - 1)

    def test_bux_is_record_local_involution(self):
        data = bytes(range(108))
        self.assertEqual(decoder.bux(decoder.bux(data)), data)
        self.assertNotEqual(decoder.bux(data[1:]), decoder.bux(data)[1:])

    def test_skill_checksum_rejects_corruption(self):
        data = bytearray(650 * 108)
        tail = struct.pack('<I', decoder.checksum(data))
        data[7] = 1
        with self.assertRaisesRegex(ValueError, 'checksum'):
            decoder.decode_skills(bytes(data) + tail)

    def test_skill_length_rejected(self):
        with self.assertRaises(ValueError):
            decoder.decode_skills(bytes(108))

    def test_negative_mix_count_rejected(self):
        with self.assertRaises(ValueError):
            decoder.decode_mixes(decoder.bux(struct.pack('<14i', -1, *([0] * 13))))

    def test_partial_quest_record_rejected(self):
        with self.assertRaises(ValueError):
            decoder.decode_quest_progress(bytes(40))

    def test_duplicate_quest_key_rejected(self):
        record = decoder.bux(struct.pack('<IB9i', 65536, 1, *([0] * 9)))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            decoder.decode_quest_progress(record * 2)

    def test_quest_key_uses_group_high_word(self):
        self.assertEqual(crosswalk.quest_key(18, 108), 0x0012006C)

    def test_legacy_layout_and_slot_index(self):
        rows = decoder.decode_legacy_quests(self.legacy_data())
        self.assertEqual((decoder.c.sizeof(decoder.LegacyAct), decoder.c.sizeof(decoder.LegacyRequest)), (24, 20))
        self.assertEqual((len(rows), rows[0]['id'], rows[0]['Name']), (200, 0, 'Fixture'))

    def test_legacy_partial_or_extra_record_rejected(self):
        data = self.legacy_data()
        for invalid in (data[:-1], data + b'\0'):
            with self.assertRaises(ValueError):
                decoder.decode_legacy_quests(invalid)

    def test_legacy_invalid_requirement_count(self):
        for field in ('ActCount', 'RequestCount'):
            data = self.legacy_data(lambda record: setattr(record, field, 17))
            with self.assertRaisesRegex(ValueError, 'count'):
                decoder.decode_legacy_quests(data)

    def test_legacy_unknown_action_type_rejected(self):
        def mutate(record):
            record.ActCount = 1
            record.Acts[0].Type = 3
        with self.assertRaisesRegex(ValueError, 'action type'):
            decoder.decode_legacy_quests(self.legacy_data(mutate))

    def test_legacy_invalid_name_encoding_rejected(self):
        with self.assertRaises(UnicodeDecodeError):
            decoder.decode_legacy_quests(self.legacy_data(lambda record: setattr(record, 'Name', b'\xff')))

    def test_legacy_conditional_class_and_request_selection(self):
        client = dict(Acts=[dict(Type=1, ItemType=14, ItemSubType=23, ItemCount=1, RequestType=0,
                                Classes=[1, 0, 0, 0, 0, 0, 0])],
                      Requests=[dict(Type=255, Zen=1000000), dict(Type=1, Zen=9000000)])
        expected = [('item', 14, 23, 1)]
        wizard = crosswalk.legacy_class_check(client, 0, expected)
        knight = crosswalk.legacy_class_check(client, 1, expected)
        self.assertTrue(wizard['requirements_match'])
        self.assertEqual(wizard['money'], [1000000])
        self.assertFalse(knight['requirements_match'])

    def test_legacy_item_and_monster_counts_are_semantic(self):
        client = dict(Acts=[dict(Type=2, ItemType=409, ItemSubType=0, ItemCount=20, RequestType=0,
                                Classes=[1] * 7)], Requests=[])
        self.assertTrue(crosswalk.legacy_class_check(client, 0, [('monster', 409, 20)])['requirements_match'])
        self.assertFalse(crosswalk.legacy_class_check(client, 0, [('monster', 409, 19)])['requirements_match'])
        self.assertFalse(crosswalk.legacy_class_check(client, 0, [('item', 0, 409, 20)])['requirements_match'])


if __name__ == '__main__':
    unittest.main()
