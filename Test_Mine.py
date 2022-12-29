import random
import unittest

import numpy as np

from Ref import Referee
from structures import Mine


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_build_mine_max_rate_2(self):
        ref = Referee(params={
            "leagueLevel": 3
        })

        income = {
            "red": ref.gameManager.players[0].gold,
            "red_fixed": 128,
            "blue": ref.gameManager.players[0].gold,
            "blue_fixed": 123,
            "red_initial": 231,
            "blue_initial": 259,
        }

        for i in range(30):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                if player.name == "red":
                    action = "BUILD 2 MINE"
                    train = "TRAIN"
                else:
                    action = "BUILD 3 MINE"
                    train = "TRAIN"

                player.outputs = [action, train]
            ref.gameTurn(i)

            for player in ref.gameManager.activePlayers:
                buildings = ref.get_buildings_of_player(player)
                if len(buildings) > 0:
                    struc = buildings[0].structure
                    if isinstance(struc, Mine):
                        mine = struc
                        income[player.name] += mine.incomeRate
                    else:
                        ValueError("This should be a Mine")

        for player in ref.gameManager.activePlayers:
            assert income[player.name] == player.gold
            assert income[f"{player.name}_fixed"] == player.gold
            buildings = ref.get_buildings_of_player(player)
            assert income[f"{player.name}_initial"] - buildings[0].gold == player.gold - 100

    def test_build_mine_max_rate_1(self):
        ref = Referee(params={
            "leagueLevel": 3
        })

        income = {
            "red": ref.gameManager.players[0].gold,
            "blue": ref.gameManager.players[0].gold
        }

        for i in range(25):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                if player.name == "red":
                    action = "BUILD 2 MINE"
                    train = "TRAIN"
                else:
                    action = "BUILD 1 MINE"
                    train = "TRAIN"

                player.outputs = [action, train]
            ref.gameTurn(i)

            for player in ref.gameManager.activePlayers:
                buildings = ref.get_buildings_of_player(player)
                if len(buildings) > 0:
                    struc = buildings[0].structure
                    if isinstance(struc, Mine):
                        mine = struc
                        income[player.name] += mine.incomeRate
                    else:
                        ValueError("This should be a Mine")

        for player in ref.gameManager.activePlayers:
            assert income[player.name] == player.gold
            assert income[player.name] == 123

    def test_destroy_mine_when_field_has_no_gold_anymore(self):
        ref = Referee(params={
            "leagueLevel": 3
        })

        for i in range(233):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 MINE"
                    train = "TRAIN"
                else:
                    if i <= 3:
                        action = "BUILD 1 MINE"
                    train = "TRAIN"

                player.outputs = [action, train]
            ref.gameTurn(i)

            for player in ref.gameManager.activePlayers:
                if len(ref.get_buildings_of_player(player)) == 0:
                    break

        for player in ref.gameManager.activePlayers:
            assert len(ref.get_buildings_of_player(player)) == 0

        for obs in ref.obstacles[:2]:
            assert obs.gold == 0
