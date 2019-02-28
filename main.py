import copy
from abc import abstractmethod
from constants import *
from characters import *
from vector2 import *
import numpy as np

h = 1000
l = 1920
field = np.zeros((h, l))  # << NO.

viewportX = list(range(l))
viewportY = list(range(h))



class AbstractPlayer:
    pass  # TODO find / fill


class Player(AbstractPlayer):
    """Player.kt : Player
    """

    def __init__(self):
        self.queenUnit = None
        self.enemyPlayer = None
        self.activeCreeps = []

        # original line:
        # 'var health by nonNegative<Player>(100).andAlso { if (score >= 0) score = it }'
        self.health = None
        self.score = -2  # := self.health ?
        self.gold = Constants.STARTING_GOLD
        self.goldPerTurn = 0  # << this looks kinda bad ..
        # self.hud = None

    # def getExpectedOutputLines: return 2
    # def fixOwner(self, player): raise NotImplementedError()
    # def printObstacleInit(self, obstacle): raise NotImplementedError()
    # def printObstaclePerTurn(self, obstacle): raise NotImplementedError()

    def allUnits(self):
        return self.activeCreeps + [self.queeUnit]  # TODO not sure <<

    def checkQueenHealth(self):
        self.queenUnit.health = self.health  # << really ?? double bookkeeping here.
        if self.health == 0:
            self.deactivate("Dead queen")
        # self.hud.update()

    def kill(self, reason):
        self.score = -1
        self.deactivate(reason)




"""
###  from Structures.kt
"""


def Obstacle(FieldObject):
    """Structures.kt : Obstacle
    """
    nextObstacleId = 0

    def __init__(self, maxMineSize, initialGold, initialRadius, initialLocation):
        super().__init__()  # TODO CHECK call
        self.maxMineSize = maxMineSize
        self.initialGold = initialGold
        self.initialRadius = initialRadius
        self.initialLocation = initialLocation
        self.obstacleId = Obstacle.nextObstacleId
        Obstacle.nextObstacleId += 1

        self.mass = 0
        assert (initialGold >= 0)
        self.gold = initialGold
        # self.obstacleImage = None
        self.radius = 0
        self.location = initialLocation
        self.area = np.pi * self.radius ** 2
        self.structure = None

    def setMine(self, owner):
        self.structure = Mine(self, owner, 1)

    def setTower(self, owner, health):
        self.structure = Tower(self, owner, 0, health)

    def setBarracks(self, owner, creepType):
        self.structure = Mine(self, owner, creepType)


class Structure:
    def __init__(self):
        self.owner = None
        self.obstacle = None

    def act(self):
        """ fun act(): Boolean // return true if the Structure should be destroyed
        """
        raise NotImplementedError()


class Mine(Structure):
    def __init__(self, obstacle, owner, incomeRate):
        super().__init__()
        self.obstacle = obstacle
        self.owner = owner
        self.incomeRate = incomeRate

    def act(self):
        cash = min(self.incomeRae, self.obstacle.gold)
        self.owner.goldPerTuren += cash
        self.owner.gold += cash
        self.obstacle.gold -= cash
        if self.obstacle.gold <= 0:
            return True  # mine exhausted >> destroy
        return False


class Tower(Structure):
    def __init__(self, obstacle, owner, attackRadius, health):
        super().__init__()
        self.obstacle = obstacle
        self.owner = owner
        self.attackRadius = attackRadius
        self.health = health

        self.attackTarget = None  # (> FieldObject)

    def damageCreep(self, targetCreep):
        shotDistance = self.target.location.distanceTo(self.obstacle.location) - self.obstacle.radius
        differenceFromMax = self.attackRadius - shotDistance
        damage = Constants.TOWER_CREEP_DAMAGE_MIN + int(differenceFromMax / Constants.TOWER_CREEP_DAMAGE_CLIMB_DISTANCE)
        self.target.damage(damage)

    def act(self):
        closestEnemy = None
        if self.owner.enemyPlayer.activeCreeps:
            closestEnemy = min(self.owner.enemyPlayer.activeCreeps,
                               key=lambda it: it.lcation.distanceTo(self.obstacle.location))
        enemyQueen = self.owner.enemyPlayer.queenUnit

        if closestEnemy != None and closestEnemy.location.distanceTo(self.obstacle.location) < self.attackRadius:
            self.attackTarget = closestEnemy
            self.damageCreep(self.attackTarget)
        elif enemyQueen.location.distanceTo(self.obstacle.location) < self.attackRadius:
            self.attackTarget = enemyQueen
            self.damageQueen(self.attackTarget)

        # duplication in self.attackTarget ..

        else:
            self.attackTarget = None

        self.healt -= Constants.TOWER_MELT_RATE
        self.attackRadius = int(((self.health * Constants.TOWER_COVERAGE_PER_HP + self.obstacle.area) / np.pi) ** 0.5)

        if self.health <= 0:
            return True  # Tower destroyed (time/attack)
        return False


