#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post process results

* Filter small and isolated polygons (some kind of median filter)
* Dissolve overlapping polygons
* Build raster from probability map
* Use OSM data to clip with buildings

"""
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import fiona
import glob
import json
import numpy as np
import os
import rasterio
import sys
import tqdm


def dissolve_overlapping_shapes(shapes):
    res = []
    while shapes:
        s = shapes.pop()
        while True:
            ss = [x for x in shapes if x != s and s.intersection(x).area > 0]
            if not ss:
                break
            s = unary_union([s] + ss)
            shapes = [x for x in shapes if x not in ss]
        res.append(s)
    return res


def write_geojson(shapes, output_path):
    d = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes:
        feat = {'type': 'Feature',
                'geometry': mapping(shape)}
        d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))


def main(args):
    with fiona.open(args.input_file) as src:
        shapes = [shape(feature['geometry']) for feature in src]

    new_shapes = dissolve_overlapping_shapes(shapes)
    write_geojson(new_shapes, args.output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description='Post process results from classification',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input_file',
            help='Results vector file')
    parser.add_argument('output_file',
            help='Post processed results vector file')

    args = parser.parse_args()

    main(args)