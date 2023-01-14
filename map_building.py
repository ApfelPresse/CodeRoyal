import random
from functools import reduce
from typing import List

from constants import Leagues, Constants
from structures import Obstacle, FieldObject
from vector2 import Vector2


def flatMap(array: List[List]):
    return reduce(list.__add__, array)


def collisionCheck(entities: List[FieldObject], acceptableGap: float = 0.0) -> bool:
    for iu1, u1 in enumerate(entities):
        rad = u1.radius
        clampDist = Constants.OBSTACLE_GAP + rad if u1.mass == 0 else rad
        u1.location = u1.location.clampWithin(clampDist, Constants.WORLD_WIDTH - clampDist, clampDist,
                                              Constants.WORLD_HEIGHT - clampDist)

        u1.location.check_if_not_smaller_zero()
        for iu2, u2 in enumerate(entities):
            if iu1 == iu2:
                continue
            overlap = u1.radius + u2.radius + acceptableGap - u1.location.distanceTo(u2.location)  # TODO: Fix this?
            if overlap <= 1e-6:
                continue
            else:
                if u1.mass == 0 and u2.mass == 0:
                    d1, d2 = 0.5, 0.5
                elif u1.mass == 0:
                    d1, d2 = 0.0, 1.0
                elif u2.mass == 0:
                    d1, d2 = 1.0, 0.0
                else:
                    d1, d2 = u2.mass / (u1.mass + u2.mass), u1.mass / (u1.mass + u2.mass)
                u1tou2 = u2.location - u1.location
                gap = 20.0 if u1.mass == 0 and u2.mass == 0 else 1.0
                u1.location -= u1tou2.resizedTo(d1 * overlap + 0.0 if (u1.mass == 0 and u2.mass > 0) else gap)
                u2.location += u1tou2.resizedTo(d2 * overlap + 0.0 if (u2.mass == 0 and u1.mass > 0) else gap)

                u1.location.check_if_not_smaller_zero()
                u2.location.check_if_not_smaller_zero()
                return True
    return False


def buildObstacles() -> List[Obstacle]:
    obstaclePairs = []
    obstacle_id = 0
    for _ in range(1, Leagues.obstacles):
        gold = sample(Constants.OBSTACLE_GOLD_RANGE)
        radius = sample(Constants.OBSTACLE_RADIUS_RANGE)
        l1 = Vector2(random.randint(0, Constants.WORLD_WIDTH), random.randint(0, Constants.WORLD_HEIGHT))
        l2 = Vector2(Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT) - l1
        gold_max_mine_size = sample(Constants.OBSTACLE_MINE_BASESIZE_RANGE)

        obstacle_id += 1
        o1 = Obstacle(maxMineSize=gold_max_mine_size, initialGold=gold, initialRadius=radius, initialLocation=l1,
                      obstacle_id=obstacle_id)

        obstacle_id += 1
        o2 = Obstacle(maxMineSize=gold_max_mine_size, initialGold=gold, initialRadius=radius, initialLocation=l2,
                      obstacle_id=obstacle_id)

        obstaclePairs.append([o1, o2])

    obstacles = flatMap(obstaclePairs)

    collision_results = []
    for i in range(1, 100 + 1):
        for pair in obstaclePairs:
            o1, o2 = pair
            mid = (o1.location + Vector2(Constants.WORLD_WIDTH - o2.location.x,
                                         Constants.WORLD_HEIGHT - o2.location.y)) / 2.0
            o1.location = mid
            o2.location = Vector2(Constants.WORLD_WIDTH - mid.x, Constants.WORLD_HEIGHT - mid.y)

        collision_results.append(collisionCheck(obstacles, float(Constants.OBSTACLE_GAP)))
    return obstacles


def sample(list_like):
    return random.choice(list_like)


def buildMap() -> List[Obstacle]:
    obstacles = None
    while obstacles is None:
        obstacles = buildObstacles()

    mapCenter = Vector2(len(Constants.viewportX) / 2, len(Constants.viewportY) / 2)
    for o in obstacles:
        o.location = o.location.snapToIntegers()
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_1:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_2:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
    return obstacles


def fixCollisions(entities: List[FieldObject], maxIterations: int = 999):
    for _ in range(maxIterations):
        if not collisionCheck(entities):
            return
