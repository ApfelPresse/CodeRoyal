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
    fig.patch.set_facecolor('black')

    width = Constants.WORLD_WIDTH
    height = Constants.WORLD_HEIGHT

    ax.set_xlim((0, width))
    ax.set_ylim((0, height))
    ax.axis("equal")
    ax.axis('off')

    ax.add_patch(plt.Circle((width // 2, height // 2), 500, color="white", alpha=0, zorder=0))

    background = plt.imread(pathlib.Path(__file__).parent.joinpath("Background.jpg"))
    axin = ax.inset_axes([0, 0, background.shape[1], background.shape[0]], transform=ax.transData, zorder=1)
    axin.imshow(background)
    axin.axis('off')

    game_json = create_game_json()
    create_hud(ax, game_json, width, ref, scale)
    create_logo(ax, height, width)

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
            x = creep.location.x
            y = creep.location.y
            radius = creep.radius
            axin = ax.inset_axes([x - radius, y - radius, 2 * radius, 2 * radius], transform=ax.transData, zorder=4)
            if player.name == "red":
                axin.imshow(game_json["Unite_Base_Rouge"]["image"])
            else:
                axin.imshow(game_json["Unite_Base_Bleu"]["image"])
            axin.axis('off')

            axin = ax.inset_axes([x - radius, y - radius, 2 * radius, 2 * radius], transform=ax.transData, zorder=5)
            if creep.unit_type == 0:
                axin.imshow(game_json["Unite_Fantassin"]["image"])
            elif creep.unit_type == 1:
                axin.imshow(game_json["Unite_Archer"]["image"])
            elif creep.unit_type == 2:
                axin.imshow(game_json["Unite_Siege"]["image"])
            else:
                raise ValueError("Not known creep")
            axin.axis('off')

    for obstacle in ref.obstacles:
        radius = obstacle.radius
        x = obstacle.location.x
        y = obstacle.location.y
        text(x, y, obstacle.obstacle_id, fontsize=4 * scale, color="orange")
        axin = ax.inset_axes([x - radius, y - radius, radius * 2, radius * 2], transform=ax.transData, zorder=2)
        axin.axis('off')

        if isinstance(obstacle.structure, Tower):
            tower_idx = (frame % 15) + 1
            tower = game_json[f"T{obstacle.structure.owner.name[0].upper()}{tower_idx:02d}"]["image"]
            axin.imshow(tower)
            ax.add_patch(
                plt.Circle((x, y), obstacle.structure.attack_radius, color=obstacle.structure.owner.name, alpha=0.1,
                           zorder=100))

        if isinstance(obstacle.structure, Mine):
            text(x, y, f"{obstacle.obstacle_id} +{obstacle.structure.income_rate}/{obstacle.max_mine_size}",
                 fontsize=4*scale, color="orange")
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


def create_logo(ax, height, width):
    logo = plt.imread(pathlib.Path(__file__).parent.joinpath("logo.png"))
    axin = ax.inset_axes([width // 2 - logo.shape[1] // 2, height, logo.shape[1], logo.shape[0]],
                         transform=ax.transData, zorder=10)
    axin.imshow(logo)
    axin.axis('off')


def create_game_json():
    with open(pathlib.Path(__file__).parent.joinpath("game.json")) as file:
        game_json = json.loads(file.read())["frames"]
    game_image = Image.open(pathlib.Path(__file__).parent.joinpath("game.png"))
    for key in game_json.keys():
        item = game_json[key]["frame"]
        im = game_image.crop((item["x"], item["y"], item["x"] + item["w"], item["y"] + item["h"]))
        game_json[key]["image"] = im
        # im.save(f'spriteso/tmp/{key}.png')
    return game_json


def create_hud(ax, game_json, width, ref, scale):
    hud = plt.imread(pathlib.Path(__file__).parent.joinpath("Hud.png"))
    axin = ax.inset_axes([0, 0, width, 153], transform=ax.transData, zorder=10)
    axin.imshow(hud)
    axin.axis('off')

    axin = ax.inset_axes([10, 0, 130, 130], transform=ax.transData, zorder=14)
    axin.imshow(game_json["Unite_Reine"]["image"])
    axin.axis('off')

    axin = ax.inset_axes([0, 0, 150, 150], transform=ax.transData, zorder=12)
    axin.imshow(game_json["Unite_Base_Bleu"]["image"])
    axin.axis('off')

    axin = ax.inset_axes([width - 10 - 130, 0, 130, 130], transform=ax.transData, zorder=14)
    axin.imshow(game_json["Unite_Reine"]["image"])
    axin.axis('off')

    axin = ax.inset_axes([width - 150, 0, 150, 150], transform=ax.transData, zorder=12)
    axin.imshow(game_json["Unite_Base_Rouge"]["image"])
    axin.axis('off')

    queen_hp = ref.queen_hp
    for player in ref.game_manager.players:
        perc = ((100 / queen_hp) * player.queen_unit.health) / 100
        if player.name == "blue":
            text((width // 2) - 250, 30, player.gold, fontsize=5 * scale, color="white", zorder=12)
            text(145, 15, player.queen_unit.health, fontsize=4 * scale, color="white", zorder=13)
            life_image = game_json["Life-Bleu"]["image"]
            axin = ax.inset_axes([145, life_image.size[1] // 2, life_image.size[0] * perc, life_image.size[1] * 0.92],
                                 transform=ax.transData, zorder=12)
        else:
            text((width // 2) + 180, 30, player.gold, fontsize=5 * scale, color="white", zorder=12)
            text(width - 560, 15, player.queen_unit.health, fontsize=4 * scale, color="white", zorder=13)
            life_image = game_json["Life-Rouge"]["image"]
            axin = ax.inset_axes(
                [width - 560, life_image.size[1] // 2, life_image.size[0] * perc, life_image.size[1] * 0.92],
                transform=ax.transData, zorder=12)

        axin.imshow(life_image, aspect="auto")
        axin.axis('off')


def convert_to_gif(name: str, frames: list):
    file_name = f'./gifs/{name}.gif'
    imageio.mimsave(file_name, frames, fps=3)
    print(file_name)
