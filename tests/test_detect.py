from mock import patch
from aplatam.detect import *
from shapely.geometry.multipolygon import MultiPolygon


def test_load_raster_contour_polygon():
    contour_path = 'tests/fixtures/settlements.geojson'
    shape, crs = load_raster_contour_polygon('tests/fixtures/settlements.geojson')
    assert isinstance(shape, MultiPolygon)
    assert crs, dict(init='epsg:4326')


def test_calculate_percentiles():
    raster = 'tests/fixtures/sen2_20161215_clipped.tif'
    low, high = calculate_percentiles(raster, block_size=1, lower_cut=2, upper_cut=98)
    assert round(low) == 0
    assert round(high) == 3404
