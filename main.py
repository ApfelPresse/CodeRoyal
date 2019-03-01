from characters import *
from vector2 import *

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

    def processPlayerActions(self):
        obstaclesAttemptedToBuildUpon = []
        scheduledBuildings = []

    def scheduleBuilding(self, player: Player, obs: Obstacle, strucType: str):
        struc = obs.structure
        if struc is not None and struc.owner == player.enemyPlayer:
            print("Cannot build: owned by enemy player")
            return
        if isinstance(struc, Barracks) and struc.owner == player and struc.isTraining:
            print("Cannot rebuild: training is in progress")
            return
        self.obstaclesAttemptedToBuildUpon += obs
        toks = strucType.split("-")

        if len(toks) == 0:
            print("Structure type must be specified")

        for firstToken in toks:
            if firstToken == "MINE" and Leagues.mines:
                if isinstance(struc, Mine):
                    struc: Mine = struc
                    struc.incomeRate += 1
                    if struc.incomeRate > obs.maxMineSize:
                        struc.incomeRate = obs.maxMineSize
                    else:
                        obs.setMine(player)
            elif firstToken == "TOWER" and Leagues.towers:
                if isinstance(struc, Tower):
                    struc: Tower = struc
                    struc.health += Constants.TOWER_HP_INCREMENT
                    if struc.health > Constants.TOWER_HP_MAXIMUM:
                        struc.health = Constants.TOWER_HP_MAXIMUM
                else:
                    obs.setTower(player, Constants.TOWER_HP_INITIAL)
            elif firstToken == "BARRACKS":
                pass


"""
### MapBuilding.kt
"""
Pair = tuple


def sample(list_like):
    """uses global <theRandom>
    """
    return theRandom.sample(list_like)


def buildMap():
    def buildObstacles():
        """
        uses global <nextObstacleId> ?
        uses global <theRandom>
        """
        Obstacle.nextObstacleId = 0  # maybe wrong.//is this even "used", WTF?!?
        obstaclePairs = []
        for _i in range(Leagues.obstacles):
            rate = sample(Constants.OBSTACLE_MINE_BASESIZE_RANGE)
            gold = sample(Constants.OBSTACLE_GOLD_RANGE)
            radius = sample(Constants.OBSTACLE_RADIUS_RANGE)
            l1 = Vector2.random(theRandom, WORLD_WIDTH, WORLD_HEIGHT)  # do we have this?!?
            l2 = Vector2(WORLD_WIDTH, WORLD_HEIGHT) - l1  # letssee if this works :P
            a = Obstacle(rate, gold, radius, l1)
            b = Obstacle(rate, gold, radius, l2)
            obstaclePairs.append([a, b])
            obstacles.append(a)
            obstacles.append(b)

        # cool code bro! TODO check this part in original...! lines 35-46
        coll_results = []  # anyway ignored later!
        for _ in range(100):
            # am i missing something?!? TODO FIXME CHECK
            # i feel this part is hilariously bad ...
            mid = (o1.location + Vector2(Constants.WORLD_WIDTH - o2.location.x,
                                         Constants.WORLD_HEIGHT - o2.location.y)) / 2.0
            o1.location = mid
            o2.location = Vector2(Constants.WORLD_WIDTH - mid.x,
                                  Constants.WORLD_HEIGHT - mid.y)
            coll_results.append(collisionCheck(obstacles, Constants.OBSTACLE_GAP))
        if all(coll_results):
            return obstacles
        return obstacles

    obstacles = None
    while obstales is None:
        obstales = buildObstacles()

    mapCenter = Vector2(len(viewportX) / 2, len(viewportY) / 2)
    for o in obstacles:
        o.location = o.location.snapToIntegers()  # TODO where is this? :D
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_1:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_2:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
    return obstacles

    def collisionCheck(entities, accetpableGap=0.0):
        """
        param entities - List<FieldObject>
        """
        result = []
        for i, u1 in enumerate(entities):
            rad = u1.radius
            clampDist = Constants.OBSTACLE_GAP + rad if u1.mass == 0 else rad
            u1.location = i1.location.clampWithin(
                clampDist, Constants.WORLD_WIDTH - clampDist,
                clampDist, Constants.WORLD_HEIGHT - clampDist)
            for j, u2 in enumerate(entities):
                if i == j:
                    continue
                dist = u1.location.distanceTo(u2.location)
                overlap = u1.radius + u2.radius + acceptableGap - dist  # IN ORIGINAL: "// TODO: Fix this?"
                if overlap <= 1e-6:
                    result.append(False)
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
                    results.append(True)
        return any(result)  # wow, this was ugly. also this return seems flawed.


if __name__ == '__main__':
    pass
