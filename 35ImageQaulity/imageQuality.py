#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:15:30 2019

@author: lewisliu
"""

import cv2

#* calculate Laplacian value of image
def Laplacian(img):
    '''
    img: gray image
    return: float. 
    '''
    return cv2.Laplacian(img, cv2.CV_64F).var()


if __name__ == "__main__":
    img_path = "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/VS/11_Lap_328_ef1dc092-4b10-4f88-a025-fc872bb7d2ab.jpg"
    img = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("Lap value: {}".format(Laplacian(img_gray)))