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


class convert_to_dot_notation(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def create_plot_config(ref):
    config = {
        "frames": [],
        "old_state": {},
        "ref": ref
    }
    return convert_to_dot_notation(config)


def plot_current_frame(config, frame=0):
    ref = config.ref

    if not "obstacles" in config.old_state:
        config.old_state["obstacles"] = {}

    if not "destroyed" in config.old_state:
        config.old_state["destroyed"] = {}

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
    destruction_json = create_destruction_json()
    create_hud(ax, game_json, width, ref, scale)
    create_logo(ax, height, width)

    for i, player in enumerate(ref.game_manager.players):
        unit_width = 80
        x = player.queen_unit.location.x
        y = player.queen_unit.location.y

        axin = ax.inset_axes([x - unit_width / 2, y - unit_width / 2, unit_width, unit_width], transform=ax.transData,
                             zorder=5)
        axin.imshow(game_json["Unite_Reine"]["image"])
        axin.axis('off')

        unite_base_width = unit_width - 20
        axin = ax.inset_axes([x - unite_base_width / 2, y - unite_base_width / 2, unite_base_width, unite_base_width],
                             transform=ax.transData, zorder=4)
        if player.name == "red":
            axin.imshow(game_json["Unite_Base_Rouge"]["image"])
        else:
            axin.imshow(game_json["Unite_Base_Bleu"]["image"])
        axin.axis('off')

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

        if obstacle.obstacle_id in config.old_state["obstacles"] and config.old_state["obstacles"][
            obstacle.obstacle_id]:
            if obstacle.structure is None:
                config.old_state["destroyed"][obstacle.obstacle_id] = True

        if obstacle.obstacle_id in config.old_state["destroyed"]:
            axin.imshow(game_json[f"LieuDetruit"]["image"])
        elif isinstance(obstacle.structure, Tower):
            tower_idx = (frame % 15) + 1
            tower = game_json[f"T{obstacle.structure.owner.name[0].upper()}{tower_idx:02d}"]["image"]
            axin.imshow(tower)
            ax.add_patch(
                plt.Circle((x, y), obstacle.structure.attack_radius, color=obstacle.structure.owner.name, alpha=0.1,
                           zorder=100))
        elif isinstance(obstacle.structure, Mine):
            text(x, y, f"{obstacle.obstacle_id} +{obstacle.structure.income_rate}/{obstacle.max_mine_size}",
                 fontsize=4 * scale, color="orange")
            axin.imshow(game_json["Mine"]["image"])
        elif isinstance(obstacle.structure, Barracks):
            if obstacle.structure.owner.name == "red":
                axin.imshow(game_json["Caserne_Rouge"]["image"])
            else:
                axin.imshow(game_json["Caserne_Bleu"]["image"])
        else:
            axin.imshow(game_json[f"LC_{obstacle.obstacle_tile_id}"]["image"])

        config.old_state["obstacles"][obstacle.obstacle_id] = obstacle.structure is not None

    create_log(ax, ref, scale, width)

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    plt.close()
    config.frames.append(image)


def create_log(ax, ref, scale, width):
    player_stats_red = []
    player_stats_blue = []
    for player in ref.game_manager.players:
        if player.name == "red":
            player_stats = player_stats_red
        else:
            player_stats = player_stats_blue

        player_stats.append(f"Gold {player.gold}")
        player_stats.append(f"Health {player.queen_unit.health}")
        player_stats.extend(player.outputs)

    w = 45
    msg = "\n".join([f"Gameturn {ref.turn} blue"] + player_stats_blue)
    ax.text(0, -(len(player_stats_blue) * w), msg, fontsize=4 * scale, color="white",
            bbox={'facecolor': 'white', 'alpha': 0, 'pad': 5})

    msg = "\n".join([f"Gameturn {ref.turn} red"] + player_stats_red)
    ax.text(width / 2, -(len(player_stats_red) * w), msg, fontsize=4 * scale, color="white",
            bbox={'facecolor': 'white', 'alpha': 0, 'pad': 5})


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


def create_destruction_json():
    with open(pathlib.Path(__file__).parent.joinpath("destruction.json")) as file:
        game_json = json.loads(file.read())["frames"]
    game_image = Image.open(pathlib.Path(__file__).parent.joinpath("destruction.png"))
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

    income_blue = 0
    income_red = 0
    for obs in ref.obstacles:
        if isinstance(obs.structure, Mine):
            mine = obs.structure
            if mine.owner.name == "blue":
                income_blue += mine.income_rate
            else:
                income_red += mine.income_rate

    queen_hp = ref.queen_hp
    for player in ref.game_manager.players:
        perc = ((100 / queen_hp) * player.queen_unit.health) / 100

        if player.name == "blue":
            label = f"{player.gold}+{income_blue}"
            label_length = "".join([" "] * (9 - len(label)))
            label = f"{player.gold}{label_length}+{income_blue}"

            text((width // 2) - 250, 30, label, fontsize=5 * scale, color="white", zorder=12)
            text(145, 15, player.queen_unit.health, fontsize=4 * scale, color="white", zorder=13)
            life_image = game_json["Life-Bleu"]["image"]
            axin = ax.inset_axes([145, life_image.size[1] // 2, life_image.size[0] * perc, life_image.size[1] * 0.92],
                                 transform=ax.transData, zorder=12)
        else:
            text((width // 2) + 60, 30, f"{income_red}+    {player.gold}", fontsize=5 * scale, color="white", zorder=12)
            text(width - 220, 15, player.queen_unit.health, fontsize=4 * scale, color="white", zorder=13)
            life_image = game_json["Life-Rouge"]["image"]
            axin = ax.inset_axes(
                [width - 560, life_image.size[1] // 2, life_image.size[0] * perc, life_image.size[1] * 0.92],
                transform=ax.transData, zorder=12)

        axin.imshow(life_image, aspect="auto")
        axin.axis('off')


def convert_to_gif(name: str, config):
    frames = config.frames
    file_name = f'./gifs/{name}.gif'
    imageio.mimsave(file_name, frames, fps=3)
    print(file_name)
