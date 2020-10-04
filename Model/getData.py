import chess.pgn

piece_to_index = {
    "p":0,
    "n":1,
    "b":2,
    "r":3,
    "q":4,
    "k":5,
    "P":6,
    "N":7,
    "B":8,
    "R":9,
    "Q":10,
    "K":11
}
index_to_piece = {
    0:"p",
    1:"n",
    2:"b",
    3:"r",
    4:"q",
    5:"k",
    6:"P",
    7:"N",
    8:"B",
    9:"R",
    10:"Q",
    11:"K"
}

def printGivenBitBoards(BitBoards):
    for index in range(len(BitBoards)):
        print(index_to_piece[index])
        for line in BitBoards[index]:
            print(line)
    return None

def fenToBitBoard(FEN):
    #k7/1n1R1P2/r1p2nN1/2ppp1Pp/pp1pN1P1/8/3K4/8 w KQkq - 0 1
    bitBoards = [[[0 for i in range(8)] for j in range(8)] for z in range(12)]
    hasSpace = False
    counter = 0
    for line in FEN.split("/"):
        chars = [char for char in line]
        file_num = 0
        for i in chars:
            if i == " ":
                hasSpace = True
            elif not hasSpace:
                if i.isnumeric():
                    file_num+=int(i)
                else:
                    additive_=piece_to_index[i]
                    bitBoards[additive_][FEN.split("/").index(line)][file_num] = 1
                    file_num+=1
                #print(i)
        counter+=1
        #print(line)
        hasSpace = False
    return bitBoards

def parseData(fpath="../data/MagnusCarlsen.pgn"):

    pass