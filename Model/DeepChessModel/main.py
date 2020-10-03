from preprocess import parsePGN
from DCData import DeepChessData
from pos2vec import Pos2VecData
from dbn import DeepBeliefNetwork
from siamnet import SiameseNetwork
import numpy as np
import tensorflow as tf

def main(filePath="../data/BehrGames2.pgn"):
    # Collect game positions
    #parsePGN(filePath)
    
    
    # Create DeepChessData
    deep_chess_data = DeepChessData("prefer_data.npz", "reject_data.npz")
    
    # Create the Pos2Vec Data
    _data_1, _data_2, _ = next(deep_chess_data.get_training_batch(500000))
    _data = np.concatenate((_data_1, _data_2))
    pos_2_vec_data = Pos2VecData(_data, deep_chess_data.avg, deep_chess_data.std)
    
    # Create Pos2Vec and DeepChess instances
    pos_2_vec = DeepBeliefNetwork(dbn_layer_sizes = [773, 100, 100, 100])
    deep_chess = SiameseNetwork(deep_belief_network = pos_2_vec, fin_layer_sizes = [100, 100, 2],batch=int(len(_data)/16))
    
    # Instantiate a tf session, a summary writer, and a model saver
    sess = tf.InteractiveSession()
    writer = tf.summary.FileWriter('./summaries', graph = sess.graph)
    saver = tf.train.Saver(keep_checkpoint_every_n_hours = 2)
    
    # Initialize the variables
    sess.run(tf.global_variables_initializer())

    # Train the Pos2Vec network
    pos_2_vec.train(sess, writer, saver, pos_2_vec_data)

    # Train the DeepChess network
    deep_chess.train(sess, writer, saver, deep_chess_data)
    
    return None

if __name__=="__main__":
    main()