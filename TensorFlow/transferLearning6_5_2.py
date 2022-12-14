# -*- coding: utf-8 -*-

import glob
import os.path
import random
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

# the bottleneck size of inception-v3
BOTTLENECK_TENSOR_SIZE = 2048

# the tensor name of inception-v3's bottleneck
BOTTLENECK_TENSOR_NAME = 'pool_3/_reshape:0'

# input jpg data's tensor flow
JPEG_DATA_TENSOR_NAME = 'DecodeJpeg/contents:0'

# inception-v3's model file's path
MODEL_DIR = '/home/liuxun/Clobotics/Data/DPData/inception_dec_2015'

# inception-v3's model name
MODEL_FILE = 'tensorflow_inception_graph.pb'

# store the image features based on incetion-V3 model, because the image features will be used many times
CACHE_DIR = '/home/liuxun/Clobotics/Data/DPData/flower_bottleneck'

# jpeg images' path
INPUT_DATA = '/home/liuxun/Clobotics/Data/DPData/flower_photos'

# the percentage number of validation data
VALIDATION_PERCENTAGE = 10
# the percentage number of test data
TEST_PERCENTAGE = 10

# the setting of neural network
LEARNING_RATE = 0.01
STEPS = 4000
BATCH = 100

# read all images from the image's path and separate them to training data, validation data, test data
def create_image_lists(testing_percentage, validation_percentage):
    result = {}
    
    #find the all sub folder
    sub_dirs = [x[0] for x in os.walk(INPUT_DATA)]
    
    is_root_dir = True
    for sub_dir in sub_dirs:
        if is_root_dir:
            is_root_dir = False
            continue
        
        #find the all validate data in current folder
        extensions = ['jpg', 'jpeg', 'JPG', 'JPEG']
        file_list = []
        dir_name = os.path.basename(sub_dir)
        for extension in extensions:
            file_glob = os.path.join(INPUT_DATA, dir_name, '*.' + extension)
            file_list.extend(glob.glob(file_glob))
            print file_glob
        if not file_list: continue
        
        # get classify name based on folder's name
        label_name = dir_name.lower()
        print label_name
        # inital current training set, testing set and validation set
        training_images = []
        testing_images = []
        validation_images = []
        for file_name in file_list:
            base_name = os.path.basename(file_name)
            chance = np.random.randint(100)
            if chance < validation_percentage:
                validation_images.append(base_name)
            elif chance < (testing_percentage + validation_percentage):
                testing_images.append(base_name)
            else:
                training_images.append(base_name)
        
        result[label_name] = {
            'dir': dir_name,
            'training': training_images,
            'testing': testing_images,
            'validation': validation_images
        }
        
        
    return result

def get_image_path(image_lists, image_dir, label_name, index, category):
    label_lists = image_lists[label_name]
    category_list = label_lists[category]
    mod_index = index % len(category_list)
    
    base_name = category_list[mod_index]
    sub_dir = label_lists['dir']
    
    full_path = os.path.join(image_dir, sub_dir, base_name)
    return full_path

def get_bottleneck_path(image_lists, label_name, index, category):
    return get_image_path(image_lists, CACHE_DIR, label_name, index, category)+ '.txt'

def run_bottleneck_on_image(sess, image_data, image_data_tensor, bottleneck_tensor):
    # the bottleneck feature is current image's feature
    bottleneck_values = sess.run(bottleneck_tensor, {image_data_tensor: image_data})
    
    bottleneck_values = np.squeeze(bottleneck_values)
    return bottleneck_values

def get_or_create_bottleneck(sess, image_lists, label_name, index, category, jpeg_data_tensor, bottleneck_tensor):
    # get the feature path of one image
    label_lists = image_lists[label_name]
    sub_dir = label_lists['dir']
    sub_dir_path = os.path.join(CACHE_DIR, sub_dir)
    if not os.path.exists(sub_dir_path): os.makedirs(sub_dir_path)
    bottleneck_path = get_bottleneck_path(image_lists, label_name, index, category)
    
    #if image's feature file is not here, we build it following
    if not os.path.exists(bottleneck_path):
        # get the original path of image
        image_path = get_image_path(image_lists, INPUT_DATA, label_name, index, category)
        
        # get image's context
        image_data = gfile.FastGFile(image_path, 'rb').read()
        # calculate feature's vector based on inception-v3 model
        bottleneck_values = run_bottleneck_on_image(sess, image_data, jpeg_data_tensor, bottleneck_tensor)
        # store feature's vector to file 
        bottleneck_string = ','.join(str(x) for x in bottleneck_values)
        with open(bottleneck_path, 'w') as bottleneck_file:
            bottleneck_file.write(bottleneck_string)
        
    else:
        # get feature's vector through feature file 
        with open(bottleneck_path, 'r') as bottleneck_file:
            bottleneck_string = bottleneck_file.read()
        bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
        
    return bottleneck_values

