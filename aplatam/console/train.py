#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train a detection model from an already prepared dataset.

"""
import argparse
import glob
import logging
import os
import random
import sys
import tempfile

from aplatam import __version__
from aplatam.class_balancing import split_dataset
import json

__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """
    Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace

    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Train a detection model from an already prepared dataset')

    # Mandatory arguments
    parser.add_argument(
        'dataset_dir', help='directory containing the prepared dataset')

    # Options
    parser.add_argument(
        '-o',
        '--output-model',
        default='model.h5',
        help='filename for output model')
    parser.add_argument('--temp-dir', help='path to temporary directory')
    parser.add_argument(
        '--seed', type=int, help='seed number for the random number generator')
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help=("The proportion of the dataset to include in the test split. "
              "Float number between 0.0 and 1.0"))
    parser.add_argument(
        "--validation-size",
        type=float,
        default=0.25,
        help=(
            "The proportion of the dataset to include in the validation split. "
            "Float number between 0.0 and 1.0"))
    parser.add_argument(
        "--balancing-multiplier",
        type=float,
        default=1.0,
        help=
        "proportion of false samples w.r.t true samples (e.g. 1.0 = 50%% true, 50%% false)"
    )
    parser.add_argument(
        "--trainable-layers",
        type=int,
        default=5,
        help="number of upper layers of ResNet-50 to retrain")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size")
    parser.add_argument(
        "--epochs", type=int, default=20, help="number of epochs to run")

    parser.add_argument(
        '--version',
        action='version',
        version='aplatam {ver}'.format(ver=__version__))
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)

    return parser.parse_args(args)


def read_metadata(dataset_dir):
    metadata_path = os.path.join(dataset_dir, "metadata.json")
    with open(metadata_path) as f:
        return json.load(f)


def setup_logging(loglevel):
    """
    Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages

    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """
    Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    dataset_opts = read_metadata(args.dataset_dir)

    # Set seed number
    if args.seed:
        _logger.info('Seed: %d', args.seed)
        random.seed(args.seed)

    # Gather all files in dataset
    true_files = glob.glob(os.path.join(args.dataset_dir, 't', '*.jpg'))
    false_files = glob.glob(os.path.join(args.dataset_dir, 'f', '*.jpg'))

    # Create temporary directory, if not supplied as argument
    if args.temp_dir:
        tempdir = args.temp_dir
    else:
        tempdir = tempfile.mkdtemp(prefix=__name__)
        _logger.info('temporary directory %s created', tempdir)

    # Split dataset into train, validation and test sets
    split_dataset(
        (true_files, false_files),
        tempdir,
        test_size=args.test_size,
        validation_size=args.validation_size,
        balancing_multiplier=args.balancing_multiplier)

    _logger.info('Done')


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
