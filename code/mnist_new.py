#
# project: project 2
# file: mnist_new.py
# author: MING Yao
#

import tensorflow as tf
import numpy as np
from convnet import *
import gzip
import os
import sys
from six.moves import urllib

SOURCE_URL = 'http://yann.lecun.com/exdb/mnist/'
WORK_DIRECTORY = 'data'
IMAGE_SIZE = 28
NUM_CHANNELS = 1
PIXEL_DEPTH = 255
NUM_LABELS = 10
# VALIDATION_SIZE = 5000  # Size of the validation set.
SEED = 66478  # Set to None for random seed.
BATCH_SIZE = 100
NUM_EPOCHS = 20
EVAL_BATCH_SIZE = 100
EVAL_FREQUENCY = 600  # Number of steps between evaluations.

def maybe_download(filename):
    """Download the data from Yann's website, unless it's already here."""
    if not tf.gfile.Exists(WORK_DIRECTORY):
        tf.gfile.MakeDirs(WORK_DIRECTORY)
    filepath = os.path.join(WORK_DIRECTORY, filename)
    if not tf.gfile.Exists(filepath):
        filepath, _ = urllib.request.urlretrieve(SOURCE_URL + filename, filepath)
        with tf.gfile.GFile(filepath) as f:
            size = f.size()
        print('Successfully downloaded', filename, size, 'bytes.')
    return filepath


def extract_data(filename, num_images):
    """Extract the images into a 4D tensor [image index, y, x, channels].

     Values are rescaled from [0, 255] down to [-0.5, 0.5].
     """
    print('Extracting', filename)
    with gzip.open(filename) as bytestream:
        bytestream.read(16)
        buf = bytestream.read(IMAGE_SIZE * IMAGE_SIZE * num_images * NUM_CHANNELS)
        data = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
        data = (data - (PIXEL_DEPTH / 2.0)) / PIXEL_DEPTH
        data = data.reshape(num_images, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS)
        return data


def extract_labels(filename, num_images):
    """Extract the labels into a vector of int64 label IDs."""
    print('Extracting', filename)
    with gzip.open(filename) as bytestream:
        bytestream.read(8)
        buf = bytestream.read(1 * num_images)
        labels = np.frombuffer(buf, dtype=np.uint8).astype(np.int64)
    return labels


def main(argv=None):  # pylint: disable=unused-argument

    # Get the data.
    train_data_filename = maybe_download('train-images-idx3-ubyte.gz')
    train_labels_filename = maybe_download('train-labels-idx1-ubyte.gz')
    test_data_filename = maybe_download('t10k-images-idx3-ubyte.gz')
    test_labels_filename = maybe_download('t10k-labels-idx1-ubyte.gz')

    # Extract it into numpy arrays.
    train_data = extract_data(train_data_filename, 60000)
    train_labels = extract_labels(train_labels_filename, 60000)
    test_data = extract_data(test_data_filename, 10000)
    test_labels = extract_labels(test_labels_filename, 10000)

    num_epochs = NUM_EPOCHS

    # LeNet-5 like Model
    model = ConvNet()
    model.input_data((BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, NUM_CHANNELS), num_label=NUM_LABELS, eval_batch=EVAL_BATCH_SIZE)
    model.add_conv_layer([5,5],32,[1,1,1,1],activation='relu')
    model.add_pool('max', [1,2,2,1], [1,2,2,1])
    model.add_conv_layer([5,5],64,[1,1,1,1],activation='relu')
    model.add_pool('max', [1,2,2,1], [1,2,2,1])
    model.add_fully_connected(512,'relu')
    model.add_dropout(0.5)
    model.add_fully_connected(NUM_LABELS,'relu')
    model.set_loss(tf.nn.sparse_softmax_cross_entropy_with_logits, reg=5e-4)
    model.set_optimizer('Adam')
    model.init()
    model.train_with_eval(train_data,train_labels,test_data,test_labels,num_epochs,EVAL_FREQUENCY)


if __name__ == '__main__':
    tf.app.run()
