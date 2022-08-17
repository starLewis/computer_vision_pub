# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 12:01:06 2019

@author: lewisliu
"""

import tensorflow as tf

with tf.variable_scope("test1", initializer=tf.constant_initializer(0.4)):
    var1 = tf.get_variable("firstvar", shape=[2], dtype = tf.float32)
    
    with tf.variable_scope("test2"):
        var2 = tf.get_variable("firstvar", shape=[2], dtype=tf.float32)
        var3 = tf.get_variable("var3", shape=[2], initializer=tf.constant_initializer(0.3))
        
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    print("var1=", var1.eval())
    print("val2=", var2.eval())
    print("val3=", var3.eval())