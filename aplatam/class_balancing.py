import os
import random
import shutil

_logger = logging.getLogger(__name__)


def split_dataset(files,
                  output_dir,
                  test_size=0.25,
                  validation_size=0.25,
                  aug=1):
    """
    Split a list of files into training, validation and test datasets

    Arguments:
        files {list(string)} -- list of file paths
        output_dir {string} -- output directory name
        test_size {float} -- proportion of test set from total of true samples
        validation_size {float} -- proportion of validation set from total of
            true samples.
        aug {float} -- proportion of false samples w.r.t true samples (e.g.
            1.0 = 50% true 50% false)

    """
    true_files, false_files = files
    n_total = len(true_files)
    n_test = round(n_total * test_size)
    n_validation = round(n_total * validation_size)

    random.shuffle(true_files)
    random.shuffle(false_files)

    t_test, t_train = true_files[:n_test], true_files[n_test:]
    f_test, f_train = false_files[:n_test], false_files[n_test:]
    _logger.info('t_train=%d, t_test=%d, f_train=%d, f_test=%d', len(t_train),
                 len(t_test), len(f_train), len(f_test))

    move_files(t_train, os.path.join(output_dir, 'train', 't'))
    move_files(f_train, os.path.join(output_dir, 'train', 'f'))
    move_files(t_test, os.path.join(output_dir, 'test', 't'))
    move_files(f_test, os.path.join(output_dir, 'test', 'f'))


def move_files(files, dst_dir):
    """
    Move all files to a destination directory, creating them if needed

    Arguments:
        files {list(string)} -- list of file paths
        dst_dir {string} -- destination directory name

    """
    os.makedirs(dst_dir, exist_ok=True)
    for src in files:
        fname = os.path.basename(src)
        dst = os.path.join(dst_dir, fname)
        shutil.copyfile(src, dst)
