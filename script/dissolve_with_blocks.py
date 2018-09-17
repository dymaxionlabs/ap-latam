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
from shapely.ops import unary_union
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
        blocks = list(ds)

    logger.info('Blocks: {}'.format(len(blocks)))

    with fiona.open(windows_file) as ds:
        windows_crs = ds.crs
        windows_schema = ds.schema.copy()
        windows = list(ds)
    logger.info('Windows: {}'.format(len(windows)))

    assert(windows_crs == blocks_crs)

    window_shapes = [shape(w['geometry']) for w in windows]
    ix = create_index(window_shapes, 'index')

    selected_features = []
    for i, block in enumerate(tqdm(blocks)):
        props = block['properties']
        block_shape = shape(block['geometry'])

        inter_window_ids = set(ix.intersection(block_shape.bounds))
        inter_window_shapes = [(i, window_shapes[i]) for i in inter_window_ids]
        inter_window_ids = set(i for i, w in inter_window_shapes if
                block_shape.intersection(w).area > 0)

        inter_windows = [windows[i] for i in inter_window_ids]

        if len(inter_windows):
            logger.debug('Block {}: {} intersecting windows'.format(i, len(inter_windows)))

            union = unary_union([window_shapes[i] for i in inter_window_ids])
            perc = union.area / block_shape.area
            logger.debug('Block area: {}, windows area: {}, {}%'.format(
                block_shape.area, union.area, round(perc, 2)))

            if perc > 0.8:
                props = dict(prob=mean(w['properties']['prob'] for w in inter_windows))
                selected_features.append(dict(geometry=mapping(block_shape),
                    properties=props))

    logger.info('Write output file {}'.format(output_file))
    new_schema = windows_schema
    new_schema['properties'] = {'prob': windows_schema['properties']['prob']}
    opts = dict(driver=blocks_driver, schema=new_schema, crs=blocks_crs)
    with fiona.open(output_file, 'w', **opts) as ds:
        for feat in selected_features:
            ds.write(feat)
