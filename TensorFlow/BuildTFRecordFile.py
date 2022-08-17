# -*- coding: utf-8 -*-
import tensorflow as tf

#make tfrecord file's helping function
def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

#num_shards, the number of tfrecord 
num_shards = 2
#instances_per_shard, the number of data in each tfrecord file
instances_per_shard = 2

for i in range(num_shards):
    filename = ('/home/liuxun/Clobotics/Data/DPData/studyTensorflow/data.tfrecords-%.5d-of-%.5d' % (i, num_shards))
    
    writer = tf.python_io.TFRecordWriter(filename)
    
    for j in range(instances_per_shard):
        example = tf.train.Example(features=tf.train.Features(feature={
            'i': _int64_feature(i),
            'j': _int64_feature(j)}))
        writer.write(example.SerializeToString())
    
    writer.close()