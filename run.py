import math
import random

import numpy as np

from helper import plot_current_frame, convert_to_gif
from ref import Referee
from structures import Obstacle


def handle_boss_1(last, game_info):
    queen = ()
    for unit in game_info["units"]:
        if unit["type"] == -1 and unit["owner"] == 0:
            queen = (unit["x"], unit["y"])

    min_dist = None
    barracks = None
    for obs in game_info["obstacles"]:
        dist = math.sqrt((queen[0] - obs["x"]) ** 2 + (queen[1] - obs["y"]) ** 2)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            barracks = obs

    action = "WAIT"
    if barracks["type"] == -1:
        action = f"BUILD {barracks['id']} BARRACKS-KNIGHT"

    if "count" not in last:
        count = 0
    else:
        count = last["count"]

    count += 1
    train = "TRAIN"
    if count == 12:
        count = 0
        if barracks["type"] == 2:
            train = f"{train} {barracks['id']}"

    last["count"] = count

    return last, [
        action,
        train
    ]

def main():
    seed_value = 6
    random.seed(seed_value)
    np.random.seed(seed_value)

    params = {
        "leagueLevel": 3
    }
    ref = Referee(params)

    frames = []
    tix = 20

    players = {
        "red": handle_boss_1,
        "blue": handle_boss_1,
    }
    last = {
        "red": {},
        "blue": {}
    }
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
                    "type": item.unit_type,
                    "health": item.health,
                }, ref.all_units()))
                info = {
                    "gold": player.gold,
                    "queen_touching": touching_side.obstacleId if touching_side is not None else -1,
                    "obstacles": obs_for_player,
                    "units": units
                }

                _last, player.outputs = players[player.name](last[player.name], info)
                last[player.name] = _last


            if i % 2 == 0:
                frames.append(plot_current_frame(ref, i))

            # if i > 30:
            #     break
            ref.gameTurn(i)
    finally:
        convert_to_gif("test", frames)
    # except Exception as ex:
    #     print(ex)


if __name__ == '__main__':
    main()
