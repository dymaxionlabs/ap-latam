import numpy as np
import logging
import rtree
from tqdm import tqdm
from shapely.ops import unary_union
from aplatam.util import ShapeWithProps

_logger = logging.getLogger(__name__)


def create_index(shapes_with_props):
    """Create an R-Tree index from a set of features"""
    index = rtree.index.Index()
    for shape_id, shape_with_props in enumerate(tqdm(shapes_with_props)):
        index.insert(shape_id, shape_with_props.shape.bounds)
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


def apply_buffer(shapes_with_props, buffer_size):
    return [ShapeWithProps(shape=s.shape.buffer(buffer_size), props=s.props) for s in shapes_with_props]


def dissolve_overlapping_shapes(shapes_with_props, buffer_size=None):
    _logger.info('Dissolve overlapping shapes')

    res = []

    if buffer_size:
        shapes_with_props = apply_buffer(shapes_with_props, buffer_size)

    total = len(shapes_with_props)
    with tqdm(total=total) as pbar:
        new_shape_with_props = None
        while shapes_with_props:
            s = shapes_with_props.pop()
            while True:
                ss = [x for x in shapes_with_props if x != s and s.shape.intersection(x.shape).area > 0]
                if not ss:
                    break

                new_shape = unary_union([s.shape] + [x.shape for x in ss])
                new_props = {'prob': np.mean([x.props['prob'] for x in ss])}
                s = ShapeWithProps(shape=new_shape, props=new_props)

                shapes_with_props = [x for x in shapes_with_props if x not in ss]
                pbar.update(total - len(shapes_with_props))

            res.append(s)

    return res


def filter_features_by_mean_prob(shapes_with_props, neigh, mean_threshold):
    _logger.info('Create index for shapes')
    ix = create_index(shapes_with_props)

    _logger.info('Filter shapes by mean probability in neighbourhoud')
    for shape_id, shape_with_prop in enumerate(tqdm(shapes_with_props)):
        shape_with_prop.props["prop_mean"] = prob_mean_filter(
            shape_id, shapes_with_props, ix, neigh)
    return [
        shape_with_prop for shape_with_prop in shapes_with_props
        if shape_with_prop.props["prop_mean"] > mean_threshold
    ]
