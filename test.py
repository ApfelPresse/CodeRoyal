from Ref import Referee

if __name__ == '__main__':

    params = {
        "seed": 123
    }
    ref = Referee(params)

    for obs in ref.obstacles:
        print(obs)

    for player in ref.gameManager.activePlayers:
        player.outputs = [
            "BUILD 1 BARRACKS-KNIGHT",
            "TRAIN 1",
        ]

    for i in range(1000):
        print(f"Round {i}")
        ref.gameTurn(i)
        for player in ref.gameManager.activePlayers:
            print(player.queenUnit.location)
