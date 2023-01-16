import json
import pathlib

import imageio
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.pyplot import text

from original.ref import Constants, Tower, Mine, Barracks


def read_image(image_file_name):
    try:
        return plt.imread(image_file_name)
    except FileNotFoundError as ex:
        return plt.imread(f"../{image_file_name}")


def plot_current_frame(ref, frame=0):
    scale = 4
    fig, ax = plt.subplots(figsize=(4 * scale, 3 * scale))

    width = Constants.WORLD_WIDTH
    height = Constants.WORLD_HEIGHT

    ax.set_xlim((0, width))
    ax.set_ylim((0, height))
    ax.axis("equal")
    ax.axis('off')

    ax.add_patch(plt.Circle((width // 2, height // 2), 500, color="white", alpha=0, zorder=0))

    background = plt.imread(pathlib.Path(__file__).parent.joinpath("Background.jpg"))
    axin = ax.inset_axes([0, 0, width, height], transform=ax.transData, zorder=1)
    axin.imshow(background)
    axin.axis('off')

    with open(pathlib.Path(__file__).parent.joinpath("game.json")) as file:
        game_json = json.loads(file.read())["frames"]

    game_image = Image.open(pathlib.Path(__file__).parent.joinpath("game.png"))
    for key in game_json.keys():
        item = game_json[key]["frame"]
        im = game_image.crop((item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"]))
        game_json[key]["image"] = im
        # im.save(f'spriteso/tmp/{key}.png')

    for i, player in enumerate(ref.game_manager.players):
        width = 80
        x = player.queen_unit.location.x
        y = player.queen_unit.location.y

        axin = ax.inset_axes([x - width / 2, y - width / 2, width, width], transform=ax.transData, zorder=5)
        axin.imshow(game_json["Unite_Reine"]["image"])
        axin.axis('off')
        ax.add_patch(
            plt.Circle((x, y), player.queen_unit.radius, color=player.name, alpha=0.6, zorder=4))

        for creep in player.active_creeps:
            ax.add_patch(
                plt.Circle((creep.location.x, creep.location.y), creep.radius, color=player.name, alpha=0.9, zorder=6))

    for obstacle in ref.obstacles:
        width = obstacle.radius * 1.5
        x = obstacle.location.x
        y = obstacle.location.y
        text(x, y, obstacle.obstacle_id, fontsize=15)
        axin = ax.inset_axes([x - width / 2, y - width / 2, width, width], transform=ax.transData, zorder=2)
        axin.axis('off')

        if isinstance(obstacle.structure, Tower):
            tower_idx = (frame % 15) + 1
            tower = game_json[f"T{obstacle.structure.owner.name[0].upper()}{tower_idx:02d}"]["image"]
            axin.imshow(tower)
            ax.add_patch(
                plt.Circle((x, y), obstacle.structure.attack_radius, color=obstacle.structure.owner.name, alpha=0.1,
                           zorder=100))

        if isinstance(obstacle.structure, Mine):
            text(x, y, f"{obstacle.obstacle_id} +{obstacle.structure.income_rate}/{obstacle.max_mine_size}", fontsize=15)
            axin.imshow(game_json["Mine"]["image"])

        if isinstance(obstacle.structure, Barracks):
            if obstacle.structure.owner.name == "red":
                axin.imshow(game_json["Caserne_Rouge"]["image"])
            else:
                axin.imshow(game_json["Caserne_Bleu"]["image"])

        if obstacle.structure is None:
            axin.imshow(game_json[f"LC_{obstacle.obstacle_tile_id}"]["image"])

        ax.add_patch(
            plt.Circle((x, y), obstacle.radius, color="b", alpha=0.9, zorder=1))

    player_stats = []
    for i, player in enumerate(ref.game_manager.players):
        player_stats.append([])
        player_stats[i].append(f"Player {i}")
        player_stats[i].append(player.gold)
        player_stats[i].append(player.queen_unit.health)

    player_stats_zip = list(map(lambda items: "-".join(map(str, items)), zip(*player_stats)))

    msg = "\n".join([f"Gameturn {ref.turn}"] + player_stats_zip)
    ax.text(width / 2, height, msg, fontsize=10, bbox={'facecolor': 'white', 'alpha': 0, 'pad': 5})

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    plt.close()
    return image


def convert_to_gif(name: str, frames: list):
    file_name = f'./gifs/{name}.gif'
    imageio.mimsave(file_name, frames, fps=3)
    print(file_name)