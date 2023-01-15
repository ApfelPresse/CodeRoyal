import random
import unittest

import numpy as np

from helper import plot_current_frame, convert_to_gif
from original.ref import Referee, Tower

class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_tower_attacking_queen(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        for i in range(40):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                if player.name == "red":
                    action = "BUILD 17 TOWER"
                    train = "TRAIN"
                else:
                    action = "BUILD 18 TOWER"
                    train = "TRAIN"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))

            ref.game_turn(i)

        queen_health = {
            "red": 74,
            "blue": 74,
        }
        if plot:
            convert_to_gif("test_tower_attacking_queen", frames)

        for player in ref.gameManager.activePlayers:
            self.assertEqual(queen_health[player.name], player.queenUnit.health)

    def test_build_tower_once_and_wait_for_destroying(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        tower_health = {
            "red": [],
            "blue": [],
        }

        for i in range(140):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 8 TOWER"
                    train = "TRAIN"
                else:
                    if i <= 3:
                        action = "BUILD 7 TOWER"
                    train = "TRAIN"

                player.outputs = [action, train]

                buildings = ref.get_buildings_of_player(player)
                for tower in buildings:
                    struc = tower.structure
                    if isinstance(struc, Tower):
                        tower_health[player.name].append(struc.attackRadius)
                    else:
                        ValueError("Expected a Tower")
            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))

            ref.game_turn(i)

        if plot:
            convert_to_gif("test_build_tower_once_and_wait_for_destroying", frames)

        for player in ref.gameManager.activePlayers:
            self.assertEqual(88, tower_health[player.name][-1])
            self.assertEqual(124, len(tower_health[player.name]))
            buildings = ref.get_buildings_of_player(player)
            self.assertEqual(0, len(buildings))
