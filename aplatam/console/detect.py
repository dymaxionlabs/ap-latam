#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train a detection model from a set of preprocessed rasters and a vector file of
polygons.

"""
import argparse
import logging
import sys
import rasterio as rio
import glob
import os
import tqdm
import numpy as np
from skimage import exposure
from keras.preprocessing.image import ImageDataGenerator
from aplatam.old.util import window_to_bounds, sliding_windows

from aplatam.detect import detect
from aplatam import __version__
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
        description="...")
    # Mandatory arguments

    parser.add_argument('model_file', help='HDF5 Keras model file path')
    parser.add_argument(
        'input_dir', help='Path where test hi-res images are stored')
    parser.add_argument('output', help='GeoJSON output file')

    # Options

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
        '--step-size',
        default=None,
        help='Step size of sliding windows (if none, same as size)')

    parser.add_argument("--threshold", type=float, default=0.3)

    parser.add_argument("--neighbours", type=int, default=3)

    parser.add_argument("--mean-threshold", type=float, default=0.3)

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

    detect(
        model_file=args.model_file,
        input_dir=args.input_dir,
        step_size=args.step_size,
        rescale_intensity=args.rescale_intensity,
        neighbours=args.neighbours,
        threshold=args.threshold,
        output=args.output,
        mean_threshold=args.mean_threshold)


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
