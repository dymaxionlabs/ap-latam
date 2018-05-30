import rtree
from shapely.geometry import shape, mapping
import numpy as np
from shapely.ops import unary_union


def create_index(features):
    """Create an R-Tree index from a set of features"""
    index = rtree.index.Index()
    for id, feature in enumerate(features):
        index.insert(id, shape(feature['geometry']).bounds)
    return index


def prob_mean_filter(feature_id, features, ix, neigh):
    f_id = int(feature_id)
    f_shape = shape(features[f_id]['geometry'])
    nearest_shapes = list(ix.nearest(f_shape.bounds, 1))
    nearest_shapes.remove(f_id)
    if len(nearest_shapes) < neigh:
        mean_filter_prob = 0
    else:
        nearest_probs = [
            features[f]['properties']['prob'] for f in nearest_shapes
        ]
        mean_filter_prob = np.mean(np.array(nearest_probs))
    return mean_filter_prob


def dissolve_overlapping_shapes(shapes):
    res = []
    while shapes:
        s = shapes.pop()
        while True:
            ss = [x for x in shapes if x != s and s.intersection(x).area > 0]
            if not ss:
                break
            s = unary_union([s] + ss)
            shapes = [x for x in shapes if x not in ss]
        res.append(s)
    return res
