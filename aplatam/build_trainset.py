import os
import fiona
import numpy as np
import rasterio
from shapely.geometry import box, shape
from skimage import exposure
from skimage.io import imsave
import glob
import random
import shutil
import logging

_logger = logging.getLogger(__name__)

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
    test_size = float(config["test_size"])

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

    true_files = glob.glob(os.path.join(temp_dir, 'all', 't', '*.jpg'))
    false_files = glob.glob(os.path.join(temp_dir, 'all', 'f', '*.jpg'))
    split_train_test((true_files, false_files), temp_dir, test_size)


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
            window_box = box(*window_to_bounds(window, src.transform))
            # Get shapes whose bounding boxes intersect with window box
            matching_shapes = intersect_window(shapes, index, window_box)
            try:
                # create image claas
                img_class = class_imagen(matching_shapes, window_box)
                # Prepare img filename
                win_fname = image_filename(tile_fname, window)
                # Create class directory
                img_dir = create_class_dir(path, img_class)
                # Extract image from raster and preprocess
                rgb = extract_img(src, window, rescale_intensity,
                                  intensity_percentiles)
                # Save .jpg image from raster
                save_jpg(img_dir, win_fname, rgb)
            except RuntimeError:
                pass


def save_jpg(img_dir, win_fname, rgb):
    """Save .jpg image from raster"""
    img_path = os.path.join(img_dir, win_fname)
    imsave(img_path, rgb)


def image_filename(tile_fname, window):
    """Prepare img filename"""
    fname, _ = os.path.splitext(os.path.basename(tile_fname))
    win_fname = '{}__{}_{}.jpg'.format(fname, window[0][0], window[1][0])
    return win_fname


def extract_img(src, window, rescale_intensity, intensity_percentiles):
    """Extract image from raster and preprocess"""
    rgb = np.dstack([src.read(b, window=window) for b in range(1, 4)])
    if rescale_intensity:
        low, high = np.percentile(rgb, intensity_percentiles)
        rgb = exposure.rescale_intensity(rgb, in_range=(low, high))
    return rgb


def create_class_dir(path, img_class):
    """Create class directory"""
    img_dir = os.path.join(path, img_class)
    os.makedirs(img_dir, exist_ok=True)
    return img_dir


def class_imagen(matching_shapes, window_box):
    """create image claas"""
    if is_image_positive(matching_shapes, window_box):
        img_class = 't'
    else:
        img_class = 'f'
    return img_class


def is_image_positive(matching_shapes, window_box):
    """ image positive """
    return matching_shapes and any(
        s.intersection(window_box).area > 0.0 for s in matching_shapes)


def intersect_window(shapes, index, window_box):
    """Get shapes whose bounding boxes intersect with window box"""
    matching_shapes = [
        shapes[s_id] for s_id in index.intersection(window_box.bounds)
    ]
    return matching_shapes


def move_files(files, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for src in files:
        fname = os.path.basename(src)
        dst = os.path.join(dst_dir, fname)
        shutil.copyfile(src, dst)


def split_train_test(files, output_dir, validation_size):
    true_files, false_files = files
    n_test = round(len(true_files) * validation_size)

    random.shuffle(true_files)
    random.shuffle(false_files)

    Xt_test, Xt_train = true_files[:n_test], true_files[n_test:]
    Xf_test, Xf_train = false_files[:n_test], false_files[n_test:]
    _logger.info('Xt_train %d , Xt_test %d , Xf_train %d, Xf_test %d ',
                 len(Xt_train), len(Xt_test), len(Xf_train), len(Xf_test))

    move_files(Xt_train, os.path.join(output_dir, 'train', 't'))
    move_files(Xf_train, os.path.join(output_dir, 'train', 'f'))
    move_files(Xt_test, os.path.join(output_dir, 'test', 't'))
    move_files(Xf_test, os.path.join(output_dir, 'test', 'f'))
