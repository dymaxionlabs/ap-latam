"""This module contains classes for building trainsets"""
import logging
import os

import fiona
import numpy as np
import rasterio
from shapely.geometry import box, shape
from skimage import exposure
from skimage.io import imsave

from aplatam.util import (create_index, get_raster_crs, reproject_shape,
                          sliding_windows, window_to_bounds, write_metadata)

_logger = logging.getLogger(__name__)


class CnnTrainsetBuilder:
    """Trainset builder for a CNN-based model

    This class allows the user to build a training set of image tiles from a
    collection of +rasters+ for a binary classifier.

    If a tile intersects with a polygon shape from a feature in +vector+,
    it is stored in the directory for "true" samples. Otherwise, it is
    stored in the directory corresponding to "false" samples.

    Both directories are stored in the output directory.

    Arguments:
        rasters {iterable} -- list of paths to rasters
        vector {string} -- path to vector file of shapes
        size {int} -- size in pixels of sliding window
        step_size {int} -- how many pixels to slide window
        version {string} -- version number

    Keyword Arguments:
        buffer_size {float} -- size of buffer (default: {0})
        rescale_intensity {bool} -- whether to rescale images intensity (default: {True})
        lower_cut {float} -- lower cut of intensity rescale (default: {2})
        upper_cut {float} -- upper cut of intensity rescale (default: {2})

    """

    def __init__(self,
                 rasters,
                 vector,
                 buffer_size=0,
                 rescale_intensity=True,
                 lower_cut=2,
                 upper_cut=2,
                 *,
                 size,
                 step_size,
                 version):
        self.rasters = rasters
        self.vector = vector
        self.size = size
        self.step_size = step_size
        self.version = version
        self.buffer_size = buffer_size
        self.rescale_intensity = rescale_intensity
        self.lower_cut = lower_cut
        self.upper_cut = upper_cut

    def build(self, output_dir):
        """Build a trainset and store it on output_dir

        Arguments:
            output_dir {string} -- output directory path
        """

        for raster in self.rasters:
            shapes, vector_crs = self._read_shapes()
            raster_crs = get_raster_crs(raster)
            shapes = self._reproject_shapes(shapes, vector_crs, raster_crs)
            shapes = self._apply_buffer(shapes)
            self._write_window_tiles(shapes, output_dir, raster)
        self._write_metadata(output_dir)

    def _read_shapes(self):
        """Read features from the vector file and return their geometry shapes"""
        with fiona.open(self.vector) as data:
            return [(shape(feat['geometry'])) for feat in data], data.crs

    def _reproject_shapes(self, shapes, src_crs, dst_crs):
        """Reproject shapes from CRS +src_crs+ to +dst_crs+"""
        return [reproject_shape(s, src_crs, dst_crs) for s in shapes]

    def _apply_buffer(self, shapes):
        """Apply a fixed-sized buffer to all shapes"""
        if self.buffer_size != 0:
            return [s.buffer(self.buffer_size) for s in shapes]
        else:
            return shapes

    def _write_window_tiles(self, shapes, output_dir, tile_fname):
        """Extract windows of +size+ by sliding it +step_size+ on a raster, and write files"""
        # Create R-Tree index with shapes to speed up intersection operation
        index = create_index(shapes)

        with rasterio.open(tile_fname) as src:
            for window in sliding_windows(self.size, self.step_size,
                                          src.shape):
                window_box = box(*window_to_bounds(window, src.transform))
                matching_shapes = self._intersect_window(
                    shapes, index, window_box)
                try:
                    img_class = self._image_class_string(
                        matching_shapes, window_box)
                    win_fname = self._prepare_img_filename(tile_fname, window)
                    img_dir = self._create_class_dir(output_dir, img_class)
                    rgb = self._extract_img(src, window)
                    self._save_jpg(img_dir, win_fname, rgb)
                except RuntimeError:
                    pass

    def _save_jpg(self, img_dir, win_fname, rgb):
        """Save .jpg image from raster"""
        img_path = os.path.join(img_dir, win_fname)
        imsave(img_path, rgb)

    def _prepare_img_filename(self, tile_fname, window):
        """Prepare img filename"""
        fname, _ = os.path.splitext(os.path.basename(tile_fname))
        win_fname = '{}__{}_{}.jpg'.format(fname, window[0][0], window[1][0])
        return win_fname

    def _extract_img(self,
                     src,
                     window,
                     rescale_intensity=True,
                     lower_cut=2,
                     upper_cut=98):
        """Extract image from raster and preprocess"""
        rgb = np.dstack([src.read(b, window=window) for b in range(1, 4)])
        if rescale_intensity:
            low, high = np.percentile(rgb, (lower_cut, upper_cut))
            rgb = exposure.rescale_intensity(rgb, in_range=(low, high))
        return rgb

    def _create_class_dir(self, path, img_class):
        """Create class directory"""
        img_dir = os.path.join(path, img_class)
        os.makedirs(img_dir, exist_ok=True)
        return img_dir

    def _image_class_string(self, matching_shapes, window_box):
        """Return image class string

        Arguments:
            matching_shapes {list(shape)} -- list of matching shapes
            window_box {shape} -- window box

        Returns:
            string -- image class string

        """
        if self._is_image_positive(matching_shapes, window_box):
            img_class = 't'
        else:
            img_class = 'f'
        return img_class

    def _is_image_positive(self, matching_shapes, window_box):
        """Decide whether image is a true sample

        Arguments:
            matching_shapes {list(shape)} -- list of matching shapes
            window_box {shape} -- window box

        Returns:
            bool -- True if image is a true sample or not

        """
        return matching_shapes and any(
            s.intersection(window_box).area > 0.0 for s in matching_shapes)

    def _intersect_window(self, shapes, index, window_box):
        """Get shapes whose bounding boxes intersect with window box

        Arguments:
            shapes {list(shape)} -- list of shapes
            index {index} -- R-Tree index object
            window_box {shape} -- window box shape

        Returns:
            list(shape) -- list of shapes that intersect with window

        """
        matching_shapes = [
            shapes[s_id] for s_id in index.intersection(window_box.bounds)
        ]
        return matching_shapes

    def _write_metadata(self, output_dir):
        write_metadata(
            output_dir,
            version=self.version,
            size=self.size,
            step_size=self.step_size,
            buffer_size=self.buffer_size,
            rescale_intensity=self.rescale_intensity,
            lower_cut=self.lower_cut,
            upper_cut=self.upper_cut)
