# coding: utf-8
import os, sys
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from dataset.mnist import load_mnist
from common.util import shuffle_dataset

(x_train, t_train), (x_test, t_test) = load_mnist(normalize=True)

x_train, t_train = shuffle_dataset(x_train, t_train)

validation_rate = 0.20
validation_num = int(x_train.shape[0] * validation_rate)

x_val = x_train[validation_num:]
t_val = t_train[validation_num:]
x_train = x_train[:validation_num]
t_train = t_train[:validation_num]

print x_val.shape
print t_val.shape
print x_train.shape
print t_train.shape