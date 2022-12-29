from constants import Constants


class AbstractPlayer:
    pass  # TODO find / fill


class Player(AbstractPlayer):
    """Player.kt : Player
    """

    # activeCreeps: List[Creep]

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
        ent = []
        ent.extend(self.activeCreeps)
        ent.append(self.queenUnit)
        return ent

    def checkQueenHealth(self):
        self.queenUnit.health = self.health  # << really ?? double bookkeeping here.
        if self.health == 0:
            raise Exception("DEAD QUEEN")
            # self.deactivate("Dead queen")
        # self.hud.update()

    def kill(self, reason):
        self.score = -1
        raise Exception(reason)
