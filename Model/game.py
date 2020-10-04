import chess
import tfdeploy as td
import itertools
import copy
import keras
import tensorflow as tf
from keras.models import Sequential, model_from_json
from keras.layers import Dense
from tensorflow.python.keras.optimizers import TFOptimizer
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np

def loadModel():
    # load json and create model
    json_file = open('modfiles/magnus.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("modfiles/magnus.h5")
    print("Loaded model from disk")
    loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    """
    x = [X[0]]
    X = [X]
    for i in range(len(X[0])):
        tmp = [[np.array(X[0][i])]]
        print(loaded_model.predict_classes(tmp))
        print(y[i])
        input()
    """
    return loaded_model

def _bitboard(board):
        """
        Converts the chess.Board representation of the position
        to a binary bit-string representation called bitboard.
        There are two sides (White and Black), 6 piece types
        (pawn, knight, bishop, rook, queen, king), and 64 squares.
        Therefore, in order to represent a position as a binary
        bit-string, we would require 2 x 6 x 64 = 768 bits. There are
        an additional five bits that represent the side to move (1 for
        White and 0 for Black) and castling rights (White can castle
        kingside, White can castle queenside, Black can castle kingside,
        and Black can castle queenside).
        @param board: position of the chess board
        @type board: chess.Board
        """
        # binary bit-string
        bitboard = np.zeros(773, dtype=bool)

        # every piece on the board gets its bit-representation
        piece_map = board.piece_map()
        for square in piece_map.keys():
            piece = piece_map[square]
            color = int(piece.color)
            piece_type = piece.piece_type
            index = (1 - color) * 6 * 64 + (piece_type - 1) * 64 + square
            bitboard[index] = 1

        # side to move
        bitboard[768] = int(board.turn)

        # castling rights
        bitboard[769] = int(board.has_kingside_castling_rights(chess.WHITE))
        bitboard[770] = int(board.has_queenside_castling_rights(chess.WHITE))
        bitboard[771] = int(board.has_kingside_castling_rights(chess.BLACK))
        bitboard[772] = int(board.has_queenside_castling_rights(chess.BLACK))

        return bitboard

def netPredict(first, second):
    global model
	
    x_1 = _bitboard(first)
    x_2 = _bitboard(second)

    res1 = model.predict([[x_1]])
    res2 = model.predict([[x_2]])
    
    if res1[0] > res2[0]:
        return(first, second)
    else:
        return(second, first)

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
	if depth == 0:
		return node
	if maximizingPlayer:
		v = -1
		for move in node.legal_moves:
			cur = copy.copy(node)
			cur.push(move)
			if v == -1:
				v = alphabeta(cur, depth-1, alpha, beta, False) 
			if alpha == -1:
				alpha = v
		
			v = netPredict(v, alphabeta(cur, depth-1, alpha, beta, False))[0]
			alpha = netPredict(alpha, v)[0] 
			if beta != 1:
				if netPredict(alpha, beta)[0] == alpha:
					break
		return v 
	else:
		v = 1
		for move in node.legal_moves:
			cur = copy.copy(node)
			cur.push(move)
			if v == 1:
				v = alphabeta(cur, depth-1, alpha, beta, True) 
			if beta == 1:
				beta = v
			
			v = netPredict(v, alphabeta(cur, depth-1, alpha, beta, True))[1]
			beta = netPredict(beta, v)[1] 
			if alpha != -1:
				if netPredict(alpha, beta)[0] == alpha:
					break
		return v 

def computerMove(board, depth):
	alpha = -1
	beta = 1
	v = -1
	for move in board.legal_moves:
		cur = copy.copy(board)
		cur.push(move)
		if v == -1:
			v = alphabeta(cur, depth-1, alpha, beta, False)
			bestMove = move
			if alpha == -1:
				alpha = v
		else:
			new_v = netPredict(alphabeta(cur, depth-1, alpha, beta, False), v)[0]
			if new_v != v:
				bestMove = move
				v = new_v
			alpha = netPredict(alpha, v)[0] 

	print(bestMove)	
	board.push(bestMove)
	return board

def playerMove(board):
	while True:
		try:
			move = input("Enter your move \n")
			board.push_san(move)
			break
		except ValueError:
			print("Illegal move, please try again")

	return board

def playGame():
	moveTotal = 0
	board = chess.Board()
	depth = input("Enter search depth \n")
	depth = int(depth)
	while board.is_game_over() == False:
		print(board)
		if moveTotal % 2 == 1:
			board = playerMove(board)
		else:
			board =	computerMove(board, depth)
		moveTotal = moveTotal+1
	
	print(board)
	print("Game is over")
		

#firstBoard = bitifyFEN(beautifyFEN(firstBoard.fen()))
#secondBoard = bitifyFEN(beautifyFEN(secondBoard.fen()))
#firstBoard = firstBoard + secondBoard
#for elem in secondBoard:
#	firstBoard.append(elem)
#print(firstBoard)
#result = y.eval({x: firstBoard})
#playGame()
#print(result)i
#computerMove(chess.Board())a
model = loadModel()
playGame()