# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 22:07:39 2019

@author: lewisliu
"""

import tensorflow as tf
hello = tf.constant("Hello, TensorFlow!")
print(hello)
sess = tf.Session()
print(sess.run(hello))
sess.close()