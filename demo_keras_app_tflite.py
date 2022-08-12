#!/usr/bin/env python

# Keras API R-MAC Layer for TensorFlow 2
# TensorFlow Lite Demo
#
# copyright (c) 2020 IMATAG
# imatag.com
#
# Author: Vedran Vukotic

import numpy as np
import tensorflow as tf
# load the pretinrained network from Keras Applications
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.layers import Lambda
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

from rmac import RMAC

# load the base model
base_model = MobileNetV2()

# check the architecture and see where to attach our RMAC layer
# print(base_model.summary())

# create the new model consisting of the base model and a RMAC layer
layer = "out_relu"
base_out = base_model.get_layer(layer).output

rmac = RMAC(base_out.shape, levels=5, norm_fm=True, sum_fm=True)

# add RMAC layer on top
rmac_layer = Lambda(rmac.rmac, input_shape=base_model.output_shape, name="rmac_" + layer)

out = rmac_layer(base_out)
# out = Dense(1024)(out) # fc to desired dimensionality
model = model = Model(base_model.input, out)

# convert model to TF lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
tflite_model = converter.convert()

# save model
with open("model.tflite", 'wb') as f:
    f.write(tflite_model)

# Load TFLite model and allocate tensors
interpreter = tf.lite.Interpreter("model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# load a sample image
i = load_img('adorable-al-reves-animal-atigrado-248280.jpg', target_size=(224, 224))
x = img_to_array(i)
x = x[None, ...]
x = preprocess_input(x)

# obtain RMAC descriptor for the image through TF Lite
interpreter.set_tensor(input_details[0]['index'], x)
interpreter.invoke()
y = interpreter.get_tensor(output_details[0]['index'])
print("\nOut:")
print("Shape:  ", y.shape)
print("Values: ", y)
print("Min:    ", np.min(y))
print("Max:    ", np.max(y))
