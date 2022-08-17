# -*- coding: UTF-8 -*-

import tensorflow as tf

with tf.name_scope("input1"):
    input1 = tf.constant([1.0, 2.0, 3.0], name="input1")

with tf.name_scope("input2"):
    input2 = tf.Variable(tf.random_uniform([3]), name="input2")
    
output = tf.add_n([input1, input2], name="add")

writer = tf.summary.FileWriter("/home/liuxun/Clobotics/Data/DPData/studyTensorflow/log",tf.get_default_graph())
writer.close()


#with tf.variable_scope("foo"):
    #a = tf.get_variable("bar", [1])
    #print a.name
    
#with tf.variable_scope("bar"):
    #a = tf.get_variable("bar", [1])
    #print a.name
    
#with tf.name_scope("a"):
    #a = tf.Variable([1])
    #print a.name
    
    ##a = tf.get_variable("b", [1])
    ##print a.name
    
#with tf.name_scope("b"):
    #a = tf.get_variable("b", [1])
    #print a.name