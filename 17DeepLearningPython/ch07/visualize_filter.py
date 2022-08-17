# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
from simple_convnet import SimpleConvNet

def filter_show(filters, figname, nx = 8, margin = 3, scale = 10):
    FN, C, FH, FW = filters.shape
    print FN
    ny = int(np.ceil(1.0 * FN / nx))

    fig = plt.figure(figname)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)

    for i in range(FN):
        # print ny, nx, i
        ax = fig.add_subplot(ny, nx, i+1, xticks=[], yticks=[])
        ax.imshow(filters[i, 0], cmap=plt.cm.gray_r, interpolation='nearest')
    plt.legend()
    plt.show()

network = SimpleConvNet()

# initial weight randomly
figname = "initial"
filter_show(network.params['W1'], figname)

# studied weight
figname = "trained"
print figname
network.load_params("params.pkl")
filter_show(network.params['W1'], figname)