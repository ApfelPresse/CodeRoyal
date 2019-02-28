import copy
from abc import abstractmethod

import numpy as np

h = 1000
l = 1920
field = np.zeros((h, l))  # << NO.


viewportX = list(range(l))
viewportY = list(range(h))


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

    def __init__(self, count, cost, speed, range_, radius, mass, hp, buildTime, assetName):
        super().__init__()
        self.count = count
        self.cost = cost
        self.speed = speed
        self.range = range_
        self.radius = radius
        self.mass = mass
        self.hp = hp
        self.buildTime = buildTime
        self.assetName = assetName


KNIGHT = CreepType(4, 80, 100, 0, 20, 400, 30, 5, "Unite_Fantassin")
ARCHER = CreepType(2, 100, 75, 200, 25, 900, 45, 8, "Unite_Archer")
GIANT = CreepType(1, 140, 50, 0, 40, 2000, 200, 10, "Unite_Siege")


#class Distance: << (Vector2.kt : Distance) - IGNORED/Useless

class Vector2:
    """Vector2.kt : Vector2
    """
    def __int__(self, x=0, y=0):
        self.x = x
        self.y = y

    # TODO Numpy faster numpy.linalg.norm(other-self) ?
    def distanceTo(self, other) -> float:
        return np.sqrt((self.x - other.x) ** 2 - (self.y - other.y) ** 2)


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
        #self.hud = None
        
    #def getExpectedOutputLines: return 2
    #def fixOwner(self, player): raise NotImplementedError()
    #def printObstacleInit(self, obstacle): raise NotImplementedError()
    #def printObstaclePerTurn(self, obstacle): raise NotImplementedError()
    
    def allUnits(self):
        return self.activeCreeps + [self.queeUnit]  # TODO not sure <<
    
    def checkQueenHealth(self):
        self.queenUnit.health = self.health  # << really ?? double bookkeeping here.
        if self.health == 0:
            self.deactivate("Dead queen")
        #self.hud.update()

    def kill(reason):
        self.score = -1
        self.deactivate(reason)
    
    

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

    def __init(self, owner):
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
    
    def __int__(self, owner):
        super().__init__(owner)  # TODO
        self.mass = Constants.QUEEN_MASS
    
    def moveTowards(self, target):
        """
        param target - Vector2
        """
        self.location = self.location.towards(target, Constants.QUEEN_SPEED)
    
    def damage(self, damageAmount):
        if (damageAmount <= 0):
            return
        owner.health = max(0, owner.health - damageAmount)  # TODO CHECK: maybe just ignore owner, and use self here?!?
        # self.health = max(0, owner.health - damageAmount)


class Creep(Unit):
    """Characters.kt : Creep
    """

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
        opp_structures = filter(lambda struct:struct != None and struct.owner and struct.owner == self.owner.enemyPlayer)
        target = min(opp_structures, key=lambda struct:struct.location.distanceTo(self.location))
        
        self.location = self.location.towards(target)

    def dealDamage(self):
        pass  # TODO
    
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


"""
###  from Structures.kt
"""

def Obstacle(FieldObject):
    """Structures.kt : Obstacle
    """
    nextObstacleId = 0
    
    def __init__(maxMineSize, initialGold, initialRadius, initialLocation):
        super().__init__()  # TODO CHECK call
        self.maxMineSize = maxMineSize
        self.initialGold = initialGold
        self.initialRadius = initialRadius
        self.initialLocation = initialLocation
        self.obstacleId = Obstacle.nextObstacleId
        Obstacle.nextObstacleId += 1
        
        self.mass = 0
        assert(initialGold >= 0)
        self.gold = initialGold
        #self.obstacleImage = None
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
        
    def act():
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
        cash = min(incomeRae, self.obstacle.gold)
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
            closestEnemy = min(self.owner.enemyPlayer.activeCreeps, key=lambda it: it.lcation.distanceTo(self.obstacle.location))
        enemyQueen = self.owner.enemyPlayer.queenUnit
        
        if closestEnemy != None and closestEnemy.location.distanceTo(obstacle.location) < attackRadius:
            self.attackTarget = closestEnemy
            self.damageCreep(self.attackTarget)
        elif enemyQueen.location.distanceTo(obstacle.location) < attackRadius:
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
            if self.progress = self.progressMax:
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
    
class Referee(AbstractReferee):
    def __init__(self, params):
        super().__init__()
        self.obstacles = []
        self.theGameManager.maxTurns = 200  # < why not Constants.XXX here?
       
        # Now, this gets interesting.
        # are Kotlin and Python RNGs 'compatible'?!?
        self.theRandom = Random(int(params['seed']) if params['seed'] else Random()
   
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
        else:
            Leagues.queenHp = Constants.QUEEN_HP.sample() * Constants.QUEEN_HP_MULT
        
        self.gameManager.frameDuration = 750  # another magic number, can also be ignored, i guess.
        
        self.gameManager.players[0].enemyPlayer = self.gameManager.players[1]
        self.gameManager.players[01.enemyPlayer = self.gameManager.players[0]
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
        
        #for p in self.gameManager.activePlayers:
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
    
