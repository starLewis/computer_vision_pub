# coding: utf-8
#!/etc/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os.path
import sys
import time

import tensorflow as tf

from tensorflow.examples.tutorials.mnist import mnist

# Basic model parameters as external flags
FLAGS = None

# Constants used for dealing with the files, matches convert_to_records
TRAIN_FILE = 'train.tfrecords'
VALIDATION_FILE = 'validation.tfrecords'

def decode(serialized_example):
    """Parses an image and label from the given 'serialized_example'"""
    features = tf.parse_single_example(
        serialized_example,
        # Defaults are not specified since both keys are required.
        features = {
            'image_raw': tf.FixedLenFeature([], tf.string),
            'label': tf.FixedLenFeature([], tf.int64),
        }
    )

    image = tf.decode_raw(features['image_raw'], tf.uint8)
    image.set_shape((mnist.IMAGE_PIXELS))

    # Convert label from a scalar uint8 tensor to an int32 scalar.
    label = tf.cast(features['label'], tf.int32)

    return image, label

def augment(image, label):
    """Placeholder for data augmentation."""
    return image, label

def normalize(image, label):
    """Convert 'image' from [0, 255] -> [-0.5, 0.5] floats."""
    image = tf.cast(image, tf.float32) * (1.0 / 255) -0.5
    return image, label

def inputs(train, batch_size, num_epochs):
    """Reads input data num_epochs times"""
    
    if not num_epochs:
        num_epochs = None
    filename = os.path.join(FLAGS.train_dir, TRAIN_FILE if train else VALIDATION_FILE)

    with tf.name_scope('input'):
        dataset = tf.data.TFRecordDataset(filename)

        dataset = dataset.map(decode)
        dataset = dataset.map(augment)
        dataset = dataset.map(normalize)

        dataset = dataset.shuffle(1000 + 3 * batch_size)
        dataset = dataset.repeat(num_epochs)
        dataset = dataset.batch(batch_size)

        iterator = tf.compat.v1.data.make_one_shot_iterator(dataset)

    return iterator.get_next()

def run_training():
    """Train MNIST for a number of steps."""

    # tell tensorflow that the model will be input into the default Graph.
    with tf.Graph().as_default():
        # Input images and labels.
        image_batch, label_batch = inputs(train = True, batch_size = FLAGS.batch_size, num_epochs = FLAGS.num_epochs)

        # Build a Graph that computes predictions from the inference model.
        logits = mnist.inference(image_batch, FLAGS.hidden1, FLAGS.hidden2)

        # Add to the Graph the loss calculation
        loss = mnist.loss(logits, label_batch)

        # Add to the Graph operations that train the model.
        train_op = mnist.training(loss, FLAGS.learning_rate)

        # The op for initializing the variables
        init_op = tf.group(tf.global_variables_initializer(), tf.local_variable_initializer())

        # Create a session for running operations in the Graph
        with tf.Session() as sess:
            sess.run(init_op)

            try:
                step = 0
                while True:
                    start_time = time.time()

                    _, loss_value = sess.run([train_op, loss])
                    duration = time.time() - start_time

                    # print an overview fairly often.
                    if step % 100 == 0:
                        print('Step %d: loss = %.2f (%.3f sec)'%(step, loss_value, duration))
                    step += 1
            except tf.errors.OutOfRangeError:
                print('Done training for %d epochs, %d steps.'%(FLAGS.num_epochs, step))

def main():
    run_training()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--learning_rate',
        type = float,
        default = 0.01,
        help = 'Initial learning rate.'
    )
    parser.add_argument(
        '--num_epochs',
        type = int,
        default = 2,
        help = 'Number of epochs to run trainer.'
    )
    parser.add_argument(
        '--hidden1',
        type = int,
        default = 128,
        help = 'Number of units in hidden layer 1.'
    )
    parser.add_argument(
        '--hidden2',
        type = int,
        default = 32,
        help = 'Number of units in hidden layer 2.'
    )
    parser.add_argument('--batch_size', type = int, default = 100, help = 'Batch size.')
    parser.add_argument(
        '--train_dir',
        type = str,
        default = 'temp/data',
        help = 'Directory with the training data.'
    )
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main = main, argv=[sys.argv[0]] + unparsed)
    
    