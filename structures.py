from __future__ import annotations

import random
from abc import abstractmethod
from typing import List

import numpy as np

from constants import Constants, CreepType, GIANT, KNIGHT, ARCHER
from vector2 import Vector2

nextObstacleId = 0


class Structure:

    def __init__(self, owner, obstacle):
        self.owner = owner
        self.obstacle = obstacle

    def onComplete(self, ob=None):
        raise ValueError("Not Implemented")

    def act(self):
        raise ValueError("Not Implemented")

    def __str__(self):
        return f"{self.owner} - {self.obstacle}"


class FieldObject:
    location: Vector2
    radius = int
    mass = int

    def __init__(self):
        self.location = None
        self.radius = 0
        self.mass = 0  # 0 := immovable


class Obstacle(FieldObject):
    structure: Structure
    obstacleId: int

    def __init__(self, maxMineSize, initialGold, initialRadius, initialLocation):
        super().__init__()

        self.structure = None
        global nextObstacleId
        nextObstacleId += 1
        self.maxMineSize = maxMineSize
        self.obstacleId = nextObstacleId
        self.mass = 0
        self.radius = initialRadius
        self.location = initialLocation
        self.gold = initialGold
        self.params = {
            "id": self.obstacleId,
            "type": "Site"
        }
        self.obstacle_tile_id = random.randint(1, 10)
        self.area = np.pi * self.radius * self.radius
        # self.structure = None

    def updateEntities(self):
        # TODO update animation and projectile from towers
        return False
        # if self.structure is not None:
        #     self.structure.updateEntities()

    def destroy(self):
        pass

    def act(self):
        if self.structure is not None and self.structure.act():
            self.structure = None
        self.updateEntities()

    def setMine(self, owner):
        self.structure = Mine(self, owner, 1)

    def setTower(self, owner, health):
        self.structure = Tower(self, owner, 0, health)

    def setBarracks(self, owner, creepType):
        self.structure = Barracks(self, owner=owner, creepType=creepType)

    def __str__(self):
        return f"{self.obstacleId} - {self.location}"


class Mine(Structure):

    def __init__(self, obstacle, owner, incomeRate):
        super().__init__(owner, obstacle)
        self.incomeRate = incomeRate

    def act(self):
        cash = min(self.incomeRate, self.obstacle.gold)
        self.owner.goldPerTurn += cash
        self.owner.gold += cash
        self.obstacle.gold -= cash
        if self.obstacle.gold <= 0:
            return True
        return False


class Tower(Structure):
    attackRadius: int
    health: int

    def __init__(self, obstacle, owner, attackRadius, health):
        super().__init__(owner, obstacle)
        self.attackTarget = None
        self.attackRadius = attackRadius
        self.health = health

    def damageCreep(self, target):
        self._damage(target, Constants.TOWER_CREEP_DAMAGE_MIN, Constants.TOWER_CREEP_DAMAGE_CLIMB_DISTANCE)

    def damageQueen(self, target):
        self._damage(target, Constants.TOWER_QUEEN_DAMAGE_MIN, Constants.TOWER_QUEEN_DAMAGE_CLIMB_DISTANCE)

    def _damage(self, target, param1, param2):
        shotDistance = target.location.distanceTo(self.obstacle.location) - self.obstacle.radius
        differenceFromMax = self.attackRadius - shotDistance
        damage = param1 + int(differenceFromMax / param2)
        target.damage(damage)

    def act(self):
        closestEnemy = None
        closestEnemyDist = None
        for creep in self.owner.enemyPlayer.activeCreeps:
            dist = self.obstacle.location.distanceTo(creep.location)
            if closestEnemyDist is None or dist < closestEnemyDist:
                closestEnemyDist = dist
                closestEnemy = creep

        enemyQueen = self.owner.enemyPlayer.queenUnit
        if closestEnemy is not None and closestEnemy.location.distanceTo(self.obstacle.location) < self.attackRadius:
            self.damageCreep(closestEnemy)
        elif enemyQueen.location.distanceTo(self.obstacle.location) < self.attackRadius:
            self.damageQueen(enemyQueen)
        # self.health = min(0, self.health - Constants.TOWER_MELT_RATE)
        self.health -= Constants.TOWER_MELT_RATE
        self.attackRadius = int(np.sqrt((self.health * Constants.TOWER_COVERAGE_PER_HP + self.obstacle.area) / np.pi))
        if self.health <= 0:
            return True
        return False


class Barracks(Structure):

    def __init__(self, obstacle: Obstacle, owner: Player, creepType: CreepType):
        super().__init__(owner, obstacle)
        self.obstacle = obstacle
        self.owner = owner
        self.creepType = creepType
        self.progressMax = creepType.buildTime
        self.progress = 0
        self.isTraining = False

    def act(self):
        if self.isTraining:
            self.progress += 1
            if self.progress == self.progressMax:
                self.progress = 0
                self.isTraining = False
                self.onComplete(self.obstacle)  # create a creep ?
        return False


class Unit(FieldObject):
    """Characters.kt : Unit
    """

    unit_type: int
    owner: Player
    location: Vector2
    maxHealth: int
    health: int

    def __init__(self, owner, unit_type):
        """
        param owner - Player
        """
        super().__init__()
        self.unit_type = unit_type
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
        super().__init__(owner, -1)
        self.mass = Constants.QUEEN_MASS
        self.radius = Constants.QUEEN_RADIUS
        self.maxHealth = Constants.QUEEN_HP

        self.tokenCircle = {
            "baseWidth": self.radius * 2,
            "baseHeight": self.radius * 2
        }

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

    def is_in_range_of(self, obs: Obstacle) -> bool:
        dist = obs.location.distanceTo(self.location)
        return dist < self.radius + obs.radius + Constants.TOUCHING_DELTA


