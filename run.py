import random

import numpy as np

from boss import handle_boss_3
from sprites.sprites import plot_current_frame, convert_to_gif
from original.ref import Referee, create_player_info
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
        from auto_profiler import Profiler
        with Profiler(depth=5):
            for i in range(ref.game_manager.max_turns):
                print(f"Round {i}")

                for j, player in enumerate(ref.game_manager.active_players):
                    last[player.name], player.outputs = players[player.name](last[player.name], create_player_info(player, ref))

                if plot and i % 2 == 0:
                    frames.append(plot_current_frame(ref, i))

                if i >= 1 and ref.game_end():
                    break

                ref.game_turn(i)

                if ref.end_game:
                    print("DEAD Queen")
                    break
    finally:
        if plot:
            convert_to_gif("test", frames)


if __name__ == '__main__':
    main()
