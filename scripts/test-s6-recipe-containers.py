#!/usr/bin/env python3
"""Boundary and mutation tests for the bounded container audit."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('containers',
    Path(__file__).with_name('audit-s6-recipe-containers.py'))
containers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(containers)
mapper = containers.load_mapper()
JEWEL = 7181
STACK = 6688


def definition(group, number, durability=1, width=1, height=1):
    return dict(Group=group, Number=number, Durability=durability,
                Width=width, Height=height, ItemSlotId=None)


def requirement(key, minimum, maximum):
    return dict(possible_items=[dict(client_id=key)], MinimumAmount=minimum,
                MaximumAmount=maximum, MinimumItemLevel=0, MaximumItemLevel=0)


def source(key, count, durability=(0, 255)):
    return dict(TypeMin=key, TypeMax=key, LevelMin=0, LevelMax=255,
                CountMin=1, CountMax=count, DurabilityMin=durability[0],
                DurabilityMax=durability[1])


class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.items = {JEWEL: definition(14, 13), STACK: definition(13, 32, 20)}

    def test_jewel_25_matches(self):
        inventory = [containers.inventory_item(JEWEL) for _ in range(25)]
        self.assertTrue(containers.client_accepts([source(JEWEL, 25)], inventory, self.items, mapper))
        self.assertTrue(containers.server_accepts([requirement(JEWEL, 1, 0)], inventory, self.items, mapper))

    def test_jewel_26_is_reachable_policy_difference(self):
        inventory = [containers.inventory_item(JEWEL) for _ in range(26)]
        self.assertIsNotNone(containers.place(inventory, self.items))
        self.assertTrue(all(containers.client_source_matches(source(JEWEL, 25), i) for i in inventory))
        self.assertFalse(containers.client_accepts([source(JEWEL, 25)], inventory, self.items, mapper))
        self.assertTrue(containers.server_accepts([requirement(JEWEL, 1, 0)], inventory, self.items, mapper))

    def test_grid_boundary(self):
        self.assertIsNotNone(containers.place([containers.inventory_item(JEWEL)] * 32, self.items))
        self.assertIsNone(containers.place([containers.inventory_item(JEWEL)] * 33, self.items))

    def test_footprint_mutation(self):
        self.items[JEWEL]['Height'] = 2
        self.assertIsNone(containers.place([containers.inventory_item(JEWEL)] * 26, self.items))

    def test_full_stack_matches(self):
        inventory = [containers.inventory_item(STACK, 20)]
        self.assertTrue(containers.client_accepts([source(STACK, 1, (20, 20))], inventory, self.items, mapper))
        self.assertTrue(containers.server_accepts([requirement(STACK, 20, 20)], inventory, self.items, mapper))

    def test_fragmented_stack_only_server_accepts(self):
        inventory = [containers.inventory_item(STACK, 10), containers.inventory_item(STACK, 10)]
        self.assertFalse(containers.client_source_matches(source(STACK, 1, (20, 20)), inventory[0]))
        self.assertFalse(containers.client_accepts([source(STACK, 1, (20, 20))], inventory, self.items, mapper))
        self.assertTrue(containers.server_accepts([requirement(STACK, 20, 20)], inventory, self.items, mapper))

    def test_wrong_total_rejected(self):
        self.assertFalse(containers.server_accepts([requirement(STACK, 20, 20)],
            [containers.inventory_item(STACK, 19)], self.items, mapper))

    def test_extra_item_rejected(self):
        self.assertFalse(containers.server_accepts([requirement(STACK, 20, 20)],
            [containers.inventory_item(STACK, 20), containers.inventory_item(JEWEL)], self.items, mapper))

    def test_level_mutation_rejected(self):
        item = containers.inventory_item(STACK, 20)
        item['level'] = 1
        self.assertFalse(containers.server_accepts([requirement(STACK, 20, 20)], [item], self.items, mapper))

    def test_server_bound_mutation_changes_policy(self):
        self.assertFalse(containers.server_accepts([requirement(JEWEL, 1, 25)],
            [containers.inventory_item(JEWEL)] * 26, self.items, mapper))


if __name__ == '__main__':
    unittest.main()
