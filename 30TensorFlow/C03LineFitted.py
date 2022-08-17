# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

def buildData():
    train_X = np.linspace(-1, 1, 100)
    train_Y = 2 * train_X + np.random.randn((train_X.shape)[0]) * 0.3
#    to do, *train_X.shape
    plt.plot(train_X, train_Y, 'ro', label='Original Data')
    plt.legend()
    plt.show()
    
    return train_X, train_Y
    
def moving_average(a, w = 10):
    if len(a) < w:
        return a[:]
    
    return [val if idx < w else sum(a[(idx-w):idx]) / w for idx, val in enumerate(a)]

if __name__ == "__main__":
    # build original data    
    train_X, train_Y = buildData()
    
#    inference
    X = tf.placeholder("float")
    Y = tf.placeholder("float")
    
    W = tf.Variable(tf.random_normal([1]), name = "weight")
    b = tf.Variable(tf.zeros([1]), name = "bias")
    
    Z = tf.multiply(X, W) + b
    
#    back propagation
    cost = tf.reduce_mean(tf.square(Y - Z))
    learning_rate = 0.01
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)
    
#    initial global variables
    init = tf.global_variables_initializer()
#    define parameters
    training_epochs = 30
    display_step = 2
    
#    start session
    with tf.Session() as sess:
        sess.run(init)
        
        plotdata = {"batchsize": [], "loss": []}
#        input data
        for epoch in range(training_epochs):
            for (x, y) in zip(train_X, train_Y):
                sess.run(optimizer, feed_dict = {X: x, Y: y})
                
#            display details
            if epoch % display_step == 0:
                loss = sess.run(cost, feed_dict = {X: train_X, Y: train_Y})
                print("Epoch: ", epoch+1, "cost=", loss, "W=", sess.run(W), "b=",sess.run(b))
                
                if not (loss == "NA"):
                    plotdata["batchsize"].append(epoch)
                    plotdata["loss"].append(loss)
                        
        print("Finished!")
#        print("cost=", sess.run(cost, feed_dict = {X: train_X, Y: train_Y}), "W=", sess.run(W), "b=", sess.run(b))
        print("cost:", cost.eval({X: train_X, Y: train_Y}))
        
#        display result
        plt.plot(train_X, train_Y, 'ro', label = 'Original data')
        plt.plot(train_X, sess.run(W) * train_X + sess.run(b), label = 'FittedLine')
        plt.legend()
        plt.show()
        
#        display middle status
        plotdata["avgloss"] = moving_average(plotdata["loss"])
        plt.figure(1)
        plt.subplot(211)
        plt.plot(plotdata["batchsize"], plotdata["avgloss"], 'b--')
        plt.xlabel("Minibatch number")
        plt.ylabel("Loss")
        plt.title("Minibatch run vs. Training loss")
        
        plt.show()
        
#        inference
        print("x=0.2, z=", sess.run(Z, feed_dict = {X: 0.2}))