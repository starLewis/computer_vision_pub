# -*- coding: utf-8 -*-
"""
#!/usr/local/bin/python2.7
#python search.py -i dataset/train/ukbench00000.jpg
"""
import argparse as ap
import cv2
import imutils
import numpy as np
import os
# from matplotlib.font_manager import FontProperties
# font = FontProperties(fname=r"c:\windows\fonts\SimSun.ttc", size=14)
from pylab import *
from sklearn.externals import joblib
from scipy.cluster.vq import *

from sklearn import preprocessing
import numpy as np

from pylab import *
from PIL import Image
from rootsift import RootSIFT

resizeImgWidth = 150
resizeImgHeight = 200

# Get the path of the training set
parser = ap.ArgumentParser()
parser.add_argument("-i", "--image", help="Path to query image", required="True")
args = vars(parser.parse_args())

# Get query image path
image_path = args["image"]

# Load the classifier, class names, scaler, number of clusters and vocabulary
im_features, image_paths, idf, numWords, voc = joblib.load("bof.pkl")

# Create feature extraction and keypoint detector objects
# fea_det = cv2.FeatureDetector_create("SIFT")
# des_ext = cv2.DescriptorExtractor_create("SIFT")
detector = cv2.xfeatures2d.SIFT_create()

# List where all the descriptors are stored
des_list = []

im = cv2.imread(image_path)
im = cv2.resize(im,(resizeImgWidth, resizeImgHeight),interpolation=cv2.INTER_CUBIC)
# cv2.imshow("1", im)
# cv2.waitKey()
grayImg = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# kpts = fea_det.detect(im)
# kpts, des = des_ext.compute(im, kpts)
kpts, des = detector.detectAndCompute(grayImg, None)

#* normalize the number of features to resizeImgWidth
if des.shape[0] > resizeImgWidth:
    des, variance = kmeans(des, resizeImgWidth, 1)

# rootsift
#rs = RootSIFT()
#des = rs.compute(kpts, des)

des_list.append((image_path, des))

# Stack all the descriptors vertically in a numpy array
descriptors = des_list[0][1]

#
test_features = np.zeros((1, numWords), "float32")
words, distance = vq(descriptors,voc)
for w in words:
    test_features[0][w] += 1

# Perform Tf-Idf vectorization and L2 normalization
test_features = test_features*idf
test_features = preprocessing.normalize(test_features, norm='l2')

print test_features.shape
print im_features.T.shape
score = np.dot(test_features, im_features.T)

# print score.shape
rank_ID = np.argsort(-score)

# Visualize the results
#figure('Demo: BoW (bag of words)   ')
gray()
subplot(2,5,3)
# title(u'查询图像',fontproperties = font)
title('search')
imshow(im[:,:,::-1])
axis('off')
for i, ID in enumerate(rank_ID[0][0:5]):
    print(score[0][rank_ID[0][i]])
    img = Image.open(image_paths[ID])
    gray()
    subplot(2,5,i+6)
    # title(u'返回结果',fontproperties = font)
    title('D: %.3f'%(score[0][rank_ID[0][i]]))
    imshow(img)
    axis('off')

show()
