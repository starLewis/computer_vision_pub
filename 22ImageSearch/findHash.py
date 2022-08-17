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

resizeImgWidth = 150
resizeImgWidth = 200

# Get the path of the training set
parser = ap.ArgumentParser()
parser.add_argument("-t", "--trainingSet", help="Path to Training Set", required="True")
args = vars(parser.parse_args())

# Get the training classes names and store them in a list
train_path = args["trainingSet"]
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
    print "Calculate Hash of %s image, %d of %d images"%(training_names[i], i, len(image_paths))

    hashValue = imagehash.average_hash(im)
    print hashValue
    hash_list.append(hashValue)

# print hash_list
# joblib.dump((hash_list, image_paths), "hash.pkl", compress=3)