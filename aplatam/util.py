# -*- coding: utf-8 -*-
import os
from functools import partial
from glob import glob

import pyproj
import rasterio
import rtree
from shapely.ops import transform


def all_raster_files(dirname, ext='.tif'):
    """Generate any raster files inside +dirname+, recursively"""
    pattern = '**/*{ext}'.format(ext=ext)
    return glob(os.path.join(dirname, pattern), recursive=True)


def create_index(shapes):
    """Create an R-Tree index from a set of shapes"""
    index = rtree.index.Index()
    for obj_id, shape in enumerate(shapes):
        index.insert(obj_id, shape.bounds)
    return index


def sliding_windows(size, step_size, raster_size):
    "Slide a window of +size+ by moving it +step_size+ pixels"
    h, w = raster_size
    for i in range(0, h, step_size):
        for j in range(0, w, step_size):
            diff_i = (i + size - h) if i + size > h else 0
            diff_j = (j + size - w) if j + size > w else 0
            yield (i - diff_i, i + size - diff_i), (j - diff_j,
                                                    j + size - diff_j)


def window_to_bounds(window, affine):
    """Convert pixels to coordinates in a window"""
    minx = ((window[1][0], window[1][1]) * affine)[0]
    maxx = ((window[1][1], window[0][0]) * affine)[0]
    miny = ((window[1][1], window[0][1]) * affine)[1]
    maxy = ((window[1][1], window[0][0]) * affine)[1]
    return minx, miny, maxx, maxy


def reproject_shape(shape, src_epsg, dst_epsg):
    """Reprojects a shape from some projection to another"""
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=src_epsg),
        pyproj.Proj(init=dst_epsg))
    return transform(project, shape)


def get_raster_crs(raster_path):
    """Return CRS of +raster_path+"""
    with rasterio.open(raster_path) as dataset:
        return dataset.crs
