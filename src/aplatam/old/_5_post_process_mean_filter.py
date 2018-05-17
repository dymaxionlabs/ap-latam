from contextlib import contextmanager
from shapely.geometry import shape, mapping
import fiona
import glob
import numpy as np
import os
import rasterio
import rtree
import shapely
import subprocess
import tempfile
import json

import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))


def create_index(features):
    """Create an R-Tree index from a set of features"""
    index = rtree.index.Index()
    for id, feature in enumerate(features):
        index.insert(id, shape(feature['geometry']).bounds)
    return index


def prob_mean_filter(feature_id, features, ix, neigh):
    f_id = int(feature_id)
    f_shape = shape(features[f_id]['geometry'])
    nearest_shapes = list(ix.nearest(f_shape.bounds,1))
    nearest_shapes.remove(f_id)
    if len(nearest_shapes) < neigh:
        mean_filter_prob = 0
    else:
        nearest_probs = [features[f]['properties']['prob'] for f in nearest_shapes]
        mean_filter_prob = np.mean(np.array(nearest_probs))
    return mean_filter_prob
   

def write_geojson(features, output_path, ix, neigh):
    d = {'type': 'FeatureCollection', 'features': []}
    for feature in features :
        feat = {'type': 'Feature',
                'geometry': mapping(shape(feature['geometry'])),
                'properties': {'prob_filt': prob_mean_filter(feature['id'], features, ix, int(neigh)),
                               'prob': feature['properties']['prob']}
                }
        if feat['properties']['prob_filt'] > 0.3:
            d['features'].append(feat)
    with open(output_path, 'w') as f:
        f.write(json.dumps(d))


def main(args):
    features = fiona.open(args.input_file)
    ix = create_index(features)
    write_geojson(features, args.output_file, ix, args.neighbors)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
            description='Filter isolated polygons based on nearest neighbors presence and compute mean probability',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input_file',
            help='Results vector file')
    parser.add_argument('output_file',
            help='Filtered vector file')
    parser.add_argument('neighbors',
            help='Number of neighbors')

    args = parser.parse_args()

    main(args)