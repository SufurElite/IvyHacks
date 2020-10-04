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

def create_baseline():
    # create model
    model = Sequential()
    model.add(Dense(200, input_dim=1023, activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def getData(position_file, target_file):
    X = np.load(position_file)
    y = np.load(target_file)
    
    #input(X.shape)
    return X, y

def train(X, y): 
    
    
    """
    encoder = LabelEncoder()
    encoder.fit(y)
    encoded_Y = encoder.transform(y)
    estimator = KerasClassifier(build_fn=create_baseline,epochs=100,batch_size=5,verbose=100)
    #pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(estimator, X, encoded_Y, cv=kfold)
    print("Standardised: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
    
    """
    model = Sequential()
    model.add(Dense(200, input_dim=1023, activation='relu'))
    model.add(Dense(120, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    X = [X]
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print("Started Training")
    model.fit(X, y, epochs=100, batch_size=32)
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %.2f' % (accuracy*100))
    model_json = model.to_json()
    with open("modfiles/fischer.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("modfiles/fischer.h5")
    print("Saved model to disk")
    pass

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
    

if __name__=="__main__":
    X, y = getData("CnnFeaturePositions.npy","CnnFeatureTarget.npy")
    train(X, y)