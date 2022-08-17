# import numpy as np

# def step_function(x):
#     y = x > 0
#     return y.astype(np.int)

# print step_function(np.array([-1.0, 1.0, 2.0]))

##*******************************************************
# import numpy as np
# import matplotlib.pylab as plt

# def step_function(x):
#     return np.array(x > 0, dtype = np.int)

# x = np.arange(-5.0, 5.0, 0.1)
# y = step_function(x)
# plt.plot(x, y)
# plt.ylim(-0.1, 1.1)
# plt.show()

##*******************************************************

# import numpy as np
# import matplotlib.pylab as plt

# def sigmoid(x):
#     return 1 / (1 + np.exp(-x))

# def step_function(x):
#     return np.array(x > 0, dtype = np.int)

# x = np.arange(-5.0, 5.0, 0.1)
# y = sigmoid(x)
# y1 = step_function(x)

# plt.plot(x, y1, linestyle = "--", label = "jieyue")
# plt.plot(x, y, label = "sigmoid")
# plt.ylim(-0.1, 1.1)
# plt.show()

##*******************************************************
# import numpy as np
# import matplotlib.pylab as plt

# def relu(x):
#     return np.maximum(0, x)

# x = np.arange(-5.0, 5.0, 0.1)
# y = relu(x)
# plt.plot(x, y)
# plt.ylim(-1, 5)
# plt.show()

##*********************************************************
# import numpy as np

# def sigmoid(x):
#     return 1 / (1 + np.exp(-x))

# X = np.array([1.0, 0.5])
# W1 = np.array([[0.1, 0.3, 0.5], [0.2, 0.4, 0.6]])
# B1 = np.array([0.1, 0.2, 0.3])

# print W1.shape
# print X.shape
# print B1.shape

# A1 = np.dot(X, W1) + B1
# Z1 = sigmoid(A1)

# print A1
# print Z1

# W2 = np.array([[0.1, 0.4], [0.2, 0.5], [0.3, 0.6]])
# B2 = np.array([0.1, 0.2])

# print W2
# print B2

# A2 = np.dot(Z1, W2) + B2
# Z2 = sigmoid(A2)

# print Z2

# def identity_function(x):
#     return x

# W3 = np.array([[0.1, 0.3], [0.2, 0.4]])
# B3 = np.array([0.1, 0.2])

# A3 = np.dot(Z2, W3) + B3
# Y = identity_function(A3)

# print A3

##**********************************************************
# import numpy as np

# def sigmoid(x):
#     return 1 / (1 + np.exp(-x))

# def identity_function(x):
#     return x

# def init_network():
#     network = {}
#     network['W1'] = np.array([[0.1, 0.3, 0.5],[0.2, 0.4, 0.6]])
#     network['b1'] = np.array([0.1, 0.2, 0.3])
#     network['W2'] = np.array([[0.1, 0.4],[0.2, 0.5],[0.3, 0.6]])
#     network['b2'] = np.array([0.1, 0.2])
#     network['W3'] = np.array([[0.1, 0.3],[0.2, 0.4]])
#     network['b3'] = np.array([0.1, 0.2])

#     return network

# def forward(network, x):
#     W1, W2, W3 = network['W1'], network['W2'], network['W3']
#     b1, b2, b3 = network['b1'], network['b2'], network['b3']

#     a1 = np.dot(x, W1) + b1
#     z1 = sigmoid(a1)
#     a2 = np.dot(z1, W2) + b2
#     z2 = sigmoid(a2)
#     a3 = np.dot(z2, W3) + b3
#     y = identity_function(a3)

#     return y

# network = init_network()
# x = np.array([1.0, 0.5])
# y = forward(network, x)

# print y

##**************************************************************
# import numpy as np

# def softmax(a):
#     exp_a = np.exp(a)
#     sum_exp_a = np.sum(exp_a)
#     y = exp_a / sum_exp_a

#     return y

# a = np.array([0.3, 2.9, 4.0])

# print softmax(a)

##***************************************************************
# import numpy as np

# def softmax(a):
#     c = np.max(a)
#     exp_a = np.exp(a - c)
#     sum_exp_a = np.sum(exp_a)
#     y = exp_a / sum_exp_a

#     return y

# a = np.array([0.3, 2.9, 4.0])
# y = softmax(a)

# print y

# print np.sum(y)

##*****************************************************************
# import pickle
# a_dict = {'da': 111, 2: [23, 1, 4], '23': {1:2, 'd':'sad'}}

