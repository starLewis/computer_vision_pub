import tensorflow as tf
import numpy as np

# with tf.Session() as sess:
#     with tf.device("/cpu:0"):
#         matrix1 = tf.constant([[3., 3.]])
#         matrix2 = tf.constant([[2.], [2.]])

#         product = tf.matmul(matrix1, matrix2)
#         result = sess.run([product])
#         print result

# input1 = tf.placeholder(tf.float32)
# input2 = tf.placeholder(tf.float32)
# output = tf.multiply(input1, input2)
# with tf.Session() as sess:
#     print sess.run([output], feed_dict = {input1:[7.], input2:[2.]})

# with tf.variable_scope("foo"):
#     with tf.name_scope("bar"):
#         v = tf.get_variable("v",[1])
#         b = tf.Variable(tf.zeros([1]), name='b')
#         x = 1.0 + v

# print v.name
# print b.name
# print x.op.name

# a = tf.constant([[1.0, 0.0], [1.0, 2.0], [1.0, 2.0]])
# sess = tf.Session()
# print sess.run(tf.nn.relu(a))

# a = tf.constant([-1.0, 2.0])
# with tf.Session() as sess:
#     b = tf.nn.relu(a)
#     print sess.run(b)

# a = tf.constant([[1.0, 2.0, 3.0, 4.0]])
# with tf.Session() as sess:
#     b = tf.nn.dropout(a, 0.5, noise_shape = [1, 4])
#     print sess.run(b)
#     b = tf.nn.dropout(a, 0.5, noise_shape = [1, 1])
#     print sess.run(b)

# input_data = tf.Variable(np.random.rand(10,9,9,3), dtype = np.float32)
# filter_data = tf.Variable(np.random.rand(2,2,3,2), dtype = np.float32)
# y = tf.nn.conv2d(input_data, filter_data, strides = [1, 1, 1, 1], padding = 'SAME')

# print y

# input_data = tf.Variable(np.random.rand(10, 9, 9, 3), dtype = np.float32)
# filter_data = tf.Variable(np.random.rand(2, 2, 3, 5), dtype = np.float32)
# y = tf.nn.depthwise_conv2d(input_data, filter_data, strides = [1, 1, 1, 1], padding = 'SAME')

# print y

# input_data = tf.Variable(np.random.rand(10, 6, 6, 3), dtype = np.float32)
# filter_data = tf.Variable(np.random.rand(2, 2, 3, 10), dtype = np.float32)
# y = tf.nn.conv2d(input_data, filter_data, strides = [1, 1, 1, 1], padding = 'SAME')
# output = tf.nn.avg_pool(value = y, ksize = [1, 2, 2, 1], strides = [1, 1, 1, 1], padding = 'SAME')
# print y

# with tf.Session() as sess:
    # sess.run(input_data)
    # sess.run(y)
