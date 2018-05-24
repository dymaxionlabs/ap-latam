import glob
import logging
import os
import random
import shutil

import fiona
import numpy as np
import rasterio
from shapely.geometry import box, shape
from skimage import exposure
from skimage.io import imsave

from aplatam.util import (create_index, get_raster_crs, reproject_shape,
                          sliding_windows, window_to_bounds)

_logger = logging.getLogger(__name__)


def build_trainset(rasters, vector, config, *, output_dir):
    """
    Build a training set of image tiles from a collection of +rasters+
    for a binary classifier.

    If a tile intersects with a polygon shape from a feature in +vector+, it
    is stored in the directory for "true" samples. Otherwise, it is stored in
    the directory corresponding to "false" samples.
    Both directories are stored in +output_dir+.

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
    validation_size = float(config["validation_size"])

    for raster in rasters:
        shapes, vector_crs = read_shapes(vector)
        raster_crs = get_raster_crs(raster)
        shapes = reproject_shapes(shapes, vector_crs, raster_crs)

        if buffer_size != 0:
            apply_buffer(buffer_size, shapes)

        write_window_tiles(
            shapes,
            output_dir,
            raster,
            size=size,
            step_size=step_size,
            intensity_percentiles=intensity_percentiles)

    true_files = glob.glob(os.path.join(output_dir, 'all', 't', '*.jpg'))
    false_files = glob.glob(os.path.join(output_dir, 'all', 'f', '*.jpg'))

    split_train_test((true_files, false_files), output_dir, test_size,
                     validation_size)


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

    with rasterio.open(tile_fname) as src:
        for window in sliding_windows(size, step_size, src.shape):
            window_box = box(*window_to_bounds(window, src.transform))
            matching_shapes = intersect_window(shapes, index, window_box)
            try:
                img_class = image_class_string(matching_shapes, window_box)
                win_fname = prepare_img_filename(tile_fname, window)
                img_dir = create_class_dir(path, img_class)
                rgb = extract_img(src, window, rescale_intensity,
                                  intensity_percentiles)
                save_jpg(img_dir, win_fname, rgb)
            except RuntimeError:
                pass


def save_jpg(img_dir, win_fname, rgb):
    """Save .jpg image from raster"""
    img_path = os.path.join(img_dir, win_fname)
    imsave(img_path, rgb)


def prepare_img_filename(tile_fname, window):
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


def image_class_string(matching_shapes, window_box):
    """
    Return image class string

    Arguments:
        matching_shapes {list(shape)} -- list of matching shapes
        window_box {shape} -- window box

    Returns:
        string -- image class string

    """
    if is_image_positive(matching_shapes, window_box):
        img_class = 't'
    else:
        img_class = 'f'
    return img_class


def is_image_positive(matching_shapes, window_box):
    """
    Decide whether image is a true sample

    Arguments:
        matching_shapes {list(shape)} -- list of matching shapes
        window_box {shape} -- window box

    Returns:
        bool -- True if image is a true sample or not

    """
    return matching_shapes and any(
        s.intersection(window_box).area > 0.0 for s in matching_shapes)


def intersect_window(shapes, index, window_box):
    """
    Get shapes whose bounding boxes intersect with window box

    Arguments:
        shapes {list(shapely.Shape)} -- list of shapes
        index {Index} -- R-Tree index object
        window_box {shape} -- window box shape

    Returns:
        list(shape) -- list of shapes that intersect with window

    """
    matching_shapes = [
        shapes[s_id] for s_id in index.intersection(window_box.bounds)
    ]
    return matching_shapes


def move_files(files, dst_dir):
    """
    Move all files to a destination directory, creating them if needed

    Arguments:
        files {iterable} -- iterable of file paths
        dst_dir {string} -- destination directory name

    """
    os.makedirs(dst_dir, exist_ok=True)
    for src in files:
        fname = os.path.basename(src)
        dst = os.path.join(dst_dir, fname)
        shutil.copyfile(src, dst)


def split_train_test(files, output_dir, test_size, _validation_size):
    """
    Split a list of files into training, validation and test datasets

    Arguments:
        files {iterable} -- iterable of file paths
        output_dir {string} -- output directory name
        test_size {float} -- proportion of test set from total of true samples
        validation_size {float} -- proportion of validation set from total of
            true samples.

    """
    true_files, false_files = files
    n_total = len(true_files)
    n_test = round(n_total * test_size)
    #n_validation = round(n_total * validation_size)

    random.shuffle(true_files)
    random.shuffle(false_files)

    t_test, t_train = true_files[:n_test], true_files[n_test:]
    f_test, f_train = false_files[:n_test], false_files[n_test:]
    _logger.info('t_train=%d, t_test=%d, f_train=%d, f_test=%d', len(t_train),
                 len(t_test), len(f_train), len(f_test))

    move_files(t_train, os.path.join(output_dir, 'train', 't'))
    move_files(f_train, os.path.join(output_dir, 'train', 'f'))
    move_files(t_test, os.path.join(output_dir, 'test', 't'))
    move_files(f_test, os.path.join(output_dir, 'test', 'f'))
