# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 22:14:11 2019

@author: lewisliu
"""

import tensorflow as tf

a = tf.constant(3)
b = tf.constant(4)

with tf.Session() as sess:
    print("Add: %i"%sess.run(a+b))
    print("Multiply: %i"%sess.run(a*b))