# -*- coding: utf-8 -*-

import json
import os
import tempfile

import pytest
from mock import call, patch

from aplatam import __version__
from aplatam.build_trainset import CnnTrainsetBuilder
from aplatam.console.prepare import validate_rasters_band_count
import glob


@pytest.fixture
def some_rasters():
    return ['a.tif', 'b.tif', 'c.tif']


@pytest.fixture
def rasters_with_different_band_count(raster):
    return {'a.tif': 4, 'b.tif': 4, 'c.tif': 3}[raster]


@pytest.fixture
def some_crs():
    return dict(init='epsg:4326')


@patch('aplatam.console.prepare.get_raster_band_count', return_value=4)
def test_validate_rasters_band_count_ok(mock_func, some_rasters):
    assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call(r) for r in some_rasters], any_order=True)


@patch(
    'aplatam.console.prepare.get_raster_band_count',
    side_effect=rasters_with_different_band_count)
def test_validate_rasters_band_count_fail(mock_func, some_rasters):
    with pytest.raises(RuntimeError):
        assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call('a.tif'), call('b.tif'), call('c.tif')])


def test_cnn_trainset_builder():
    builder = CnnTrainsetBuilder(
        ['tests/fixtures/sen2_20161215_clipped.tif'],
        'tests/fixtures/settlements.geojson',
        size=128,
        step_size=64)

    with tempfile.TemporaryDirectory(prefix='aplatam_test_') as tmpdir:
        builder.build(tmpdir)

        metadata_path = os.path.join(tmpdir, 'metadata.json')
        assert os.path.exists(metadata_path)
        with open(metadata_path) as f:
            metadata = json.load(f)
            assert isinstance(metadata, dict)
            assert metadata["version"] == __version__
            list_argument = [
                'size', 'step_size', 'buffer_size', 'rescale_intensity',
                'lower_cut', 'upper_cut'
            ]
            for name_argument in list_argument:
                assert metadata[name_argument] == getattr(
                    builder, name_argument)

        test_t = os.path.join(tmpdir, "t")
        assert os.path.exists(test_t)
        test_f = os.path.join(tmpdir, "f")
        assert os.path.exists(test_f)
        t_jpg = glob.glob(os.path.join(test_t, '*.jpg'))
        f_jpg = glob.glob(os.path.join(test_f, '*.jpg'))
        assert len(t_jpg) > 0
        assert len(f_jpg) > 0
