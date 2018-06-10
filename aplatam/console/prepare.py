#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prepare a dataset for training a model from a set of preprocessed rasters and a
vector file of polygons.

"""
import argparse
import logging
import sys

import fiona
import rasterio
from aplatam import __version__
from aplatam.build_trainset import CnnTrainsetBuilder
from aplatam.util import all_raster_files

__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)

# Number of bands that all rasters must have
BAND_COUNT = 4


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
        description=('Prepare a dataset for training a model from a set of. '
                     'preprocessed rasters and a vector file of polygons.'))

    # Mandatory arguments
    parser.add_argument(
        'rasters_dir', help='directory containing raster images')
    parser.add_argument('vector', help='vector file of polygons')
    parser.add_argument('output_dir', help='path to output dataset directory')

    # Options
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
    logformat = "[%(asctime)s] %(levelname)s %(name)s -- %(message)s"
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

    opts = dict(
        size=args.size,
        step_size=args.step_size,
        buffer_size=args.buffer_size,
        rescale_intensity=args.rescale_intensity,
        lower_cut=args.lower_cut,
        upper_cut=args.upper_cut,
        block_size=args.block_size)
    _logger.info('Options: %s', opts)

    _logger.info('Collect all rasters from %s', args.rasters_dir)
    rasters = all_raster_files(args.rasters_dir)

    validate_rasters_band_count(rasters)

    builder = CnnTrainsetBuilder(rasters, args.vector, **opts)
    builder.build(args.output_dir)

    _logger.info('Done')


def validate_rasters_band_count(rasters):
    """
    Validates all rasters have a count of 4 bands

    Returns True if they are all valid.
    Otherwise it raises a RuntimeError.

    """
    _logger.debug('Validate rasters band count')
    for raster_path in rasters:
        count = get_raster_band_count(raster_path)
        if count != BAND_COUNT:
            raise RuntimeError(
                'Rasters must have exactly 4 bands (was {})'.format(count))
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
