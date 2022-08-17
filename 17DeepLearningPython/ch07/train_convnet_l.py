# coding: utf-8
import sys, os
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from dataset.mnist import load_mnist
from simple_convnet import SimpleConvNet
from common.trainer import Trainer
from common.functions import *

# read data
(x_train, t_train), (x_test, t_test) = load_mnist(flatten=False)

x_test, t_test = x_test[:10], t_test[:10]

network = SimpleConvNet(input_dim=(1, 28, 28), conv_param={'filter_num':30, 'filter_size':5, 'pad':0, 'stride':1},
                        hidden_size=100, output_size=10, weight_init_std=0.01)

# load paramseters
network.load_params('params.pkl')

# x_unit_test = x_test[0]
res = network.predict(x_test)

res = softmax(res)

res = np.argmax(res, axis=1)

print res