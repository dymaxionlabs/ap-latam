import glob
import logging
import os
import pickle
from collections import namedtuple

import dask_rasterio
import fiona
import keras
import numpy as np
import rasterio as rio
import tqdm
from shapely.geometry import box, shape
from skimage import exposure

from aplatam.post_process import (dissolve_overlapping_shapes,
                                  filter_features_by_mean_prob)
from aplatam.util import reproject_shape, sliding_windows, write_geojson

_logger = logging.getLogger(__name__)

WGS84_CRS = {"init": "epsg:4326"}

ShapeWithProps = namedtuple('ShapeWithProps', ['shape', 'props'])


def detect(model_file,
           input_dir,
           output,
           rasters_contour=None,
           step_size=None,
           rescale_intensity=True,
           lower_cut=2,
           upper_cut=98,
           *,
           neighbours,
           threshold,
           mean_threshold):

    model = keras.models.load_model(model_file)
    img_size = model.input_shape[1]

    if not step_size:
        step_size = img_size

    fname, _ = os.path.splitext(output)
    predictions_path = '{}.pred.pkl'.format(fname)

    if os.path.exists(predictions_path):
        with open(predictions_path, 'rb') as file:
            shapes_with_props = pickle.load(file)
        _logger.info(
            'Going to reuse existing %s predictions file from a previous run',
            predictions_path)
    else:
        shapes_with_props = predict_images(
            input_dir,
            model,
            img_size,
            step_size=step_size,
            rasters_contour=rasters_contour,
            rescale_intensity=rescale_intensity,
            lower_cut=lower_cut,
            upper_cut=upper_cut,
            threshold=threshold)

        with open(predictions_path, 'wb') as file:
            pickle.dump(shapes_with_props, file)
        _logger.info('%s of predicted windows written')

    _logger.info('Total detected windows: %d', len(shapes_with_props))

    # Filter out polygons with low probablity by calculating
    # mean probability from neighbours.
    shapes_with_props = filter_features_by_mean_prob(
        shapes_with_props, neighbours, mean_threshold)

    # Dissolve overlapping polygons
    shapes = [s.shape for s in shapes_with_props]
    shapes = dissolve_overlapping_shapes(shapes)

    write_geojson(shapes, output)


def predict_image(fname,
                  model,
                  size,
                  threshold,
                  step_size=None,
                  rasters_contour=None,
                  rescale_intensity=True,
                  lower_cut=2,
                  upper_cut=98):

    if not step_size:
        step_size = size

    if rescale_intensity:
        percentiles = calculate_percentiles(
            fname, lower_cut=lower_cut, upper_cut=upper_cut)

    with rio.open(fname) as src:
        matching_windows = []

        windows = sliding_windows(
            size, step_size, height=src.shape[0], width=src.shape[1])

        windows_and_boxes = [(w, box(*src.window_bounds(w))) for w in windows]
        _logger.info('Total windows: %d', len(windows_and_boxes))

        if rasters_contour:
            contour_polygon, contour_crs = load_raster_contour_polygon(
                rasters_contour)
            contour_polygon = reproject_shape(contour_polygon, contour_crs,
                                              src.crs)
            windows_and_boxes = [(w, b) for w, b in windows_and_boxes
                                 if contour_polygon.intersection(b)]
            _logger.info(
                'Total windows (after filtering with raster contour shape): %d',
                len(windows_and_boxes))

        for window, window_box in tqdm.tqdm(windows_and_boxes):
            img = np.dstack([src.read(b, window=window) for b in range(1, 4)])

            if rescale_intensity:
                img = exposure.rescale_intensity(img, in_range=percentiles)

            img = img / 255.
            preds = model.predict(np.array([img]))
            preds_b = preds[:, 0]

            for i in np.nonzero(preds_b > threshold)[0]:
                _logger.info((window, float(preds_b[i])))
                reproject_window_box = reproject_shape(window_box, src.crs,
                                                       WGS84_CRS)
                shape_with = ShapeWithProps(
                    shape=reproject_window_box, props={})
                shape_with.props["prob"] = float(preds_b[i])
                matching_windows.append(shape_with)

        return matching_windows


def predict_images(input_dir, model, size, **kwargs):
    polygons = []

    rasters = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    _logger.info(rasters)

    for raster in rasters:
        polygons.extend(predict_image(raster, model, size, **kwargs))
    _logger.info('Found %d matching windows on all files', (len(polygons)))

    return polygons


def load_raster_contour_polygon(rasters_contour):
    with fiona.open(rasters_contour) as src:
        contour_shape = [shape(feature['geometry']) for feature in src][0]
        return contour_shape, src.crs


def calculate_percentiles(raster, block_size=1, *, lower_cut, upper_cut):
    rgb_img = dask_rasterio.read_raster(
        raster, band=(1, 2, 3), block_size=block_size)
    return tuple(np.percentile(rgb_img, (lower_cut, upper_cut)))
