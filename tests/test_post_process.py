from mock import patch
from aplatam.post_process import *
from shapely.geometry import box, mapping


def test_apply_buffer():
    boxes = [box(0, 0, 1, 1), box(2, 3, 2, 4)]
    boxes_with_props = [ShapeWithProps(b, {}) for b in boxes]

    new_boxes_with_props = apply_buffer(boxes_with_props, 3)
    assert all(a.props == b.props for a, b in zip(boxes_with_props, new_boxes_with_props))
    assert all(a.shape.buffer(3) == b.shape for a, b in zip(boxes_with_props, new_boxes_with_props))


def test_filter_features_by_mean_prob():
    shapes = [
        # first row
        ShapeWithProps(box(0, 0, 1, 1), dict(prob=0.75)),
        ShapeWithProps(box(1, 0, 2, 1), dict(prob=0.5)),
        ShapeWithProps(box(2, 0, 3, 1), dict(prob=0.5)),

        # second row
        ShapeWithProps(box(0, 1, 1, 2), dict(prob=0.15)),
        ShapeWithProps(box(1, 1, 2, 2), dict(prob=0.9)),
        ShapeWithProps(box(2, 1, 3, 2), dict(prob=0.1)),

        # third row
        ShapeWithProps(box(0, 2, 1, 3), dict(prob=0.75)),
        ShapeWithProps(box(1, 2, 2, 3), dict(prob=0.5)),
        ShapeWithProps(box(2, 2, 3, 3), dict(prob=0.5)),
    ]

    res = filter_features_by_mean_prob(shapes, 4, 0.5)
    assert [{'prob': 0.15, 'prob_mean': 0.6799999999999999},
            {'prob': 0.1, 'prob_mean': 0.58}] == [r.props for r in res]
