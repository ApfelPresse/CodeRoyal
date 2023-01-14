import random
import unittest

import numpy as np

from ref import Referee
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
            "red_fixed": 187,
            "blue": ref.gameManager.players[0].gold,
            "blue_fixed": 187,
        }

        for i in range(30):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                if player.name == "red":
                    action = "BUILD 8 MINE"
                    train = "TRAIN"
                else:
                    action = "BUILD 7 MINE"
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
            self.assertEqual(income[player.name], player.gold)
            self.assertEqual(income[f"{player.name}_fixed"], player.gold)

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
                    action = "BUILD 8 MINE"
                    train = "TRAIN"
                else:
                    action = "BUILD 7 MINE"
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
            self.assertEqual(income[player.name], player.gold)
            self.assertEqual(income[player.name], 172)

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
                        action = "BUILD 8 MINE"
                    train = "TRAIN"
                else:
                    if i <= 3:
                        action = "BUILD 7 MINE"
                    train = "TRAIN"

                player.outputs = [action, train]
            ref.gameTurn(i)

            for player in ref.gameManager.activePlayers:
                if len(ref.get_buildings_of_player(player)) == 0:
                    break

        for player in ref.gameManager.activePlayers:
            self.assertEqual(0, len(ref.get_buildings_of_player(player)))

        for obs in ref.obstacles:
            if obs.obstacleId == 8:
                self.assertEqual(0, obs.gold)
            if obs.obstacleId == 7:
                self.assertEqual(0, obs.gold)

