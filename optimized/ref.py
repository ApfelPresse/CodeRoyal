from __future__ import annotations

import math
import random
from abc import abstractmethod
from functools import reduce
from typing import List

import numpy as np


class GameManager:
    maxTurns: int = 200
    leagueLevel: int
    solo: bool
    players: List[Player]
    activePlayers: List[Player]

    def __init__(self, league_level=1, solo=False):
        self.players = []
        self.activePlayers = []
        self.players.append(Player("blue"))

        self.solo = solo
        if not self.solo:
            self.players.append(Player("red"))

        self.activePlayers = self.players
        self.leagueLevel = league_level


class AbstractReferee:  # TODO find, fill or ignore
    gameManager: GameManager

    def __init__(self, solo):
        self.gameManager = GameManager(solo=solo)


class Referee(AbstractReferee):
    obstacles: List[Obstacle]

    end_game: bool

    def __init__(self, params, solo=False):
        super().__init__(solo=solo)
        self.obstacles = []
        self.gameManager.maxTurns = 200  # < why not Constants.XXX here?

        self.end_game = False
        self.turn = 0

        if "leagueLevel" in params:
            self.gameManager.leagueLevel = params["leagueLevel"]

        if self.gameManager.leagueLevel == 1:
            self.towers = False
            self.giants = False
            self.mines = False
            self.fixedIncome = Constants.WOOD_FIXED_INCOME
            self.obstacles_count = sample(Constants.OBSTACLE_PAIRS)
            self.queenHp = 100
        elif self.gameManager.leagueLevel == 2:
            self.towers = True
            self.giants = True
            self.mines = False
            self.fixedIncome = Constants.WOOD_FIXED_INCOME
            self.obstacles_count = sample(Constants.OBSTACLE_PAIRS)
            self.queenHp = 100
        elif self.gameManager.leagueLevel == 3:
            self.towers = True
            self.giants = True
            self.mines = True
            self.fixedIncome = 0
            self.obstacles_count = Constants.OBSTACLE_PAIRS[-1]
            self.queenHp = 100
        else:
            self.towers = True
            self.giants = True
            self.mines = True
            self.fixedIncome = 0
            self.obstacles_count = Constants.OBSTACLE_PAIRS[-1]
            self.queenHp = sample(Constants.QUEEN_HP) * Constants.QUEEN_HP_MULT

        self.gameManager.frameDuration = 750  # another magic number, can also be ignored, i guess.

        if not self.gameManager.solo:
            self.gameManager.players[0].enemyPlayer = self.gameManager.players[1]
            self.gameManager.players[1].enemyPlayer = self.gameManager.players[0]
            self.gameManager.players[1].isSecondPlayer = True
        for p in self.gameManager.players:
            p.health = self.queenHp

        self.obstacles = buildMap(self.obstacles_count)

        for activePlayer, invert in zip(self.gameManager.activePlayers, [False, True]):
            spawnDistance = 200  # Magic number
            if invert:
                corner = Vector2(Constants.WORLD_WIDTH - spawnDistance, Constants.WORLD_HEIGHT - spawnDistance)
            else:
                corner = Vector2(spawnDistance, spawnDistance)
            activePlayer.queenUnit = Queen(activePlayer)
            activePlayer.queenUnit.location = corner

        fixCollisions(self.allEntities())

    def get_buildings_of_player(self, player) -> List[Obstacle]:
        buildings = []
        for ent in self.obstacles:
            if ent.structure is not None and ent.structure.owner.name == player.name:
                buildings.append(ent)
        return buildings

    def game_end(self):
        for player in self.gameManager.players:
            if player.queenUnit.health <= 0:
                return True
        return False

    def all_units(self) -> List[Unit]:
        units = []
        for player in self.gameManager.players:
            units.extend(player.allUnits())
        return units

    def allEntities(self):
        ent = []
        ent.extend(self.obstacles)
        ent.extend(self.all_units())
        return ent
        # return [u for p in self.gameManager.players for u in p.allUnits()] + self.obstacles

    def scheduleBuilding(self, player: Player, obs: Obstacle, strucType: str, obstaclesAttemptedToBuildUpon: list,
                         scheduledBuildings: list):
        struc = obs.structure
        if struc is not None and struc.owner == player.enemyPlayer:
            raise Exception("Cannot build: owned by enemy player")
        if isinstance(struc, Barracks) and struc.owner == player and struc.isTraining:
            raise Exception("Cannot rebuild: training is in progress")
        obstaclesAttemptedToBuildUpon.append(obs)
        toks = strucType.split('-')
        firstToken = toks.pop(0)

        if firstToken == "MINE":
            if not self.mines:
                raise ValueError("MINE NOT ACTIVATED")

            if isinstance(struc, Mine):
                struc.incomeRate += 1
                if struc.incomeRate > obs.maxMineSize:
                    struc.incomeRate = obs.maxMineSize
            else:
                obs.setMine(player)
        elif firstToken == "TOWER":
            if not self.towers:
                raise ValueError("TOWERS NOT ACTIVATED")

            if isinstance(struc, Tower):
                struc.health += Constants.TOWER_HP_INCREMENT
                if struc.health > Constants.TOWER_HP_MAXIMUM: struc.health = Constants.TOWER_HP_MAXIMUM
            else:
                obs.setTower(player, Constants.TOWER_HP_INITIAL)

        elif firstToken == "BARRACKS":
            creepInputType = toks.pop(0)
            if creepInputType == "KNIGHT":
                creepType = KNIGHT
            elif creepInputType == "ARCHER":
                creepType = ARCHER
            elif creepInputType == "GIANT":
                creepType = GIANT
            else:
                raise Exception(f"CreepType {creepInputType} not found")
            obs.setBarracks(player, creepType)
        else:
            raise ValueError(f"Invalid structure type: {firstToken}")
        scheduledBuildings.append(player)

        return obstaclesAttemptedToBuildUpon, scheduledBuildings

    def processPlayerActions(self, turn):
        obstaclesAttemptedToBuildUpon = []
        scheduledBuildings = []

        obstaclesAttemptedToBuildUpon, scheduledBuildings = self.player_loop(obstaclesAttemptedToBuildUpon,
                                                                             scheduledBuildings)

        # If they're both building onto the same one, then actually build only one: depending on parity of the turn number
        if len(obstaclesAttemptedToBuildUpon) == 2 and obstaclesAttemptedToBuildUpon[0] == \
                obstaclesAttemptedToBuildUpon[1]:
            del scheduledBuildings[turn % 2]

    def processCreeps(self):
        # TODO Sorted
        allCreeps = flatMap(list(map(lambda player: player.activeCreeps, self.gameManager.activePlayers)))
        for _ in range(5):
            for creep in allCreeps:
                creep.move(1.0 / 5)
            fixCollisions(self.allEntities(), 1)

        for creep in allCreeps:
            creep.dealDamage()

        for creep in allCreeps:
            dist_obstacle = None
            closestObstacle = None
            for obs in self.obstacles:
                dist = obs.location.distanceTo(creep.location)
                if dist_obstacle is None or dist < dist_obstacle:
                    dist_obstacle = dist
                    closestObstacle = obs
                if closestObstacle.location.distanceTo(
                        creep.location) >= closestObstacle.radius + creep.radius + Constants.TOUCHING_DELTA:
                    continue
                struc = closestObstacle.structure
                if isinstance(struc, Mine) and struc.owner != creep.owner:
                    closestObstacle.structure = None
        for creep in allCreeps:
            creep.damage(1)

        for creep in allCreeps:
            creep.finalizeFrame()

        for it in self.gameManager.activePlayers:
            queen = it.queenUnit

            dist_obstacle = None
            closestObstacle = None
            for obs in self.obstacles:
                dist = obs.location.distanceTo(queen.location)
                if dist_obstacle is None or dist < dist_obstacle:
                    dist_obstacle = dist
                    closestObstacle = obs
                if closestObstacle.location.distanceTo(
                        queen.location) >= closestObstacle.radius + queen.radius + Constants.TOUCHING_DELTA:
                    continue
                struc = closestObstacle.structure
                if (isinstance(struc, Mine) or isinstance(struc, Barracks)) and struc.owner != queen.owner:
                    closestObstacle.structure = None

    def player_loop(self, obstaclesAttemptedToBuildUpon, scheduledBuildings):

        for player in self.gameManager.activePlayers:
            queen = player.queenUnit

            toks = player.outputs[1].split(" ")

            if toks.pop(0) != "TRAIN":
                raise ValueError("Expected TRAIN on the second line")

            # Process building creeps
            buildingBarracks: List[Barracks] = []
            allObstacles: List[Obstacle] = []
            for obstacle in self.obstacles:
                for obs in toks:
                    obsId = int(obs)
                    if obsId == obstacle.obstacleId:
                        # obs = self.obstacles[toks[1]]
                        if not isinstance(obstacle.structure, Barracks):
                            raise ValueError(f"Cannot spawn from {obstacle.obstacleId}: not a barracks")
                        if obstacle.structure.owner != player:
                            raise ValueError(f"Cannot spawn from {obstacle.obstacleId}: not owned")
                        if obstacle.structure.isTraining:
                            raise ValueError(f"Barracks {obstacle.obstacleId} is training")
                        buildingBarracks.append(obstacle)

                allObstacles.append(obstacle)

            self.obstacles = allObstacles
            fixCollisions(self.allEntities())

            # TODO remove duplicates
            # if len(buildingBarracks() > buildingBarracks.toSet().size:
            #     raise ValueError("Training from some barracks more than once")

            sumcosts = sum(map(lambda item: item.structure.creepType.cost, buildingBarracks))
            if sumcosts > player.gold:
                print(
                    f"WARNING: Player {player.name} - Training too many creeps ({sumcosts} total gold requested and player has {player.gold})")
                continue

            for obstacle in buildingBarracks:
                barracks: Barracks = obstacle.structure
                barracks.progress = 0
                barracks.isTraining = True

                def on_complete(ob):
                    structure = ob.structure
                    for iter in range(structure.creepType.count):
                        if structure.creepType.assetName == KNIGHT.assetName:
                            it = KnightCreep(ob.structure.owner)
                        elif structure.creepType.assetName == ARCHER.assetName:
                            it = ArcherCreep(ob.structure.owner)
                        elif structure.creepType.assetName == GIANT.assetName:
                            it = GiantCreep(ob.structure.owner, self.obstacles)
                        else:
                            raise ValueError()

                        c = -1 if ob.structure.owner.isSecondPlayer else 1
                        it.location = ob.location + Vector2(c * iter, c * iter)
                        it.finalizeFrame()
                        it.location = it.location.towards(ob.structure.owner.enemyPlayer.queenUnit.location,
                                                          30.0)
                        it.finalizeFrame()
                        # it.commitState(0.0)
                        ob.structure.owner.activeCreeps.append(it)

                barracks.onComplete = on_complete
                obstacle.structure = barracks

            player.gold -= sumcosts

            # Process queen command
            line = player.outputs[0].strip()
            toks = line.split(" ")
            command = toks.pop(0)

            if command == "WAIT":
                pass
            elif command == "MOVE":
                try:
                    x = int(toks.pop(0))
                    y = int(toks.pop(0))
                    queen.moveTowards(Vector2(x, y))
                except Exception as ex:
                    raise ValueError("In MOVE command, x and y must be integers")
            elif command == "BUILD":
                try:
                    obsId = int(toks.pop(0))
                except Exception as ex:
                    raise ValueError("Could not parse siteId")
                # if obsId not in self.obstacles:
                #     raise ValueError(f"Site id {obsId} does not exist")

                # list(filter(lambda item: item.obstacleId, self.obstacles))[0]
                obss = list(filter(lambda item: item.obstacleId == obsId, self.obstacles))
                if len(obss) == 0 or len(obss) > 1:
                    raise ValueError(f"Site id {obsId} does not exist")

                obs = obss[0]
                strucType = toks.pop(0)

                # dist = obs.location.distanceTo(queen.location)
                # if dist < queen.radius + obs.radius + Constants.TOUCHING_DELTA:
                if queen.is_in_range_of(obs):
                    obstaclesAttemptedToBuildUpon, scheduledBuildings = self.scheduleBuilding(player, obs,
                                                                                              strucType,
                                                                                              obstaclesAttemptedToBuildUpon,
                                                                                              scheduledBuildings)
                else:
                    queen.moveTowards(obs.location)
            else:
                raise ValueError(f"Didn't understand command: {command}")
            # if (toks.hasNext()) throw PlayerInputException("Too many tokens after $command command")

            # exceptions
            # timout exeception
            # player.kill("Timeout!")

        return obstaclesAttemptedToBuildUpon, scheduledBuildings

    def gameTurn(self, turn):
        self.turn = turn
        for it in self.gameManager.activePlayers:
            it.goldPerTurn = 0

        self.processPlayerActions(turn)
        self.processCreeps()

        for it in self.obstacles:
            it.act()

        for it in self.gameManager.activePlayers:
            it.goldPerTurn = self.fixedIncome
            it.gold += self.fixedIncome

        for player in self.gameManager.activePlayers:
            for it in player.activeCreeps:
                if it.health > 0:
                    continue
                player.activeCreeps.remove(it)
                # death animation

        for player in self.gameManager.activePlayers:
            player.checkQueenHealth()
            self.end_game = True

        for it in self.allEntities():
            it.location = it.location.snapToIntegers()


