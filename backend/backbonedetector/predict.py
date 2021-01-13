import os
import numpy as np
import cv2
from tensorflow import keras
from variables import *
import os

def predict(img):
    dirname = os.path.dirname(__file__)
    model_path = os.path.join(dirname, 'model.h5')
    model = keras.models.load_model(model_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (300, 300))
    X = []
    X.append(img)
    X = np.array(X, dtype="uint8")
    X = X.reshape(1, 300, 300, 1)
    predicted_img = model.predict(X)
    index = np.argmax(predicted_img)
    return index