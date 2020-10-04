import chess.pgn
import numpy as np
from random import randint as rint 

class PGNData():
    
    def __init__(self, file_name, username):
        """
        Initializes a PGNData object and processes the data.
        
        @param file_name: The name of the data file to process.
        
        @type file_name: str
        
        """
        self.pgn_chess_games = open(file_name)
        self.username = username

    def _bitboard(self, board):
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

    def preprocess(self):
        """
        Processes each game with a probability of 0.5. From each selected
        game, randomly extracts ten positions, with the restriction that
        the selected position cannot be from one of the first five moves
        in the game, and that the actual move played in the selected
        position is not a capture. Capture moves are misleading as they
        mostly result in a transient advantage since the other side is
        likely to capture back right away.
        """
        # read the first game from the file opened in text mode
        game = chess.pgn.read_game(self.pgn_chess_games)
        
        prefer_data = []
        reject_data = []
        processed_games = 0

        # repeat until the end of the file is reached
        while game != None:
            # process each game with a 0.5 probability
            process = np.random.binomial(n = 1, p = 0.5)

            # ignore the games that ended in a draw
            if process and "PlyCount" in game.headers:
                isWhite = False
                if game.headers["Black"] == self.username: isWhite = False
                elif game.headers["White"] == self.username: isWhite = True
                else: continue
                
                #print(game)
                #input(isWhite)
                # The Preferred Data - i.e. positions selected by person 
                prefer_tmp_data = []
                
                # The Rejected Data - i.e. positions randomly selected that is not the same
                # as the preferred data
                reject_tmp_data = []
                
                board = game.board()

                moves = iter(game.mainline_moves())
                # copies for identification of non-capture moves
                board_copy = game.board()
                moves_copy = iter(game.mainline_moves())
                
                # ignore the first 5 moves
                all_moves = []
                
                ply = int(game.headers['PlyCount'])
                

                # identify non-capture moves
                try:
                    for move in range(ply):
                        next_move = next(moves_copy)
                        if board_copy.turn==isWhite:
                            all_moves.append(move)
                        board_copy.push(next_move)
                except Exception as e:
                    print(e)
                    game = chess.pgn.read_game(self.pgn_chess_games)
                    continue
                # choose 10 random non-capture moves
                if len(all_moves)<30: random_moves = np.random.choice(all_moves, len(all_moves), replace=False)
                else: random_moves = np.random.choice(all_moves, 30, replace=False)
                

                # extract bitboard representations of the positions
                # in which the chosen random moves are played board.turn
                for move in range(ply):
                    bc = board.copy()
                    board.push(next(moves))
                    if move in random_moves:
                        """print(bc)
                        print("\nAfter my move")
                        print(board)
                        print("\nAfter computer move")"""
                        lg_moves = list(bc.legal_moves)
                        mv = lg_moves[rint(0,len(lg_moves)-1)]
                        #print(mv)
                        bc.push(mv)
                        
                        prefer_tmp_data.append(self._bitboard(board))
                        reject_tmp_data.append(self._bitboard(bc))

                # store the extracted bitboard representations
                prefer_data += prefer_tmp_data
                
                reject_data += reject_tmp_data

            # read a new game from the file opened in text mode
            game = chess.pgn.read_game(self.pgn_chess_games)

            # print the number of processed games every 10,000 games
            processed_games += 1
            if processed_games % 10000 == 0:
                print('Processed %d games!' % processed_games)

        # save the results
        print(processed_games)
        print(prefer_data[0])
        print(len(reject_data))
        input(len(prefer_data))
        prefer_data = np.array(prefer_data)
        reject_data = np.array(reject_data)
        np.savez_compressed('prefer_data', prefer_data)
        np.savez_compressed('reject_data', reject_data)

def parsePGN(file_name="../data/BobbyFischer.pgn", username="Robert James Fischer"):
    """
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'f:h', ['file_name=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-f', '--file_name'):
            c.set_test_dir(arg)
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
    """
    # initialize a PGNData object
    pgn_data = PGNData(file_name, username)
    
    # process the data
    pgn_data.preprocess()


if __name__ == '__main__':
    parsePGN()