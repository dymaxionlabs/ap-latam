import os

import fiona
import numpy as np
import rasterio
from shapely.geometry import box, shape
from skimage import exposure
from skimage.io import imsave

from aplatam.util import (create_index, get_raster_crs, reproject_shape,
                          sliding_windows, window_to_bounds)


def build_trainset(rasters, vector, config, *, temp_dir):
    """
    Build a training set of image tiles from a collection of +rasters+
    for a binary classifier.

    If a tile intersects with a polygon shape from a feature in +vector+, it
    is stored in the directory for "true" samples. Otherwise, it is stored in
    the directory corresponding to "false" samples.
    Both directories are stored in +temp_dir+.

    +config+ is a configuration dictionary with several options:

    * lower_cut, upper_cut: Lower/upper cut of percentiles for intensity
      rescaling.
    * buffer_size: Size of buffer (in rasters projection distance unit)
    * size: Window size (in pixels)
    * step_size: Sliding window size (in pixels)

    """
    intensity_percentiles = int(config['lower_cut']), int(config['upper_cut'])
    buffer_size = int(config['buffer_size'])
    size, step_size = int(config['size']), int(config['step_size'])

    for raster in rasters:
        shapes, vector_crs = read_shapes(vector)
        raster_crs = get_raster_crs(raster)
        shapes = reproject_shapes(shapes, vector_crs, raster_crs)

        if buffer_size != 0:
            apply_buffer(buffer_size, shapes)

        write_window_tiles(
            shapes,
            temp_dir,
            raster,
            size=size,
            step_size=step_size,
            intensity_percentiles=intensity_percentiles)


def read_shapes(vector):
    """Read features from a vector file and return their geometry shapes"""
    with fiona.open(vector) as data:
        return [(shape(feat['geometry'])) for feat in data], data.crs


def reproject_shapes(shapes, src_crs, dst_crs):
    """Reproject shapes from CRS +src_crs+ to +dst_crs+"""
    return [reproject_shape(s, src_crs, dst_crs) for s in shapes]


def apply_buffer(shapes, buffer_size):
    """Apply a fixed-sized buffer to all shapes"""
    return [s.buffer(buffer_size) for s in shapes]


def write_window_tiles(shapes,
                       output_dir,
                       tile_fname,
                       size=64,
                       step_size=16,
                       rescale_intensity=True,
                       intensity_percentiles=(2, 98)):
    "Extract windows of +size+ by sliding it +step_size+ on a raster, and write files"

    # Create R-Tree index with shapes to speed up intersection operation
    index = create_index(shapes)

    path = os.path.join(output_dir, 'all')
    #temp_windows = []
    with rasterio.open(tile_fname) as src:
        for window in sliding_windows(size, step_size, src.shape):
            # Build shape from window bounds
            #bounds = rio.transform.xy(src.transform, window[0], window[1], offset='ul')
            #window_box = box(bounds[0][0], bounds[1][0], bounds[0][1], bounds[1][1])
            window_box = box(*window_to_bounds(window, src.transform))

            # Get shapes whose bounding boxes intersect with window box
            matching_shapes = [
                shapes[s_id] for s_id in index.intersection(window_box.bounds)
            ]
            try:
                if matching_shapes and any(
                        s.intersection(window_box).area > 0.0
                        for s in matching_shapes):
                    img_class = 't'
                #temp_windows.append(window_box)
                else:
                    img_class = 'f'

                # Prepare img filename
                fname, _ = os.path.splitext(os.path.basename(tile_fname))
                win_fname = '{}__{}_{}.jpg'.format(fname, window[0][0],
                                                   window[1][0])

                # Create class directory
                img_dir = os.path.join(path, img_class)
                os.makedirs(img_dir, exist_ok=True)

                # Extract image from raster and preprocess
                rgb = np.dstack(
                    [src.read(b, window=window) for b in range(1, 4)])

                if rescale_intensity:
                    low, high = np.percentile(rgb, intensity_percentiles)
                    rgb = exposure.rescale_intensity(rgb, in_range=(low, high))

                # Save .jpg image from raster
                img_path = os.path.join(img_dir, win_fname)
                imsave(img_path, rgb)
            except RuntimeError:
                pass
