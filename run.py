import random

import imageio
import numpy as np
from matplotlib import pyplot as plt

from ref import Referee
from constants import Constants
from structures import Tower, Mine, Barracks


def plot_current_frame(ref):
    scale = 2
    fig, ax = plt.subplots(figsize=(4 * scale, 3 * scale))

    height = Constants.WORLD_HEIGHT + Constants.WORLD_HEIGHT / 2
    width = Constants.WORLD_WIDTH

    ax.set_xlim((0, width))
    ax.set_ylim((0, height))

    image = plt.imread("sprites/hintergrund.png")
    axin = ax.inset_axes([-width / 2, -height / 2, width * 2, height * 2], transform=ax.transData, zorder=0)
    axin.imshow(image)
    axin.axis('off')

    ax.axis('off')

    sprite_gelaende_1 = plt.imread("sprites/sprite_gelaende_1.png")
    queen_blue = plt.imread("sprites/queen_blue.png")
    queen_red = plt.imread("sprites/queen_red.png")
    tower = plt.imread("sprites/tower.png")
    mine = plt.imread("sprites/mine.png")
    barracks = plt.imread("sprites/barracks.png")

    for obstacle in ref.obstacles:
        c = "b"
        if obstacle.structure is not None:
            c = "y"

        width = 120
        axin = ax.inset_axes([obstacle.location.x - width / 2, obstacle.location.y - width / 2, width, width],
                             transform=ax.transData, zorder=1)
        axin.imshow(sprite_gelaende_1)
        axin.axis('off')

        ax.add_patch(plt.Circle((obstacle.location.x, obstacle.location.y), 20, color=c, alpha=0.8))

    for i, player in enumerate(ref.gameManager.players):
        width = 80
        x = player.queenUnit.location.x
        y = player.queenUnit.location.y
        axin = ax.inset_axes([x - width / 2, y - width / 2, width, width], transform=ax.transData, zorder=5)
        if i == 0:
            axin.imshow(queen_blue)
        else:
            axin.imshow(queen_red)
        axin.axis('off')

        for creep in player.activeCreeps:
            ax.add_patch(
                plt.Circle((creep.location.x, creep.location.y), 15, color=player.name, alpha=0.9, zorder=6))

    for obstacle in ref.obstacles:
        width = 120
        x = obstacle.location.x
        y = obstacle.location.y
        axin = ax.inset_axes([x - width / 2, y - width / 2, width, width], transform=ax.transData, zorder=2)

        if isinstance(obstacle.structure, Tower):
            axin.imshow(tower)
            ax.add_patch(
                plt.Circle((x, y), obstacle.structure.attackRadius, color=obstacle.structure.owner.name, alpha=0.2,
                           zorder=100))
        if isinstance(obstacle.structure, Mine):
            axin.imshow(mine)

        if isinstance(obstacle.structure, Barracks):
            axin.imshow(barracks)

        axin.axis('off')

    player_stats = []
    for i, player in enumerate(ref.gameManager.players):
        player_stats.append([])
        player_stats[i].append(f"Player {i}")
        player_stats[i].append(player.gold)
        player_stats[i].append(player.queenUnit.health)

    player_stats_zip = list(map(lambda items: "-".join(map(str, items)), zip(*player_stats)))

    msg = "\n".join([f"Gameturn {ref.turn}"] + player_stats_zip)
    ax.text(0, height - height / 4, msg, fontsize=10, bbox={'facecolor': 'white', 'alpha': 0, 'pad': 5})

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    plt.close()
    return image


def convert_to_gif(name: str, frames: list):
    file_name = f'./{name}.gif'
    imageio.mimsave(file_name, frames, fps=3)
    print(file_name)


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
