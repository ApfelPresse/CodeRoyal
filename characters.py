import math
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
        super().__init__(owner, GIANT)
        self.obstacles = []  # type: Obstacle

    def move(self, frames):
        """
        params frames - double, ?
        """
        # TODO (how/where to) get current obstacles ? - set externally?
        opp_structures = filter(
            lambda struct: struct != None
                           and isinstance(struct, Tower)
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

    def __int__(self, owner):
        super().__init__(owner, KNIGHT)
        self.owner = owner
        self.lastLocation = None
        self.attacksThisTurn = False

    def dealDamage(self):
        self.attacksThisTurn = False
        enemyQueen = self.owner.enemyPlayer.queenUnit
        if self.location.distanceTo(
                enemyQueen.location) < self.radius + enemyQueen.radius + self.attackRange + Constants.TOUCHING_DELTA:
            self.attacksThisTurn = True

            # TODO REMOVE ME
            self.characterSprite = {}
            self.theEntityManager = {}

            self.characterSprite.setAnchorX(0.5, Curve.IMMEDIATE)
            self.theEntityManager.commitEntityState(0.4, self.characterSprite)
            self.characterSprite.anchorX = 0.2
            self.theEntityManager.commitEntityState(0.7, self.characterSprite)
            self.characterSprite.anchorX = 0.5
            self.theEntityManager.commitEntityState(1.0, self.characterSprite)
            self.owner.enemyPlayer.health -= Constants.KNIGHT_DAMAGE

    def move(self, frames: float):
        enemyQueen = self.owner.enemyPlayer.queenUnit
        # move toward enemy queen, if not yet in range
        if self.location.distanceTo(enemyQueen.location) > self.radius + enemyQueen.radius + self.attackRange:
            self.location = self.location.towards(
                (enemyQueen.location + (self.location - enemyQueen.location).resizedTo(3.0)),
                self.speed * frames)

    def finalizeFrame(self):
        if self.lastLocation is not None:

            last = self.lastLocation.copy()

            if last.distanceTo(self.location) > 30 and not self.attacksThisTurn:
                movementVector = self.location - last
            else:
                movementVector = self.owner.enemyPlayer.queenUnit.location - self.location

            # TODO REMOVE MEEE
            characterSprite = {}

            characterSprite.rotation = movementVector.angle

        self.lastLocation = self.location


class ArcherCreep(Creep):

    def __int__(self, owner):
        super().__init__(owner, ARCHER)
        self.owner = owner
        self.lastLocation = None
        self.attacksThisTurn = False
        self.attackTarget = None
        # projectile = theEntityManager.createSprite()!!.setZIndex(60).setImage("Fleche_$color").setVisible(false).setAnchorX(1.0).setAnchorY(0.5)

    def dealDamage(self):
        target = self.findTarget()
        if target is None:
            return

        if self.location.distanceTo(
                target.location) < self.radius + target.radius + self.attackRange + Constants.TOUCHING_DELTA:
            dmg = Constants.ARCHER_DAMAGE_TO_GIANTS if isinstance(target, GiantCreep) else Constants.ARCHER_DAMAGE
            target.damage(dmg)
            self.attackTarget = target

    def move(self, frames: float):
        target = self.findTarget()
        if target is None:
            return
        # move toward target, if not yet in range

        if self.location.distanceTo(target.location) > self.radius + target.radius + self.attackRange:
            self.location = self.location.towards((target.location + (self.location - target.location).resizedTo(3.0)),
                                                  self.speed * frames)

    def finalizeFrame(self):
        target = self.findTarget()

        # TODO REMOVE MEEEEE
        characterSprite = {}
        theEntityManager = {}
        projectile = {}
        viewportX = {}
        viewportY = {}

        if self.lastLocation is not None:
            if self.lastLocation.distanceTo(self.location) > 30:
                movementVector = self.location - self.lastLocation
            else:
                movementVector = target.location - self.location

            characterSprite.rotation = math.atan2(movementVector.y, movementVector.x)

        self.lastLocation = self.location

        if self.attackTarget is not None:
            characterSprite.anchorX = 0.8
            theEntityManager.commitEntityState(0.3, characterSprite)
            characterSprite.anchorX = 0.5
            theEntityManager.commitEntityState(0.4, characterSprite)

            projectile.setRotation((self.attackTarget.location - self.location).angle, Curve.IMMEDIATE)
            projectile.isVisible = True
            projectile.setX(self.location.x.toInt() + viewportX.first, Curve.NONE)
            projectile.setY(self.location.y.toInt() + viewportY.first, Curve.NONE)
            theEntityManager.commitEntityState(0.4, projectile)
            projectile.setX(self.attackTarget.location.x.toInt() + viewportX.first, Curve.EASE_IN_AND_OUT)
            projectile.setY(self.attackTarget.location.y.toInt() + viewportY.first, Curve.EASE_IN_AND_OUT)
            theEntityManager.commitEntityState(0.99, projectile)
            projectile.isVisible = False
            theEntityManager.commitEntityState(1.0, projectile)

    def findTarget(self):
        target = min(self.owner.enemyPlayer.activeCreeps, lambda creep: creep.location.distanceTo(self.location))
        return target