def flatMap(array: List[List]):
    return reduce(list.__add__, array)


class FieldObject:
    location: Vector2
    radius = int
    mass = int

    def __init__(self):
        self.location = None
        self.radius = 0
        self.mass = 0  # 0 := immovable


def collisionCheck(entities: List[FieldObject], acceptableGap: float = 0.0) -> bool:
    for iu1, u1 in enumerate(entities):
        rad = u1.radius
        clampDist = Constants.OBSTACLE_GAP + rad if u1.mass == 0 else rad
        u1.location = u1.location.clampWithin(clampDist, Constants.WORLD_WIDTH - clampDist, clampDist,
                                              Constants.WORLD_HEIGHT - clampDist)

        u1.location.check_if_not_smaller_zero()
        for iu2, u2 in enumerate(entities):
            if iu1 == iu2:
                continue
            overlap = u1.radius + u2.radius + acceptableGap - u1.location.distanceTo(u2.location)  # TODO: Fix this?
            if overlap <= 1e-6:
                continue
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

                u1.location.check_if_not_smaller_zero()
                u2.location.check_if_not_smaller_zero()
                return True
    return False


class Obstacle(FieldObject):
    structure: Structure
    obstacleId: int

    def __init__(self, maxMineSize, initialGold, initialRadius, initialLocation, obstacle_id):
        super().__init__()

        self.structure = None
        # global nextObstacleId
        # nextObstacleId += 1
        self.maxMineSize = maxMineSize
        self.obstacleId = obstacle_id
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
        self.structure = Mine(obstacle=self, owner=owner, incomeRate=1)

    def setTower(self, owner, health):
        self.structure = Tower(self, owner, 0, health)

    def setBarracks(self, owner, creepType):
        self.structure = Barracks(self, owner=owner, creepType=creepType)

    def __str__(self):
        return f"{self.obstacleId} - {self.location}"


