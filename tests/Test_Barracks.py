import random
import unittest

import numpy as np

from sprites.sprites import plot_current_frame, convert_to_gif
from original.ref import Referee, Vector2


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

        for i in range(27):
            print(f"Turn {i}")
            for player in ref.game_manager.active_players:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 2:
                        action = "BUILD 8 BARRACKS-ARCHER"
                    if i == 3:
                        train += " 8"
                else:
                    if i <= 2:
                        action = "BUILD 7 BARRACKS-ARCHER"
                    if i == 3:
                        train += " 7"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.game_turn(i)

        if plot:
            convert_to_gif("test_build_barracks_archer", frames)

        for player in ref.game_manager.active_players:
            self.assertEqual(len(player.active_creeps), 2)
            self.assertEqual(len(player.active_creeps), 2)
            self.assertEqual(player.gold, 0)
            for creep in player.active_creeps:
                self.assertLess(creep.health, 50)

        ref.game_turn(0)
        ref.game_turn(0)
        for player in ref.game_manager.active_players:
            self.assertEqual(len(player.active_creeps), 1)

        for _ in range(11):
            ref.game_turn(0)

        for player in ref.game_manager.active_players:
            self.assertEqual(len(player.active_creeps), 0)

    def test_build_barracks_knight(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        for i in range(35):
            print(f"Turn {i}")
            for player in ref.game_manager.active_players:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 8 BARRACKS-KNIGHT"
                    if i == 4:
                        train += " 8"
                else:
                    if i <= 3:
                        action = "BUILD 7 BARRACKS-KNIGHT"
                    if i == 4:
                        train += " 7"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.game_turn(i)

        if plot:
            convert_to_gif("test_build_barracks_knight", frames)

        queen = {
            "blue": {
                "location": Vector2(249, 82),
                "health": 54,
                "gold": 20
            },
            "red": {
                "location": Vector2(1711, 970),
                "health": 53,
                "gold": 20
            }
        }
        for player in ref.game_manager.active_players:
            self.assertEqual(queen[player.name]["location"], player.queen_unit.location)
            self.assertEqual(queen[player.name]["health"], player.queen_unit.health)
            self.assertEqual(queen[player.name]["gold"], player.gold)

    def test_build_barracks_giant_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 2
        })
        plot = False
        frames = []

        for player in ref.game_manager.active_players:
            player.gold = 140

        for i in range(14):
            print(f"Turn {i}")
            for player in ref.game_manager.active_players:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 8 BARRACKS-GIANT"
                    if 3 < i < 15:
                        action = "BUILD 13 TOWER"
                    if i == 4:
                        train += " 8"
                else:
                    if i <= 3:
                        action = "BUILD 7 BARRACKS-GIANT"
                    if 3 < i < 20:
                        action = "BUILD 14 TOWER"
                    if i == 4:
                        train += " 7"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.game_turn(i)

        if plot:
            convert_to_gif("test_build_barracks_giant_and_tower", frames)

        for player in ref.game_manager.active_players:
            buildings = ref.get_buildings_of_player(player)
            self.assertEqual(2, len(buildings))

        for i in range(28):
            ref.game_turn(0)

        for player in ref.game_manager.active_players:
            buildings = ref.get_buildings_of_player(player)
            self.assertEqual(1, len(buildings))

    def test_build_barracks_knight_and_tower(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        for player in ref.game_manager.active_players:
            player.gold = 200

        for i in range(60):
            print(f"Turn {i}")
            for player in ref.game_manager.active_players:
                action = "WAIT"
                train = "TRAIN"
                if player.name == "red":
                    if i <= 3:
                        action = "BUILD 8 BARRACKS-KNIGHT"
                    if 3 < i < 20:
                        action = "BUILD 13 TOWER"
                    if i == 4 or i == 20:
                        train += " 8"
                else:
                    if i <= 3:
                        action = "BUILD 7 BARRACKS-KNIGHT"
                    if 3 < i < 20:
                        action = "BUILD 14 TOWER"
                    if i == 4 or i == 20:
                        train += " 7"

                player.outputs = [action, train]

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))

            ref.game_turn(i)

        queen = {
            "blue": {
                "health": 70
            },
            "red": {
                "health": 70
            }
        }
        if plot:
            convert_to_gif("test_build_barracks_knight_and_tower", frames)

        for player in ref.game_manager.active_players:
            self.assertEqual(queen[player.name]["health"], player.health)
