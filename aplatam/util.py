# -*- coding: utf-8 -*-
import json
import logging
import os
from collections import namedtuple
from functools import partial
from glob import glob

import pyproj
import rasterio
import rtree
from rasterio.windows import Window
from shapely.geometry import mapping
from shapely.ops import transform

_logger = logging.getLogger(__name__)

METADATA_FILENAME = 'metadata.json'


ShapeWithProps = namedtuple('ShapeWithProps', ['shape', 'props'])


def all_raster_files(dirname, ext='.tif'):
    """Generate any raster files inside +dirname+, recursively"""
    pattern = '**/*{ext}'.format(ext=ext)
    return glob(os.path.join(dirname, pattern), recursive=True)


def create_index(shapes):
    """Create an R-Tree index from a set of shapes"""
    index = rtree.index.Index()
    for shape_id, shape in enumerate(shapes):
        index.insert(shape_id, shape.bounds)
    return index


def sliding_windows(size, step_size, width, height):
    """Slide a window of +size+ by moving it +step_size+ pixels"""
    for i in range(0, height - size + 1, step_size):
        for j in range(0, width - size + 1, step_size):
            yield Window(j, i, size, size)


def reproject_shape(shape, src_crs, dst_crs):
    """Reprojects a shape from some projection to another"""
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=src_crs['init']),
        pyproj.Proj(init=dst_crs['init']))
    return transform(project, shape)


def get_raster_crs(raster_path):
    """Return CRS of +raster_path+"""
    with rasterio.open(raster_path) as dataset:
        return dataset.crs


def read_metadata(input_dir):
    """Read metadata JSON file in +input_dir+ into a dictionary"""
    metadata_path = os.path.join(input_dir, METADATA_FILENAME)
    with open(metadata_path) as src:
        return json.load(src)


def write_metadata(output_dir, **kwargs):
    """Write a dictionary as JSON to a file"""
    os.makedirs(output_dir, exist_ok=True)
    metadata_path = os.path.join(output_dir, METADATA_FILENAME)
    with open(metadata_path, 'w') as dst:
        json.dump(kwargs, dst)


def write_geojson(shapes, output_path):
    """
    Write a GeoJSON to +output_path+ with each shape in +shapes+ as a feature

    Shapes must be in WGS84 projection

    """
    dicc = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes:
        feat = {'type': 'Feature',
                'geometry': mapping(shape.shape),
                'properties': shape.props}
        dicc['features'].append(feat)
    with open(output_path, 'w') as dst:
        dst.write(json.dumps(dicc))
    _logger.info('%s written', output_path)
