import copy
from abc import abstractmethod

import numpy as np

h = 1000
l = 1920
field = np.zeros((h, l))


class Constants:
    STARTING_GOLD = 100

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


class CreepType:

    def __int__(self, count, cost, speed, range, radius, mass, hp, buildTime, assetName):
        self.count = count
        self.cost = cost
        self.speed = speed
        self.range = range
        self.radius = radius
        self.mass = mass
        self.hp = hp
        self.buildTime = buildTime
        self.assetName = assetName


KNIGHT = CreepType(4, 80, 100, 0, 20, 400, 30, 5, "Unite_Fantassin")
ARCHER = CreepType(2, 100, 75, 200, 25, 900, 45, 8, "Unite_Archer")
GIANT = CreepType(1, 140, 50, 0, 40, 2000, 200, 10, "Unite_Siege")


class Vector2:

    def __int__(self, x=0, y=0):
        self.x = x
        self.y = y

    # TODO Numpy faster numpy.linalg.norm(other-self) ?
    def distanceTo(self, other):
        return np.sqrt((self.x - other.x) ** 2 - (self.y - other.y) ** 2)


class FieldObject:

    def __int__(self):
        self.location = None
        self.radius = 0
        self.mass = 0


class Unit(FieldObject):

    def __init(self, owner):
        super().__init__()
        self.owner = owner
        self.location = Vector2()
        self.maxHealth = 0
        self.health = 0

    @abstractmethod
    def damage(self, damageAmount):
        pass


class Creep(Unit):

    def __int__(self, owner, creepType):
        super().__init__(owner)
        self.speed = creepType.speed
        self.attackRange = creepType.attackRange
        self.mass = creepType.mass
        self.maxHealth = creepType.hp
        self.radius = creepType.radius
        self.health = creepType.hp

        self.tokenCircle = {}
        self.tokenCircle.baseWidth = self.radius * 2
        self.tokenCircle.baseHeight = self.radius * 2
        self.characterSprite.image = creepType.assetName
        self.characterSprite.baseWidth = self.radius * 2
        self.characterSprite.baseHeight = self.radius * 2

    @abstractmethod
    def finalizeFrame(self):
        pass

    def damage(self, damageAmount):
        if (damageAmount <= 0): return
        self.health -= damageAmount

    @abstractmethod
    def dealDamage(self):
        pass

    @abstractmethod
    def move(self, frames):
        pass


class KnightCreep(Creep):

    def __int__(self, owner):
        super().__init__(owner, KNIGHT)
        self.owner
        self.lastLocation = None
        self.attacksThisTurn = False

    def finalizeFrame(self):
        last = copy.copy(self.lastLocation)

        if last != None:
            if last.distanceTo(self.location) > 30 and not self.attacksThisTurn:
                last = self.location - last
        else:
            pass


#   override fun finalizeFrame() {
#     val last = lastLocation
#
#     if (last != null) {
#       val movementVector = when {
#         last.distanceTo(location) > 30 && !attacksThisTurn -> location - last
#         else -> owner.enemyPlayer.queenUnit.location - location
#       }
#       characterSprite.rotation = movementVector.angle
#     }
#
#     lastLocation = location
#   }
#
#   override fun move(frames: Double)  {
#     val enemyQueen = owner.enemyPlayer.queenUnit
#     // move toward enemy queen, if not yet in range
#     if (location.distanceTo(enemyQueen.location) > radius + enemyQueen.radius + attackRange)
#       location = location.towards((enemyQueen.location + (location - enemyQueen.location).resizedTo(3.0)), speed.toDouble() * frames)
#   }
#
#   override fun dealDamage() {
#     attacksThisTurn = false
#     val enemyQueen = owner.enemyPlayer.queenUnit
#     if (location.distanceTo(enemyQueen.location) < radius + enemyQueen.radius + attackRange + TOUCHING_DELTA) {
#       attacksThisTurn = true
#       characterSprite.setAnchorX(0.5, Curve.IMMEDIATE)
#       theEntityManager.commitEntityState(0.4, characterSprite)
#       characterSprite.anchorX = 0.2
#       theEntityManager.commitEntityState(0.7, characterSprite)
#       characterSprite.anchorX = 0.5
#       theEntityManager.commitEntityState(1.0, characterSprite)
#       owner.enemyPlayer.health -= KNIGHT_DAMAGE
#     }
#   }
# }

if __name__ == '__main__':
    print(Constants.test)
