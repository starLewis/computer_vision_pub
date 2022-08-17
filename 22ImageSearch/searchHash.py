# -*- coding: utf-8 -*-
"""
#!/usr/local/bin/python2.7
"""
import argparse as ap
import imagehash
from PIL import Image
import numpy as np
import os
from sklearn.externals import joblib
import imutils
from pylab import *
import cv2

resizeImgWidth = 150
resizeImgHeight = 200

def hashList(trainPath):
    # Get the training classes names and store them in a list
    train_path = trainPath
    #train_path = "dataset/train/"

    training_names = os.listdir(train_path)

    # Get all the path to the images and save the
    # m in a list
    # image_paths and the corresponding label in image_paths
    image_paths = []
    for training_name in training_names:
        image_path = os.path.join(train_path, training_name)
        image_paths += [image_path]

    hash_list = []
    for i, image_path in enumerate(image_paths):
        im = Image.open(image_path)
        im = im.resize((resizeImgWidth, resizeImgHeight))

        print "Calculate Hash of %s image, %d of %d images"%(training_names[i], i, len(image_paths))

        hashValue = imagehash.average_hash(im)
        print hashValue
        hash_list.append(hashValue)
    return hash_list,image_paths

def search(imgPath, hash_list, image_paths):
    # Get query image path
    image_path = imgPath
    im = Image.open(image_path)
    im = im.resize((resizeImgWidth, resizeImgHeight))

    hash_value = imagehash.average_hash(im)
    
    score = []
    for hashValue in hash_list:
        score.append(hashValue - hash_value)

    rank_ID = np.argsort(score)
    im = cv2.imread(image_path)

    gray()
    subplot(2,5,3)
    title('search')
    imshow(im[:,:,::-1])
    axis('off')
    for i, ID in enumerate(rank_ID[0:5]):
        print(score[rank_ID[i]])
        img = Image.open(image_paths[ID])
        gray()
        subplot(2,5,i+6)
        # title(u'返回结果',fontproperties = font)
        title('D: %.3f'%(score[rank_ID[i]]))
        imshow(img)
        axis('off')
    show()

    # print imagehash.ImageHash(hash_value)
    # print hash_list[0]
    # print str(hash_value) - hash_list[0]
    return 0

if __name__ == "__main__":
    # Get the path of the training set
    parser = ap.ArgumentParser()
    parser.add_argument("-i", "--image", help="Path to query image", required="True")
    args = vars(parser.parse_args())

    imgPath = args["image"]

    trainPath = "/home/lewisliu/Clobotics/Codes/CVTestCodes/22ImageSearch/dataset/train"
    hash_list,image_paths = hashList(trainPath)

    search(imgPath, hash_list, image_paths)