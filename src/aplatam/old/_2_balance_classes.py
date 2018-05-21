#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import glob
from shutil import copyfile
import shutil

#train_dir = 'data/hires/256_256_0/all/'
aug = 2


def cnn_training_dir_structure(train_dir):
    np.random.seed(33)
    pos_files = glob.glob(os.path.join(train_dir, 't', '*.jpg'))
    neg_files = glob.glob(os.path.join(train_dir, 'f', '*.jpg'))
    training_pos_files = set(
        np.random.choice(
            pos_files, int(round(len(pos_files) * 0.75)), replace=False))
    training_neg_files = set(
        np.random.choice(
            neg_files, int(round(len(pos_files) * aug * 0.75)), replace=False))
    testing_pos_files = set(pos_files) - set(training_pos_files)
    testing_neg_files = set(
        np.random.choice(
            list(set(neg_files) - set(training_neg_files)),
            len(testing_pos_files),
            replace=False))
    #testing_pos_files = [pos_file for pos_file in pos_files if not (pos_file in training_pos_files)]
    #testing_neg_files = [neg_file for neg_file in neg_files if not (neg_file in training_neg_files)]
    print(len(training_pos_files), len(training_neg_files))
    shutil.rmtree('data_keras/train_hires_balanced/')
    shutil.rmtree('data_keras/validation_hires_balanced/')
    labels = {
        'training_pos_files': training_pos_files,
        'training_neg_files': training_neg_files,
        'testing_pos_files': testing_pos_files,
        'testing_neg_files': testing_neg_files
    }

    for label in list(labels.keys()):
        for fname in labels[label]:
            base_fname = os.path.basename(fname)
            splitted_label = label.split("_")
            if splitted_label[0] == 'training' and splitted_label[1] == 'pos':
                if not os.path.exists('data_keras/train_hires_balanced/vya/'):
                    os.makedirs('data_keras/train_hires_balanced/vya/')
                copyfile(
                    fname,
                    os.path.join(
                        'data_keras/train_hires_balanced/vya/{0}'.format(
                            base_fname)))

            if splitted_label[0] == 'training' and splitted_label[1] == 'neg':
                if not os.path.exists(
                        'data_keras/train_hires_balanced/no_vya/'):
                    os.makedirs('data_keras/train_hires_balanced/no_vya/')
                copyfile(
                    fname,
                    os.path.join(
                        'data_keras/train_hires_balanced/no_vya/{0}'.format(
                            base_fname)))

            if splitted_label[0] == 'testing' and splitted_label[1] == 'pos':
                if not os.path.exists(
                        'data_keras/validation_hires_balanced/vya/'):
                    os.makedirs('data_keras/validation_hires_balanced/vya/')
                copyfile(
                    fname,
                    os.path.join(
                        'data_keras/validation_hires_balanced/vya/{0}'.format(
                            base_fname)))

            if splitted_label[0] == 'testing' and splitted_label[1] == 'neg':
                if not os.path.exists(
                        'data_keras/validation_hires_balanced/no_vya/'):
                    os.makedirs('data_keras/validation_hires_balanced/no_vya/')
                copyfile(
                    fname,
                    os.path.join(
                        'data_keras/validation_hires_balanced/no_vya/{0}'.
                        format(base_fname)))

    print('Done')


def main(args):
    cnn_training_dir_structure(args.input_dir)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Creates directory structure for cnn training',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', help='Path where jpg tiles are stored')

    args = parser.parse_args()

    main(args)
