#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train a detection model from an already prepared dataset.

"""
import argparse
import logging
import os
import random
import sys
import warnings

import rasterio

from aplatam import __version__
from aplatam.build_trainset import CnnTrainsetBuilder
from aplatam.train_classifier import train
from aplatam.util import all_raster_files

__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)

# Number of bands that all rasters must have
BAND_COUNT = 4

# Default output model filename
DEFAULT_MODEL_FILENAME = 'model.h5'


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
        description=('Prepare a dataset from a set of preprocessed rasters '
                     'and a vector file of polygons and train a detection '
                     'model.'))

    # Mandatory arguments
    parser.add_argument(
        'rasters_dir', help='directory containing raster images')
    parser.add_argument('vector', help='vector file of training polygons')
    parser.add_argument(
        'output_dir', help='directory of output training dataset')

    # Options
    parser.add_argument(
        '-o',
        '--output-model',
        default=None,
        help=('filename for output model. '
              'Default: OUTPUT_DIR/model.h5'))

    parser.add_argument(
        '--seed', type=int, help='seed number for the random number generator')
    parser.add_argument("--size", type=int, default=256, help="window size")
    parser.add_argument(
        "--step-size",
        type=int,
        default=128,
        help="step size for sliding window")
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=0,
        help=
        "if buffer_size > 0, polygons are expanded with a fixed-sized buffer")
    parser.add_argument(
        "--rasters-contour",
        help="path to rasters contour vector file (optional)")
    parser.add_argument(
        "--rescale-intensity",
        dest='rescale_intensity',
        default=True,
        action='store_true',
        help="Rescale intensity")
    parser.add_argument(
        "--no-rescale-intensity",
        dest='rescale_intensity',
        action='store_false',
        help="Do not rescale intensity")
    parser.add_argument(
        "--lower-cut",
        type=int,
        default=2,
        help=
        "Lower cut of percentiles for cumulative count in intensity rescaling")
    parser.add_argument(
        "--upper-cut",
        type=int,
        default=98,
        help=
        "upper cut of percentiles for cumulative count in intensity rescaling")
    parser.add_argument(
        "--block-size", type=int, default=1, help="block size multiplier")
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

    # Set default output model path, if not set
    if args.output_model:
        output_model = args.output_model
    else:
        output_model = os.path.join(args.output_dir, DEFAULT_MODEL_FILENAME)

    opts = dict(
        size=args.size,
        step_size=args.step_size,
        buffer_size=args.buffer_size,
        rescale_intensity=args.rescale_intensity,
        lower_cut=args.lower_cut,
        upper_cut=args.upper_cut,
        block_size=args.block_size,
        test_size=args.test_size,
        validation_size=args.validation_size,
        balancing_multiplier=args.balancing_multiplier,
        rasters_contour=args.rasters_contour)
    _logger.info('Options: %s', opts)

    # Set seed number
    if args.seed:
        _logger.info('Seed: %d', args.seed)
        random.seed(args.seed)

    _logger.info('Collect all rasters from %s', args.rasters_dir)
    rasters = all_raster_files(args.rasters_dir)

    validate_rasters_band_count(rasters)

    if not os.path.exists(args.output_dir):
        builder = CnnTrainsetBuilder(rasters, args.vector, **opts)
        builder.build(args.output_dir)

    # Train and save model
    train(
        output_model,
        args.output_dir,
        trainable_layers=args.trainable_layers,
        batch_size=args.batch_size,
        epochs=args.epochs,
        size=args.size)

    _logger.info('Done')


def validate_rasters_band_count(rasters):
    """Validate all rasters have at least 3 bands

    Returns True if they are all valid.
    Otherwise it raises a RuntimeError.

    """
    _logger.debug('Validate rasters band count')
    for raster_path in rasters:
        count = get_raster_band_count(raster_path)
        if count < 3:
            raise RuntimeError(
                'Raster {} has {} bands, but should have 3 (true color RGB)'.
                format(raster_path, count))
        if count >= 3:
            warnings.warn(
                ('Raster {} has more than 3 bands ({}). '
                 'Going to assume the first 3 bands are RGB...').format(
                     raster_path, count))
    return True


def get_raster_band_count(raster_path):
    """Return band count of +raster_path+"""
    with rasterio.open(raster_path) as dataset:
        return dataset.count


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
