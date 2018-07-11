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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: {} BLOCKS_FILE WINDOWS_FILE OUTPUT_FILE'.format(sys.argv[0]))
        sys.exit(1)

    blocks_file = sys.argv[1]
    windows_file = sys.argv[2]
    output_file = sys.argv[3]

    with fiona.open(blocks_file) as ds:
        blocks_driver = ds.driver
        blocks_schema = ds.schema.copy()
        blocks_crs = ds.crs
        blocks = [shape(f['geometry']) for f in ds]

    logger.info('Blocks: {}'.format(len(blocks)))

    with fiona.open(windows_file) as src:
        windows_crs = src.crs
        windows = [shape(f['geometry']) for f in src]
    logger.info('Windows: {}'.format(len(windows)))

    assert(windows_crs == blocks_crs)

    ix = create_index(windows, 'index')

    selected_blocks = []
    for i, block in enumerate(tqdm(blocks)):
        inter_windows_ids = set(ix.intersection(block.bounds))
        inter_windows = [windows[i] for i in inter_windows_ids]
        if len(inter_windows):
            logger.info('Block {}: {} intersecting windows'.format(i, len(inter_windows)))
            windows_area = sum(w.area for w in inter_windows)
            perc = windows_area / block.area
            logger.info('Block area: {}, windows area: {}, {}%'.format(block.area, windows_area, perc))
            if perc > 0.5:
                selected_blocks.append(block)

    logger.info('Write output file {}'.format(output_file))
    new_schema = blocks_schema
    new_schema['properties'] = {}
    with fiona.open(output_file, 'w', driver=blocks_driver, schema=new_schema,
            crs=blocks_crs) as ds:
        for block in selected_blocks:
            feat = {'geometry': mapping(block), 'properties': {}}
            ds.write(feat)
