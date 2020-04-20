import numpy as np

from characters import FieldObject
from constants import Constants

nextObstacleId = 0


class Structure:

    def __int__(self, owner, obstacle):
        self.owner = owner
        self.obstacle = obstacle


class Obstacle(FieldObject):

    def __int__(self, maxMineSize, initialGold, initialRadius, initialLocation):
        super().__init__()
        global nextObstacleId
        nextObstacleId += 1
        self.obstacleId = nextObstacleId
        self.mass = 0
        self.radius = initialRadius
        self.location = initialLocation
        self.gold = initialGold
        self.params = {
            "id": self.obstacleId,
            "type": "Site"
        }
        self.area = np.PI * self.radius * self.radius
        self.structure = None

    def updateEntities(self):
        if self.structure is not None:
            self.structure.updateEntities()

    def destroy(self):
        pass

    def act(self):
        if self.structure is not None:
            print("TOOOODOOOO")
            pass
        self.updateEntities()

    def setMine(self, owner):
        self.structure = Mine(self, owner, 1)

    def setTower(self, owner, health):
        self.structure = Tower(self, owner, 0, health)

    def setBarracks(self, owner, creepType):
        self.structure = Barracks(self, owner, creepType)


class Mine(Structure):

    def __int__(self, obstacle, owner, incomeRate):
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

    def __int__(self, obstacle, owner, attackRadius, health):
        super().__init__(owner, obstacle)
        self.attackTarget = None

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
        closestEnemy = min(self.owner.enemyPlayer.activeCreeps, key=lambda x: self.location.distanceTo(x.location))
        enemyQueen = self.owner.enemyPlayer.queenUnit
        if closestEnemy is not None and closestEnemy.location.distanceTo(self.obstacle.location) < self.attackRadius:
            self.damageCreep(closestEnemy)
        elif enemyQueen.location.distanceTo(self.obstacle) < self.attackRadius:
            self.damageQueen(enemyQueen)
        self.health -= Constants.TOWER_MELT_RATE
        self.attackRadius = int(np.sqrt((self.health * Constants.TOWER_COVERAGE_PER_HP + self.obstacle.area) / np.PI))
        if self.health <= 0:
            return True
        return False


class Barracks(Structure):

    def __int__(self, obstacle, owner, creepType, health):
        super().__init__(owner, obstacle)
        self.isTraining = False
        self.progress = 0
        self.progressMax = creepType.buildTime

    def act(self):
        if self.isTraining:
            self.progress += 1
            if self.progress == self.progressMax:
                self.progress = 0
                self.isTraining = False
        return False
