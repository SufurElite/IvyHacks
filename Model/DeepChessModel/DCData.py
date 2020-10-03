"""
Model based on implementation of an implementation 
on Deep Chess by David et al.
"""
import numpy as np
import tensorflow as tf
from scipy.interpolate import interp1d

class DeepChessData(object):
    
    def __init__(self, preferred_file, rejected_file):
        
        prefer_data = np.load(preferred_file)['arr_0']
        reject_data = np.load(rejected_file)['arr_0']
        
        
        self.training_samples_n = 500000
        self.validation_samples_n = 50000        
        if len(prefer_data)+len(reject_data)<self.training_samples_n:
            self.training_samples_n = len(prefer_data)+len(reject_data)
            self.validation_samples_n = int((len(prefer_data)+len(reject_data))/15)
        
        # Small value to avoid zero division
        epsilon = 1e-9
        
        # Take preferred data samples for population moments calculation
        # It is computationally expensive to do it for the full data
        np.random.seed(0)
        indices_p = np.random.choice(len(prefer_data), size = self.training_samples_n // 2, replace = False)
        prefer_samples = prefer_data[indices_p]
        
        # Clean the cache
        del indices_p
        
        # Take rejected data samples for population moments calculation
        # It is computationally expensive to do it for the full data
        np.random.seed(1)
        indices_r = np.random.choice(len(reject_data), size = self.training_samples_n // 2, replace = False)
        reject_samples = reject_data[indices_r]
        
        # Clean the cache
        del indices_r
        
        # Combine preffered and rejected samples
        samples = np.concatenate((prefer_samples, reject_samples))
        
        # Clean the cache
        del prefer_samples
        del reject_samples
        
        # Calculate population moments
        self.avg = np.mean(samples, 0)
        self.std = np.std(samples, 0) + epsilon
        
        # Clean the cache
        del samples
        
        # Separate validation and training preffered data
        np.random.seed(2)
        indices_p = np.random.choice(len(prefer_data), size = self.validation_samples_n, replace = False)
        self.validation_prefer_data = prefer_data[indices_p]
        self.training_prefer_data = np.delete(prefer_data, indices_p, axis = 0)
        
        # Clean the cache
        del prefer_data
        del indices_p
        
        # Separate validation and training reject data
        np.random.seed(3)
        indices_r = np.random.choice(len(reject_data), size = self.validation_samples_n, replace = False)        
        self.validation_reject_data = reject_data[indices_r]
        self.training_reject_data = np.delete(reject_data, indices_r, axis = 0)
        
        # Clean the cache
        del reject_data
        del indices_r
    
    def get_training_batch(self, batch_size):
        if(batch_size<self.training_samples_n):
            return self._get_batch(self.training_prefer_data, self.training_reject_data, batch_size, self.training_samples_n)
        else:
            return self._get_batch(self.training_prefer_data, self.training_reject_data, int(self.training_samples_n/8), self.training_samples_n)

    
    def get_validation_batch(self, batch_size):
        return self._get_batch(self.validation_prefer_data, self.validation_reject_data, batch_size, self.validation_samples_n)
    
    def _get_batch(self, prefer_data, reject_data, batch_size, samples_n):
        prefer_samples_n = prefer_data.shape[0]
        reject_samples_n = reject_data.shape[0]
        """print(batch_size)
        print(samples_n)
        input(prefer_samples_n)"""
        if batch_size <= 0:
            batch_size = samples_n
        
        # Generate random indices to rearrange the preferred data
        # Need to look closer into this:
        # There is some fault in the general logic, when will samples_n be less than prefer_samples_n?
        if samples_n<prefer_samples_n:
            prefer_indices = np.random.choice(prefer_samples_n, samples_n, replace = False)
        else:
            prefer_indices = np.random.choice(prefer_samples_n, prefer_samples_n, replace = False)
        prefer_samples = prefer_data[prefer_indices]
        
        # Clean the cache
        del prefer_indices
        
        # Generate random indices to rearrange the reject data
        if samples_n<reject_samples_n:
            reject_indices = np.random.choice(reject_samples_n, samples_n, replace = False)
        else:
            reject_indices = np.random.choice(reject_samples_n, reject_samples_n, replace = False)
        reject_samples = reject_data[reject_indices]
        
        # Clean the cache
        del reject_indices
        
        for i in range(samples_n // batch_size):
            on = i * batch_size
            off = on + batch_size
            
            batch_1 = prefer_samples[on : off]
            batch_2 = reject_samples[on : off]
            labels = np.zeros(len(batch_1))
            
            # Generate random indices to switch prefer and reject pairs
            permut_indices = np.random.choice(len(batch_1), size = len(batch_1) // 2, replace = False)
            
            temp_batch = batch_1[permut_indices]
            batch_1[permut_indices] = batch_2[permut_indices]
            batch_2[permut_indices] = temp_batch
            
            # Clean the cache
            del temp_batch
            
            labels[permut_indices] = 1
            
            # Clean the cache
            del permut_indices
            
            yield batch_1, batch_2, labels
        
        # Clean the cache
        del prefer_samples
        del reject_samples
            
    def get_sizes(self):
        return self.training_samples_n, self.validation_samples_n