import random
import unittest

import numpy as np

from Ref import Referee
from structures import Tower
from test_main import convert_to_gif, plot_current_frame
from vector2 import Vector2


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_build_tower_once_and_wait_for_destroying(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        # frames = []

        tower_health = {
            "red": [],
            "blue": [],
        }

        for i in range(90):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 TOWER"
                    train = "TRAIN"
                else:
                    if i <= 3:
                        action = "BUILD 1 TOWER"
                    train = "TRAIN"

                player.outputs = [action, train]

                buildings = ref.get_buildings_of_player(player)
                for tower in buildings:
                    struc = tower.structure
                    if isinstance(struc, Tower):
                        tower_health[player.name].append(struc.attackRadius)
                    else:
                        ValueError("Expected a Tower")
            # frames.append(plot_current_frame(ref))

            ref.gameTurn(i)
        for player in ref.gameManager.activePlayers:
            assert tower_health[player.name][-1] == 91
            assert len(tower_health[player.name]) == 74
            buildings = ref.get_buildings_of_player(player)
            assert len(buildings) == 0

        # convert_to_gif("test_move", frames)
