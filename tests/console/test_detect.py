import os
import tempfile

from mock import patch

import aplatam.console.detect as ap_detect


@patch('aplatam.console.detect.detect')
def test_run_script_default_arguments(train_mock_func):
    with tempfile.TemporaryDirectory(prefix='ap_detect') as tmpdir:
        output_geojson = os.path.join(tmpdir, 'detection.geojson')

        ap_detect.main(
            ['tests/fixtures/model.h5', 'tests/fixtures/', output_geojson])

        train_mock_func.assert_called_once_with(
            input_dir='tests/fixtures/',
            mean_threshold=0.3,
            model_file='tests/fixtures/model.h5',
            neighbours=3,
            output=output_geojson,
            rasters_contour=None,
            rescale_intensity=True,
            lower_cut=2,
            upper_cut=98,
            step_size=None,
            threshold=0.3)
