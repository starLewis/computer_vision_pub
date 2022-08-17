# import sys, os
# sys.path.append(os.pardir)
# import numpy as np
# from common.functions import softmax, cross_entropy_error
# from common.gradient import numerical_gradient

# class simpleNet:
#     def __init__(self):
#         self.W = np.random.randn(2, 3)

#     def predict(self, x):
#         return np.dot(x, self.W)

#     def loss(self, x, t):
#         z = self.predict(x)
#         y = softmax(z)
#         loss = cross_entropy_error(y, t)

#         return loss


# net = simpleNet()

# print net.W

# x = np.array([0.6, 0.9])
# p = net.predict(x)

# print np.argmax(p)

# t = np.array([0, 0, 1])
# print net.loss(x, t)
############################################################

# import sys, os
# sys.path.append(os.pardir)
# import numpy as np
# from dataset.mnist import load_mnist

# def cross_entropy_error(y, t):
#     if y.ndim == 1:
#         t = t.reshape(1, t.size)
#         y = y.reshape(1, y.size)
    
#     batch_size = y.shape[0]
#     return -np.sum(np.log(y[np.arange(batch_size), t] + 1e-7)) / batch_size


# (x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, one_hot_label=True)

# print x_train.shape
# print t_train.shape

# train_size = x_test.shape[0]
# batch_size = 10
# batch_mask = np.random.choice(train_size, batch_size)
# print batch_mask

# x_batch = x_train[batch_mask]
# t_batch = t_train[batch_mask]
# print x_batch.shape
#**********************************************************************

# import numpy as np
# import matplotlib.pyplot as plt
# import math
# from mpl_toolkits.mplot3d import Axes3D


# def function_2(x):
#     return x[0]**2 + x[1]**2


# x = np.arange(-3, 3, 0.5)
# y = np.arange(-3, 3, 0.5)
# x,y = np.meshgrid(x, y)

# x2 = [x, y]

# z = function_2(x2)
# print z

# fig = plt.figure()
# # ax = Axes3D(fig)
# ax = fig.add_subplot(111, projection='3d')

# # ax = plt.subplot(111, projection='3d')
# ax.plot_trisurf(x, y, z)

# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')

# plt.show()

#************************************************************************

# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
 
# def function_2(x):
#     return x[0]**2 + x[1]**2

# fig = plt.figure()
# ax = Axes3D(fig)
 
# X = np.arange(-3, 3, 0.05)
# Y = np.arange(-3, 3, 0.05)
# X, Y = np.meshgrid(X, Y)
# # Z = X ** 2 + Y ** 2
# Z = function_2([X, Y])

# ax.plot_surface(X, Y, Z, cmap=plt.cm.winter)
 
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')

# # plt.show()

# def numerical_gradient(f, x):
#     h = 1e-4
#     grad = np.zeros_like(x)

#     for idx in range(x.size):
#         tmp_val = x[idx]

#         x[idx] = tmp_val + h
#         fxh1 = f(x)

#         x[idx] = tmp_val - h
#         fxh2 = f(x)

#         grad[idx] = (fxh1 - fxh2) / (2*h)
#         x[idx] = tmp_val

#     return grad

# print numerical_gradient(function_2, np.array([3.0, 4.0]))
# print numerical_gradient(function_2, np.array([0.0, 2.0]))
# print numerical_gradient(function_2, np.array([3.0, 0.0]))
#*******************************************************************

# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

# def _numerical_gradient_no_batch(f, x):
#     h = 1e-4
#     grad = np.zeros_like(x)

#     for idx in range(x.size):
#         tmp_val = x[idx]
#         x[idx] =  float(tmp_val) + h
#         fxh1 = f(x)

#         x[idx] = float(tmp_val) - h
#         fxh2 = f(x)
#         grad[idx] = (fxh1 - fxh2) / (2*h)
#         x[idx] = tmp_val

#     return grad

# def numerical_gradient(f, X):
#     if X.ndim == 1:
#         return _numerical_gradient_no_batch(f, X)
#     else:
#         grad = np.zeros_like(X)

#         for idx, x in enumerate(X):
#             grad[idx] = _numerical_gradient_no_batch(f, x)
        
#         return grad

# def function_2(x):
#     if x.ndim == 1:
#         return np.sum(x**2)
#     else:
#         return np.sum(x**2, axis=1)


# def gradient_descent(f, init_x, lr = 0.01, step_num = 100):
#     x = init_x
    
#     for i in range(step_num):
#         grad = numerical_gradient(f, x)
#         x -= lr * grad

#     return x

# if __name__ == "__main__":
#     # x0 = np.arange(-2, 2.5, 0.25)
#     # x1 = np.arange(-2, 2.5, 0.25)
#     # X, Y = np.meshgrid(x0, x1)

#     # X = X.flatten()
#     # Y = Y.flatten()

#     # grad = numerical_gradient(function_2, np.array([X, Y]))

#     # plt.figure()
#     # plt.quiver(X, Y, -grad[0], -grad[1], angles='xy', color='#666666')
#     # plt.xlim([-2, 2])
#     # plt.ylim([-2, 2])
#     # plt.xlabel('x0')
#     # plt.ylabel('x1')
#     # plt.grid()
#     # # plt.legend()
#     # # plt.draw()
#     # plt.show()


#     init_x = np.array([-4.0, 3.0])
#     print gradient_descent(function_2, init_x=init_x, lr = 1e-10, step_num=100)
#**********************************************************************************

import sys, os
sys.path.append(os.pardir)
import numpy as np
from common.functions import softmax, cross_entropy_error
from common.gradient import numerical_gradient

def _numerical_gradient_no_batch(f, x):
    h = 1e-4
    grad = np.zeros_like(x)

    for idx in range(x.size):
        tmp_val = x[idx]
        x[idx] =  float(tmp_val) + h
        fxh1 = f(x)

        x[idx] = float(tmp_val) - h
        fxh2 = f(x)
        grad[idx] = (fxh1 - fxh2) / (2*h)
        x[idx] = tmp_val

    return grad

def numerical_gradient(f, X):
    if X.ndim == 1:
        return _numerical_gradient_no_batch(f, X)
    else:
        grad = np.zeros_like(X)

        for idx, x in enumerate(X):
            grad[idx] = _numerical_gradient_no_batch(f, x)
        
        return grad

def gradient_descent(f, init_x, lr = 0.01, step_num = 100):
    x = init_x
    
    for i in range(step_num):
        grad = numerical_gradient(f, x)
        x -= lr * grad

    return x

class simpleNet:
    def __init__(self):
        self.W = np.random.randn(2, 3)
        self.init_x = np.array([0.6, 0.9])
        self.t = np.array([0, 0, 1])

    def predict(self, x):
        return np.dot(x, self.W)

    def loss(self, x, t):
        z = self.predict(x)
        y =softmax(z)
        loss = cross_entropy_error(y, t)

        return loss

    def f(self, W):
        return self.loss(self.init_x, self.t)


if __name__ == "__main__":
    net = simpleNet()

    # print net.W

    x = np.array([0.6, 0.9])
    p = net.predict(x)

    p = softmax(p)

    # print p

    # print np.argmax(p)

    t = np.array([0, 0, 1])
    print 'loss:', net.loss(x, t)

    dW = gradient_descent(net.f, net.W)
    print dW
