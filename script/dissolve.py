#!/usr/bin/env python3
"""
Dissolve overlapping tile polygons

"""
from tqdm import tqdm
from shapely.geometry import shape
import fiona
import logging
import os

from aplatam.util import ShapeWithProps, write_geojson
from aplatam.post_process import dissolve_overlapping_shapes

logger = logging.getLogger(__name__)


def dissolve(in_path, out_path, buffer_size=None):
    with fiona.open(in_path) as src:
        shapes = [ShapeWithProps(shape(f['geometry']), props=f['properties']) for f in src]
    shapes = dissolve_overlapping_shapes(shapes, buffer_size=None)
    write_geojson(shapes, out_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='Dissolve overlapping tile polygons',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'input_vector',
        help='input vector file')
    parser.add_argument(
        'output_vector',
        help='output vector file')

    parser.add_argument(
        "--buffer-size",
        type=int,
        help="expand polygons with a fixed-sized buffer")

    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    dissolve(args.input_vector, args.output_vector, buffer_size=args.buffer_size)
