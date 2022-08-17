# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 22:19:24 2019

@author: lewisliu
"""

import tensorflow as tf

a = tf.placeholder(tf.int16)
b = tf.placeholder(tf.int16)

add = tf.add(a, b)
mul = tf.multiply(a, b)

with tf.Session() as sess:
#    calculate value
    print("Add: %i"%sess.run(add, feed_dict = {a: 3, b: 4}))
    print("Multiply: %i"%sess.run(mul, feed_dict = {a: 3, b: 4}))