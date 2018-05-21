import fiona
import rasterio
import os
import numpy as np
from shapely.geometry import shape, box
from aplatam.util import reproject_shape, create_index, sliding_windows, window_to_bounds
from aplatam.util import get_raster_crs
from skimage import exposure
from skimage.io import imsave


def read_shapes(vector):
    with fiona.open(vector) as data:
        src = data.crs
    return [(shape(feature["geometria"])) for feature in data], src


def reproject_shapes(shapes, vector_crs, raster_crs):
    return [reproject_shape(s, vector_crs, raster_crs) for s in shapes]


def aply_buffer(buffer_size, shapes):
    return [C.buffer(buffer_size) for C in shapes]


def build_trainset(rasters, vector, config, temp_dir):
    intensity_percentiles = config["lower_cut"], config["upper_cut"]
    for varRaster in rasters:
        shapes, src = read_shapes(vector)
        raster_crs = get_raster_crs(varRaster)
        shapes = reproject_shapes(shapes, src, raster_crs)
        if config["buffer_size"] != 0:
            aply_buffer(config["buffer_size"], shapes)
        write_window_tiles(shapes, temp_dir, varRaster, config["size"],
                           config["sep_size"], intensity_percentiles)


def write_window_tiles(shapes,
                       output_dir,
                       tile_fname,
                       size=64,
                       step_size=16,
                       rescale_intensity=True,
                       intensity_percentiles=(2, 98)):
    "Extract windows of +size+ by sliding it +step_size+ on a raster, and write files"

    # Create R-Tree index with shapes to speed up intersection operation
    index = create_index(shapes)

    path = os.path.join(output_dir, 'all')
    #temp_windows = []
    with rasterio.open(tile_fname) as src:
        for window in sliding_windows(size, step_size, src.shape):
            # Build shape from window bounds
            #bounds = rio.transform.xy(src.transform, window[0], window[1], offset='ul')
            #window_box = box(bounds[0][0], bounds[1][0], bounds[0][1], bounds[1][1])
            window_box = box(*window_to_bounds(window, src.transform))

            # Get shapes whose bounding boxes intersect with window box
            matching_shapes = [
                shapes[s_id] for s_id in index.intersection(window_box.bounds)
            ]
            try:
                if matching_shapes and any(
                        s.intersection(window_box).area > 0.0
                        for s in matching_shapes):
                    img_class = 't'
                #temp_windows.append(window_box)
                else:
                    img_class = 'f'

            # Prepare img filename
                fname, _ = os.path.splitext(os.path.basename(tile_fname))
                win_fname = '{}__{}_{}.jpg'.format(fname, window[0][0],
                                                   window[1][0])

                # Create class directory
                img_dir = os.path.join(path, img_class)
                os.makedirs(img_dir, exist_ok=True)

                # Extract image from raster and preprocess
                rgb = np.dstack(
                    [src.read(b, window=window) for b in range(1, 4)])

                if rescale_intensity:
                    low, high = np.percentile(rgb, intensity_percentiles)
                    rgb = exposure.rescale_intensity(rgb, in_range=(low, high))

            # Save .jpg image from raster
                img_path = os.path.join(img_dir, win_fname)
                imsave(img_path, rgb)
            except:
                pass
    # FIXME
    #fname, ext = os.path.splitext(os.path.basename(tile_fname))
    #write_geojson(temp_windows, '/tmp/window_{}.geojson'.format(fname))
