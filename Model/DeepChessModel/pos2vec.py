"""
Model based on implementation of an implementation 
on Deep Chess by David et al.
"""
import numpy as np
import tensorflow as tf
from scipy.interpolate import interp1d

class Pos2VecData(object):
    
    def __init__(self, data, avg, std):
        self.data = data
        self.avg = avg
        self.std = std
    
    def get_batch(self, batch_size):
        samples_n = self.data.shape[0]
        if batch_size <= 0:
            batch_size = samples_n
            
        # Generate random indices to rearrange the data
        random_indices = np.random.choice(samples_n, samples_n, replace = False)
        data = self.data[random_indices]
        
        # Clean the cache
        del random_indices
        
        for i in range(samples_n // batch_size):
            on = i * batch_size
            off = on + batch_size
            
            yield data[on : off]
        
        # Clean the cache
        del data
    
    def get_size(self):
        return self.data.shape[0]