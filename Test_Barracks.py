import random
import unittest

import numpy as np

from ref import Referee
from structures import Tower
from run import convert_to_gif, plot_current_frame
from vector2 import Vector2


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_build_barracks_archer(self):
        ref = Referee(params={
            "leagueLevel": 3
        })

        for i in range(25):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 BARRACKS-ARCHER"
                    if i == 4:
                        train += " 2"
                else:
                    if i <= 3:
                        action = "BUILD 1 BARRACKS-ARCHER"
                    if i == 4:
                        train += " 1"

                player.outputs = [action, train]

            ref.gameTurn(i)

        for player in ref.gameManager.activePlayers:
            assert len(player.activeCreeps) == 2
            assert player.gold == 0
            for creep in player.activeCreeps:
                assert creep.health < 50

    def test_build_barracks_knight(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        # frames = []

        for i in range(35):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 BARRACKS-KNIGHT"
                    if i == 4:
                        train += " 2"
                else:
                    if i <= 3:
                        action = "BUILD 1 BARRACKS-KNIGHT"
                    if i == 4:
                        train += " 1"

                player.outputs = [action, train]

            # frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        queen = {
            "blue": {
                "location": Vector2(73, 30),
                "health": 44,
                "gold": 20
            },
            "red": {
                "location": Vector2(1783, 970),
                "health": 43,
                "gold": 20
            }
        }
        for player in ref.gameManager.activePlayers:
            assert player.queenUnit.location == queen[player.name]["location"]
            assert player.queenUnit.health == queen[player.name]["health"]
            assert player.gold == queen[player.name]["gold"]

        # convert_to_gif("test_move", frames)

    def test_build_barracks_giant_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        # frames = []

        for player in ref.gameManager.activePlayers:
            player.gold = 140

        for i in range(26):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 BARRACKS-GIANT"
                    if 3 < i < 15:
                        action = "BUILD 3 TOWER"

                    if i == 4:
                        train += " 2"
                else:
                    if i <= 3:
                        action = "BUILD 1 BARRACKS-GIANT"
                    if 3 < i < 15:
                        action = "BUILD 4 TOWER"
                    if i == 4:
                        train += " 1"

                player.outputs = [action, train]

            # frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        for player in ref.gameManager.activePlayers:
            buildings = ref.get_buildings_of_player(player)
            assert player.gold == 0
            assert len(buildings) == 2

        ref.gameTurn(0)

        for player in ref.gameManager.activePlayers:
            buildings = ref.get_buildings_of_player(player)
            assert len(buildings) == 1

        # convert_to_gif("test_move", frames)

    def test_build_barracks_knight_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        # frames = []

        for player in ref.gameManager.activePlayers:
            player.gold = 200

        for i in range(60):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 BARRACKS-KNIGHT"
                    if 3 < i < 20:
                        action = "BUILD 6 TOWER"

                    if i == 4 or i == 20:
                        train += " 2"
                else:
                    if i <= 3:
                        action = "BUILD 1 BARRACKS-KNIGHT"
                    if 3 < i < 20:
                        action = "BUILD 5 TOWER"
                    if i == 4 or i == 20:
                        train += " 1"

                player.outputs = [action, train]

            # if i % 3 == 0:
            #     frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        queen = {
            "blue": {
                "health": 60
            },
            "red": {
                "health": 62
            }
        }

        for player in ref.gameManager.activePlayers:
            assert queen[player.name]["health"] == player.health
        # convert_to_gif("test_move", frames)
