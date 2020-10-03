"""
Model based on implementation of an implementation 
on Deep Chess by David et al.
"""
import numpy as np
import tensorflow as tf
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
# Class that defines the behavior of an Autoencoder
class Autoencoder(object):
    
    # Encode input with input_size as an output with output_size
    def __init__(self, input_size, output_size):
        
        # Defining the hyperparameters
        self.input_size = input_size # The input size
        self.output_size = output_size # The output size
        self.epochs = 100 # Number of training epochs
        self.batch_size = 10000 # The batch size
        self.display_freq = 5 # Display logs and update the plot every display_freq epochs
        self.summary_freq = 1 # Update the summary every summary_freq training steps
        self.model_save_freq = 50 # Save the model every model_save_freq epochs
        
        # Training weights and biases
        self.weights = {}
        self.biases = {}
        
        # Encoder
        with tf.variable_scope('encoder_vars'):
            
            # ReLU weights
            var_init = tf.truncated_normal_initializer(stddev = 2 / input_size)
            self.weights['encoder_h'] = tf.get_variable('encoder_h_' + str(input_size) + '_-_' + str(output_size),
                                                        [input_size, output_size],
                                                        tf.float32,
                                                        var_init)
            
            # ReLU biases
            var_init = tf.constant_initializer(0.01)
            self.biases['encoder_b'] = tf.get_variable('encoder_b' + str(output_size),
                                                       [output_size],
                                                       tf.float32,
                                                       var_init)
        
        # Decoder
        with tf.variable_scope('decoder_vars'):

            # ReLU weights
            var_init = tf.truncated_normal_initializer(stddev = 2 / input_size)
            self.weights['decoder_h'] = tf.get_variable('decoder_h' + str(output_size) + '_-_' + str(input_size),
                                                        [output_size, input_size],
                                                        tf.float32,
                                                        var_init)
            
            # ReLU biases
            var_init = tf.constant_initializer(0.01)
            self.biases['decoder_b'] = tf.get_variable('decoder_b' + str(input_size),
                                                       [input_size], 
                                                       tf.float32,
                                                       var_init)
    
        # Input
        self.X = tf.placeholder(tf.float32, [None, self.input_size])
        
        # Stage indicator for batch normalization
        self.is_training = tf.placeholder(tf.bool, None)

        # Construct model
        with tf.variable_scope('encoder_op'):
            self.encoder_op = self.encoder(self.X, True)
        with tf.variable_scope('decoder_op'):
            decoder_op = self.decoder(self.encoder_op, True)

        # Prediction
        y_pred = decoder_op
        
        # Targets (labels) are the input data
        y_true = self.X
        
        # Step counter
        var_init = tf.constant_initializer(0)
        self.global_step = tf.get_variable('global_step', [], tf.int64, var_init, trainable = False)
        
        # Learning rate parameters
        initial_learning_rate = 0.005
        decay_steps = 1000000 // self.batch_size
        decay_rate = 0.98

        # Multiply the learning rate by decay_rate at the end of each epoch
        learning_rate = tf.train.exponential_decay(initial_learning_rate,
                                                   self.global_step,
                                                   decay_steps,
                                                   decay_rate,
                                                   staircase = True,
                                                   name = 'learning_rate')

        # Define the cost
        with tf.name_scope('cost'):
            self.cost = tf.losses.mean_squared_error(labels = y_true, predictions = y_pred)
        
        # Define the cost summary
        with tf.name_scope('cost_summary'):
            self.cost_summary = tf.summary.scalar('autoencoder_cost', self.cost)
        
        # Optimizer: minimize the mean squared error, clip exploding gradients before applying them
        with tf.name_scope('optimizer'):
            optimizer = tf.train.MomentumOptimizer(learning_rate, 0.1, name = 'optimizer')
            _grads_and_vars = optimizer.compute_gradients(self.cost, var_list = [self.weights['encoder_h'],
                                                                                 self.biases['encoder_b'],
                                                                                 self.weights['decoder_h'],
                                                                                 self.biases['decoder_b']])
            clipped = [(tf.clip_by_value(grad, -1, 1), var) if grad is not None else (grad, var) for grad, var in
                           _grads_and_vars]
            self.train_step = optimizer.apply_gradients(clipped,
                                                        global_step = self.global_step,
                                                        name = 'train_step')
    
    # Batch Normalization with population parameters (non-training)
    def _pop_batch_norm(self, x, pop_mean, pop_var, offset, scale):
            return tf.nn.batch_normalization(x, pop_mean, pop_var, offset, scale, 1e-6)

    # Batch Normalization with batch parameters (training)
    def _batch_norm(self, x, pop_mean, pop_var, mean, var, offset, scale):
        decay = 0.99

        dependency_1 = tf.assign(pop_mean, pop_mean * decay + mean * (1 - decay))
        dependency_2 = tf.assign(pop_var, pop_var * decay + var * (1 - decay))

        with tf.control_dependencies([dependency_1, dependency_2]):
            return tf.nn.batch_normalization(x, mean, var, offset, scale, 1e-6)

    # Batch Normalization
    def _batch_normalize(self, x, axes):
        depth = x.shape[-1]
        mean, var = tf.nn.moments(x, axes = axes)

        var_init = tf.constant_initializer(0.0)
        offset = tf.get_variable('offset', [depth], tf.float32, var_init)
        var_init = tf.constant_initializer(1.0)
        scale = tf.get_variable('scale', [depth], tf.float32, var_init)

        pop_mean = tf.get_variable('pop_mean', [depth], initializer = tf.zeros_initializer(), trainable = False)
        pop_var = tf.get_variable('pop_var', [depth], initializer = tf.ones_initializer(), trainable = False)

        return tf.cond(
            self.is_training,
            lambda: self._batch_norm(x, pop_mean, pop_var, mean, var, offset, scale),
            lambda: self._pop_batch_norm(x, pop_mean, pop_var, offset, scale)
        )
    
    # Building the encoder: encode the input with ReLU activation
    def encoder(self, x, normalize = False):

        activation = tf.add(tf.matmul(x, self.weights['encoder_h']), self.biases['encoder_b'])

        # Batch Normalization
        if normalize:
            activation = self._batch_normalize(activation, [0])

        return tf.nn.relu(activation)

    # Building the decoder: decode the input with ReLU activation
    def decoder(self, x, normalize = False):

        activation = tf.add(tf.matmul(x, self.weights['decoder_h']), self.biases['decoder_b'])

        # Batch Normalization
        if normalize:
            activation = self._batch_normalize(activation, [0])

        return tf.nn.relu(activation)
    
    # Training method for the model
    def train(self, sess, writer, saver, data, fig, ax, title):
        
        # Plotting data
        samples_n = data.get_size()
        steps = samples_n // self.batch_size
        cost_data = np.zeros(self.epochs * steps)
        cost = self.cost
        with tf.name_scope('training'):

            print("Training the Autoencoder ...")
            
            # Training loop
            for epoch in range(self.epochs):

                # For each training step/batch
                for batch in data.get_batch(self.batch_size):
                    
                    # Normalize the input
                    batch = (batch - data.avg) / data.std
                    
                    # Run optimization, and get cost, step, summary
                    cost, step, summary, _ = sess.run([self.cost, self.global_step, self.cost_summary, self.train_step],
                                                      feed_dict = {self.X: batch, self.is_training: True})
                    
                    # Update the plotting data
                    cost_data[step - 1] = cost
                    
                    # Update the summary per summary_freq training steps
                    if step % self.summary_freq == 0:
                        writer.add_summary(summary, step)

                # Display logs and update the plot per display_freq epoch steps
                if (epoch + 1) % self.display_freq == 0:
                    print("Epoch:", '%03d' % (epoch + 1))#,"| cost =", '{:.4f}'.format(cost))
                    
                    # Update the plot
                    plt.sca(ax)
                    ax.cla()
                    plt.plot(cost_data)
                    plt.ylabel("Cost")
                    plt.xlabel("Training Step")
                    plt.title(title + " Cost")

                    fig.canvas.draw()
                
                # Save the model per model_save_freq epoch steps
                if (epoch + 1) % self.model_save_freq == 0:
                    print("Saving models ...")               
                    saver.save(sess, './model/model.ckpt')
                    print("Saved models!")

            print("The Autoencoder training is finished!")
    
    # Encoder output method for the Deep Belief Network
    def encoder_output(self, sess, X):
        output = np.zeros((len(X), self.output_size))
        
        for start, end in zip(range(0, len(X), self.batch_size), range(self.batch_size, len(X), self.batch_size)):
            batch = X[start : end]
            output[start : end] = sess.run(self.encoder_op, feed_dict = {self.X: batch, self.is_training: False})
        
        return output