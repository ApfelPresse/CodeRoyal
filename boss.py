import math


def get_value(last: dict, key: str, default):
    if key in last:
        return last[key]
    return default


def distance_between(o1: tuple, o2: tuple):
    return math.sqrt((o1[0] - o2[0]) ** 2 + (o1[1] - o2[1]) ** 2)


def handle_boss_4(last, game_info):
    income = 0
    for obs in game_info["obstacles"]:
        if obs["type"] == 0 and obs["owner"] == 0:
            income += obs["income_rate"]

    queen = ()
    for unit in game_info["units"]:
        if unit["type"] == -1 and unit["owner"] == 0:
            queen = (unit["x"], unit["y"])

    barracks = get_value(last, "barracks", None)
    if barracks is None:
        min_dist = None
        for obs in game_info["obstacles"]:
            dist = distance_between(queen, (obs["x"], obs["y"]))
            if min_dist is None or dist < min_dist:
                min_dist = dist
                barracks = obs
    barracks = list(filter(lambda item: item["id"] == barracks["id"], game_info["obstacles"]))[0]

    action = "WAIT"
    if barracks["type"] == -1:
        action = f"BUILD {barracks['id']} BARRACKS-KNIGHT"
    elif income < 10:
        min_dist = None
        target = None
        for obs in game_info["obstacles"]:
            dist = distance_between((barracks["x"], barracks["y"]), (obs["x"], obs["y"]))
            if (min_dist is None or dist < min_dist) and obs["gold"] > 0 and \
                    (obs["type"] == -1 or (obs["type"] == 0 and obs["income_rate"] < obs["max_mine_size"])):
                min_dist = dist
                target = obs
            if target is not None:
                action = f"BUILD {target['id']} MINE"
    else:
        min_dist = None
        target = None
        for obs in game_info["obstacles"]:
            dist = distance_between((barracks["x"], barracks["y"]), (obs["x"], obs["y"]))
            if (min_dist is None or dist < min_dist) and obs["type"] == -1:
                min_dist = dist
                target = obs
        action = f"BUILD {target['id']} TOWER"

    train = "TRAIN"
    if game_info["gold"] >= 80:
        if barracks["type"] == 2 and barracks["owner"] == 0:
            train = f"{train} {barracks['id']}"
    return {
        "barracks": barracks,
    }, [
        action,
        train
    ]


def handle_boss_3(last, game_info):
    income = 0
    for obs in game_info["obstacles"]:
        if obs["type"] == 0 and obs["owner"] == 0:
            income += obs["income_rate"]

    queen = ()
    for unit in game_info["units"]:
        if unit["type"] == -1 and unit["owner"] == 0:
            queen = (unit["x"], unit["y"])

    barracks = get_value(last, "barracks", None)
    if barracks is None:
        min_dist = None
        for obs in game_info["obstacles"]:
            dist = distance_between(queen, (obs["x"], obs["y"]))
            if min_dist is None or dist < min_dist:
                min_dist = dist
                barracks = obs
    barracks = list(filter(lambda item: item["id"] == barracks["id"], game_info["obstacles"]))[0]

    action = "WAIT"
    if barracks["type"] == -1:
        action = f"BUILD {barracks['id']} BARRACKS-KNIGHT"
    elif income < 8:
        min_dist = None
        target = None
        for obs in game_info["obstacles"]:
            dist = distance_between((barracks["x"], barracks["y"]), (obs["x"], obs["y"]))
            if (min_dist is None or dist < min_dist) and obs["gold"] > 0 and \
                    (obs["type"] == -1 or (obs["type"] == 0 and obs["income_rate"] < obs["max_mine_size"])):
                min_dist = dist
                target = obs
            if target is not None:
                action = f"BUILD {target['id']} MINE"
    else:
        min_dist = None
        target = None
        for obs in game_info["obstacles"]:
            dist = distance_between((barracks["x"], barracks["y"]), (obs["x"], obs["y"]))
            if (min_dist is None or dist < min_dist) and obs["type"] == -1:
                min_dist = dist
                target = obs
        action = f"BUILD {target['id']} TOWER"

    train = "TRAIN"
    if game_info["gold"] >= 80:
        if barracks["type"] == 2:
            train = f"{train} {barracks['id']}"

    return {
        "barracks": barracks,
    }, [
        action,
        train
    ]


def handle_boss_2(last, game_info):
    def distance_between(o1: tuple, o2: tuple):
        return math.sqrt((o1[0] - o2[0]) ** 2 + (o1[1] - o2[1]) ** 2)

    queen = ()
    for unit in game_info["units"]:
        if unit["type"] == -1 and unit["owner"] == 0:
            queen = (unit["x"], unit["y"])

    barracks = get_value(last, "barracks", None)
    if barracks is None:
        min_dist = None
        for obs in game_info["obstacles"]:
            dist = distance_between(queen, (obs["x"], obs["y"]))
            if min_dist is None or dist < min_dist:
                min_dist = dist
                barracks = obs
    barracks = list(filter(lambda item: item["id"] == barracks["id"], game_info["obstacles"]))[0]

    action = "WAIT"
    if barracks["type"] == -1:
        action = f"BUILD {barracks['id']} BARRACKS-KNIGHT"
    else:
        min_dist = None
        target = None
        for obs in game_info["obstacles"]:
            dist = distance_between((barracks["x"], barracks["y"]), (obs["x"], obs["y"]))
            if min_dist is None or dist < min_dist and obs["type"] == -1:
                min_dist = dist
                target = obs
        if target is not None:
            action = f"BUILD {target['id']} BARRACKS-KNIGHT"

    train = "TRAIN"
    if game_info["gold"] >= 80:
        if barracks["type"] == 2:
            train = f"{train} {barracks['id']}"

    return {
        "barracks": barracks,
    }, [
        action,
        train
    ]


def handle_boss_1(last, game_info):
    queen = ()
    for unit in game_info["units"]:
        if unit["type"] == -1 and unit["owner"] == 0:
            queen = (unit["x"], unit["y"])

    barracks = get_value(last, "barracks", None)
    if barracks is None:
        min_dist = None
        for obs in game_info["obstacles"]:
            dist = distance_between(queen, (obs["x"], obs["y"]))
            if min_dist is None or dist < min_dist:
                min_dist = dist
                barracks = obs
    barracks = list(filter(lambda item: item["id"] == barracks["id"], game_info["obstacles"]))[0]

    action = "WAIT"
    if barracks["type"] == -1:
        action = f"BUILD {barracks['id']} BARRACKS-KNIGHT"

    count = get_value(last, "count", 0)

    count += 1
    train = "TRAIN"
    if count == 12:
        count = 0
        if barracks["type"] == 2:
            train = f"{train} {barracks['id']}"

    return {
        "count": count,
        "barracks": barracks,
    }, [
        action,
        train
    ]
