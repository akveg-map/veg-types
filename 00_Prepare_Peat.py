# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Peatland Raw
# Author: Timm Nawrocki
# Last Updated: 2026-07-06
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Prepare Peatland Raw" ensures that the peatland raster lines up with the area raster.
# ---------------------------------------------------------------------------

# Set execution parameters
nodata_value = -128

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
soils_folder = os.path.join(drive, root_folder,
                            'Projects/VegetationEcology/AKSDB/Data',
                            'Data_Output/rasters_final/version_20260415')
ancillary_folder = os.path.join(project_folder, 'Data_Input/ancillary_data/processed')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
peat_input = os.path.join(soils_folder, 'Peat_Probability_Alaska_rf11.tif')

# Define output files
peat_output = os.path.join(ancillary_folder, 'peat_dst_10m_3338.tif')

#### PROCESS PEAT PROBABILITY RASTER
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
    srcNodata=255,
    dstNodata=nodata_value,
    outputType=gdal.GDT_Int8,
    creationOptions=[
        'COMPRESS=DEFLATE',
        'PREDICTOR=STANDARD',
        'BLOCKSIZE=512',
        'NUM_THREADS=ALL_CPUS',
        'BIGTIFF=YES',
        'RESAMPLING=BILINEAR',
        'OVERVIEW_RESAMPLING=AVERAGE'
    ]
)

# Warp raster directly to cloud-optimized geotiff
print('Warping to cloud-optimized raster using GDAL...')
start_time = time.time()
gdal.Warp(peat_output, peat_input, options=warp_options)
end_timing(start_time)
