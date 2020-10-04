import chess.pgn
import os
PATH = os.getcwd()

pgn = open(PATH+"/MagnusCarlsen.pgn")

first_game = chess.pgn.read_game(pgn)

while first_game: 
    game_name = first_game.headers['White'] + '-' + first_game.headers['Black']
    print(game_name)
    out = open(PATH+"/pgns/"+game_name.replace("/","")+'.pgn', 'w')
    exporter = chess.pgn.FileExporter(out)
    first_game.accept(exporter)
    first_game = chess.pgn.read_game(pgn)
