# -*- coding: utf-8 -*-
from glob import glob
import os
import pdb
def all_raster_files(dirname, ext='.tif'):
    """Generate any raster files inside +dirname+, recursively"""
    pattern = '**/*{ext}'.format(ext=ext)
    return glob(os.path.join(dirname, pattern), recursive=True)
    

