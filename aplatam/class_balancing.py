import logging
import os
import random
import shutil
import warnings

_logger = logging.getLogger(__name__)


def split_dataset(true_samples,
                  false_samples,
                  test_size=0.25,
                  validation_size=0.25,
                  balancing_multiplier=1):
    """
    Split a list of samples into training, validation and test datasets

    Arguments:
        true_samples {list(obj)} -- list of true samples
        false_samples {list(obj)} -- list of false samples
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

    if len(true_samples) >= len(false_samples):
        warnings.warn('There are more true samples than false samples')

    # First shuffle dataset
    random.shuffle(true_samples)
    random.shuffle(false_samples)

    # Calculate test size based on total of true samples
    n_total_true = min(len(true_samples), len(false_samples))
    _logger.info('Total true samples: %d', n_total_true)
    n_total_false = round(n_total_true * balancing_multiplier)
    _logger.info('Total false samples: %d (multiplier %d)', n_total_false,
                 balancing_multiplier)

    true_samples = true_samples[:n_total_true]
    false_samples = false_samples[:n_total_false]

    # Calculate sizes
    n_test_t = round(n_total_true * test_size)
    n_test_f = round(n_total_false * test_size)
    n_validation_t = round(n_total_true * validation_size)
    n_validation_f = round(n_total_false * validation_size)

    # Split to build sets
    t_test, t_validation, t_train = true_samples[:n_test_t], true_samples[
        n_test_t:n_test_t + n_validation_t], true_samples[n_test_t +
                                                          n_validation_t:]
    f_test, f_validation, f_train = false_samples[:n_test_f], false_samples[
        n_test_f:n_test_f + n_validation_f], false_samples[n_test_f +
                                                           n_validation_f:]

    _logger.info('t_train=%d, t_validation=%d, t_test=%d', len(t_train),
                 len(t_validation), len(t_test))
    _logger.info('f_train=%d, f_validation=%d, f_test=%d', len(f_train),
                 len(f_validation), len(f_test))

    return ((t_train, f_train), (t_validation, f_validation), (t_test, f_test))


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
