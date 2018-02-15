# AP Latam

This repository contains the source code for the website of AP Latam.
Visit the website at http://dymaxionlabs.com/ap-latam/

## Install

To build and deploy you need to have Node and npm installed.  After cloning the
repo, run `yarn` to install all dependencies.

You have to create a `.env.development` and `.env.production` with the variable
`MapboxAccessToken` defined in both files.

For updating Mapbox dataset, you also will need to have installed:
* [tippecanoe](https://github.com/mapbox/tippecanoe/)
* [mapbox-cli-py](https://github.com/mapbox/mapbox-cli-py)

## Develop

Simply run `npm start` to start the development server. For a production build,
run `npm run build`.

### Update datasets

The map view uses a Mapbox style to show datasets via vector tiles. If you add
a new city, or update datasets, you should update the Mapbox dataset.

```
geojson-merge data/**/latest.geojson > /tmp/ap-latem.geojson
tippecanoe -o /tmp/ap-latam.mbtiles -zg --drop-densest-as-needed /tmp/ap-latam.geojson
mapbox upload $USER.ap-latam /tmp/ap-latam.mbtiles --access-token $TOKEN
```

where `$USER` is the Mapbox user, and `$TOKEN` is an access token with the
appropriate permission for uploading datasets.

## License

All files contained in the `data` directory are made available under the Public
Domain Dedication and License version v1.0 whose full text can be found at
http://opendatacommons.org/licenses/pddl/

The web site source code is released under a BSD-2 license.  Refer to
[LICENSE.md](LICENSE.md) for more information.
