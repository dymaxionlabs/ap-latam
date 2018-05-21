# -*- coding: utf-8 -*-

import pytest
from mock import call, patch
from aplatam.train import validate_rasters_crs, validate_vector_crs, validate_rasters_band_count


@pytest.fixture
def some_rasters():
    return ['a.tif', 'b.tif', 'c.tif']


@pytest.fixture
def some_vector():
    return 'foo.geojson'


@pytest.fixture
def rasters_with_different_crs(raster):
    return {
        'a.tif': {
            'init': 'epsg:4326'
        },
        'b.tif': {
            'init': 'epsg:32720'
        },
        'c.tif': {
            'init': 'epsg:4326'
        }
    }[raster]


@pytest.fixture
def rasters_with_different_band_count(raster):
    return {'a.tif': 4, 'b.tif': 4, 'c.tif': 3}[raster]


@pytest.fixture
def some_crs():
    return dict(init='epsg:4326')


@pytest.fixture
def another_crs():
    return dict(init='epsg:32720')


@patch('aplatam.train.get_raster_crs', return_value=some_crs)
def test_validate_rasters_crs_ok(mock_func, some_rasters):
    assert validate_rasters_crs(some_rasters)
    mock_func.assert_has_calls([call(r) for r in some_rasters], any_order=True)


@patch('aplatam.train.get_raster_crs', side_effect=rasters_with_different_crs)
def test_validate_rasters_crs_fail(mock_func, some_rasters):
    with pytest.raises(RuntimeError):
        assert validate_rasters_crs(some_rasters)
    mock_func.assert_has_calls([call('a.tif'), call('b.tif')])


@patch('aplatam.train.get_vector_crs', return_value=some_crs)
@patch('aplatam.train.get_raster_crs', return_value=some_crs)
def test_validate_vector_crs_ok(raster_mock, vector_mock, some_rasters,
                                some_vector):
    assert validate_vector_crs(some_rasters, some_vector)
    raster_mock.assert_called_with('a.tif')
    vector_mock.assert_called_with('foo.geojson')


@patch('aplatam.train.get_vector_crs', return_value=some_crs)
@patch('aplatam.train.get_raster_crs', return_value=another_crs)
def test_validate_vector_crs_fail(raster_mock, vector_mock, some_rasters,
                                  some_vector):
    with pytest.raises(RuntimeError):
        validate_vector_crs(some_rasters, some_vector)
    raster_mock.assert_called_with('a.tif')
    vector_mock.assert_called_with('foo.geojson')


@patch('aplatam.train.get_raster_band_count', return_value=4)
def test_validate_rasters_band_count_ok(mock_func, some_rasters):
    assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call(r) for r in some_rasters], any_order=True)


@patch(
    'aplatam.train.get_raster_band_count',
    side_effect=rasters_with_different_band_count)
def test_validate_rasters_band_count_fail(mock_func, some_rasters):
    with pytest.raises(RuntimeError):
        assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call('a.tif'), call('b.tif'), call('c.tif')])
