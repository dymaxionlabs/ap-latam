import glob
import json
import os
import tempfile

from aplatam import __version__
from aplatam.build_trainset import CnnTrainsetBuilder


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
        assert t_jpg
        assert f_jpg
