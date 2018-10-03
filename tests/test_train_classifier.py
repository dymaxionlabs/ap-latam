from mock import patch
from aplatam.train_classifier import *


DATASET_DIR = '/tmp/dataset'
TRAIN_TRUE_FILES = ['{}.jpg'.format(str(n).zfill(3)) for n in range(5)]
TRAIN_FALSE_FILES = ['{}.jpg'.format(str(n).zfill(3)) for n in range(5, 10)]
VALIDATION_FILES = ['{}.jpg'.format(str(n).zfill(3)) for n in range(10, 15)]


@patch('aplatam.train_classifier.glob', return_value=TRAIN_TRUE_FILES)
def test_find_true_samples(glob_mock):
    dirname = os.path.join(DATASET_DIR, 'train')
    true_samples = find_true_samples(dirname)
    glob_mock.assert_called_once_with(os.path.join(DATASET_DIR, 'train', 't', '*.jpg'))
    assert true_samples == TRAIN_TRUE_FILES


@patch('aplatam.train_classifier.glob', return_value=TRAIN_FALSE_FILES)
def test_find_false_samples(glob_mock):
    dirname = os.path.join(DATASET_DIR, 'train')
    false_samples = find_false_samples(dirname)
    glob_mock.assert_called_once_with(os.path.join(DATASET_DIR, 'train', 'f', '*.jpg'))
    assert false_samples == TRAIN_FALSE_FILES


@patch('aplatam.train_classifier.glob', return_value=VALIDATION_FILES)
def test_find_false_samples(glob_mock):
    dirname = os.path.join(DATASET_DIR, 'val')
    all_samples = find_all_samples(dirname)
    glob_mock.assert_called_once_with(os.path.join(DATASET_DIR, 'val', '**', '*.jpg'))
    assert all_samples == VALIDATION_FILES


@patch('aplatam.train_classifier.find_true_samples', return_value=TRAIN_TRUE_FILES)
@patch('aplatam.train_classifier.find_false_samples', return_value=TRAIN_FALSE_FILES)
@patch('aplatam.train_classifier.find_all_samples', return_value=VALIDATION_FILES)
def test_find_dataset_files(find_all_mock, find_false_mock, find_true_mock):
    files_dict = find_dataset_files(DATASET_DIR)
    assert isinstance(files_dict, dict)
    assert files_dict['true_train'] == TRAIN_TRUE_FILES
    assert files_dict['false_train'] == TRAIN_FALSE_FILES
    assert files_dict['validation'] == VALIDATION_FILES


DATASET_DICT = dict(true_train=TRAIN_TRUE_FILES,
                    false_train=TRAIN_FALSE_FILES,
                    validation=VALIDATION_FILES)


@patch('aplatam.train_classifier.save_model')
@patch('aplatam.train_classifier.train_model')
@patch('aplatam.train_classifier.train_data_generator')
@patch('aplatam.train_classifier.validation_data_generator')
@patch('aplatam.train_classifier.find_dataset_files', return_value=DATASET_DICT)
def test_train(find_dataset_files_mock, validation_data_gen_mock, train_data_gen_mock, train_model_mock, save_model_mock):
    model_file = '/tmp/foo.h5'
    train(model_file, DATASET_DIR,
        trainable_layers=30,
        batch_size=20,
        epochs=10,
        size=256)
