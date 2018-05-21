#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a training set from high resolution images

* Get all polygons from features of input vector file
* Reproject polygons to epsg:3857
* Expand polygons with a fixed buffer (param).
* For each image:
  - Slide a window of fixed size (param) with a step size (param) over extended polygons:
    . If it intersects with original polygon, it is a match.
    . Store windows as flattened arrays inside a HDF5 file.
"""
from functools import partial
from shapely.geometry import shape, box, mapping
from skimage import exposure
from skimage.io import imsave
import fiona
import glob
import json
import multiprocessing as mp
import numpy as np
import os
import random
import rasterio as rio
import shutil
import sys
import tqdm
import pdb

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from aplatam.old.util import reproject_shape, window_to_bounds, create_index, sliding_windows

epsg3857_crs = 'epsg:3857'
epsg4326_crs = 'epsg:4326'

intensity_percentiles = (2, 98)


def write_geojson(shapes, output_path):
    import json
    from shapely.geometry import mapping
    d = {'type': 'FeatureCollection', 'features': []}
    for shape in shapes:
        feat = {'type': 'Feature', 'geometry': mapping(shape)}
        d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    from itertools import zip_longest
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def write_window_tiles(shapes,
                       output_dir,
                       tile_fname,
                       size=64,
                       step_size=16,
                       rescale_intensity=True):
    "Extract windows of +size+ by sliding it +step_size+ on a raster, and write files"

    # Create R-Tree index with shapes to speed up intersection operation
    index = create_index(shapes)

    path = os.path.join(output_dir, 'all')

    #temp_windows = []
    with rio.open(tile_fname) as src:
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
            except:
                pass
    # FIXME
    #fname, ext = os.path.splitext(os.path.basename(tile_fname))
    #write_geojson(temp_windows, '/tmp/window_{}.geojson'.format(fname))


def extract_all_images(input_dir, output_dir, shapes, **kwargs):
    files = glob.glob(os.path.join(input_dir, '**/*.tif'), recursive=True)
    worker = partial(write_window_tiles, shapes, output_dir, **kwargs)
    with mp.Pool(mp.cpu_count()) as pool:
        list(tqdm.tqdm(pool.imap(worker, files), total=len(files)))


def write_metadata(output_dir, **kwargs):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(kwargs, f)


def balance_classes(true_files, false_files, undersample=True, limit=None):
    if limit:
        true_files = random.sample(true_files, limit)
    if len(true_files) < len(false_files) and undersample:
        false_files = random.sample(false_files, len(true_files))
    return true_files, false_files


def split_train_test(files, output_dir, validation_size):
    true_files, false_files = files
    n_test = round(len(true_files) * validation_size)

    random.shuffle(true_files)
    random.shuffle(false_files)

    Xt_test, Xt_train = true_files[:n_test], true_files[n_test:]
    Xf_test, Xf_train = false_files[:n_test], false_files[n_test:]
    print('Xt_train:', len(Xt_train), 'Xt_test:', len(Xt_test), 'Xf_train:',
          len(Xf_train), 'Xf_test:', len(Xf_test))

    move_files(Xt_train, os.path.join(output_dir, 'train', 't'))
    move_files(Xf_train, os.path.join(output_dir, 'train', 'f'))
    move_files(Xt_test, os.path.join(output_dir, 'test', 't'))
    move_files(Xf_test, os.path.join(output_dir, 'test', 'f'))


def move_files(files, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for src in files:
        fname = os.path.basename(src)
        dst = os.path.join(dst_dir, fname)
        shutil.copyfile(src, dst)


def main(args):
    #undersample = not args.no_undersample

    if args.seed:
        print('Seed: {}'.format(args.seed))
        random.seed(args.seed)

    # Generate default output path based on parameters
    if args.output_dir == default_output_dir:
        args.output_dir = args.output_dir.format(
            size=args.size, step_size=args.step_size, buffer=args.buffer)

    # Open vector file and fetch feature geometries
    with fiona.open(args.vector_file) as src:
        src_crs = src.crs['init']
        # Reproject shapes to WGS84 pseudomercator so we can apply a buffer in meters
        shapes = [
            reproject_shape(shape(f['geometry']), src_crs, epsg3857_crs)
            for f in src
        ]

    # Extend shapes with a fixed-size buffer (if requested)
    if args.buffer > 0:
        shapes_with_buffer = [s.buffer(args.buffer) for s in shapes]
    else:
        shapes_with_buffer = shapes

    # Go back to WGS84 in degrees
    #shapes_with_buffer = [reproject_shape(s, epsg3857_crs, epsg4326_crs)
    #                        for s in shapes_with_buffer]
    #write_geojson(shapes_with_buffer, 'shapes.geojson')

    # Delete output directory if it exists and --overwrite is active
    if os.path.exists(args.output_dir) and os.listdir(args.output_dir):
        if args.overwrite:
            shutil.rmtree(args.output_dir)
        else:
            parser.error('{} exists and is not empty.\n' \
                    'Run with --overwrite to overwrite all files inside, ' \
                    'or choose some other path.'.format(args.output_dir))

    write_metadata(
        args.output_dir,
        size=args.size,
        step_size=args.step_size,
        buffer=args.buffer)

    extract_all_images(
        args.input_dir,
        args.output_dir,
        shapes_with_buffer,
        size=args.size,
        step_size=args.step_size,
        rescale_intensity=args.rescale_intensity)

    true_files = glob.glob(os.path.join(args.output_dir, 'all', 't', '*.jpg'))
    false_files = glob.glob(os.path.join(args.output_dir, 'all', 'f', '*.jpg'))

    # Balance classes in all/ by undersampling
    #true_files, false_files = balance_classes(true_files, false_files,
    #        undersample=undersample, limit=args.limit)

    # Split all images into train/test directories, based on args.validation_size
    split_train_test((true_files, false_files), args.output_dir,
                     args.validation_size)

    print('Done')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description='Build training dataset from a tagged vector file and ' \
                        'high resolution multiband rasters',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    default_output_dir = os.path.join('data', 'hires', 'clips',
                                      '{size}_{step_size}_{buffer}')

    parser.add_argument(
        'vector_file',
        help=
        'Vector data file with tagged geometries (Shapefile, GeoJSON, etc.)')
    parser.add_argument(
        'input_dir', help='Path where hi-res images are stored')
    parser.add_argument(
        '--output-dir',
        default=default_output_dir,
        help='Path where train/validation tiles will be stored')
    parser.add_argument('--size', type=int, default=128, help='Window size')
    parser.add_argument(
        '--step-size', type=int, default=64, help='Window step size')
    parser.add_argument('--buffer', type=int, default=0, help='Buffer size')
    parser.add_argument(
        '--validation-size',
        type=int,
        default=0.25,
        help='Validation dataset size with respect to the complete dataset')
    parser.add_argument(
        '--overwrite',
        '-f',
        action='store_true',
        default=False,
        help='Overwrite existing output directory and files')
    parser.add_argument(
        '--rescale-intensity',
        action='store_true',
        default=True,
        help='Rescale intensity of images, with percentiles {}'.format(
            intensity_percentiles))
    parser.add_argument(
        '--no-undersample',
        action='store_false',
        default=False,
        help='Do not balance classes by undersampling the larger class')
    parser.add_argument('--seed', '-s', type=int, help='Random seed')
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Use only a limited set of samples with positive label')

    args = parser.parse_args()

    main(args)
