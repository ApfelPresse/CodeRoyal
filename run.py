import random

import numpy as np

from helper import plot_current_frame, convert_to_gif
from ref import Referee
from structures import Obstacle

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

            # for player in self.gameManager.players:
            #     ent.extend(player.allUnits())

            for j, player in enumerate(ref.gameManager.activePlayers):

                obs_for_player = []
                touching_side: Obstacle = None
                for obs in ref.obstacles:
                    if player.queenUnit.is_in_range_of(obs):
                        touching_side = obs
                    obs_for_player.append(player.printObstaclePerTurn(obs))

                units = list(map(lambda item: {
                    "x": item.location.x,
                    "y": item.location.y,
                    "owner": player.fixOwner(item.owner),
                    "unit_type": item.unit_type,
                    "health": item.health,
                }, ref.all_units()))
                # ref.
                info = {
                    "gold": player.gold,
                    "queen_touching": touching_side.obstacleId if touching_side is not None else -1,
                    "obstacles": obs_for_player,
                    "units": []
                }

                if j == 0:
                    side = 1
                else:
                    side = 4

                b = f"BUILD {side} TOWER"
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

            if i % 2 == 0:
                frames.append(plot_current_frame(ref, i))

            if i > 10:
                break
            ref.gameTurn(i)
    finally:
        convert_to_gif("test", frames)
    # except Exception as ex:
    #     print(ex)
