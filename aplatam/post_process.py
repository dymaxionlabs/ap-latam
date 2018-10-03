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


def filter_features_by_mean_prob(shapes_with_props, neigh, mean_threshold):
    _logger.info('Create index for shapes')
    ix = create_index(shapes_with_props)

    _logger.info('Filter shapes by mean probability in neighbourhoud')
    for shape_id, shape_with_prop in enumerate(tqdm(shapes_with_props)):
        shape_with_prop.props['prob_mean'] = prob_mean_filter(
            shape_id, shapes_with_props, ix, neigh)

    return [s for s in shapes_with_props if s.props['prob_mean'] > mean_threshold]
