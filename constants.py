import numpy as np


class Constants:
    STARTING_GOLD = 100

    viewportX = np.arange(0, 1920 + 1)
    viewportY = np.arange(0, 1000 + 1)

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
    OBSTACLE_RADIUS_RANGE = np.arange(60, 90 + 1)  # 60..90
    OBSTACLE_GOLD_RANGE = np.arange(200, 250 + 1)  # 200..250
    OBSTACLE_MINE_BASESIZE_RANGE = [1, 2, 3]  # np.arange(1, 5)  # 1..3
    OBSTACLE_GOLD_INCREASE = 50
    OBSTACLE_GOLD_INCREASE_DISTANCE_1 = 500
    OBSTACLE_GOLD_INCREASE_DISTANCE_2 = 200
    OBSTACLE_PAIRS = np.arange(6, 12 + 1)  # 6..12

    KNIGHT_DAMAGE = 1
    ARCHER_DAMAGE = 2
    ARCHER_DAMAGE_TO_GIANTS = 10

    QUEEN_RADIUS = 30
    QUEEN_MASS = 10000
    QUEEN_HP = np.arange(5, 20 + 1)  # 5..20
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


KNIGHT = CreepType(count=4, cost=80, speed=100, range_=0, radius=20, mass=400, hp=30, buildTime=5,
                   assetName="Unite_Fantassin", ordinal=0)
ARCHER = CreepType(count=2, cost=100, speed=75, range_=200, radius=25, mass=900, hp=45, buildTime=8,
                   assetName="Unite_Archer", ordinal=1)
GIANT = CreepType(count=1, cost=140, speed=50, range_=0, radius=40, mass=2000, hp=200, buildTime=10,
                  assetName="Unite_Siege", ordinal=2)
