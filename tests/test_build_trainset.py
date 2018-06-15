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

    with tempfile.TemporaryDirectory() as tmpdir:
        builder.build(tmpdir)
        assert_trainset(tmpdir, builder)


def test_cnn_trainset_builder_with_buffer_size():
    builder = CnnTrainsetBuilder(
        ['tests/fixtures/sen2_20161215_clipped.tif'],
        'tests/fixtures/settlements.geojson',
        size=128,
        step_size=64,
        buffer_size=5)

    with tempfile.TemporaryDirectory(
            prefix='aplatam_test_build_trainset') as tmpdir:
        builder.build(tmpdir)
        assert_trainset(tmpdir, builder)


def test_cnn_trainset_builder_with_no_rescale_intensity():
    builder = CnnTrainsetBuilder(
        ['tests/fixtures/sen2_20161215_clipped.tif'],
        'tests/fixtures/settlements.geojson',
        size=128,
        step_size=64,
        rescale_intensity=False)

    with tempfile.TemporaryDirectory(
            prefix='aplatam_test_build_trainset') as tmpdir:
        builder.build(tmpdir)
        assert_trainset(tmpdir, builder, empty_dirs=True)


def assert_trainset(tmpdir, builder, empty_dirs=False):
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
            assert metadata[name_argument] == getattr(builder, name_argument)

    for dir_a, dir_b in zip(('train', 'validation', 'test'), ('t', 'f')):
        dirname = os.path.join(tmpdir, dir_a, dir_b)
        assert os.path.exists(dirname), '{} exists'.format(dirname)
        if not empty_dirs:
            assert glob.glob(os.path.join(
                dirname, '*.jpg')), '{} contains at least one jpg file'
