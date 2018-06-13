import glob
import json
import logging
import os
from collections import namedtuple

import keras
import numpy as np
import rasterio as rio
import tqdm
from shapely.geometry import box, mapping
from skimage import exposure

from aplatam.post_process import (dissolve_overlapping_shapes,
                                  filter_features_by_mean_prob)
from aplatam.util import (reproject_shape, sliding_windows, write_geojson)

_logger = logging.getLogger(__name__)

WGS84_CRS = {"init": "epsg:4326"}

ShapeWithProps = namedtuple('ShapeWithProps', ['shape', 'props'])


def predict_image(fname,
                  model,
                  size,
                  threshold,
                  step_size=None,
                  rescale_intensity=False,
                  lower_cut=2,
                  upper_cut=98):
    if not step_size:
        step_size = size

    with rio.open(fname) as src:
        matching_windows = []

        windows = list(sliding_windows(
            size, step_size, height=src.shape[0], width=src.shape[1]))

        for window in tqdm.tqdm(windows):
            window_box = box(*src.window_bounds(window))

            img = np.dstack([src.read(b, window=window) for b in range(1, 4)])

            if rescale_intensity:
                low, high = np.percentile(img, (lower_cut, upper_cut))
                img = exposure.rescale_intensity(img, in_range=(low, high))

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
    all_windows = []
    files = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    _logger.info(files)
    for fname in files:
        all_windows.extend(predict_image(fname, model, size, **kwargs))
    _logger.info("Done! Found %d matching windows  on all files ",
                 (len(all_windows)))
    return all_windows


def build_geojson(shapes_and_roces):
    dicc = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes_and_roces:
        feat = {
            'type': 'Feature',
            'geometry': mapping(shape),
            "properties": []
        }
        dicc['features'].append(feat)
    return json.dumps(dicc)


def detect(*, model_file, input_dir, step_size, rescale_intensity, neighbours,
           threshold, output, mean_threshold):

    model = keras.models.load_model(model_file)
    img_size = model.input_shape[1]

    shapes_with_props = predict_images(
        input_dir,
        model,
        img_size,
        step_size=step_size,
        rescale_intensity=rescale_intensity,
        threshold=threshold)
    shapes_with_props = filter_features_by_mean_prob(
        shapes_with_props, neighbours, mean_threshold)
    shapes_with = [shape_with.shape for shape_with in shapes_with_props]
    shape_w = dissolve_overlapping_shapes(shapes_with)
    write_geojson(shape_w, output)
