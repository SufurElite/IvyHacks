"""
Model based on implementation of an implementation 
on Deep Chess by David et al.
"""
import numpy as np
import tensorflow as tf
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt 

# Class that defines the behavior of a Siamese Network
class SiameseNetwork(object):
    
    # Stack fin_layer_sizes on top of a pair of deep_belief_network
    def __init__(self, deep_belief_network, fin_layer_sizes, batch):
        
        print("Initializing the Siamese Network Data Flow Graph ...")
        
        # Defining the hyperparameters
        self.epochs = 500 # Number of training epochs
        if batch<5000: self.batch_size=batch
        else: self.batch_size = 5000 # The batch size
        self.display_freq = 5 # Display logs and update the plot every display_freq epochs
        self.summary_freq = 5 # Update summaries every summary_freq training steps
        self.model_save_freq = 50 # Save the model every model_save_freq epochs
        
        # List to hold stage indicators for batch normalization in the Deep Belief Network
        self.is_training_list = []
        
        # Deep Belief Network
        for i, autoencoder in enumerate(deep_belief_network.autoencoders):
            print("DBN Layer ", i + 1, ": ", autoencoder.input_size, "->", autoencoder.output_size)
            self.is_training_list.append(autoencoder.is_training)
            
        # Training weights and biases
        self.fin_weights = []
        self.fin_biases = []
        
        # Final layers
        with tf.variable_scope('final_layers'):

            input_size = 2 * autoencoder.output_size
            for i, fin_layer_size in enumerate(fin_layer_sizes):
                output_size = fin_layer_size
                
                # ReLU weights
                var_init = tf.truncated_normal_initializer(stddev = 2 / input_size)
                
                # Non-ReLU weights for the last layer
                if (i == len(fin_layer_sizes) - 1):
                    var_init = tf.truncated_normal_initializer(stddev = input_size ** (-1/2))                    
                
                self.fin_weights.append(tf.get_variable('fin_weights_' + str(i) + '_' + str(input_size) + '_-_' + str(output_size),
                                                        [input_size, output_size],
                                                        tf.float32,
                                                        var_init))
                
                # ReLU biases
                var_init = tf.constant_initializer(0.01)
                
                # Non-ReLU biases for the last layer
                if (i == len(fin_layer_sizes) - 1):
                    var_init = tf.constant_initializer(0.0)
                
                self.fin_biases.append(tf.get_variable('fin_biases_' + str(i) + '_' + str(output_size),
                                                       [output_size],
                                                       tf.float32,
                                                       var_init))
                
                print("Final Layer ", i + 1, ": ", input_size, "->", output_size)
                input_size = output_size
            
        # First and second inputs
        self.X1 = tf.placeholder(tf.float32, [None, deep_belief_network.autoencoders[0].input_size])
        self.X2 = tf.placeholder(tf.float32, [None, deep_belief_network.autoencoders[0].input_size])
        
        # Stage indicator for batch normalization in final layers
        self.is_training = tf.placeholder(tf.bool, None)

        # Construct model
        dbn_forward_pass_op1 = self.dbn_forward_pass(self.X1, deep_belief_network.autoencoders)
        dbn_forward_pass_op2 = self.dbn_forward_pass(self.X2, deep_belief_network.autoencoders)
        X = tf.concat([dbn_forward_pass_op1, dbn_forward_pass_op2], axis = 1)
        input_X = X
        for i in range(len(fin_layer_sizes) - 1):
            with tf.variable_scope('fin_forward_pass_op_' + str(i + 1)):
                fin_weights = self.fin_weights[i]
                fin_biases = self.fin_biases[i]
                input_X = self.fin_forward_pass(input_X, fin_weights, fin_biases, True, tf.nn.relu)
        fin_weights = self.fin_weights[-1]
        fin_biases = self.fin_biases[-1]
        with tf.variable_scope('fin_forward_pass_op_' + str(len(fin_layer_sizes))):
            fin_forward_pass_op = self.fin_forward_pass(input_X, fin_weights, fin_biases, True)

        # Prediction
        y_pred = fin_forward_pass_op
        
        # Targets (labels)
        self.y_true = tf.placeholder(tf.int64, shape = [None], name = 'y_true')
        
        # Step counter
        var_init = tf.constant_initializer(0)
        self.global_step = tf.get_variable('global_step', [], tf.int64, var_init, trainable = False)
        
        # Learning rate parameters
        initial_learning_rate = 0.01
        decay_steps = 500000 // self.batch_size
        decay_rate = 0.99

        # Multiply the learning rate by decay_rate at the end of each epoch
        learning_rate = tf.train.exponential_decay(initial_learning_rate,
                                                   self.global_step,
                                                   decay_steps,
                                                   decay_rate,
                                                   staircase = True,
                                                   name = 'learning_rate')

        # Define the training cost
        with tf.name_scope('training_cost'):
            tr_cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels = self.y_true, logits = y_pred)
            self.tr_cost = tf.reduce_mean(tr_cross_entropy)
            
        # Define the training cost summary
        with tf.name_scope('training_cost_summary'):
            tr_cost_summary = tf.summary.scalar('siamese_network_training_cost', self.tr_cost)
        
        # Define the training accuracy as the percentage of correct guesses
        with tf.name_scope('training_accuracy'):
            tr_correct_prediction = tf.equal(tf.argmax(tf.nn.softmax(y_pred), 1), self.y_true)
            self.tr_accuracy = tf.reduce_mean(tf.cast(tr_correct_prediction, tf.float32))
            
        # Define the training accuracy summary
        with tf.name_scope('training_accuracy_summary'):
            tr_accuracy_summary = tf.summary.scalar('siamese_network_training_accuracy', self.tr_accuracy)
        
        # Merge training summaries
        with tf.name_scope('training_summaries'):
            self.tr_summaries = tf.summary.merge([tr_cost_summary, tr_accuracy_summary])
            
        # Define the validation cost
        with tf.name_scope('validation_cost'):
            val_cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels = self.y_true, logits = y_pred)
            self.val_cost = tf.reduce_mean(val_cross_entropy)
            
        # Define the validation cost summary
        with tf.name_scope('validation_cost_summary'):
            val_cost_summary = tf.summary.scalar('siamese_network_validation_cost', self.val_cost)
        
        # Define the validation accuracy as the percentage of correct guesses
        with tf.name_scope('validation_accuracy'):
            val_correct_prediction = tf.equal(tf.argmax(tf.nn.softmax(y_pred), 1), self.y_true)
            self.val_accuracy = tf.reduce_mean(tf.cast(val_correct_prediction, tf.float32))
            
        # Define the validation accuracy summary
        with tf.name_scope('validation_accuracy_summary'):
            val_accuracy_summary = tf.summary.scalar('siamese_network_validation_accuracy', self.val_accuracy)
        
        # Merge training summaries
        with tf.name_scope('validation_summaries'):
            self.val_summaries = tf.summary.merge([val_cost_summary, val_accuracy_summary])
        
        # Optimizer: minimize the mean squared error, clip exploding gradients before applying them
        with tf.name_scope('optimizer'):
            optimizer = tf.train.MomentumOptimizer(learning_rate, 0.1, name = 'optimizer')
            _grads_and_vars = optimizer.compute_gradients(self.tr_cost)
            clipped = [(tf.clip_by_value(grad, -1, 1), var) if grad is not None else (grad, var) for grad, var in
                           _grads_and_vars]
            self.train_step = optimizer.apply_gradients(clipped,
                                                        global_step = self.global_step,
                                                        name = 'train_step')
        
        print("The Siamese Network Data Flow Graph is initialized!")
        
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
    
    # Pass the input through the Deep Belief Network
    def dbn_forward_pass(self, x, autoencoders):

        output = x

        for i, autoencoder in enumerate(autoencoders):
            with tf.variable_scope('Autoencoder_' + str(i + 1)):
                with tf.variable_scope('encoder_op', reuse = True):
                    output = autoencoder.encoder(output, True)

        return output

    # Building final layers: pass the input through the layers with given activation functions
    def fin_forward_pass(self, x, weights, biases, normalize = False, activation_function = None):
        activation = tf.add(tf.matmul(x, weights), biases)

        # Batch Normalization
        if normalize:
            activation = self._batch_normalize(activation, [0])

        return activation_function(activation) if callable(activation_function) else activation
    
    # Training method for the model
    def train(self, sess, writer, saver, data):
        
        # Figure for plotting cross entropy and accuracy
        fig, axs = plt.subplots(2, 1, figsize = (10, 10))
        fig.subplots_adjust(hspace = 1)

        # Plotting data
        tr_samples_n, val_samples_n = data.get_sizes()
        print(tr_samples_n)
        print(val_samples_n)
        val_freq = tr_samples_n // val_samples_n
        tr_steps = tr_samples_n // self.batch_size
        input(tr_steps)
        val_steps = val_samples_n // self.batch_size
        tr_cost_data = np.zeros(self.epochs * tr_steps)
        tr_accuracy_data = np.zeros(self.epochs * tr_steps)
        val_cost_data = np.zeros(self.epochs * val_steps)
        val_accuracy_data = np.zeros(self.epochs * val_steps)
        input(val_steps)
        with tf.name_scope('training'):
            
            print("Training the Siamese Network ...")

            # Training loop
            for epoch in range(self.epochs):
                
                # Training and validation batches
                tr_batches = data.get_training_batch(self.batch_size)
                val_batches = data.get_validation_batch(self.batch_size)
                # For each training step/batch
                for batch_x1, batch_x2, labels in tr_batches:
                    
                    # Normalize the input
                    batch_x1 = (batch_x1 - data.avg) / data.std
                    batch_x2 = (batch_x2 - data.avg) / data.std
                    
                    # Run optimization, and get cost, accuracy, step, summaries
                    feed_dict = {self.X1: batch_x1, self.X2: batch_x2, self.y_true: labels, self.is_training: True}
                    for is_training in self.is_training_list:
                        feed_dict[is_training] = True
                    cost, accuracy, step, summaries, _ = sess.run([self.tr_cost,
                                                                   self.tr_accuracy,
                                                                   self.global_step,
                                                                   self.tr_summaries,
                                                                   self.train_step], feed_dict = feed_dict)
                    
                    # Update the plotting data
                    tr_cost_data[step - 1] = cost
                    tr_accuracy_data[step - 1] = accuracy
                    
                    # Update summaries per summary_freq training steps
                    if step % self.summary_freq == 0:    
                        writer.add_summary(summaries, step)
                    
                    # Every time global_step is a multiple of val_freq, validate the network
                    if step % val_freq == 0:
                    
                        # Get the validation batch
                        try:
                            batch_x1, batch_x2, labels = next(val_batches)

                            # Normalize the input
                            batch_x1 = (batch_x1 - data.avg) / data.std
                            batch_x2 = (batch_x2 - data.avg) / data.std

                            # Get cost, accuracy, step, summaries
                            feed_dict = {self.X1: batch_x1, self.X2: batch_x2, self.y_true: labels, self.is_training: False}
                            for is_training in self.is_training_list:
                                feed_dict[is_training] = False
                            cost, accuracy, summaries = sess.run([self.val_cost,
                                                                self.val_accuracy,
                                                                self.val_summaries], feed_dict = feed_dict)

                            # Update the plotting data
                            val_cost_data[step // val_freq - 1] = cost
                            val_accuracy_data[step // val_freq - 1] = accuracy
                        
                            # Update summaries per summary_freq training steps
                            if step % self.summary_freq == 0:    
                                writer.add_summary(summaries, step)
                        except Exception as e:
                            pass
                
                # Display logs and update the plots per display_freq epoch steps
                if (epoch + 1) % self.display_freq == 0:
                    print("Epoch:", '%03d' % (epoch + 1),
                          "| training cost =", '{:.4f}'.format(tr_cost_data[step - 1]),
                          "| training accuracy =", '{:.4f}'.format(tr_accuracy_data[step - 1]),
                          "| validation cost =", '{:.4f}'.format(val_cost_data[step // val_freq - 1]),
                          "| validation accuracy =", '{:.4f}'.format(val_accuracy_data[step // val_freq - 1]))
                    
                    # Interpolation step for filling in the missing validation graph points
                    interp_val_steps = np.linspace(1, self.epochs * tr_steps, num = self.epochs * val_steps)
                    interp_tr_steps = np.linspace(1, self.epochs * tr_steps, num = self.epochs * tr_steps)
                    interp_val_cost = interp1d(interp_val_steps, val_cost_data)
                    interp_val_accuracy = interp1d(interp_val_steps, val_accuracy_data)
                    
                    # Update the entropy plot
                    plt.sca(axs[0])
                    axs[0].cla()
                    plt.plot(tr_cost_data)
                    plt.plot(interp_tr_steps, interp_val_cost(interp_tr_steps))
                    plt.legend(["Training data", "Validation data"], loc = 'best')
                    plt.ylabel("Entropy")
                    plt.xlabel("Training Step")
                    plt.title("Siamese Network Cross Entropy")
                    
                    # Update the accuracy plot
                    plt.sca(axs[1])
                    axs[1].cla()
                    plt.plot(tr_accuracy_data)
                    plt.plot(interp_tr_steps, interp_val_accuracy(interp_tr_steps))
                    plt.legend(["Training data", "Validation data"], loc = 'best')
                    plt.ylabel("Accuracy")
                    plt.xlabel("Training Step")
                    plt.title("Siamese Network Accuracy")

                    fig.canvas.draw()
                
                # Save the model per model_save_freq epoch steps
                if (epoch + 1) % self.model_save_freq == 0:
                    print("Saving models ...")
                    saver.save(sess, './model/model.ckpt')
                    print("Saved models!")

            print("The Siamese Network training is finished!")