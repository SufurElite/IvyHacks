# Script that labels different board positions according to Stockfish's evaluation
# function and creates suitable chess board representations for the ANNs

from __future__ import division

import time
import chess
import chess.pgn
import chess.engine
import numpy as np
import os
from random import randint as rint 
GAMES_DIRECTORY = os.getcwd()+"/pgns/"	# Directory where the pgn games are saved
STORING_PATH = os.getcwd()+'/games_data/'		# Where to store the games evaluated by Stockfish
username = "Robert James Fischer"
# Import the Stockfish Engine
engine = chess.engine.SimpleEngine.popen_uci("stockfish")	# Be sure to have Stockfish installed
#engine.uci()

ImportantSquareSet = chess.SquareSet(

	chess.BB_D4 | chess.BB_D5 |
	chess.BB_C4 | chess.BB_C5 |
	chess.BB_E4 | chess.BB_E5 |
	chess.BB_F2 | chess.BB_F7 | 
	chess.BB_H2 | chess.BB_H7

	)

SquareSet = chess.SquareSet(

	chess.BB_A1 | chess.BB_A2 | chess.BB_A3 | chess.BB_A4 | chess.BB_A5 |
	chess.BB_A6 | chess.BB_A7 | chess.BB_A8 |
	chess.BB_B1 | chess.BB_B2 | chess.BB_B3 | chess.BB_B4 | chess.BB_B5 |
	chess.BB_B6 | chess.BB_B7 | chess.BB_B8 |
	chess.BB_C1 | chess.BB_C2 | chess.BB_C3 | chess.BB_C4 | chess.BB_C5 |
	chess.BB_C6 | chess.BB_C7 | chess.BB_C8 |
	chess.BB_D1 | chess.BB_D2 | chess.BB_D3 | chess.BB_D4 | chess.BB_D5 |
	chess.BB_D6 | chess.BB_D7 | chess.BB_D8 |
	chess.BB_A1 | chess.BB_E2 | chess.BB_E3 | chess.BB_E4 | chess.BB_E5 |
	chess.BB_E6 | chess.BB_E7 | chess.BB_E8 |
	chess.BB_F1 | chess.BB_F2 | chess.BB_F3 | chess.BB_F4 | chess.BB_F5 |
	chess.BB_F6 | chess.BB_F7 | chess.BB_F8 |
	chess.BB_G1 | chess.BB_G2 | chess.BB_G3 | chess.BB_G4 | chess.BB_G5 |
	chess.BB_G6 | chess.BB_G7 | chess.BB_G8 |
	chess.BB_H1 | chess.BB_H2 | chess.BB_H3 | chess.BB_H4 | chess.BB_H5 |
	chess.BB_H6 | chess.BB_H7 | chess.BB_H8
)

def load_game():
	for root, dirs, filenames in os.walk(GAMES_DIRECTORY):
		for f in filenames:
			if f.endswith('.pgn'):
				print("Current pgn : " + str(f))
				try:
					pgn = open(os.path.join(root, f), 'r')
					game = chess.pgn.read_game(pgn)
					process_game(game)
					os.remove(GAMES_DIRECTORY+"/"+str(f))
				except:
					pass

def splitter(inputStr, black):
	
	inputStr = format(inputStr, "064b")
	tmp = [inputStr[i:i+8] for i in range(0, len(inputStr), 8)]
	
	for i in range(0, len(tmp)):
		tmp2 = list(tmp[i])
		tmp2 = [int(x) * black for x in tmp2]
		tmp[i] = tmp2

	return tmp

def is_checked(board):

	if board.is_check() and board.turn is True:
		CheckedInfo = [-1] * 64
	
	elif board.is_check() and board.turn is False:
		CheckedInfo = [1] * 64
	
	elif not board.is_check():
		CheckedInfo = [0] * 64
	
	return CheckedInfo

def CnnBitmaps(board, e):
	
	P_input = splitter(int(board.pieces(chess.PAWN, chess.WHITE)), 1)
	R_input = splitter(int(board.pieces(chess.ROOK, chess.WHITE)), 1)
	N_input = splitter(int(board.pieces(chess.KNIGHT, chess.WHITE)), 1)
	B_input = splitter(int(board.pieces(chess.BISHOP, chess.WHITE)), 1)
	Q_input = splitter(int(board.pieces(chess.QUEEN, chess.WHITE)), 1)
	K_input = splitter(int(board.pieces(chess.KING, chess.WHITE)), 1)

	p_input = splitter(int(board.pieces(chess.PAWN, chess.BLACK)), -1)
	r_input = splitter(int(board.pieces(chess.ROOK, chess.BLACK)), -1)
	n_input = splitter(int(board.pieces(chess.KNIGHT, chess.BLACK)), -1)
	b_input = splitter(int(board.pieces(chess.BISHOP, chess.BLACK)), -1)
	q_input = splitter(int(board.pieces(chess.QUEEN, chess.BLACK)), -1)
	k_input = splitter(int(board.pieces(chess.KING, chess.BLACK)), -1)

	CheckedInfo = is_checked(board)

	SquareAttackers = []
	PinnedSquares = []

	ImportantAttackers = []
	
	for square in SquareSet:
		if board.is_attacked_by(chess.WHITE, square):
			SquareAttackers.append(1)
		elif board.is_attacked_by(chess.BLACK, square):
			SquareAttackers.append(-1)
		else:
			SquareAttackers.append(0) 

		if board.is_pinned(chess.WHITE, square):
			PinnedSquares.append(1)
		elif board.is_attacked_by(chess.BLACK, square):
			PinnedSquares.append(-1)
		else:
			PinnedSquares.append(-1)
	attackers_tracker = []
	for ImportantSquare in ImportantSquareSet:
		WhiteAttackers = board.attackers(chess.WHITE, ImportantSquare)
		BlackAttackers = board.attackers(chess.BLACK, ImportantSquare)
		
		if len(WhiteAttackers) > len(BlackAttackers):
			ImportantAttackersFeatures = [1] * 64
		elif len(WhiteAttackers) < len(BlackAttackers):
			ImportantAttackersFeatures = [-1] * 64
		else:
			ImportantAttackersFeatures = [0] * 64
	data = [P_input + R_input + N_input + B_input + Q_input + K_input + p_input + r_input + n_input + b_input + q_input + k_input]
	newData = []
	for i in np.asarray(data).flatten():
		newData.append(i)
	
	more_data = np.asarray([CheckedInfo + SquareAttackers + PinnedSquares + ImportantAttackersFeatures]).flatten()
	for i in more_data:
		newData.append(i)
	newData.append(e)
	
	return np.asarray(newData)

def process_game(board):
    movetime = .1	#Milliseconds, the lower the more approximate Stockfish's evaluation is
    res = engine.analyse(board, chess.engine.Limit(time=movetime))
    if not res["score"].is_mate():
        info = res["score"].relative.score()
    else:
        info = 10000
    if info is not None:				
        stock_evaluation = info/100 
        data = CnnBitmaps(board,stock_evaluation)
    return data
if __name__=="__main__":
	board = chess.Board()
	data = process_game(board)
	print(data)
	print(data.shape)