def buildObstacles(obstacles: int) -> List[Obstacle]:
    obstaclePairs = []
    obstacle_id = 0
    for _ in range(1, obstacles):
        gold = sample(Constants.OBSTACLE_GOLD_RANGE)
        radius = sample(Constants.OBSTACLE_RADIUS_RANGE)
        l1 = Vector2(random.randint(0, Constants.WORLD_WIDTH), random.randint(0, Constants.WORLD_HEIGHT))
        l2 = Vector2(Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT) - l1
        gold_max_mine_size = sample(Constants.OBSTACLE_MINE_BASESIZE_RANGE)

        obstacle_id += 1
        o1 = Obstacle(maxMineSize=gold_max_mine_size, initialGold=gold, initialRadius=radius, initialLocation=l1,
                      obstacle_id=obstacle_id)

        obstacle_id += 1
        o2 = Obstacle(maxMineSize=gold_max_mine_size, initialGold=gold, initialRadius=radius, initialLocation=l2,
                      obstacle_id=obstacle_id)

        obstaclePairs.append([o1, o2])

    obstacles = flatMap(obstaclePairs)

    collision_results = []
    for i in range(1, 100 + 1):
        for pair in obstaclePairs:
            o1, o2 = pair
            mid = (o1.location + Vector2(Constants.WORLD_WIDTH - o2.location.x,
                                         Constants.WORLD_HEIGHT - o2.location.y)) / 2.0
            o1.location = mid
            o2.location = Vector2(Constants.WORLD_WIDTH - mid.x, Constants.WORLD_HEIGHT - mid.y)

        collision_results.append(collisionCheck(obstacles, float(Constants.OBSTACLE_GAP)))
    return obstacles


