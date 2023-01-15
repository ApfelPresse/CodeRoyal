import random
import unittest

import numpy as np

from helper import plot_current_frame, convert_to_gif
from ref import Referee, Vector2


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_simple_move(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        for i in range(12):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                player.outputs = [
                    f"MOVE 500 500",
                    "TRAIN",
                ]

                print(f"{player.name} - {player.queenUnit.location}")
            print("---")
            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        if plot:
            convert_to_gif("test_simple_move", frames)

        self.assertEqual(Vector2(500, 500), ref.gameManager.players[0].queenUnit.location)

    def test_simple_collision_move(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        plot = False
        frames = []

        for i in range(25):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                player.outputs = [
                    f"MOVE 500 500",
                    "TRAIN",
                ]

                print(f"{player.name} - {player.queenUnit.location}")
            print("---")
            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        if plot:
            convert_to_gif("test_simple_collision_move", frames)

        self.assertEqual(Vector2(475, 496), ref.gameManager.players[0].queenUnit.location)
        self.assertEqual(Vector2(505, 501), ref.gameManager.players[1].queenUnit.location)
