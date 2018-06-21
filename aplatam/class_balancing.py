import logging
import random
import warnings

_logger = logging.getLogger(__name__)


def split_dataset(true_samples,
                  false_samples,
                  test_size=0.25,
                  balancing_multiplier=1):
    """
    Split a list of samples into training and test datasets

    Arguments:
        true_samples {list(obj)} -- list of true samples
        false_samples {list(obj)} -- list of false samples
        test_size {float} -- proportion of test set from total of true samples
        balancing_multiplier {float} -- proportion of false samples w.r.t
            true samples (e.g. 1.0 = 50% true 50% false)

    """
    assert test_size >= 0.0 and test_size <= 1.0, (
        'test_size should be between 0.0 and 1.0')
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

    # Split to build sets
    t_test, t_train = true_samples[:n_test_t], true_samples[n_test_t:]
    f_test, f_train = false_samples[:n_test_f], false_samples[n_test_f:]

    _logger.info('t_train=%d, t_test=%d', len(t_train), len(t_test))
    _logger.info('f_train=%d, f_test=%d', len(f_train), len(f_test))

    return ((t_train, f_train), (t_test, f_test))
