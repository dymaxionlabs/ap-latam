from rasterio.windows import Window

from aplatam.util import sliding_windows


def test_sliding_windows_whole_width_and_height():
    windows = list(sliding_windows(size=2, step_size=2, width=6, height=6))
    assert windows == [
        # row 0
        Window(col_off=0, row_off=0, width=2, height=2),
        Window(col_off=2, row_off=0, width=2, height=2),
        Window(col_off=4, row_off=0, width=2, height=2),
        # row 1
        Window(col_off=0, row_off=2, width=2, height=2),
        Window(col_off=2, row_off=2, width=2, height=2),
        Window(col_off=4, row_off=2, width=2, height=2),
        # row 2
        Window(col_off=0, row_off=4, width=2, height=2),
        Window(col_off=2, row_off=4, width=2, height=2),
        Window(col_off=4, row_off=4, width=2, height=2),
    ]


def test_sliding_windows_whole_height_only():
    windows = list(sliding_windows(size=2, step_size=2, width=5, height=6))
    assert windows == [
        # row 0
        Window(col_off=0, row_off=0, width=2, height=2),
        Window(col_off=2, row_off=0, width=2, height=2),
        # row 1
        Window(col_off=0, row_off=2, width=2, height=2),
        Window(col_off=2, row_off=2, width=2, height=2),
        # row 2
        Window(col_off=0, row_off=4, width=2, height=2),
        Window(col_off=2, row_off=4, width=2, height=2),
    ]


def test_sliding_windows_whole_width_only():
    windows = list(sliding_windows(size=2, step_size=2, width=6, height=5))
    assert windows == [
        # row 0
        Window(col_off=0, row_off=0, width=2, height=2),
        Window(col_off=2, row_off=0, width=2, height=2),
        Window(col_off=4, row_off=0, width=2, height=2),
        # row 1
        Window(col_off=0, row_off=2, width=2, height=2),
        Window(col_off=2, row_off=2, width=2, height=2),
        Window(col_off=4, row_off=2, width=2, height=2),
    ]


def test_sliding_windows_odd_size():
    windows = list(sliding_windows(size=4, step_size=2, width=7, height=9))
    assert windows == [
        # row 0
        Window(col_off=0, row_off=0, width=4, height=4),
        Window(col_off=2, row_off=0, width=4, height=4),
        # row 1
        Window(col_off=0, row_off=2, width=4, height=4),
        Window(col_off=2, row_off=2, width=4, height=4),
        # row 2
        Window(col_off=0, row_off=4, width=4, height=4),
        Window(col_off=2, row_off=4, width=4, height=4),
    ]
