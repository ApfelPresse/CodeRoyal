import random
import unittest

import numpy as np

from sprites.sprites import plot_current_frame, convert_to_gif
from original.ref import Referee, Vector2, Tower, Mine


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_mine_upgrade(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = True
        frames = []

        for i in range(1):
            print(f"Turn {i}")
            for player in ref.game_manager.active_players:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 2:
                        action = "BUILD 8 MINE"
                else:
                    if i <= 2:
                        action = "BUILD 7 MINE"

                player.outputs = [action, train]

            frames.append(plot_current_frame(ref))
            ref.game_turn(i)

        if plot:
            convert_to_gif("test_mine_upgrade", frames)

        for player in ref.game_manager.active_players:
            buildings = ref.get_buildings_of_player(player)
            self.assertEqual(1, len(buildings))
            for tower in buildings:
                struc = tower.structure
                if isinstance(struc, Mine):
                    self.assertEqual(1, struc.income_rate)

        ref.game_turn(0)

        for player in ref.game_manager.active_players:
            buildings = ref.get_buildings_of_player(player)
            self.assertEqual(1, len(buildings))
            for tower in buildings:
                struc = tower.structure
                if isinstance(struc, Mine):
                    self.assertEqual(2, struc.income_rate)

