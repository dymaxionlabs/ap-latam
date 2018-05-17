#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classify a set of high resolution Tiff images downloaded with gsmaps
using a training model built with build_trainset_hires.py

* For each image:
  - Slide a window of fixed size (param) with a step size (param)
  - Predict window with model
  - If prediction result > 0.3, generate a polygon
* Write a vector file with all polygons
"""
from keras.preprocessing.image import ImageDataGenerator
from shapely.geometry import shape, box, mapping
from shapely.ops import transform
from skimage import exposure
from functools import partial
import glob
import keras.models
import numpy as np
import os
import pyproj
import rasterio as rio
import sys
import tqdm

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from aplatam.old.util import window_to_bounds, sliding_windows


def write_geojson(shapes_and_probs, output_path):
    import json
    from shapely.geometry import mapping
    d = {'type': 'FeatureCollection', 'features': []}
    for shape, prob in shapes_and_probs:
        project = partial(pyproj.transform,
                pyproj.Proj(init='epsg:3857'),
                pyproj.Proj(init='epsg:4326'))
        shape_wgs = transform(project, shape)
        feat = {'type': 'Feature',
                'geometry': mapping(shape_wgs),
                'properties': {'prob': prob}}
        d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))


def predict_image(fname, model, size, step_size=None, rescale_intensity=False):
    if not step_size:
        step_size = size

    with rio.open(fname) as src:
        #imgs = []
        windows = []
        for window in sliding_windows(size, step_size, src.shape):
            window_box = box(*window_to_bounds(window, src.transform))

            img = np.dstack([src.read(b, window=window) for b in range(1, 4)])

            if rescale_intensity:
                low, high = np.percentile(img, (2, 98))
                img = exposure.rescale_intensity(img, in_range=(low, high))

            img = img / 255.
            preds = model.predict(np.array([img]))
            preds_b = preds[:, 0]
            for i in np.nonzero(preds_b > 0.3)[0]:
                print((window, float(preds_b[i])))
                windows.append((window_box, float(preds_b[i])))
        #if cur_windows:
        #    name, _ = os.path.splitext(os.path.basename(fname))
        #    output = '/tmp/{}_windows.geojson'.format(name)
        #    write_geojson(cur_windows, output)

        return windows


def predict_images(input_dir, output, model, size, **kwargs):
    all_windows = []
    files = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    print(files)
    for fname in tqdm.tqdm(files):
        all_windows.extend(predict_image(fname, model, size, **kwargs))
    print('Done! Found {} matching windows on all files'.format(len(all_windows)))

    write_geojson(all_windows, output)
    print('{} written'.format(output))


def main(args):
    #datagen = ImageDataGenerator(rescale=1. / 255)
    model = keras.models.load_model(args.model_file)
    img_size = model.input_shape[1]

    step_size = None
    if args.step_size:
        step_size = int(args.step_size)

    predict_images(args.input_dir, args.output, model, img_size,
            step_size=step_size, rescale_intensity=args.rescale_intensity)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description='Classify a set of hi-res images',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('model_file', help='HDF5 Keras model file path')
    parser.add_argument('input_dir',
            help='Path where test hi-res images are stored')
    parser.add_argument('--step-size', default=None,
            help='Step size of sliding windows (if none, same as size)')
    parser.add_argument('--rescale-intensity', action='store_true', default=False,
            help='Rescale intensity with 2-98 percentiles')
    parser.add_argument('output', help='GeoJSON output file')

    args = parser.parse_args()

    main(args)