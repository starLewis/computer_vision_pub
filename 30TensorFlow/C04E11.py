# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 22:58:06 2019

@author: lewisliu
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

#define storing array
plotdata = {"batchsize": [], "loss": []}
def moving_average(a, w = 10):
    if len(a) < w:
        return a[:]
    return [val if idx < w else sum(a[(idx-w):idx])/w for idx, val in enumerate(a)]
    
#build data
train_X = np.linspace(-1, 1, 100)
train_Y = 2 * train_X + np.random.randn(*train_X.shape) * 0.3

#show through plt
plt.plot(train_X, train_Y, 'ro', label="original data")
plt.legend()
plt.show()

tf.reset_default_graph()

#build model
X = tf.placeholder("float")
Y = tf.placeholder("float")
W= tf.Variable(tf.random_normal([1]), name="weight")
b = tf.Variable(tf.zeros([1]), name="bias")
#forward propagation
z = tf.multiply(X, W) + b

#optimization
cost = tf.reduce_mean(tf.square(Y - z))
learning_rate = 0.01
optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

#inital
init = tf.global_variables_initializer()

#define study parameters
training_epochs = 20
display_step = 2
saver = tf.train.Saver(max_to_keep=1)
saverdir = "log/"

#run session
with tf.Session() as sess:
    sess.run(init)
    
#    push data to model
    for epoch in range(training_epochs):
        for (x, y) in zip(train_X, train_Y):
            sess.run(optimizer, feed_dict={X:x, Y:y})
        
#        show details
        if epoch % display_step == 0:
            loss = sess.run(cost, feed_dict = {X: train_X, Y: train_Y})
            print("Epoch:", epoch+1, "cost=",loss, "W=",sess.run(W), "b=", sess.run(b))
            if not (loss == "NA"):
                plotdata["batchsize"].append(epoch)
                plotdata["loss"].append(loss)
                
            saver.save(sess, saverdir+"linermodel.cpkt", global_step=epoch)
            
    print("Finished!")
    print("cost=", sess.run(cost, feed_dict={X: train_X, Y: train_Y}), "W=", sess.run(W), "b=", sess.run(b))
    
#    show model
    plt.plot(train_X, train_Y, 'ro', label = "orginial_data")
    plt.plot(train_X, sess.run(W)*train_X + sess.run(b), label="FittedWLine")
    plt.legend()
    plt.show()
    
    plotdata["avgloss"] = moving_average(plotdata["loss"])
    plt.figure(1)
    plt.subplot(211)
    plt.plot(plotdata["batchsize"], plotdata["avgloss"], 'b--')
    plt.xlabel("Minibatch number")
    plt.ylabel("Loss")
    plt.title("Minibatch run vs. Training loss")

    plt.show()
    
    
    