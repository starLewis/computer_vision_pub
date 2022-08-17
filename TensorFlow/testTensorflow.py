# -*- coding: utf-8 -*-

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf

tf.enable_eager_execution()
a = tf.add(1, 2)

print a.numpy()
print a.dtype

hello = tf.constant('Hello, TensorFlow!')
print hello.numpy()