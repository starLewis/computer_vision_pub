# coding: utf-8
import sys, os
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from deep_convnet import DeepConvNet
from dataset.mnist import load_mnist

(x_train, t_train), (x_test, t_test) = load_mnist(flatten=False)

network = DeepConvNet()
network.load_params("deep_convnet_params.pkl")

sampled = 10000
x_test = x_test[:sampled]
t_test = t_test[:sampled]

print("calculate accuracy (float64)...")
print(network.accuracy(x_test, t_test))

# convert float16
x_test = x_test.astype(np.float16)
for param in network.params.values():
    param[...] = param.astype(np.float16)

print("calculate accuracy (float16) ... ")
print(network.accuracy(x_test, t_test))