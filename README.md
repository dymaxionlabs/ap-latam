# AP Latam

[![Build Status](https://travis-ci.org/dymaxionlabs/ap-latam.svg?branch=master)](https://travis-ci.org/dymaxionlabs/ap-latam)
[![codecov](https://codecov.io/gh/dymaxionlabs/ap-latam/branch/master/graph/badge.svg)](https://codecov.io/gh/dymaxionlabs/ap-latam)
[![Join the chat at https://gitter.im/dymaxionlabs/ap-latam](https://badges.gitter.im/dymaxionlabs/ap-latam.svg)](https://gitter.im/dymaxionlabs/ap-latam?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

This is the main repository of AP Latam project.

For more information on the website frontend, see the repository at
[https://github.com/dymaxionlabs/ap-latam-web](dymaxionlabs/ap-latam-web).


## Dependencies

* Python 3+
* GDAL
* Proj4
* libspatialindex
* Dependencies for TensorFlow with GPU support


## Install

### Quick install and usage: Docker image

If you have [Docker](https://www.docker.com/community-edition) installed on
your machine, with NVIDIA CUDA installed and configured, you can simply pull
our image and run the scripts for training and detection.

Otherwise, follow the steps in this
[tutorial](https://medium.com/google-cloud/jupyter-tensorflow-nvidia-gpu-docker-google-compute-engine-4a146f085f17)
to install Docker, CUDA and `nvidia-docker`.  This has been tested on an Ubuntu
16.04 LTS instance on Google Cloud Platform.

For all scripts you will need to mount a data volume so that the scripts can
read the input rasters and vector files, and write the resulting vector file.

It is recommended that you first set an environment variable that points to the
data directory in your host machine, like this:

```
export APLATAM_DATA=$HOME/aplatam-data
```

Then, to use any of the scripts, you would have to run them using
`nvidia-docker` and mounting a volume to `$APLATAM_DATA` like this:

```
nvidia-docker run -ti -v $APLATAM_DATA:/data dymaxionlabs/ap-latam SCRIPT_TO_RUN [ARGS...]
```

where `SCRIPT_TO_RUN` is either `ap_prepare`, `ap_train` or `ap_detect` and
`[ARGS...]` the command line arguments of the specified script. You can run
with `--help` to see all available options on each script.

For example, suppose you have the following files inside the `$APLATAM_DATA`
directory:

* Training rasters on `images/`
* A settlements vector file `settlements.geojson`

To prepare a dataset for training you would run:

```
nvidia-docker run -ti -v $APLATAM_DATA:/data dymaxionlabs/ap-latam \
  ap_prepare /data/images /data/settlements.geojson /data/my_dataset
```

When using `[nvidia-]docker run` for the first time, it will pull the image
automatically for you, so it is not neccessary to do `[nvidia-]docker pull`
first.

## Development

First you will need to install the following packages.  On Debian-based distros
run:

```
sudo apt install libproj-dev gdal-bin build-essential libgdal-dev libspatialindex-dev python3-venv virtualenv
```

This project is being managed by [Poetry](https://github.com/sdispater/poetry).
If you do not have it installed, please refer to [Poetry
instructions](https://github.com/sdispater/poetry#installation).  Make sure to
install Poetry using Python 3, in case you also have Python 2 installed.

Now, clone the repository and run `poetry install`.  This will create a virtual
environment and install all required packages there.

Run `make` to run tests and `make cov` to build a code coverage report. You can
run `make` to do both.


## Issue tracker

Please report any bugs and enhancement ideas using the GitHub issue tracker:

  https://github.com/dymaxionlabs/ap-latam/issues

Feel free to also ask questions on our
[Gitter channel](https://gitter.im/dymaxionlabs/ap-latam), or by email.


## Help wanted

Any help in testing, development, documentation and other tasks is highly
appreciated and useful to the project.

For more details, see the file [CONTRIBUTING.md](CONTRIBUTING.md).


## License

Source code is released under a BSD-2 license.  Please refer to
[LICENSE.md](LICENSE.md) for more information.
