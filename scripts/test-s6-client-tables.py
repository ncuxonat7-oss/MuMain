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


if __name__ == '__main__':
    unittest.main()
