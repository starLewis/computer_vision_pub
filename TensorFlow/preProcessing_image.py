# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# random preprocess image
def distort_color(image, color_ordering=0):
    if color_ordering == 0:
        image = tf.image.random_brightness(image, max_delta=32.0/255.0)
        image = tf.image.random_saturation(image, lower=0.5, upper=1.5)
        image = tf.image.random_hue(image, max_delta=0.2)
        image = tf.image.random_contrast(image, lower=0.5, upper=1.5)
    elif color_ordering == 1:
        image = tf.image.random_saturation(image, lower=0.5, upper=1.5)
        image = tf.image.random_brightness(image, max_delta=32.0/255.0)
        image = tf.image.random_contrast(image, lower=0.5, upper=1.5)
        image = tf.image.random_hue(image, max_delta=0.2)
    #elif color_ordering == 2:
    
    return tf.clip_by_value(image, 0.0, 1.0)

#change image randomly for training
def preprocess_for_train(image, height, width, bbox):
    if bbox is None:
        bbox = tf.constant([0.0, 0.0, 1.0, 1.0],
                           dtype=tf.float32, shape=[1, 1, 4])
    #convert image's type to tensor's type
    if image.dtype != tf.float32:
        image = tf.image.convert_image_dtype(image, dtype=tf.float32)
        
    #clip image randomly
    bbox_begin, bbox_size, _ = tf.image.sample_distorted_bounding_box(tf.shape(image), bounding_boxes=bbox, min_object_covered=0.1)
    distorted_image = tf.slice(image, bbox_begin, bbox_size)
    
    #resize cliped image to fit nerualnetwork
    distorted_image = tf.image.resize_images(distorted_image, size=[height, width], method=np.random.randint(4))
    
    #flip left and right randomly
    distorted_image = tf.image.random_flip_left_right(distorted_image)
    
    #change image's color randomly
    distorted_image = distort_color(distorted_image, np.random.randint(2))
    
    return distorted_image

image_raw_data = tf.gfile.FastGFile("/home/liuxun/Clobotics/Data/DPData/cat13.jpg","r").read()

with tf.Session() as sess:
    img_data = tf.image.decode_jpeg(image_raw_data)
    boxes = tf.constant([[[0.05, 0.05, 0.9, 0.7],[0.35, 0.47, 0.5, 0.56]]])
    
    #run 6 times
    for i in range(6):
        #resize image to 299x299
        result = preprocess_for_train(img_data, 299, 299, boxes)
        if result.dtype != tf.float32:
            result = tf.image.convert_image_dtype(result, dtype=tf.float32)
        
        plt.imshow(result.eval())
        plt.show()