#!/usr/bin/env python2
#-*-coding:utf-8-*-
"""
Created on Fri Mar 20 15:39:30 2019

@author: lewisliu
"""

import cv2
import numpy as np
import math
import os
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import imageQuality
from tqdm import tqdm
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

# # 支持中文
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

plt.figure(figsize=(10,6))

ours_imgs_folder_paths = [
    "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/1_0",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/1_1",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/1_2",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/1_3",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/2_0",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/2_1",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/2_2",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/2_3",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/3_0",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/3_1",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/3_2",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOurs/3_3"
]
others_imgs_folder_paths = [
    "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOthers/A",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOthers/B",
    # "/home/lewisliu/Clobotics/WindPower/ImageQuality/Data/IQVS01/FromOthers/C"
]

#* list all images in the folder
def list_images_in_one_folder(folder_path):
    pics_path = []
    for i in os.walk(folder_path):
        for j in i[2]:
            if 'JPG' in j or 'jpg' in j:
                pic_path = os.path.join(i[0],j)
                pics_path.append(pic_path)
    
    return pics_path

#* define calculate one image's image quality value
def cal_img_qaulity(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img_q = imageQuality.Laplacian(img_gray)
    
    return img_q

#* calculate all images' q and hist
def cal_all_images_q_hist(folder_paths):
    img_q_sum = 0
    img_num = 0
    img_q_array = []
    for cur_folder_path in tqdm(folder_paths):
        pics_path = list_images_in_one_folder(cur_folder_path)
        for pic_path in tqdm(pics_path):
            img_num += 1
            img_data = cv2.imread(pic_path)
            img_q = cal_img_qaulity(img_data)
            img_q_sum += img_q
            img_q_array.append(img_q)

    img_q_average = 0
    if img_num > 0:
        img_q_average = img_q_sum / img_num
    
    print("img_q_average: {}".format(img_q_average))
    print("min_q: {}, max_q: {}".format(min(img_q_array), max(img_q_array)))
    print("img_sum: {}".format(img_num))
    # print(img_q_array)
    #* calculate the distribution
    scale = 10.0
    # X = np.linspace(0, 100, 100)
    X = np.arange(0, 100, 1)
    Y = np.zeros(100)
    for cur_img_q in img_q_array:
        y = int(cur_img_q)
        if y >= len(Y):
            print("Wrong! cur_y: {} is out the range of array {}".format(y, len(Y)))
        else:
            Y[y] += 1
    for index in range(len(Y)):
        Y[index] /= img_num
    X = np.array(X)
    Y = np.array(Y)
    
    return img_q_average, img_num, X, Y

if __name__ == "__main__":
    #* calculate the average laplacian value for ours images
    our_imgs_ave_q, our_imgs_sum, our_X, our_Y = cal_all_images_q_hist(ours_imgs_folder_paths)
    print("our_imgs_ave_q: {}".format(our_imgs_ave_q))
    print("our_imgs_sum: {}".format(our_imgs_sum))

    #* calculate the average laplacian value for others images
    other_imgs_ave_q, other_imgs_sum, other_X, other_Y = cal_all_images_q_hist(others_imgs_folder_paths)
    print("other_imgs_ave_q: {}".format(other_imgs_ave_q))
    print("other_imgs_sum: {}".format(other_imgs_sum))

    # plt.plot(our_X, our_Y, linestyle='-', color ='b', label="Clobotics Images")
    plt.plot(our_X, our_Y, linestyle='-', color ='b', label="Dataset A: Clobotics Images Qaulity Distribution Curve") # Qaulity Distribution Curve
    plt.plot(other_X, other_Y,linestyle='-', color = 'r', label="Dataset B: Third-part Images Qaulity Distribution Curve")
    # plt.title(u'图集图像清晰度分布图')
    plt.xlabel('Image Quality Laplacian Value')
    plt.ylabel('Images Quality Probability')
    plt.title("Images Quality Distribution Graph")
    plt.grid(alpha=0.2)
    plt.legend()
    plt.savefig("g.png")
    plt.show()


    # xnew = np.linspace(0,100,1000) #300 represents numbof points to make between T.min and T.max
    # power_smooth = spline(X,Y,xnew)
    # plt.plot(xnew,power_smooth)
    # plt.show()

#     # plt.savefig("g.png")

# if __name__ == "__main__":
#     T = np.array([6, 7, 8, 9, 10, 11, 12])
#     power = np.array([1.53E+03, 5.92E+02, 2.04E+02, 7.24E+01, 2.72E+01, 1.10E+01, 4.70E+00])
#     plt.plot(T,power)
#     plt.show()
