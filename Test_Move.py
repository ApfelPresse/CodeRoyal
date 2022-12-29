import random
import unittest

import numpy as np

from Ref import Referee
from vector2 import Vector2


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_simple_move(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        frames = []

        for i in range(6):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                player.outputs = [
                    f"MOVE 500 500",
                    "TRAIN",
                ]

                print(f"{player.name} - {player.queenUnit.location}")
            print("---")
            # frames.append(plot_current_frame(ref))
            ref.gameTurn(i)

        # convert_to_gif("test_move", frames)

        assert ref.gameManager.players[0].queenUnit.location == Vector2(500, 500)

    def test_simple_collision_move(self):
        ref = Referee(params={
            "leagueLevel": 3
        })

        for i in range(25):
            print(f"Turn {i}")
            for player in ref.gameManager.activePlayers:
                player.outputs = [
                    f"MOVE 500 500",
                    "TRAIN",
                ]

                print(f"{player.name} - {player.queenUnit.location}")
            print("---")
            ref.gameTurn(i)

        assert ref.gameManager.players[0].queenUnit.location == Vector2(485, 501)
        assert ref.gameManager.players[1].queenUnit.location == Vector2(505, 500)

