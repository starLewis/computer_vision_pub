# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 22:39:23 2019

@author: lewisliu
"""

import tensorflow as tf
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file

savedir = "log/"
print_tensors_in_checkpoint_file(savedir+"linermodel.cpkt", None, True)

W = tf.Variable(1.0, name = "weight")
b = tf.Variable(2.0, name = "bias")

saver = tf.train.Saver({"weight":b, "bias": W})

with tf.Session() as sess:
    tf.global_variables_initializer().run()
    
    saver.save(sess, savedir+"linermodel.cpkt")

print_tensors_in_checkpoint_file(savedir+"linermodel.cpkt", None, True)