import logging
import os
import random
import shutil
import warnings

_logger = logging.getLogger(__name__)


def split_dataset(files,
                  output_dir,
                  test_size=0.25,
                  validation_size=0.25,
                  balancing_multiplier=1):
    """
    Split a list of files into training, validation and test datasets

    Arguments:
        files {list(string)} -- list of file paths
        output_dir {string} -- output directory name
        test_size {float} -- proportion of test set from total of true samples
        validation_size {float} -- proportion of validation set from total of
            true samples.
        balancing_multiplier {float} -- proportion of false samples w.r.t
            true samples (e.g. 1.0 = 50% true 50% false)

    """
    assert test_size >= 0.0 and test_size <= 1.0, (
        'test_size should be between 0.0 and 1.0')
    assert validation_size >= 0.0 and validation_size <= 1.0, (
        'validation_size should be between 0.0 and 1.0')
    assert balancing_multiplier >= 1.0, 'aug should be greater or equal to 1'

    # First shuffle dataset
    true_files, false_files = files

    if len(true_files) < len(false_files):
        warnings.warn('There are less true samples than false samples')

    random.shuffle(true_files)
    random.shuffle(false_files)

    # Calculate test size based on total of true samples
    n_total = min(len(true_files), len(false_files))
    n_test_t = round(n_total * test_size)
    n_test_f = round(n_test_t * balancing_multiplier)

    # Split to build test set
    t_test, t_rest = true_files[:n_test_t], true_files[n_test_t:]
    f_test, f_rest = false_files[:n_test_f], false_files[n_test_f:]

    # Calculate validation size
    n_validation_t = round(n_total * validation_size)
    n_validation_f = round(n_validation_t * balancing_multiplier)

    # Split again to build validation set
    t_validation, t_train = t_rest[:n_validation_t], t_rest[n_validation_t:]
    f_validation, f_train = f_rest[:n_validation_f], f_rest[n_validation_f:]

    _logger.info('t_train=%d, t_validation=%d, t_test=%d', len(t_train),
                 len(t_validation), len(t_test))
    _logger.info('f_train=%d, f_validation=%d, f_test=%d', len(f_train),
                 len(f_validation), len(f_test))

    copy_files(t_train, os.path.join(output_dir, 'train', 't'))
    copy_files(f_train, os.path.join(output_dir, 'train', 'f'))
    copy_files(t_test, os.path.join(output_dir, 'validation', 't'))
    copy_files(f_test, os.path.join(output_dir, 'validation', 'f'))
    copy_files(t_test, os.path.join(output_dir, 'test', 't'))
    copy_files(f_test, os.path.join(output_dir, 'test', 'f'))


def copy_files(files, dst_dir):
    """
    Copy all files to a destination directory, creating them if needed

    Arguments:
        files {list(string)} -- list of file paths
        dst_dir {string} -- destination directory name

    """
    os.makedirs(dst_dir, exist_ok=True)
    for src in files:
        fname = os.path.basename(src)
        dst = os.path.join(dst_dir, fname)
        shutil.copyfile(src, dst)