def sample(list_like):
    return random.choice(list_like)


def buildMap(obstacles_count: int) -> List[Obstacle]:
    obstacles = None
    while obstacles is None:
        obstacles = buildObstacles(obstacles=obstacles_count)

    mapCenter = Vector2(len(Constants.viewportX) / 2, len(Constants.viewportY) / 2)
    for o in obstacles:
        o.location = o.location.snapToIntegers()
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_1:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
        if o.location.distanceTo(mapCenter) < Constants.OBSTACLE_GOLD_INCREASE_DISTANCE_2:
            o.maxMineSize += 1
            o.gold += Constants.OBSTACLE_GOLD_INCREASE
    return obstacles


def fixCollisions(entities: List[FieldObject], maxIterations: int = 999):
    for _ in range(maxIterations):
        if not collisionCheck(entities):
            return


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
        self.obstacles = obstacles

    def __str__(self):
        return f"GiantCreep - {self.location}"

    def move(self, frames):
        """
        params frames - double, ?
        """
        # TODO (how/where to) get current obstacles ? - set externally?
        opp_structures = []
        for struct in self.obstacles:
            if struct.structure is None:
                continue
            if not isinstance(struct.structure, Tower):
                continue
            if struct.structure.owner != self.owner.enemyPlayer:
                continue
            opp_structures.append(struct)

        # opp_structures = list(filter(
        #     lambda struct: struct.structure is not None
        #                    and isinstance(struct.structure, Tower)
        #                    and struct.structure.owner == self.owner.enemyPlayer,
        #     self.obstacles))

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

    def __str__(self):
        return f"KnightCreep - {self.location}"

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

    def __str__(self):
        return f"ArcherCreep - {self.location}"

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


