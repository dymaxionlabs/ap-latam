# AP Latam

This is the main repository of AP Latam project.

For more information on the website frontend, see
[web/README.md](web/README.md).

## Dependencies

## Development

You will need to have installed GDAL and Proj4. On Debian-based distros run:

```
sudo apt install libproj-dev gdal-bin build-essential libgdal-dev libspatialindex-dev
```

Then, create a virtual environment for Python 3 and activate it:

```
virtualenv -p python3 env/
source env/bin/activate
```

Install dependencies with pip:

```
pip install -r requirements.txt
```

Finally install `aplatam` package:

```
pip install -e .
```

## License

Source code is released under a BSD-2 license.  Please refer to
[LICENSE.md](LICENSE.md) for more information.
