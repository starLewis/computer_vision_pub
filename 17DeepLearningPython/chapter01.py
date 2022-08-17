# class Man:
#     def __init__(self, name):
#         self.name = name
#         print('Initialized!')

#     def hello(self):
#         print("Hello " + self.name + "!")

#     def goodbye(self):
#         print("Good-bye " + self.name + "!")

# if __name__ == "__main__":
#     m = Man("David")
#     m.hello()
#     m.goodbye()

# import numpy as np
# import matplotlib.pyplot as plt

# x = np.arange(0, 6, 0.1)
# y = np.sin(x)

# plt.plot(x, y)
# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt

# x = np.arange(0, 6, 0.1)
# y1 = np.sin(x)
# y2 = np.cos(x)

# plt.plot(x, y1, label = "sin")
# plt.plot(x, y2, linestyle = "--", label = "cos")
# plt.xlabel("x")
# plt.ylabel("y")
# plt.title('sin & cos')
# plt.legend()
# plt.show()

##***********************************************************
# def AND(x1, x2):
#     w1, w2, theta = 0.5, 0.5, 0.7
#     temp = x1*w1 + x2*w2
#     if temp <= theta:
#         return 0
#     elif temp > theta:
#         return 1

# print AND(0, 0)
# print AND(0, 1)
# print AND(1, 0)
# print AND(1, 1)


##************************************************************
import numpy as np
def AND(x1, x2):
    x = np.array([x1, x2])
    w = np.array([0.5, 0.5])
    b = -0.7
    tmp = np.sum(w*x) + b
    if tmp <= 0:
        return 0
    else:
        return 1

def NAND(x1, x2):
    x = np.array([x1, x2])
    w = np.array([-0.5, -0.5])
    b = 0.7
    tmp = np.sum(w*x) + b
    if tmp <= 0:
        return 0
    else:
        return 1

def OR(x1, x2):
    x = np.array([x1, x2])
    w = np.array([0.5, 0.5])
    b = -0.2
    tmp = np.sum(w*x) + b
    if tmp <= 0:
        return 0
    else:
        return 1

def XOR(x1, x2):
    s1 = NAND(x1, x2)
    s2 = OR(x1, x2)
    y = AND(s1, s2)
    return y

print XOR(0,0)
print XOR(0,1)
print XOR(1,0)
print XOR(1,1)