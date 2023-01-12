import random
import unittest

import numpy as np

from helper import plot_current_frame, convert_to_gif
from ref import Referee
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
        plot = False
        frames = []

        for i in range(23):
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

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        if plot:
            convert_to_gif("test_build_barracks_archer", frames)

        for player in ref.gameManager.activePlayers:
            assert len(player.activeCreeps) == 2
            assert player.gold == 0
            for creep in player.activeCreeps:
                assert creep.health < 50

        ref.gameTurn(0)
        for player in ref.gameManager.activePlayers:
            assert len(player.activeCreeps) == 1

        for _ in range(11):
            ref.gameTurn(0)

        for player in ref.gameManager.activePlayers:
            assert len(player.activeCreeps) == 0

    def test_build_barracks_knight(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

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

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        if plot:
            convert_to_gif("test_build_barracks_knight", frames)

        queen = {
            "blue": {
                "location": Vector2(172, 34),
                "health": 42,
                "gold": 20
            },
            "red": {
                "location": Vector2(1800, 861),
                "health": 41,
                "gold": 20
            }
        }
        for player in ref.gameManager.activePlayers:
            assert player.queenUnit.location == queen[player.name]["location"]
            assert player.queenUnit.health == queen[player.name]["health"]
            assert player.gold == queen[player.name]["gold"]


    def test_build_barracks_giant_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 2
        })
        plot = True
        frames = []

        for player in ref.gameManager.activePlayers:
            player.gold = 140

        for i in range(40):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 2 BARRACKS-GIANT"
                    if 3 < i < 15:
                        action = "BUILD 4 TOWER"

                    if i == 4:
                        train += " 2"
                else:
                    if i <= 3:
                        action = "BUILD 1 BARRACKS-GIANT"
                    if 3 < i < 14:
                        action = "BUILD 3 TOWER"
                    # if i == 4:
                    #     train += " 1"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.gameTurn(i)
            for player in ref.gameManager.activePlayers:
                buildings = ref.get_buildings_of_player(player)
                print(buildings)

        if plot:
            convert_to_gif("test_build_barracks_giant_and_tower", frames)

        for player in ref.gameManager.activePlayers:
            buildings = ref.get_buildings_of_player(player)
            assert player.gold == 0
            assert len(buildings) == 2

        ref.gameTurn(0)

        for player in ref.gameManager.activePlayers:
            buildings = ref.get_buildings_of_player(player)
            assert len(buildings) == 1

    def test_build_barracks_knight_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = True
        frames = []

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

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))

            ref.gameTurn(i)

        queen = {
            "blue": {
                "health": 60
            },
            "red": {
                "health": 62
            }
        }
        if plot:
            convert_to_gif("test_build_barracks_knight_and_tower", frames)

        for player in ref.gameManager.activePlayers:
            assert queen[player.name]["health"] == player.health
