import random

import numpy as np

from boss import handle_boss_3
from helper import plot_current_frame, convert_to_gif
from ref import Referee, Obstacle


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
        "red": handle_boss_3,
        "blue": handle_boss_3,
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

            if i >= 1 and ref.game_end():
                break

            ref.gameTurn(i)

            # if i > 30:
            #     break
    finally:
        convert_to_gif("test", frames)
    # except Exception as ex:
    #     print(ex)


if __name__ == '__main__':
    main()
