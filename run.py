import random
from typing import Optional

import numpy as np

from boss import handle_boss_3
from sprites.sprites import plot_current_frame, convert_to_gif
from optimized.ref import Referee, Obstacle
from util import timeit


@timeit
def main():
    seed_value = 6
    random.seed(seed_value)
    np.random.seed(seed_value)

    params = {
        "leagueLevel": 3
    }
    ref = Referee(params)

    plot = False
    frames = []

    players = {
        "red": handle_boss_3,
        "blue": handle_boss_3,
    }
    last = {
        "red": {},
        "blue": {}
    }
    try:
        for i in range(ref.game_manager.max_turns):
            print(f"Round {i}")

            for j, player in enumerate(ref.game_manager.active_players):
                obs_for_player = []
                touching_side: Optional[Obstacle] = None
                for obs in ref.obstacles:
                    if player.queen_unit.is_in_range_of(obs):
                        touching_side = obs
                    obs_for_player.append(player.print_obstacle_per_turn(obs))

                units = list(map(lambda item: {
                    "x": item.location.x,
                    "y": item.location.y,
                    "owner": player.fix_owner(item.owner),
                    "type": item.unit_type,
                    "health": item.health,
                }, ref.all_units()))
                info = {
                    "gold": player.gold,
                    "queen_touching": touching_side.obstacle_id if touching_side is not None else -1,
                    "obstacles": obs_for_player,
                    "units": units
                }

                _last, player.outputs = players[player.name](last[player.name], info)
                last[player.name] = _last

            if plot and i % 2 == 0:
                frames.append(plot_current_frame(ref, i))

            if i >= 1 and ref.game_end():
                break

            ref.game_turn(i)
    finally:
        if plot:
            convert_to_gif("test", frames)


if __name__ == '__main__':
    main()