class Creep(Unit):
    """Characters.kt : Creep
    """

    def __init__(self, owner, creepType):
        super().__init__(owner, creepType.ordinal)
        self.speed = creepType.speed
        self.attackRange = creepType.attackRange
        self.mass = creepType.mass
        self.maxHealth = creepType.hp
        self.radius = creepType.radius
        self.health = creepType.hp

        # TODO REMOVE MEEEE
        self.tokenCircle = {
            "baseWidth": self.radius * 2,
            "baseHeight": self.radius * 2
        }

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

    obstacles: List[Obstacle]

    def __init__(self, owner, obstacles=None):
        super().__init__(owner, GIANT)
        if obstacles is None:
            obstacles = []
        self.obstacles = obstacles  # type: Obstacle

    def move(self, frames):
        """
        params frames - double, ?
        """
        # TODO (how/where to) get current obstacles ? - set externally?
        opp_structures = list(filter(
            lambda struct: struct.structure is not None
                           and isinstance(struct.structure, Tower)
                           and struct.structure.owner == self.owner.enemyPlayer,
            self.obstacles))

        if len(opp_structures) == 0:
            return

        target = min(opp_structures, key=lambda struct: struct.location.distanceTo(self.location)).location
        self.location = self.location.towards(target, self.speed * frames)

    def dealDamage(self):
        target = None
        for obs in self.obstacles:
            if obs.structure is None or obs.structure.owner != self.owner.enemyPlayer or not isinstance(obs.structure,
                                                                                                        Tower):
                continue
            dist = obs.location.distanceTo(self.location)
            if dist >= self.radius + obs.radius + Constants.TOUCHING_DELTA:
                continue
            target = obs
            break
        if target is None:
            return

        target.structure.health = min(0, target.structure.health - Constants.GIANT_BUST_RATE)

    def finalizeFrame(self):
        pass


class KnightCreep(Creep):

    def __init__(self, owner):
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
            self.owner.enemyPlayer.health -= Constants.KNIGHT_DAMAGE

    def move(self, frames: float):
        enemyQueen = self.owner.enemyPlayer.queenUnit
        # move toward enemy queen, if not yet in range
        if self.location.distanceTo(enemyQueen.location) > self.radius + enemyQueen.radius + self.attackRange:
            self.location = self.location.towards(
                (enemyQueen.location + (self.location - enemyQueen.location).resizedTo(3.0)),
                self.speed * frames)

    def finalizeFrame(self):
        # TODO animation etc.
        return


class ArcherCreep(Creep):

    def __init__(self, owner):
        super().__init__(owner, ARCHER)
        self.owner = owner
        self.lastLocation = None
        self.attacksThisTurn = False
        self.attackTarget = None

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
        # TODO Character Sprite movement
        return

    def findTarget(self) -> Creep:
        min_dist = None
        target = None
        for creep in self.owner.enemyPlayer.activeCreeps:
            dist = creep.location.distanceTo(self.location)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                target = creep
        return target


class AbstractPlayer:
    pass  # TODO find / fill


class Player(AbstractPlayer):
    """Player.kt : Player
    """

    # activeCreeps: List[Creep]

    queenUnit: Queen

    def printObstaclePerTurn(self, obstacle: Obstacle):
        struc = obstacle.structure
        visible = (struc is not None and struc.owner.name == self.name) or obstacle.location.distanceTo(
            self.queenUnit.location) < Constants.QUEEN_VISION

        if struc is None:
            struc_info = {
                "type": -1
            }
        elif isinstance(struc, Mine):
            struc_info = {
                "type": 0,
                "type_name": "Mine",
                "owner": self.fixOwner(struc.owner),
                "income_rate": struc.incomeRate if visible else -1 # param1
            }
        elif isinstance(struc, Tower):
            struc_info = {
                "type": 1,
                "type_name": "Tower",
                "owner": self.fixOwner(struc.owner),
                "health": struc.health,
                "attack_radius": struc.attackRadius
            }
        elif isinstance(struc, Barracks):
            struc_info = {
                "type": 2,
                "type_name": "Tower",
                "owner": self.fixOwner(struc.owner),
                "until_next_train": 0 if not struc.isTraining else struc.progressMax - struc.progress,
                "creep_type": struc.creepType.ordinal
            }
        else:
            raise ValueError("")

        return {**struc_info, **{
            "id": obstacle.obstacleId,
            "gold": obstacle.gold if visible else -1,
            "x": obstacle.location.x,
            "y": obstacle.location.y,
            "radius": obstacle.radius,
            "max_mine_size": obstacle.maxMineSize if visible else -1,
        }}

    def __init__(self, name):
        self.isSecondPlayer = None
        self.queenUnit = None
        self.enemyPlayer = None
        self.activeCreeps = []
        self.name = name
        self.outputs = [
            "",
            "",
        ]

        self.health = None
        self.score = -2
        self.gold = Constants.STARTING_GOLD
        self.goldPerTurn = 0

    def allUnits(self):
        ent = []
        ent.extend(self.activeCreeps)
        ent.append(self.queenUnit)
        return ent

    def checkQueenHealth(self):
        self.queenUnit.health = self.health  # << really ?? double bookkeeping here.
        if self.health == 0:
            raise Exception("DEAD QUEEN")

    def kill(self, reason):
        self.score = -1
        raise Exception(reason)

    def fixOwner(self, player: Player) -> int:
        if player is None:
            return -1
        if player.name == self.name:
            return 0
        return 1
