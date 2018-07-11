#!/usr/bin/env python3
"""
Intersect with blocks polygons, as a temporary alternative to
dissolve_overlapping_shapes.

The dissolve algorithm is too slow right now, so as a workaround we calculate
the intersection between blocks polygons and detected windows.

Pseudocode
----------

    Read block polygons
    Read window polygons
    Create R-Tree index of window polygons
    For every block polygon b:
        Get intersection between b and windows
        If sum of areas of intersected windows >= 50% block window, select block

"""
import fiona
import os
import rtree
import sys
import logging

from shapely.geometry import shape, mapping
from tqdm import tqdm

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)



def create_index(shapes, index_path):
    reuse = os.path.exists('index.idx')
    ix = rtree.index.Rtree(index_path)
    if not reuse:
        logger.info('Creating index for windows shapes...')
        for s_id, shape in enumerate(tqdm(shapes)):
            ix.insert(s_id, shape.bounds)
    return ix

def mean(array):
    array = list(array)
    return sum(array) / len(array)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: {} BLOCKS_FILE WINDOWS_FILE OUTPUT_FILE'.format(sys.argv[0]))
        sys.exit(1)

    blocks_file = sys.argv[1]
    windows_file = sys.argv[2]
    output_file = sys.argv[3]

    with fiona.open(blocks_file) as ds:
        blocks_driver = ds.driver
        blocks_crs = ds.crs
        block_shapes = [shape(f['geometry']) for f in ds]

    logger.info('Blocks: {}'.format(len(block_shapes)))

    with fiona.open(windows_file) as ds:
        windows_crs = ds.crs
        windows_schema = ds.schema.copy()
        windows = list(ds)
    logger.info('Windows: {}'.format(len(windows)))

    assert(windows_crs == blocks_crs)

    window_shapes = [shape(w['geometry']) for w in windows]
    ix = create_index(window_shapes, 'index')

    selected_features = []
    for i, block_shape in enumerate(tqdm(block_shapes)):
        inter_windows_ids = set(ix.intersection(block_shape.bounds))
        inter_windows = [windows[i] for i in inter_windows_ids]
        if len(inter_windows):
            logger.debug('Block {}: {} intersecting windows'.format(i, len(inter_windows)))
            windows_area = sum(shape(w['geometry']).area for w in inter_windows)
            perc = windows_area / block_shape.area
            logger.debug('Block area: {}, windows area: {}, {}%'.format(block_shape.area, windows_area, perc))
            if perc > 0.5:
                props = dict(prob=mean(w['properties']['prob'] for w in inter_windows))
                selected_features.append(dict(geometry=mapping(block_shape), properties=props))

    logger.info('Write output file {}'.format(output_file))
    new_schema = windows_schema
    new_schema['properties'] = {'prob': windows_schema['properties']['prob']}
    opts = dict(driver=blocks_driver, schema=new_schema, crs=blocks_crs)
    with fiona.open(output_file, 'w', **opts) as ds:
        for feat in selected_features:
            ds.write(feat)
