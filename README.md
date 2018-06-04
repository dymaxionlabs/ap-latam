# AP Latam

[![Build Status](https://travis-ci.org/dymaxionlabs/ap-latam.svg?branch=master)](https://travis-ci.org/dymaxionlabs/ap-latam)

This is the main repository of AP Latam project.

For more information on the website frontend, see
[web/README.md](web/README.md).

## Dependencies

* Python 3+
* GDAL
* Proj4
* libspatialindex
* Dependencies for TensorFlow with GPU support

## Development

First you will need to install the following packages.  On Debian-based distros
run:

```
sudo apt install libproj-dev gdal-bin build-essential libgdal-dev libspatialindex-dev
```

This project is being managed by [Poetry](https://github.com/sdispater/poetry).
If you do not have it installed, please refer to [Poetry
instructions](https://github.com/sdispater/poetry#installation).  Make sure to
install Poetry using Python 3, in case you also have Python 2 installed.

Now, clone the repository and run `poetry install`.  This will create a virtual
environment and install all required packages there.

Run `make` to run tests and `make cov` to build a code coverage report. You can
run `make` to do both.

## License

Source code is released under a BSD-2 license.  Please refer to
[LICENSE.md](LICENSE.md) for more information.
