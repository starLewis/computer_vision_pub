#-*- coding: utf-8
import numpy as np
import cv2

# def hello(a, b):
#     return a + b

def print_arr():
    da = [0,0]
    print(da)
    return 1

def doStuff( x):
    print "X is %d" % x
    return 2 * x

def change(data):
    da = np.array(data, dtype=float)
    print(da)
    return 10

def add2args(a, b):
    print(a + b)
    return a + b

w = 300
h = 200
c = 3
def arrayreset(array):
    # print array
    a = array[0:len(array):3,:]
    b = array[1:len(array):3,:]
    c = array[2:len(array):3,:]
    
    a = a.T
    b = b.T
    c = c.T
    a = a[:,:,None]
    b = b[:,:,None]
    c = c[:,:,None]
    
    m = np.concatenate((a,b,c),axis=2)
    return m

def load_image(image):
    img = arrayreset(image)
    # cv2.imshow("pythonImg",img)
    print("hello")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray",imgGray)
    # cv2.waitKey()
    resultImgList = imgGray.tolist()
    print len(resultImgList)
    print len(resultImgList[0])
    return resultImgList