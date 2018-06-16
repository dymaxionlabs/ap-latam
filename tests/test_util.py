import io
import json
import os
import tempfile

from mock import patch
from rasterio.windows import Window
from shapely.geometry import Point

from aplatam.util import (ShapeWithProps, all_raster_files, read_metadata,
                          sliding_windows, write_geojson)

TIF_FILES = ['data/test/20161215.full.tif']
POINT = Point(0.0, 0.0)
DATA_DIC = {'data': 'tdp2'}


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


@patch('aplatam.util.glob', return_value=TIF_FILES)
def test_all_raster_files(glob_mock):
    raster_files = all_raster_files('data/test')
    list_string = TIF_FILES
    glob_mock.assert_called_once_with('data/test/**/*.tif', recursive=True)
    assert raster_files == list_string


@patch('aplatam.util.open', return_value=io.StringIO(json.dumps(DATA_DIC)))
def test_read_metadata(open_mock):
    metadata_read = read_metadata('data/dtp2')
    assert metadata_read == DATA_DIC
    open_mock.assert_called_once_with('data/dtp2/metadata.json')


def test_write_geojson():
    shapes = [ShapeWithProps(shape=POINT, props={}) for i in range(3)]
    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = os.path.join(tmpdir, 'metadata.json')
        write_geojson(shapes, data_path)
        assert os.path.exists(data_path)
