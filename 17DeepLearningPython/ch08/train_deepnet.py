# coding: utf-8
import sys, os
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from dataset.mnist import load_mnist
from deep_convnet import DeepConvNet
from common.trainer import Trainer

(x_train, t_train), (x_test, t_test) = load_mnist(flatten=False)

x_train = x_train[:5000]
t_train = t_train[:5000]
x_test = x_test[:1000]
t_test = t_test[:1000]

network = DeepConvNet()
trainer = Trainer(network, x_train, t_train, x_test, t_test,
                epochs=20, mini_batch_size=100,
                optimizer='Adam', optimizer_param={'lr':0.001},
                evaluate_sample_num_per_epoch=50)

trainer.train()

# save parameters
network.save_params("deep_convnet_params.pkl")
print("Saved Network Parameters!")

