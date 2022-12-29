from typing import List

from MapBuilding import buildMap, fixCollisions, flatMap, sample
from Player import Player
from constants import Leagues, Constants, KNIGHT, ARCHER, GIANT
from structures import Obstacle, Barracks, Mine, Tower, Queen, GiantCreep, KnightCreep, ArcherCreep
from vector2 import Vector2


class GameManager:
    maxTurns: int = 200
    leagueLevel: int
    solo: bool
    players: List[Player] = []
    activePlayers: List[Player] = []

    def __init__(self, leagueLevel=1, solo=False):
        self.players.append(Player("blue"))

        self.solo = solo
        if not self.solo:
            self.players.append(Player("red"))

        self.activePlayers = self.players
        self.leagueLevel = leagueLevel


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
        # Now, this gets interesting.
        # are Kotlin and Python RNGs 'compatible'?!?
        # self.theRandom = Random(int(params['seed'])) if params['seed'] else Random()

        if "leagueLevel" in params:
            self.gameManager.leagueLevel = params["leagueLevel"]

        if self.gameManager.leagueLevel == 1:
            Leagues.mines = False
            Leagues.fixedIncome = Constants.WOOD_FIXED_INCOME
            Leagues.towers = False
            Leagues.giants = False
            Leagues.obstacles = sample(Constants.OBSTACLE_PAIRS)
        elif self.gameManager.leagueLevel == 2:
            Leagues.mines = False
            Leagues.fixedIncome = Constants.WOOD_FIXED_INCOME
            Leagues.obstacles = sample(Constants.OBSTACLE_PAIRS)
        elif self.gameManager.leagueLevel == 3:
            pass
        else:
            Leagues.queenHp = sample(Constants.QUEEN_HP) * Constants.QUEEN_HP_MULT

        self.gameManager.frameDuration = 750  # another magic number, can also be ignored, i guess.

        if not self.gameManager.solo:
            self.gameManager.players[0].enemyPlayer = self.gameManager.players[1]
            self.gameManager.players[1].enemyPlayer = self.gameManager.players[0]
            self.gameManager.players[1].isSecondPlayer = True
        for p in self.gameManager.players:
            p.health = Leagues.queenHp

        self.obstacles = buildMap()

        for activePlayer, invert in zip(self.gameManager.activePlayers, [False, True]):
            spawnDistance = 200  # Magic number
            if invert:
                corner = Vector2(Constants.WORLD_WIDTH - spawnDistance, Constants.WORLD_HEIGHT - spawnDistance)
            else:
                corner = Vector2(spawnDistance, spawnDistance)
            activePlayer.queenUnit = Queen(activePlayer)
            activePlayer.queenUnit.location = corner

        # for e in self.allEntities():
        #     if e is None:
        #         print()

        fixCollisions(self.allEntities())

        # for p in self.gameManager.activePlayers:
        #    p.hud.update()
        #    p.sendInputLine(len(self.obstacles))
        #    for o in self.obstacles:
        #        p.printObstacleInit(o)

        # return params

    def get_buildings_of_player(self, player) -> List[Obstacle]:
        buildings = []
        for ent in self.obstacles:
            if ent.structure is not None and ent.structure.owner.name == player.name:
                buildings.append(ent)
        return buildings

    def allEntities(self):
        ent = []
        ent.extend(self.obstacles)
        for player in self.gameManager.players:
            ent.extend(player.allUnits())
        return ent
        # return [u for p in self.gameManager.players for u in p.allUnits()] + self.obstacles

    def scheduleBuilding(self, player: Player, obs: Obstacle, strucType: str, obstaclesAttemptedToBuildUpon: list,
                         scheduledBuildings: list):
        struc = obs.structure
        if struc is not None and struc.owner == player.enemyPlayer:
            raise Exception("Cannot build: owned by enemy player")
        if struc is Barracks and struc.owner == player and struc.isTraining:
            raise Exception("Cannot rebuild: training is in progress")
        obstaclesAttemptedToBuildUpon.append(obs)
        toks = strucType.split('-')
        firstToken = toks.pop(0)

        if firstToken == "MINE":
            if not Leagues.mines:
                raise ValueError("MINE NOT ACTIVATED")

            if isinstance(struc, Mine):
                struc.incomeRate += 1
                if struc.incomeRate > obs.maxMineSize: struc.incomeRate = obs.maxMineSize
            else:
                obs.setMine(player)
        elif firstToken == "TOWER":
            if not Leagues.towers:
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

            # Execute builds that remain TODO do we need this ?
            # scheduledBuildings.forEach { (player: Player, callback: () -> kotlin.Unit) ->
            #     try { callback.invoke() }
            #     catch (e: PlayerInputException) {
            #         System.err.println("WARNING: Deactivating ${player.nicknameToken} because of:")
            #     e.printStackTrace()
            #     player.kill("${e.message}")
            #     gameManager.addToGameSummary("${player.nicknameToken}: ${e.message}")
            #     }
            # }

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
                if struc is Mine and struc.owner != creep.owner:
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
                if (struc is Mine or struc is Barracks) and struc.owner != queen.owner:
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
                    barracks: Barracks = obstacle.structure
                    obsId = int(obs)
                    if obsId == obstacle.obstacleId:
                        # obs = self.obstacles[toks[1]]
                        if not isinstance(obstacle.structure, Barracks):
                            raise ValueError(f"Cannot spawn from {obstacle.obstacleId}: not a barracks")
                        if obstacle.structure.owner != player:
                            raise ValueError(f"Cannot spawn from {obstacle.obstacleId}: not owned")
                        if obstacle.structure.isTraining:
                            raise ValueError(f"Barracks {obstacle.obstacleId} is training")
                        buildingBarracks.append(barracks)
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
                allObstacles.append(obstacle)

            self.obstacles = allObstacles
            fixCollisions(self.allEntities())

            # TODO remove duplicates
            # if len(buildingBarracks() > buildingBarracks.toSet().size:
            #     raise ValueError("Training from some barracks more than once")

            sumcosts = sum(map(lambda item: item.creepType.cost, buildingBarracks))
            if sumcosts > player.gold:
                raise ValueError("Training too many creeps ($sum total gold requested)")

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

                dist = obs.location.distanceTo(queen.location)
                if dist < queen.radius + obs.radius + Constants.TOUCHING_DELTA:
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
            it.goldPerTurn = Leagues.fixedIncome
            it.gold += Leagues.fixedIncome

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