class Player():
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
                "income_rate": struc.incomeRate if visible else -1  # param1
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


class Vector2:
    """Vector2.kt : Vector2
    """
    x: float
    y: float

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def snapToIntegers(self):
        return Vector2(round(self.x), round(self.y))

    # TODO Numpy faster numpy.linalg.norm(other-self) ?
    def distanceTo(self, other: Vector2) -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def check_if_not_smaller_zero(self):
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

    def copy(self):
        return Vector2(self.x, self.y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __truediv__(self, value: float):
        x = self.x / value
        y = self.y / value
        return Vector2(x, y)

    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def clampWithin(self, minX: float, maxX: float, minY: float, maxY: float) -> Vector2:
        if self.x < minX:
            nx = minX
        elif self.x > maxX:
            nx = maxX
        else:
            nx = self.x

        if self.y < minY:
            ny = minY
        elif self.y > maxY:
            ny = maxY
        else:
            ny = self.y

        return Vector2(nx, ny)

    def lengthSquared(self):
        return self.x * self.x + self.y * self.y

    def resizedTo(self, newLength):
        return self.normalized() * newLength

    def normalized(self):
        length = math.sqrt(self.lengthSquared())
        if length < 1e-6:
            return Vector2(1, 0)
        return Vector2(self.x / length, self.y / length)

    def towards(self, other: Vector2, maxDistance: float):
        if self.distanceTo(other) < maxDistance:
            return other
        else:
            new_loc = self + (other - self).resizedTo(maxDistance)
            return new_loc


class Constants:
    STARTING_GOLD = 100

    WORLD_WIDTH = 1920
    WORLD_HEIGHT = 1000

    viewportX = np.arange(0, WORLD_WIDTH + 1)
    viewportY = np.arange(0, WORLD_HEIGHT + 1)

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
    OBSTACLE_MINE_BASESIZE_RANGE = np.arange(1, 3 + 1)  # 1..3
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

    TOUCHING_DELTA = 5
    WOOD_FIXED_INCOME = 10


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
