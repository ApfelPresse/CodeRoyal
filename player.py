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
