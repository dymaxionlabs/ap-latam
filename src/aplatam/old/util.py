# -*- coding: utf-8 -*-
from contextlib import contextmanager
from functools import partial
from shapely.geometry import box
from shapely.ops import transform
import glob
import os
import pyproj
import rasterio as rio
import subprocess
import tempfile
import rtree


def all_scene_dirs(input_dir, patterns=('*.tif', '*.jp2')):
    for root, _, files in os.walk(input_dir):
        if files:
            if any(glob.glob(os.path.join(root, p)) for p in patterns):
                yield root


@contextmanager
def open_sentinel2_bands(scene_path, band_ids):
    """
    Open all Sentinel-2 band images with rasterio based on +band_ids+

    Check first if there is a GeoTIFF file and open it.  If not, convert
    JPG2000 files to GeoTIFF. This allows Rasterio to read/write with windows.

    """

    def band_file(scene_path, band, ext):
        pattern = os.path.join(scene_path, '*_B{}.{}'.format(b, ext))
        files = glob.glob(pattern)
        return files[0] if files else None

    fname, _ = os.path.splitext(scene_path)
    prefix = '{}_'.format(os.path.basename(fname))

    with tempfile.TemporaryDirectory(prefix=prefix) as tmpdirname:
        fs = []

        for b in band_ids:
            tif_file = band_file(scene_path, b, 'tif')
            if not tif_file:
                jp2_file = band_file(scene_path, b, 'jp2')
                fname, _ = os.path.splitext(os.path.basename(jp2_file))
                tif_file = os.path.join(tmpdirname, '{}.tif'.format(fname))

                # Run gdal_translate to convert JPG2000 to GeoTIFF
                cmd = 'gdal_translate -q -of GTiff "{src}" "{dst}"'.format(
                    src=jp2_file, dst=tif_file)
                print('Converting {} to GeoTIFF...'.format(jp2_file))
                subprocess.run(cmd, shell=True)
                print('{} written'.format(tif_file))

            # Open tiff file
            f = rio.open(tif_file)
            fs.append(f)

        yield fs

        for f in fs:
            f.close()


@contextmanager
def open_sentinel2_band(scene_path, band_id):
    """Open one Sentinel-2 band image with rasterio"""
    with open_sentinel2_bands(scene_path, [band_id]) as bands:
        yield bands[0]


def window_to_bounds(window, affine):
    """Convert pixels to coordinates in a window"""
    minx = ((window[1][0], window[1][1]) * affine)[0]
    maxx = ((window[1][1], window[0][0]) * affine)[0]
    miny = ((window[1][1], window[0][1]) * affine)[1]
    maxy = ((window[1][1], window[0][0]) * affine)[1]
    return minx, miny, maxx, maxy


def windows(size, raster):
    """Generate windows of +size+ for a specific raster band"""
    w, h = raster.shape
    win_w, win_h = size
    for i in range(0, w, win_w):
        for j in range(0, h, win_h):
            window = (i, i + win_h), (j, j + win_w)
            yield box(*window_to_bounds(window, raster.transform)), (i, j)


@contextmanager
def reproject_vector_layer(path, t_srs):
    """Reproject a vector layer using ogr2ogr"""
    fname, _ = os.path.splitext(path)
    prefix = '{}_'.format(os.path.basename(fname))

    with tempfile.TemporaryDirectory(prefix=prefix) as tmpdirname:
        cmd = 'ogr2ogr -t_srs "{t_srs}" "{dst}" "{src}"'.format(
            t_srs=t_srs, src=path, dst=tmpdirname)
        subprocess.run(cmd, shell=True)
        pattern = os.path.join(tmpdirname, '*.shp')
        files = glob.glob(pattern)
        yield files[0]


def reproject_shape(shape, src_epsg, dst_epsg):
    """Reprojects a shape from some projection to another"""
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=src_epsg),
        pyproj.Proj(init=dst_epsg))
    return transform(project, shape)


def create_index(shapes):
    """Create an R-Tree index from a set of shapes"""
    index = rtree.index.Index()
    for id, shape in enumerate(shapes):
        index.insert(id, shape.bounds)
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
