# -*- coding: utf-8 -*-

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np

# build int feature
def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

# build bytes feature
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

mnist = input_data.read_data_sets("/home/liuxun/Clobotics/Data/CvDataOwnCloud/DeepLearning/MNIST_DATA", dtype=tf.uint8, one_hot=True)

images = mnist.train.images
labels = mnist.train.labels
# print labels
pixels = images.shape[1]
# print pixels    # 28x28 image size
num_examples = mnist.train.num_examples
# print num_examples

# save to TFRecord file
filename = "/home/liuxun/Clobotics/Data/CvDataOwnCloud/DeepLearning/MNIST_DATA_TFRecord/mnist_data_tfrecord.tfrecords"
writer = tf.python_io.TFRecordWriter(filename)
for index in range(num_examples):
    image_raw = images[index].tostring()
    # print image_raw
    example = tf.train.Example(features=tf.train.Features(feature={
        'pixels': _int64_feature(pixels),
        'label': _int64_feature(np.argmax(labels[index])),
        'image_raw': _bytes_feature(image_raw)}))
    writer.write(example.SerializeToString())
    
writer.close()