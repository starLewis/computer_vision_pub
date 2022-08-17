import sys, os
sys.path.append(os.pardir)
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def function03(x):
    return  x[0] + x[1]

def showFunction03Figure():
    fig = plt.figure()
    ax = Axes3D(fig)

    X = np.arange(-3, 3, 0.05)
    Y = np.arange(-3, 3, 0.05)
    Z = np.arange(-3, 3, 0.05)
    [X, Y] = np.meshgrid(X, Y)

    # Z = function03([X, Y])

    ax.plot_surface(X, Y, Z, cmap = plt.cm.winter)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()

if __name__ == "__main__":
    showFunction03Figure()
    