import copy
from abc import abstractmethod

from constants import *
from vector2 import *


class FieldObject:
    """Characters.kt : FieldObject
    """

    def __int__(self):
        self.location = None
        self.radius = 0
        self.mass = 0  # 0 := immovable


class Unit(FieldObject):
    """Characters.kt : Unit
    """

    def __init__(self, owner):
        """
        param owner - Player
        """
        super().__init__()
        self.owner = owner
        self.location = Vector2()
        self.maxHealth = 0
        self.health = 0  # >> self.health >= 0

    @abstractmethod
    def damage(self, damageAmount):
        pass


class Queen(Unit):
    """Characters.kt : Queen
    """

    def __init__(self, owner):
        super().__init__(owner)
        self.mass = Constants.QUEEN_MASS
        self.radius = Constants.QUEEN_RADIUS
        self.maxHealth = Constants.QUEEN_HP

        # TODO REMOVE ME
        self.characterSprite = {}
        self.tokenCircle = {}

        self.characterSprite.image = "Unite_Reine"
        # theTooltipModule.registerEntity(tokenGroup, mapOf("type" to "Queen"))
        self.tokenCircle.baseWidth = self.radius * 2
        self.tokenCircle.baseHeight = self.radius * 2
        self.characterSprite.baseWidth = self.radius * 2
        self.characterSprite.baseHeight = self.radius * 2

    def moveTowards(self, target: Vector2):
        """
        param target - Vector2
        """
        self.location = self.location.towards(target, Constants.QUEEN_SPEED)

    def damage(self, damageAmount):
        if damageAmount <= 0:
            return
        # TODO CHECK: maybe just ignore owner, and use self here?!?
        self.owner.health = max(0, self.owner.health - damageAmount)


class Creep(Unit):
    """Characters.kt : Creep
    """

    def __init__(self, owner, creepType):
        super().__init__(owner)
        self.speed = creepType.speed
        self.attackRange = creepType.attackRange
        self.mass = creepType.mass
        self.maxHealth = creepType.hp
        self.radius = creepType.radius
        self.health = creepType.hp

        # TODO REMOVE MEEEE
        self.tokenCircle = {}
        self.characterSprite = {}

        self.tokenCircle.baseWidth = self.radius * 2
        self.tokenCircle.baseHeight = self.radius * 2
        self.characterSprite.image = creepType.assetName
        self.characterSprite.baseWidth = self.radius * 2
        self.characterSprite.baseHeight = self.radius * 2

        # theTooltipModule.registerEntity(tokenGroup,mapOf("type" to creepType.toString()))

    @abstractmethod
    def finalizeFrame(self):
        pass

    def damage(self, damageAmount):
        if damageAmount <= 0:
            return
        self.health -= damageAmount
        # theTooltipModule.updateExtraTooltipText(tokenCircle, "Health: $health")

    @abstractmethod
    def dealDamage(self):
        pass

    @abstractmethod
    def move(self, frames):
        pass


class GiantCreep(Creep):
    """Characters.kt : GiantCreep
    """

    def __int__(self, owner):
        super().__init__(owner, KNIGHT)
        self.obstacles = []  # type: Obstacle

    def move(self, frames):
        """
        params frames - double, ?
        """
        # TODO (how/where to) get current obstacles ? - set externally?
        opp_structures = filter(
            lambda struct: struct != None
                           and struct == Tower
                           and struct.owner == self.owner.enemyPlayer,
            self.obstacles)
        target = min(opp_structures, key=lambda struct: struct.location.distanceTo(self.location))

        self.location = self.location.towards(target)

    def dealDamage(self):
        opp_structures = filter(
            lambda
                struct: struct != None
                        and isinstance(struct, Tower)
                        and struct.owner == self.owner.enemyPlayer
                        and struct.location.distanceTo(
                self.location) < self.radius + struct.radius + Constants.TOUCHING_DELTA,
            self.obstacles)
        if len(opp_structures) == 0:
            return
        target = opp_structures[0]
        # target should be a tower
        target.health -= Constants.GIANT_BUST_RATE
        creepToTower = target.location - self.location

        # TODO REMOVE ME
        characterSprite = {}
        theEntityManager = {}

        characterSprite.location = creepToTower.resizedTo(self.radius)
        theEntityManager.commitEntityState(0.2, characterSprite)
        characterSprite.location = Vector2(0, 0)
        theEntityManager.commitEntityState(1.0, characterSprite)

    def finalizeFrame(self):
        pass


class KnightCreep(Creep):

    def dealDamage(self):
        pass

    def move(self, frames):
        pass

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
