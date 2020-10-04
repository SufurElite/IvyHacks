from flask import Flask, render_template, request 
import numpy as np
import keras.models
import re, sys, os 
from game import computerMove, loadModel, _bitboard
import chess 
sys.path.append(os.path.abspath('./modelfiles'))
from load import *
from flask_cors import CORS

# ./python_code/api.py
import os
import pickle
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import numpy as np
# initialise flask app


app = Flask(__name__)
CORS(app)
api = Api(app)

# Require a parser to parse our POST request.
parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("fen")



class Predict(Resource):
  def post(self):
    args = parser.parse_args()
    
    board = chess.Board(args["fen"])
    model = loadModel(args["name"])
    
    #boardData = request.get_data()
    #Get fen of board from request
    #then get python-chess board from fen and pass into 
    # _bitboard
    res = computerMove(model, board)
    return res


api.add_resource(Predict, "/predict")
if __name__ == "__main__":
  app.run(debug=False, threaded=False)