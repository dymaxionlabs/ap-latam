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
from shapely.geometry import shape, box, mapping
import numpy as np
from skimage import exposure
from keras.preprocessing.image import ImageDataGenerator
from aplatam.old.util import window_to_bounds, sliding_windows
from aplatam import __version__
import json
from shapely.geometry import shape, mapping

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


def predict_image(fname, model, size, step_size=None, rescale_intensity=False):
    if not step_size:
        step_size = size

    with rio.open(fname) as src:
        #imgs = []
        windows = []
        for window in sliding_windows(size, step_size, src.shape):
            window_box = box(*window_to_bounds(window, src.transform))

            img = np.dstack([src.read(b, window=window) for b in range(1, 4)])

            if rescale_intensity:
                low, high = np.percentile(img, (2, 98))
                img = exposure.rescale_intensity(img, in_range=(low, high))

            img = img / 255.
            preds = model.predict(np.array([img]))
            preds_b = preds[:, 0]
            for i in np.nonzero(preds_b > 0.3)[0]:
                _logger.info((window, float(preds_b[i])))
                windows.append((window_box, float(preds_b[i])))
        #if cur_windows:
        #    name, _ = os.path.splitext(os.path.basename(fname))
        #    output = '/tmp/{}_windows.geojson'.format(name)
        #    write_geojson(cur_windows, output)

        return windows


def predict_images(input_dir, model, size, **kwargs):
    all_windows = []
    files = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    _logger.info(files)
    for fname in tqdm.tqdm(files):
        all_windows.extend(predict_image(fname, model, size, **kwargs))
    _logger.info("Done! Found %d matching windows  on all files ",
                 (len(all_windows)))
    return all_windows
    #print('{} written'.format(output))


def main(args):
    """
    Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    #_logger.debug("Starting script...")
    # ...
    _logger.warn("Not done yet")
    #_logger.info("Done")

    datagen = ImageDataGenerator(rescale=1. / 255)
    model = keras.models.load_model(args.model_file)
    img_size = model.input_shape[1]

    predict_images(
        args.input_dir,
        model,
        img_size,
        step_size=args.step_size,
        rescale_intensity=args.rescale_intensity)


def write_geojson(shapes, output_path):
    d = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes:
        feat = {'type': 'Feature', 'geometry': mapping(shape)}
        d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
