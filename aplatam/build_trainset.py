"""This module contains classes for building trainsets"""
import logging
import os

import dask_rasterio
import fiona
import numpy as np
import rasterio
import rasterio.mask
from shapely.geometry import box, shape
from skimage import exposure
from skimage.io import imsave

from aplatam import __version__
from aplatam.class_balancing import split_dataset
from aplatam.util import (create_index, get_raster_crs, reproject_shape,
                          sliding_windows, write_metadata)

_logger = logging.getLogger(__name__)


class CnnTrainsetBuilder:
    """
    Trainset builder for a CNN-based model

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

    Keyword Arguments:
        test_size {float} -- proportion of test set from total of true samples
        balancing_multiplier {float} -- proportion of false samples w.r.t
            true samples (e.g. 1.0 = 50% true 50% false) (default: {0.25})
        buffer_size {float} -- size of buffer (default: {0})
        rescale_intensity {bool} -- whether to rescale images intensity
            (default: {True})
        lower_cut {float} -- lower cut of intensity rescale (default: {2})
        upper_cut {float} -- upper cut of intensity rescale (default: {98})
        block_size {int} -- block size multiplier (default: {1})

    """

    DATASET_DIRNAMES = ('train', 'test')

    def __init__(self,
                 rasters,
                 vector,
                 test_size=0.25,
                 balancing_multiplier=1,
                 buffer_size=0,
                 rescale_intensity=True,
                 lower_cut=2,
                 upper_cut=98,
                 block_size=1,
                 rasters_contour=None,
                 *,
                 size,
                 step_size):
        self.rasters = rasters
        self.vector = vector
        self.test_size = test_size
        self.balancing_multiplier = balancing_multiplier
        self.size = size
        self.step_size = step_size
        self.buffer_size = buffer_size
        self.rescale_intensity = rescale_intensity
        self.lower_cut = lower_cut
        self.upper_cut = upper_cut
        self.block_size = block_size
        self.rasters_contour = rasters_contour

    def build(self, output_dir):
        """
        Build a trainset and store it on output_dir

        Arguments:
            output_dir {string} -- output directory path

        """
        shapes, vector_crs = self._read_shapes()
        _logger.info('Total shapes: %d', len(shapes))
        _logger.info('Vector CRS is %s', vector_crs)

        contour_shape, contour_crs = self._load_raster_contour_polygon()

        self._create_dataset_directories(output_dir)

        for raster in self.rasters:
            _logger.info('Processing raster %s', raster)

            raster_crs = get_raster_crs(raster)
            _logger.info('Raster CRS is %s', raster_crs)

            percentiles = self._calculate_percentiles(raster)

            new_contour_shape = self._reproject_contour_shape(
                contour_shape, contour_crs, raster_crs)

            new_shapes = self._reproject_shapes(shapes, vector_crs, raster_crs)
            new_shapes = self._apply_buffer(new_shapes)
            new_shapes = self._intersection_with_raster_extent(
                new_shapes, raster)

            self._extract_samples(
                raster=raster,
                shapes=new_shapes,
                output_dir=output_dir,
                percentiles=percentiles,
                contour_polygon=new_contour_shape)

        self._write_metadata(output_dir)

    def _reproject_contour_shape(self, contour_shape, contour_crs, raster_crs):
        if self.rasters_contour and contour_crs != raster_crs:
            _logger.info('Reproject raster contour shape from %s to %s',
                         contour_crs, raster_crs)
            return reproject_shape(contour_shape, contour_crs, raster_crs)
        else:
            return contour_shape

    def _create_dataset_directories(self, output_dir):
        class_dirs = [
            os.path.join(output_dir, dirname)
            for dirname in self.DATASET_DIRNAMES
        ]
        for path in class_dirs:
            _logger.info('Create directory %s', path)
            os.makedirs(path, exist_ok=True)

    def _load_raster_contour_polygon(self):
        rasters_contour_shape, rasters_contour_crs = None, None
        if self.rasters_contour:
            _logger.info('Load raster contour polygon shape from %s',
                         self.rasters_contour)
            with fiona.open(self.rasters_contour) as src:
                rasters_contour_shape = [
                    shape(feature['geometry']) for feature in src
                ][0]
                rasters_contour_crs = src.crs
        return rasters_contour_shape, rasters_contour_crs

    def _intersection_with_raster_extent(self, shapes, raster):
        with rasterio.open(raster) as src:
            raster_bbox = box(*src.bounds)
        filtered_shapes = [
            shape for shape in shapes if raster_bbox.contains(shape)
        ]
        _logger.info(
            'There are %d shapes inside current raster extent (total %d)',
            len(filtered_shapes), len(shapes))
        return filtered_shapes

    def _extract_samples(self,
                         raster,
                         shapes,
                         output_dir,
                         percentiles=None,
                         contour_polygon=None):

        index = create_index(shapes)

        windows_and_boxes = self._sliding_windows(raster)
        _logger.info('Total windows: %d', len(windows_and_boxes))

        if contour_polygon:
            windows_and_boxes = [(w, b) for w, b in windows_and_boxes
                                 if contour_polygon.intersection(b)]
            _logger.info(
                'Total windows (after filtering with raster contour shape): %d',
                len(windows_and_boxes))

        matching_windows, non_matching_windows = self._partition_windows(
            windows_and_boxes, shapes, index)

        _logger.info('Total matching windows: %d', len(matching_windows))
        _logger.info('Total non-matching windows: %d',
                     len(non_matching_windows))

        # Split dataset
        datasets = split_dataset(
            matching_windows,
            non_matching_windows,
            test_size=self.test_size,
            balancing_multiplier=self.balancing_multiplier)

        # Extract and store images
        for i, windows in enumerate(datasets):
            dirname = self.DATASET_DIRNAMES[i]
            for j, cls_name in enumerate(('t', 'f')):
                # Create directory
                os.makedirs(
                    os.path.join(output_dir, dirname, cls_name), exist_ok=True)
                # Extract image
                self._extract_images_from_windows(
                    windows[j], raster, percentiles,
                    os.path.join(output_dir, dirname, cls_name))

    def _sliding_windows(self, raster):
        with rasterio.open(raster) as src:
            windows = sliding_windows(
                self.size, self.step_size, height=src.height, width=src.width)
            return [(win, box(*src.window_bounds(win))) for win in windows]

    def _partition_windows(self, windows_and_boxes, shapes, index):
        matching_windows = []
        non_matching_windows = []
        for win, wbox in windows_and_boxes:
            matching_shapes = [
                shapes[i] for i in index.intersection(wbox.bounds)
            ]
            if matching_shapes and any(
                    shape.intersection(wbox) for shape in matching_shapes):
                matching_windows.append(win)
            else:
                non_matching_windows.append(win)
        return matching_windows, non_matching_windows

    def _extract_images_from_windows(self, windows, raster, percentiles,
                                     output_dir):
        with rasterio.open(raster) as src:
            for window in windows:
                fname = self._prepare_img_filename(raster, window)
                rgb = self._extract_img(src, window, percentiles=percentiles)
                if not exposure.is_low_contrast(rgb):
                    self._save_jpg(output_dir, fname, rgb)

    def _read_shapes(self):
        """Read features from the vector file and return their geometry shapes"""
        with fiona.open(self.vector) as data:
            return [(shape(feat['geometry'])) for feat in data], data.crs

    def _reproject_shapes(self, shapes, src_crs, dst_crs):
        """Reproject shapes from CRS +src_crs+ to +dst_crs+"""
        if dict(src_crs) != dict(dst_crs):
            _logger.info('Reproject shapes from %s to %s', src_crs, dst_crs)
            return [reproject_shape(s, src_crs, dst_crs) for s in shapes]
        else:
            return shapes

    def _apply_buffer(self, shapes):
        """Apply a fixed-sized buffer to all shapes"""
        if self.buffer_size != 0:
            _logger.info('Apply fixed-sized buffer of %d to all shapes',
                         self.buffer_size)
            return [s.buffer(self.buffer_size) for s in shapes]
        else:
            return shapes

    def _calculate_percentiles(self, raster):
        if self.rescale_intensity:
            rgb_img = dask_rasterio.read_raster(
                raster, band=(1, 2, 3), block_size=self.block_size)
            return tuple(
                np.percentile(rgb_img, (self.lower_cut, self.upper_cut)))
        else:
            return None

    def _save_jpg(self, img_dir, win_fname, rgb):
        """Save .jpg image from raster"""
        img_path = os.path.join(img_dir, win_fname)
        imsave(img_path, rgb)

    def _prepare_img_filename(self, raster, window):
        """Prepare img filename"""
        fname, _ = os.path.splitext(os.path.basename(raster))
        win_fname = '{fname}__{i}_{j}.jpg'.format(
            fname=fname, i=window.row_off, j=window.col_off)
        return win_fname

    def _extract_img(self, src, window, percentiles=None):
        """Extract image from raster and preprocess"""
        rgb = np.dstack([src.read(b, window=window) for b in range(1, 4)])
        if self.rescale_intensity:
            rgb = exposure.rescale_intensity(rgb, in_range=percentiles)
        return rgb

    def _write_metadata(self, output_dir):
        write_metadata(
            output_dir,
            version=__version__,
            size=self.size,
            step_size=self.step_size,
            buffer_size=self.buffer_size,
            rescale_intensity=self.rescale_intensity,
            lower_cut=self.lower_cut,
            upper_cut=self.upper_cut)
