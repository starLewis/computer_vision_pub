# -*- coding: utf-8 -*-

import tensorflow as tf

# build a reader to read data from TFRecord
reader = tf.TFRecordReader()

# create a list for TFRecord files
filename_queue = tf.train.string_input_producer(
    ["/home/liuxun/Clobotics/Data/CvDataOwnCloud/DeepLearning/MNIST_DATA_TFRecord/mnist_data_tfrecord.tfrecords"])

# read one example
_, serialized_example = reader.read(filename_queue)
print serialized_example
# analysis one example
features = tf.parse_single_example(
    serialized_example, 
    features={
        'image_raw': tf.FixedLenFeature([], tf.string),
        'pixels': tf.FixedLenFeature([], tf.int64),
        'label': tf.FixedLenFeature([], tf.int64),
    })

#tf.decode_raw can change char to pixels' array
images = tf.decode_raw(features['image_raw'], tf.uint8)
labels = tf.cast(features['label'], tf.int32)
pixels = tf.cast(features['pixels'], tf.int32)

sess = tf.Session()
coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess, coord=coord)

for i in range(10):
    image, label, pixel = sess.run([images, labels, pixels])
    #print image
    #print label
    print pixel