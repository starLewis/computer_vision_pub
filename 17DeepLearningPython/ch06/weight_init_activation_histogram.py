import numpy as np
import matplotlib.pyplot as plt

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)


x = np.random.randn(1000, 100)
node_num = 100
hidden_layer_size = 5
activations1 = {}
activations2 = {}

for i in range(hidden_layer_size):
    if i != 0:
        x = activations1[i-1]

    # w = np.random.randn(node_num, node_num) * 0.05
    w1 = np.random.randn(node_num, node_num) * 0.01

    print x.shape
    z1 = np.dot(x, w1)
    # a = sigmoid(z)
    a1 = relu(z1)
    print a1.shape
    activations1[i] = a1

    #*
    w2 = np.random.randn(node_num, node_num) * np.sqrt(2.0/node_num)
    z2 = np.dot(x, w2)
    a2 = relu(z2)
    activations2[i] = a2


for i, a in activations1.items():
    plt.subplot(1, len(activations1), i + 1)
    plt.title(str(i+1) + "-layer")
    plt.hist(a.flatten(), 30, range = (0, 1))


for i, a in activations2.items():
    plt.subplot(1, len(activations2), i+1)
    plt.title(str(i+1) + "-layer")
    if i != 0: plt.yticks([], [])
    plt.xlim(0.1, 1)
    plt.ylim(0, 7000)
    plt.hist(a.flatten(), 30, range = (0, 1))

    print a.flatten().shape
plt.show()