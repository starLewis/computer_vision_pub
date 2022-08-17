# coding: utf-8
import sys, os
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from dataset.mnist import load_mnist
from common.multi_layer_net_extend import MultiLayerNetExtend
from common.trainer import Trainer

(x_train, t_train), (x_test, t_test) = load_mnist(normalize=True)

#* reduce trainning data
x_train = x_train[:300]
t_train = t_train[:300]

#* set dropout and ratio
use_dropout = True
dropout_ratio = 0.2

network = MultiLayerNetExtend(input_size = 784, hidden_size_list = [100, 100, 100, 100, 100, 100],
                                output_size = 10, use_dropout = use_dropout, dropout_ration = dropout_ratio)

trainer = Trainer(network, x_train, t_train, x_test, t_test, epochs = 301, mini_batch_size = 100,
                    optimizer = 'sgd', optimizer_param = {'lr': 0.01}, verbose = True)

trainer.train()

train_acc_list, test_acc_list = trainer.train_acc_list, trainer.test_acc_list

#* draw figure
markers = {}