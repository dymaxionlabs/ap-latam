import os
import tempfile

import pytest
from mock import call, patch

import aplatam.console.train as ap_train
from aplatam import __version__
from aplatam.console.train import validate_rasters_band_count


@pytest.fixture
def some_rasters():
    return ['a.tif', 'b.tif', 'c.tif']


@pytest.fixture
def rasters_with_different_band_count(raster):
    return {'a.tif': 3, 'b.tif': 1, 'c.tif': 3}[raster]


@pytest.fixture
def some_crs():
    return dict(init='epsg:4326')


@patch('aplatam.console.train.get_raster_band_count', return_value=4)
def test_validate_rasters_band_count_ok(mock_func, some_rasters):
    assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call(r) for r in some_rasters], any_order=True)


@patch(
    'aplatam.console.train.get_raster_band_count',
    side_effect=rasters_with_different_band_count)
def test_validate_rasters_band_count_fail(mock_func, some_rasters):
    with pytest.raises(RuntimeError):
        assert validate_rasters_band_count(some_rasters)
    mock_func.assert_has_calls([call('a.tif'), call('b.tif')])


#@pytest.mark.skip(reason="issues with TravisCI and tensorflow-gpu")
@patch('aplatam.console.train.train')
def test_run_script_default_arguments(train_mock_func):
    with tempfile.TemporaryDirectory(prefix='ap_train') as tmpdir:
        ap_train.main(
            ['tests/fixtures/', 'tests/fixtures/settlements.geojson', tmpdir])

        output_model_path = os.path.join(tmpdir, 'model.h5')
        train_mock_func.assert_called_once_with(
            output_model_path,
            tmpdir,
            trainable_layers=5,
            batch_size=5,
            epochs=20,
            size=256)