# get a batch randomly for training
def get_random_cached_bottlenecks(sess, n_classes, image_lists, how_many, category, jpeg_data_tensor, bottleneck_tensor):
    bottlenecks = []
    ground_truths = []
    for _ in range(how_many):
        # add one random image's index and classify to current training data
        label_index = random.randrange(n_classes)
        label_name = list(image_lists.keys())[label_index]
        image_index = random.randrange(65536)
        bottleneck = get_or_create_bottleneck(sess, image_lists, label_name, image_index, category, jpeg_data_tensor, bottleneck_tensor)
        ground_truth = np.zeros(n_classes, dtype=np.float32)
        ground_truth[label_index] = 1.0
        bottlenecks.append(bottleneck)
        ground_truths.append(ground_truth)
    
    
    
    return bottlenecks, ground_truths

# get all testing data, we should test the accuracy on all the testing data
def get_test_bottlenecks(sess, image_lists, n_classes, jpeg_data_tensor, bottleneck_tensor):
    bottlenecks = []
    ground_truths = []
    label_name_list = list(image_lists.keys())
    
    # enum all classify data
    for label_index, label_name in enumerate(label_name_list):
        category = 'testing'
        for index, unused_base_name in enumerate(image_lists[label_name][category]):
            bottleneck = get_or_create_bottleneck(sess, image_lists, label_name, index, category, jpeg_data_tensor, bottleneck_tensor)
            ground_truth = np.zeros(n_classes, dtype=np.float32)
            ground_truth[label_index] = 1.0
            bottlenecks.append(bottleneck)
            ground_truths.append(ground_truth)
            
    return bottlenecks, ground_truths

def main(_):
    # read all pictures
    image_lists = create_image_lists(TEST_PERCENTAGE, VALIDATION_PERCENTAGE)
    n_classes = len(image_lists.keys())
    print n_classes
    
    # read inception-v3 model
    print os.path.join(MODEL_DIR,MODEL_FILE)
    with gfile.FastGFile(os.path.join(MODEL_DIR, MODEL_FILE), 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        
    # print graph_def
    # load inception_v3 model
    bottleneck_tensor, jpeg_data_tensor = tf.import_graph_def(graph_def, return_elements=[BOTTLENECK_TENSOR_NAME, JPEG_DATA_TENSOR_NAME])
    
    print bottleneck_tensor
    print jpeg_data_tensor
    
    # define new network's input, all the nodes are defined as the feature vector 
    boottleneck_input = tf.placeholder(tf.float32, [None, BOTTLENECK_TENSOR_SIZE], name='BottleneckInputPlaceHolder')
    # define the new input result data
    ground_truth_input = tf.placeholder(tf.float32, [None, n_classes], name='GroundTruthInput')
    global_step = tf.Variable(0, trainable=False)
    
    
    # define a full connection layer
    with tf.name_scope('final_training_ops'):
        weights = tf.Variable(tf.truncated_normal([BOTTLENECK_TENSOR_SIZE, n_classes], stddev=0.001))
        biases = tf.Variable(tf.zeros([n_classes]))
        logits = tf.matmul(boottleneck_input, weights) + biases
        final_tensor = tf.nn.softmax(logits)
        
    # define cross entropy
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=ground_truth_input)
    cross_entropy_mean = tf.reduce_mean(cross_entropy)
    #train_step = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cross_entropy_mean)
    train_step = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cross_entropy_mean)
    
    # calculate the accurate rate
    with tf.name_scope('evaluation'):
        correct_prediction = tf.equal(tf.argmax(final_tensor, 1), tf.argmax(ground_truth_input, 1))
        evaluation_step = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    
    with tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        
        #training
        for i in range(STEPS):
            # get 1 batch for training one time
            train_bottlenecks, train_ground_truth = get_random_cached_bottlenecks(sess, n_classes, image_lists, BATCH, 'training', jpeg_data_tensor, bottleneck_tensor)
            sess.run(train_step, feed_dict={boottleneck_input: train_bottlenecks, ground_truth_input: train_ground_truth})
            
            # test accurate rate on validation data
            if i % 100 == 0 or i+1 == STEPS:
                validation_bottlenecks, validation_ground_truth = get_random_cached_bottlenecks(sess, n_classes, image_lists, BATCH, 'validation', jpeg_data_tensor, bottleneck_tensor)
                validation_accuracy = sess.run(evaluation_step, feed_dict={boottleneck_input: validation_bottlenecks, ground_truth_input: validation_ground_truth})
                print('Step %d: Validation accuracy on random sampled %d examples = %.1f%%' % (i, BATCH, validation_accuracy*100))
                
        # test final accurate rate on testing data
        test_bottlenecks, test_ground_truth = get_test_bottlenecks(sess, image_lists, n_classes, jpeg_data_tensor, bottleneck_tensor)
        test_accuracy = sess.run(evaluation_step, feed_dict={boottleneck_input: test_bottlenecks, ground_truth_input: test_ground_truth})
    print('Final test accuracy = %1.f%%' % (test_accuracy*100))
            
            
if __name__ == '__main__':
    tf.app.run()
    