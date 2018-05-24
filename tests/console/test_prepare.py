# -*- coding: utf-8 -*-

import pytest
from mock import call, patch

from aplatam.console.prepare import validate_rasters_band_count


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
