# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare fire year
# Author: Timm Nawrocki
# Last Updated: 2026-07-09
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Prepare fire year" ensures that the most recent fire year raster lines up with the area raster.
# ---------------------------------------------------------------------------

# Set execution parameters
nodata_value = -32768

# Import packages
import os
import time
import rasterio
from osgeo import gdal
from akutils import *

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
region_folder = os.path.join(project_folder, 'Data_Input/region_data')
ancillary_folder = os.path.join(project_folder, 'Data_Input/ancillary_data/processed')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
fire_input = os.path.join(ancillary_folder, 'AlaskaYukon_FireYear_10m_3338.tif')

# Define output files
fire_output = os.path.join(ancillary_folder, 'fire_year_10m_3338.tif')

#### PROCESS FIRE YEAR RASTER
####____________________________________________________

# Read area bounds
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Set Warp options for spatial snapping, data conversion, and COG creation
warp_options = gdal.WarpOptions(
    format='COG',
    outputBounds=area_bounds,
    width=target_width,
    height=target_height,
    srcNodata=nodata_value,
    dstNodata=nodata_value,
    outputType=gdal.GDT_Int16,
    resampleAlg=gdal.GRA_NearestNeighbour,
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

# Warp raster directly to cloud-optimized geotiff
print('Warping to cloud-optimized raster using GDAL...')
start_time = time.time()
gdal.Warp(fire_output, fire_input, options=warp_options)
end_timing(start_time)
