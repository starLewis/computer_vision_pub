# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 21:51:21 2019

@author: lewisliu
"""

import tensorflow as tf
import numpy as np

sess = tf.Session()

t = [[2, 3, 3],[1, 5, 5]]

t1 = tf.expand_dims(t, 0)
print np.shape(t1)
print sess.run(t1)

t2 = tf.expand_dims(t, 1)
print np.shape(t2)
print sess.run(t2)

