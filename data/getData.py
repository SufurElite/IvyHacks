import lichess.api, chess.pgn
from lichess.format import SINGLE_PGN

def load_games(pgn_file="BehrGames.pgn"):
    """ Will load in the games from a pgn file, uses my games by default """
    games = ""
    with open(pgn_file) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game == None:
                break
            moves = game.mainline_moves()
            count = 0
            for i in moves:
                count+=1
            game.headers["Plycount"] = str(count)
            games+=str(game)+"\n\n\n"
    print("Number of games in pgn file: " + str(len(games)))
    with open("BehrGames2.pgn", "w+") as f:
        f.write(games)
    return games

def getGames(username, numberOfGames): 
    pgns = lichess.api.user_games(username, max=numberOfGames,format=SINGLE_PGN)
    with open(username+"Games.pgn", "w+") as f:
        f.write(pgns)

    return pgns

getGames("Behr",100000)
games = load_games()

#print(games[0])