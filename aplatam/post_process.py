import rtree
from shapely.geometry import shape, mapping
import numpy as np
from shapely.ops import unary_union
import fiona


def create_index(shapes_with_props):
    """Create an R-Tree index from a set of features"""
    index = rtree.index.Index()
    for id, shape_with_props in enumerate(shapes_with_props):
        index.insert(id, shape_with_props.shape.bounds)
    return index


def prob_mean_filter(shape_id, shapes_with_props, ix, neigh):
    f_id = int(shape_id)
    f_shape = shapes_with_props[f_id].shape
    nearest_shapes = list(ix.nearest(f_shape.bounds, 1))
    nearest_shapes.remove(f_id)
    if len(nearest_shapes) < neigh:
        mean_filter_prob = 0
    else:
        nearest_probs = [
            shapes_with_props[f].props["prob"] for f in nearest_shapes
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


def filter_features_by_mean_prob(shapes_with_props, neigh, mean_threshold):
    ix = create_index(shapes_with_props)
    for shape_id, shape_with_prop in enumerate(shapes_with_props):
        shape_with_prop.props["prop_mean"] = prob_mean_filter(
            shape_id, shapes_with_props, ix, neigh)
    return [
        shapes_with_prop for shapes_with_prop in shapes_with_props
        if shape_with_prop.props["prop_mean"] > mean_threshold
    ]
