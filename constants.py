import numpy as np


class Constants:
    STARTING_GOLD = 100

    viewportX = np.arange(0, 1920)
    viewportY = np.arange(0, 1000)

    QUEEN_SPEED = 60
    TOWER_HP_INITIAL = 200
    TOWER_HP_INCREMENT = 100
    TOWER_HP_MAXIMUM = 800
    TOWER_CREEP_DAMAGE_MIN = 3
    TOWER_CREEP_DAMAGE_CLIMB_DISTANCE = 200
    TOWER_QUEEN_DAMAGE_MIN = 1
    TOWER_QUEEN_DAMAGE_CLIMB_DISTANCE = 200
    TOWER_MELT_RATE = 4
    TOWER_COVERAGE_PER_HP = 1000

    GIANT_BUST_RATE = 80

    OBSTACLE_GAP = 90
    OBSTACLE_RADIUS_RANGE = np.arange(60, 90)  # 60..90
    OBSTACLE_GOLD_RANGE = np.arange(200, 250)  # 200..250
    OBSTACLE_MINE_BASESIZE_RANGE = np.arange(1, 3)  # 1..3
    OBSTACLE_GOLD_INCREASE = 50
    OBSTACLE_GOLD_INCREASE_DISTANCE_1 = 500
    OBSTACLE_GOLD_INCREASE_DISTANCE_2 = 200
    OBSTACLE_PAIRS = np.arange(6, 12)  # 6..12

    KNIGHT_DAMAGE = 1
    ARCHER_DAMAGE = 2
    ARCHER_DAMAGE_TO_GIANTS = 10

    QUEEN_RADIUS = 30
    QUEEN_MASS = 10000
    QUEEN_HP = np.arange(5, 20)  # 5..20
    QUEEN_HP_MULT = 5  # i.e. 25. .100 by 5
    QUEEN_VISION = 300

    WORLD_WIDTH = 1920
    WORLD_HEIGHT = 1000

    TOUCHING_DELTA = 5
    WOOD_FIXED_INCOME = 10


class Leagues:
    towers: bool = True
    giants: bool = True
    mines: bool = True
    fixedIncome: int = 0
    obstacles: np.array = Constants.OBSTACLE_PAIRS[-1]
    queenHp: int = 100


class CreepType:
    ordinal: int
    count: int
    cost: int
    speed: int
    range: int
    attackRange: int
    radius: int
    mass: int
    hp: int
    buildTime: int
    assetName: str

    def __init__(self, count, cost, speed, range_, radius, mass, hp, buildTime, assetName, ordinal=-1):
        self.ordinal = ordinal
        self.count = count
        self.cost = cost
        self.speed = speed

        self.range = range_
        self.attackRange = range_

        self.radius = radius
        self.mass = mass
        self.hp = hp
        self.buildTime = buildTime
        self.assetName = assetName


KNIGHT = CreepType(4, 80, 100, 0, 20, 400, 30, 5, "Unite_Fantassin", 0)
ARCHER = CreepType(2, 100, 75, 200, 25, 900, 45, 8, "Unite_Archer", 1)
GIANT = CreepType(1, 140, 50, 0, 40, 2000, 200, 10, "Unite_Siege", 2)