class Barracks(Structure):

    def __init__(self, obstacle, owner, creepType):
        super().__init__()
        self.obstacle = obstacle
        self.owner = owner
        self.creepType = creepType
        self.progressMax = creepType.buildTime
        self.progress = 0
        self.isTraining = False

        # 'var onComplete: () -> Unit = {}  ## << ??    

    def act(self):
        if self.isTraining:
            self.progress += 1
            if self.progress == self.progressMax:
                self.progress = 0
                self.isTraining = False
                self.onComplete()  # create a creep ?
        return False


# End: Structures.kt


"""
### Referee.kt
"""
from random import Random


class AbstractReferee:  # TODO find, fill or ignore
    pass


class Leagues:
    """ Source: unknown
    """
    def __init__(self):
        self.mines = True
        self.fixedIncome = None
        self.towers = True
        self.giants = True
        self.obstacles = None
        self.queenHp = 100  # ?
        
        
class Referee(AbstractReferee):
    def __init__(self, params):
        super().__init__()
        self.obstacles = []
        self.theGameManager.maxTurns = 200  # < why not Constants.XXX here?

        # Now, this gets interesting.
        # are Kotlin and Python RNGs 'compatible'?!?
        self.theRandom = Random(int(params['seed'])) if params['seed'] else Random()

        if self.gameManager.leagueLevel == 1:
            Leagues.mines = False
            Leagues.fixedIncome = Constants.WOOD_FIXED_INCOME
            Leagues.towers = False
            Leagues.giants = False
            Leagues.obstacles = Constants.OBSTACLE_PAIRS.sample()
        elif self.gameManager.leagueLevel == 2:
            Leagues.mines = False
            Leagues.fixedIncome = Constants.WOOD_FIXED_INCOME
            Leagues.obstacles = Constants.OBSTACLE_PAIRS.sample()
        elif self.gameManager.leagueLevel == 3:
            pass
        else:
            Leagues.queenHp = Constants.QUEEN_HP.sample() * Constants.QUEEN_HP_MULT

        self.gameManager.frameDuration = 750  # another magic number, can also be ignored, i guess.

        self.gameManager.players[0].enemyPlayer = self.gameManager.players[1]
        self.gameManager.players[1].enemyPlayer = self.gameManager.players[0]
        self.gameManager.players[1].isSecondPlayer = True
        for p in self.gameManager.players:
            p.health = Leagues.queenHp

        self.obstacles = buildMap()

        for activePlaye, invert in zip(self.gameManger.activePlayers, [False, True]):
            spawnDistance = 200  # Magic number
            if invert:
                corner = Vector2(Constants.WORLD_WIDTH - spawnDistance, Constants.WORLD_HEIGHT - spawnDistance)
            else:
                corner = Vector2(spawnDistance, spawnDistance)
        activePlayer.queenUnit = Queen(activePlayer)
        activePlayer.queenUnit.location = corner

        self.fixCollisions(self.allEntities())

        # for p in self.gameManager.activePlayers:
        #    p.hud.update()
        #    p.sendInputLine(len(self.obstacles))
        #    for o in self.obstacles:
        #        p.printObstacleInit(o)

        return params

    def allEntities(self):
        return [u for p in self.gameManager.players for u in p.allUnits()] + self.obstacles

    def gameTurn(self, turn):
        def sendGameStates():
            pass  # TODO Referee.kt lines 95 .. 117 missing
            # only needed if stdin/out interaction is necessary.

        def processPlayerActions():
            pass  # FIXME Referee.kt lines 119 .. 167
            # TODO most interesting stuff happens here..


"""
### MapBuilding.kt
"""

# TODO ...


if __name__ == '__main__':
    pass
