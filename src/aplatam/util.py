# -*- coding: utf-8 -*-
from glob import iglob

def all_raster_files(dirname, ext='.tif'):
    """Generate any raster files inside +dirname+, recursively"""
    pattern = '**/*.{ext}'.format(ext)
    return iglob(os.path.join(dirname, pattern), recursive=True)
