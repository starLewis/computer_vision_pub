# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 22:39:41 2019

@author: lewisliu
"""

import os
import glob
import zipfile
import functools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['axes.grid'] = False
mpl.rcParams["figure.figsize"] = (12, 12)

from sklearn.model_selection import train_test_split
import matplotlib.image as mpimg
import pandas as pd
from PIL import Image

import tensorflow as tf
import tensorflow.contrib as tfcontrib
from tensorflow.python.keras import layers
from tensorflow.python.keras import losses
from tensorflow.python.keras import models
from tensorflow.python.keras import backend as K

competition_data_path = "/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/Studying/carvana-image-masking-challenge"
img_dir = os.path.join(competition_data_path, "train")
label_dir = os.path.join(competition_data_path, "train_masks")

df_train = pd.read_csv(os.path.join(competition_data_path, "train_masks.csv"))
ids_train = df_train['img'].map(lambda s: s.split('.')[0])
print("len ids_train: {}".format(len(ids_train)))

x_train_filenames = []
y_train_filenames = []
for img_id in ids_train:
    x_train_filenames.append(os.path.join(img_dir, "{}.jpg".format(img_id)))
    y_train_filenames.append(os.path.join(label_dir, "{}_mask.gif".format(img_id)))

x_train_filenames, x_val_filenames, y_train_filenames, y_val_filenames = train_test_split(x_train_filenames, y_train_filenames, test_size=0.2, random_state=42)
num_train_examples = len(x_train_filenames)
num_val_examples = len(x_val_filenames)

print("Number of training examples: {}".format(num_train_examples))
print("Number of validation examples: {}".format(num_val_examples))

# take a look at some of the images examples
display_num = 5
r_choices = np.random.choice(num_train_examples, display_num)
print(r_choices)

plt.figure(figsize=(10, 15))
for i in range(0, display_num * 2, 2):
    img_num = r_choices[i//2]
    x_pathname = x_train_filenames[img_num]
    y_pathname = y_train_filenames[img_num]
    
    plt.subplot(display_num, 2, i+1)
    plt.imshow(mpimg.imread(x_pathname))
    plt.title("Original Image")
    
    example_labels = Image.open(y_pathname)
    label_vals = np.unique(example_labels)

    plt.subplot(display_num, 2, i+2)
    plt.imshow(example_labels)
    plt.title("Masked Image")
    
plt.suptitle("Examples of Images and their Masks")
plt.show()

# set up
img_shape = (256, 256, 3)
batch_size = 3
epochs = 5

def _process_pathnames(fname, label_path):
#    We map this function onto each pathname pair
    img_str = tf.read_file(fname)
    img = tf.image.decode_jpeg(img_str, channels=3)
    
    label_img_str = tf.read_file(label_path)
    
#    These are gif images so they return as (num_frames, h, w, c)
    label_img = tf.image.decode_gif(label_img_str)[0]
    
#    The label image should only have values of 1 or 0, indicating pixel wise
#    object (car) or not (background). We take the first channel only.
    
    label_img = label_img[:, :, 0]
    label_img = tf.expand_dims(label_img, axis=-1)
    
    return img, label_img
    
def shift_img(output_img, label_img, width_shift_range, height_shift_range):
    """This fn will perform the horizontal or vertical shift"""
    if width_shift_range or height_shift_range:
        if width_shift_range:
            width_shift_range = tf.random_uniform([], -width_shift_range * img_shape[1], width_shift_range*img_shape[1])
            
        if height_shift_range:
            height_shift_range = tf.random_uniform([], -height_shift_range * img_shape[0], height_shift_range * img_shape[0])
            
#        Translate both
        output_img = tfcontrib.image.translate(output_img, [width_shift_range, height_shift_range])
        label_img = tfcontrib.image.translate(label_img, [width_shift_range, height_shift_range])
        
    return output_img, label_img
    

# flipping the image randomly
def flip_img(horizontal_flip, tr_img, label_img):
    if horizontal_flip:
        flip_prob = tf.random_uniform([], 0.0, 1.0)
        tr_img, label_img = tf.cond(tf.less(flip_prob, 0.5), 
                                    lambda: (tf.image.flip_left_right(tr_img), tf.image.flip_left_right(label_img)),
                                    lambda: (tr_img, label_img))
                                    
    return tr_img, label_img
    
# Assembling our transformations into our augment function
def _augment(img, 
             label_img, 
             resize = None, 
             scale = 1, 
             hue_delta = 0, 
             horizontal_flip = False, 
             width_shift_range = 0, 
             height_shift_range = 0):
    if resize is not None:
#        Resize both images
        img = tf.image.resize_images(img, resize)
        label_img = tf.image.resize_images(label_img, resize)
    if hue_delta:
        img = tf.image.random_hue(img, hue_delta)
        
    img, label_img = flip_img(horizontal_flip, img, label_img)
    img, label_img = shift_img(img, label_img, width_shift_range, height_shift_range)

    img = tf.to_float(img) * scale
    label_img = tf.to_float(label_img) * scale
    
    return img, label_img
    
def get_baseline_dataset(filenames,
                         labels,
                         preproc_fn = functools.partial(_augment), 
                         threads = 5, 
                         batch_size = batch_size,
                         shuffle = True):
    num_x = len(filenames)
#    Create a dataset from the filenames and labels
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
#    Map our preprocessing function to every element in our dataset, taking
#    advantage of multithreading
    
    dataset = dataset.map(_process_pathnames, num_parallel_calls = threads)
    if preproc_fn.keywords is not None and 'resize' not in preproc_fn.keywords:
        assert batch_size == 1, "Batching images must be of the same size"

    dataset = dataset.map(preproc_fn, num_parallel_calls = threads)

    if shuffle:
        dataset = dataset.shuffle(num_x)

#    It's necessary to repeat our data for all epochs
    dataset = dataset.repeat().batch(batch_size)

    return dataset

#Set up train and validation datasets
tr_cfg = {
    'resize': [img_shape[0], img_shape[1]],
    'scale': 1 / 255.,
    'hue_delta': 0.1, 
    'horizontal_flip': False,
    'width_shift_range': 0.1,
    'height_shift_range': 0.1
}
tr_preprocessing_fn = functools.partial(_augment, **tr_cfg)

val_cfg = {
    'resize': [img_shape[0], img_shape[1]],
    'scale': 1 / 255.
}
val_preprocessing_fn = functools.partial(_augment, **val_cfg)

train_ds = get_baseline_dataset(x_train_filenames,
                                y_train_filenames,
                                preproc_fn=tr_preprocessing_fn,
                                batch_size=batch_size)

val_ds = get_baseline_dataset(x_val_filenames,
                              y_val_filenames,
                              preproc_fn=val_preprocessing_fn,
                              batch_size=batch_size)

# show augmented data
temp_ds = get_baseline_dataset(x_train_filenames,
                               y_train_filenames,
                               preproc_fn=tr_preprocessing_fn,
                               batch_size=1,
                               shuffle=False)
# Let's examine some of these agumented images
data_aug_iter = temp_ds.make_one_shot_iterator()
next_element = data_aug_iter.get_next()

with tf.Session() as sess:
    batch_of_imgs, label = sess.run(next_element)
#    print("len batch_of_imgs: {}".format(len(batch_of_imgs)))
    
#    Running next element in our graph will produce a batch of images
    plt.figure(figsize=(10, 10))
    img = batch_of_imgs[0]
#    print(img.shape)
    
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    
    plt.subplot(1, 2, 2)
    plt.imshow(label[0, :, :, 0])
    plt.show()

# Build Model
def conv_block(input_tensor, num_filters):
    encoder = layers.Conv2D(num_filters, (3, 3), padding = "same")(input_tensor)
    encoder = layers.BatchNormalization()(encoder)
    encoder = layers.Activation("relu")(encoder)
    encoder = layers.Conv2D(num_filters, (3, 3), padding = "same")(encoder)
    encoder = layers.BatchNormalization()(encoder)
    encoder = layers.Activation("relu")(encoder)
    
    return encoder
    
def encoder_block(input_tensor, num_filters):
    encoder = conv_block(input_tensor, num_filters)
    encoder_pool = layers.MaxPooling2D((2, 2), strides = (2, 2))(encoder)
    
    return encoder_pool, encoder
    
def decoder_block(input_tensor, concat_tensor, num_filters):
    decoder = layers.Conv2DTranspose(num_filters, (2, 2), strides=(2, 2), padding="same")(input_tensor)
    decoder = layers.concatenate([concat_tensor, decoder], axis=-1)
    decoder = layers.BatchNormalization()(decoder)
    decoder = layers.Activation("relu")(decoder)
    
    decoder = layers.Conv2D(num_filters, (3, 3), padding = "same")(decoder)
    decoder = layers.BatchNormalization()(decoder)
    decoder = layers.Activation("relu")(decoder)
    
    decoder = layers.Conv2D(num_filters, (3, 3), padding = "same")(decoder)
    decoder = layers.BatchNormalization()(decoder)
    decoder = layers.Activation("relu")(decoder)
    
    return decoder
    
inputs = layers.Input(shape = img_shape)
# 256

encoder0_pool, encoder0 = encoder_block(inputs, 32)
# 128

encoder1_pool, encoder1 = encoder_block(encoder0_pool, 64)
# 64

encoder2_pool, encoder2 = encoder_block(encoder1_pool, 128)
# 32

encoder3_pool, encoder3 = encoder_block(encoder2_pool, 256)
# 16

encoder4_pool, encoder4 = encoder_block(encoder3_pool, 512)
# 8

center = conv_block(encoder4_pool, 1024)

decoder4 = decoder_block(center, encoder4, 512)
# 16

decoder3 = decoder_block(decoder4, encoder3, 256)
    
    

    
    
































