"""
Model based on implementation of an implementation 
on Deep Chess by David et al.
"""
import numpy as np
import tensorflow as tf
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt 
from acencoder import Autoencoder

# Class that defines the behavior of a Deep Belief Network
class DeepBeliefNetwork(object):
    
    # Create layers of Autoencoders with sizes dbn_layer_sizes
    def __init__(self, dbn_layer_sizes):
        
        print("Initializing the Deep Belief Network Data Flow Graph ...")
        
        # Create list to hold the Autoencoders
        self.autoencoders = []
        
        # For each Autoencoder we want to generate
        for i in range(len(dbn_layer_sizes) - 1):
            with tf.variable_scope('Autoencoder_' + str(i + 1)):
                input_size = dbn_layer_sizes[i]
                output_size = dbn_layer_sizes[i + 1]
                print("Autoencoder ", i + 1, ": ", input_size, "->", output_size, "->", input_size)
                self.autoencoders.append(Autoencoder(input_size, output_size))
                
        print("The Deep Belief Network Data Flow Graph is initialized!")
    
    # Training method for the model
    def train(self, sess, writer, saver, dbn_data):
        with tf.name_scope('training'):
            
            # Figure for plotting training cost
            fig, axs = plt.subplots(len(self.autoencoders), 1, figsize=(10, 15))
            fig.subplots_adjust(hspace = 1)
            
            print("Training the Deep Belief Network ...")
            
            # For each Autoencoder in our list
            for i, autoencoder in enumerate(self.autoencoders):
                with tf.variable_scope('Autoencoder_' + str(i + 1)):
                    print("Autoencoder " + str(i + 1) + ":")
                    
                    # Train it
                    autoencoder.train(sess, writer, saver, dbn_data, fig, axs[i], 'Autoencoder ' + str(i + 1))
                    
                    # Return the encoded input
                    dbn_data.data = autoencoder.encoder_output(sess, dbn_data.data)
                    
                    # Moments will be learned through batch normalization
                    dbn_data.avg = 0
                    dbn_data.std = 1
            
            print("The Deep Belief Network training is finished!")