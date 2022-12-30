import random

import numpy as np

from helper import plot_current_frame, convert_to_gif
from ref import Referee

if __name__ == '__main__':

    seed_value = 6
    random.seed(seed_value)
    np.random.seed(seed_value)

    params = {
        "leagueLevel": 3
    }
    ref = Referee(params)

    frames = []
    tix = 20
    try:
        for i in range(ref.gameManager.maxTurns):
            print(f"Round {i}")
            for j, player in enumerate(ref.gameManager.activePlayers):
                if j == 0:
                    side = 1
                else:
                    side = 4

                b = f"MOVE 500 500"
                t = "TRAIN"

                # if i <= tix:
                #     b = f"BUILD {side} BARRACKS-KNIGHT"

                # if i == tix + 2:
                #     t += f" {side}"
                #     b =
                #
                # if i == tix + 2:
                #     b = "WAIT"
                #     t += f" {side}"

                player.outputs = [
                    b,
                    t,
                ]

            if i > 0 and i % 2 == 0:
                frames.append(plot_current_frame(ref))

            if i == 30:
                break
            ref.gameTurn(i)
    finally:
        convert_to_gif("test", frames)
    # except Exception as ex:
    #     print(ex)
