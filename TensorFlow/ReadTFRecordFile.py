# -*- coding: UTF-8 -*-
import tensorflow as tf

# use match_filenames_once to get files
files = tf.train.match_filenames_once('/home/liuxun/Clobotics/Data/DPData/studyTensorflow/data.tfrecords-*')

#
filename_queue = tf.train.string_input_producer(files, shuffle=False)

#read and decode one example data
reader = tf.TFRecordReader()
_, serialized_example = reader.read(filename_queue)
features = tf.parse_single_example(
    serialized_example,
    features={
        'i': tf.FixedLenFeature([], tf.int64),
        'j': tf.FixedLenFeature([], tf.int64),
    })

with tf.Session() as sess:
    init_op = tf.global_variables_initializer()
    #tf.initialize_all_variables().run()
    sess.run(init_op)
    
    sess.run(files)
    
    #tf.train.Coordinator
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)
    
    for i in range(6):
        print sess.run([features['i'], features['j']])
        
    coord.request_stop()
    coord.join(threads)