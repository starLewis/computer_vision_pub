# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 21:56:05 2019

@author: lewisliu
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

train_X = np.linspace(-1, 1, 100)
train_Y = 2 * train_X + np.random.randn(*train_X.shape) * 0.3

#show data
plt.plot(train_X, train_Y, 'ro', label='Original Data')
plt.legend()
plt.show()

#reset graph
tf.reset_default_graph()

#init model
X = tf.placeholder("float")
Y = tf.placeholder("float")
#model parameters
W = tf.Variable(tf.random_normal([1]), name = "weight")
b = tf.Variable(tf.zeros([1]), name = "bias")

#forward propagation
z = tf.multiply(X, W) + b

training_epochs = 20
display_step = 2

saver = tf.train.Saver()
saverdir = "log/"


#optimization
cost = tf.reduce_mean(tf.square(Y - z))
learning_rate = 0.01
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

#call session
#with tf.Session() as sess:
#    sess.run(tf.global_variables_initializer())
#    
#    plotdata = {"batchSize":[], "loss": []}
##    push data to model
#    for epoch in range(training_epochs):
#        for (x, y) in zip(train_X, train_Y):
#            sess.run(optimizer, feed_dict={X: x, Y: y})
##        show middle result
#        if epoch % display_step == 0:
#            loss = sess.run(cost, feed_dict = {X: train_X, Y: train_Y})
#            print("Epoch: ", epoch+1, "cost=",loss, "W=", sess.run(W), "b=", sess.run(b))
#        
#        print("Finished!")
#        print("cost=", sess.run(cost, feed_dict = {X: train_X, Y: train_Y}), "W=", sess.run(W), "b=", sess.run(b))
#        
#        saver.save(sess, saverdir+"linermodel.cpkt")

#call ckpt
with tf.Session() as sess2:
    sess2.run(tf.global_variables_initializer())
    
    saver.restore(sess2, saverdir+"linermodel.cpkt")
    print("x=0.2, z=",sess2.run(z, feed_dict={X: 0.2}))
