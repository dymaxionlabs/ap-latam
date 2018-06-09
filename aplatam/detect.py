import rasterio as rio
import logging
_logger = logging.getLogger(__name__)
import glob
import numpy as np
from aplatam.old.util import window_to_bounds, sliding_windows
from skimage import exposure
from shapely.geometry import shape, box, mapping
import os
import tqdm
import json
from collections import namedtuple
import keras
from keras.preprocessing.image import ImageDataGenerator
from aplatam.post_process import filter_features_by_mean_prob
from aplatam.post_process import dissolve_overlapping_shapes
from aplatam.util import write_geojson, reproject_shape

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
        #imgs = []
        windows = []

        for window in sliding_windows(size, step_size, src.shape):

            window_box = box(*window_to_bounds(window, src.transform))

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
                windows.append(shape_with)
        #if cur_windows:
        #    name, _ = os.path.splitext(os.path.basename(fname))
        #    output = '/tmp/{}_windows.geojson'.format(name)
        #    write_geojson(cur_windows, output)

        return windows


def predict_images(input_dir, model, size, **kwargs):
    all_windows = []
    files = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    _logger.info(files)
    for fname in tqdm.tqdm(files):
        all_windows.extend(predict_image(fname, model, size, **kwargs))
    _logger.info("Done! Found %d matching windows  on all files ",
                 (len(all_windows)))
    return all_windows
    #print('{} written'.format(output))


def build_geojson(shapes_and_roces):
    d = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes_and_roces:
        feat = {
            'type': 'Feature',
            'geometry': mapping(shape),
            "properties": []
        }
        d['features'].append(feat)
    return json.dumps(d)


def detect(*, model_file, input_dir, step_size, rescale_intensity, neighbours,
           threshold, output, mean_threshold):
    datagen = ImageDataGenerator(rescale=1. / 255)
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
