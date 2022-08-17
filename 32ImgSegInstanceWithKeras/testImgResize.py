# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:16:50 2019

@author: lewisliu
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


fname = "/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/Studying/carvana-image-masking-challenge/29bb3ece3180_11.jpg"
img_str = tf.read_file(fname)
img = tf.image.decode_jpeg(img_str)

img = tf.to_float(img)/255.0

with tf.Session() as sess:
    img = sess.run(img)
    
    plt.figure(figsize=(10, 15))
    plt.imshow(img)
