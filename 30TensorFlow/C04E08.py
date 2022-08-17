# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 22:27:41 2019

@author: lewisliu
"""

import tensorflow as tf

a = tf.placeholder(tf.int16)
b = tf.placeholder(tf.int16)

add = tf.add(a, b)
mul = tf.multiply(a, b)

with tf.Session() as sess:
    print("add: %i"%sess.run(add, feed_dict={a: 3, b: 4}))
    print("mul: %i"%sess.run(mul, feed_dict={a: 3, b: 4}))
    print(sess.run([mul, add], feed_dict={a: 3, b: 4}))