# file = open("/home/lewisliu/Desktop/pickle_example.pickle",'wb')
# pickle.dump(a_dict, file)
# file.close

##*****************************************************************
# import pickle
# with open("/home/lewisliu/Desktop/pickle_example.pickle", 'rb') as file:
#     a_dict1 = pickle.load(file)

# print a_dict1
##******************************************************************

# import sys, os
# sys.path.append(os.pardir)
# import numpy as np
# from dataset.mnist import load_mnist
# from PIL import Image

# def img_show(img):
#     pil_img = Image.fromarray(np.uint8(img))
#     pil_img.show()

# (x_train, t_train), (x_test, t_test) = load_mnist(flatten=True, normalize=False)

# img = x_train[0]
# label = t_train[0]
# print(label)  # 5

# print(img.shape)  # (784,)
# img = img.reshape(28, 28)
# print(img.shape)  # (28, 28)

# print x_train.shape
# print t_train.shape
# print x_test.shape
# print t_test.shape

# img_show(img)

##**********************************************************************
# import sys, os
# sys.path.append(os.pardir)
# import numpy as np
# from dataset.mnist import load_mnist
# from PIL import Image
# import pickle

# def sigmoid(x):
#     return 1 / (1 + np.exp(-x))

# def get_data():
#     (x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, flatten=True, one_hot_label=False)

#     return x_test, t_test

# def init_network():
#     with open("/home/lewisliu/Clobotics/Codes/CVTestCodes/17DeepLearningPython/sample_weight_py2.pkl", "rb") as f:
#         network = pickle.load(f)
#         # pickle.dump()

#     return network

# def softmax(a):
#     c = np.max(a)
#     exp_a = np.exp(a - c)
#     sum_exp_a = np.sum(exp_a)
#     y = exp_a / sum_exp_a

#     return y

# def predict(network, x):
#     W1, W2, W3 = network['W1'], network['W2'], network['W3']
#     b1, b2, b3 = network['b1'], network['b2'], network['b3']

#     a1 = np.dot(x, W1) + b1
#     z1 = sigmoid(a1)
#     a2 = np.dot(z1, W2) + b2
#     z2 = sigmoid(a2)
#     a3 = np.dot(z2, W3) + b3
#     y = softmax(a3)

#     return y

# # network = init_network()
# # print network

# x, t = get_data()
# network = init_network()
# print network

# # accuracy_cnt = 0
# # for i in range(len(x)):
# #     y = predict(network, x[i])
# #     p = np.argmax(x)
# #     if p == t[i]:
# #         accuracy_cnt +=1

# # print "Accuracy: " + str(float(accuracy_cnt) / len(x))

##**************************************************************
# import numpy as np

# def mean_squared_error(y, t):
#         return 0.5 * np.sum((y - t)**2)

# t = [  0,    0,   1,   0,    0,   0,   0,   0,   0,   0]
# y = [0.1, 0.05, 0.6, 0.0, 0.05, 0.1, 0.0, 0.1, 0.0, 0.0]

# t = np.array(t)
# y = np.array(y)
# print y-t

# print mean_squared_error(y, t)

# y1 = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]

# print mean_squared_error(y1, t)
##************************************************************

# import numpy as np

# def cross_entropy_error(y, t):
#         delta = 1e-7
#         return -np.sum(t * np.log(y + delta))

# t = [  0,    0,   1,   0,    0,   0,   0,   0,   0,   0]
# y = [0.1, 0.05, 0.6, 0.0, 0.05, 0.1, 0.0, 0.1, 0.0, 0.0]

# y1 = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]

# t = np.array(t)
# y = np.array(y)
# y1 = np.array(y1)

# print cross_entropy_error(y, t)

# print cross_entropy_error(y1, t)
##************************************************************

# import numpy as np
# print np.random.choice(60000, 10)

##************************************************************
import numpy as np
import matplotlib.pylab as plt

def function_1(x):
        return 0.01*x**2 + 0.1*x

def numerical_diff(f, x):
        h = 1e-4
        return (np.array(f(x+h)) - np.array(f(x-h)))/(2*h)
        

def function_2(x, k, x1):
        y1 = function_1(x1)
        return k * (x - x1) + y1

x = np.arange(0.0, 20.0, 0.1)
y = function_1(x)
k = numerical_diff(function_1, x)
yy = function_2(x, k, 5)

plt.xlabel("x")
plt.ylabel("f(x)")
plt.plot(x, yy)
plt.plot(x, y)
plt.show()
