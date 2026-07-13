# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert polygonal complex range to raster
# Author: Timm Nawrocki
# Last Updated: 2026-07-12
# Usage: Must be executed in a Python 3.11+ installation with GDAL 3.9+.
# Description: 'Convert polygonal complex range to raster' creates a raster designating the area in which polygonal complexes will be identified.
# ---------------------------------------------------------------------------

# Set execution parameters
nodata_value = -128

# Import packages
import os
import time
from osgeo import gdal
from akutils import *

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
range_folder = os.path.join(drive, root_folder, 'Data_Input/range_data/processed')
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
intermediate_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/intermediate')
ancillary_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/processed')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
range_input = os.path.join(range_folder, 'range_polygonalcomplex_3338.shp')

# Define intermediate files
range_intermediate = os.path.join(intermediate_folder, 'range_polygonalcomplex_3338.tif')

# Define output files
range_output = os.path.join(ancillary_folder, 'range_polygonalcomplex_10m_3338.tif')

#### CONVERT RANGE TO RASTER
####____________________________________________________

# Read area bounds
area_bounds = raster_bounds(area_input)

# Set output raster options
range_options = gdal.RasterizeOptions(
    format='GTiff',
    outputType=gdal.GDT_Int8,
    creationOptions=[
        'COMPRESS=LZW',
        'TILED=YES',
        'BIGTIFF=YES',
        'NUM_THREADS=ALL_CPUS'
    ],
    outputBounds=area_bounds,
    xRes=10,
    yRes=10,
    initValues=[0],
    burnValues=[1],
    noData= nodata_value,
    allTouched=False
)

# Convert the range to raster
if not os.path.exists(range_intermediate):
    print('Converting range to raster...')
    start_time = time.time()
    gdal.Rasterize(range_intermediate, range_input, options=range_options)
    end_timing(start_time)

# Set translation options for GDAL COG driver
cog_options = gdal.TranslateOptions(
    format='COG',
    creationOptions=[
        'COMPRESS=DEFLATE',
        'PREDICTOR=NO',
        'BLOCKSIZE=512',
        'NUM_THREADS=ALL_CPUS',
        'BIGTIFF=YES',
        'RESAMPLING=NEAREST',
        'OVERVIEW_RESAMPLING=NEAREST'
    ]
)

# Translate raster to cloud-optimized geotiff
print('Converting raster to cloud-optimized geotiff...')
start_time = time.time()
gdal.Translate(range_output, range_intermediate, options=cog_options)
end_timing(start_time)
