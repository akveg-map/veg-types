# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare glacier correction
# Author: Timm Nawrocki
# Last Updated: 2026-08-04
# Usage: Execute in Python 3.9+.
# Description: "Prepare glacier correction" converts glacier polygons to raster.
# ---------------------------------------------------------------------------

# Set nodata value
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
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
input_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/corrections')
intermediate_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/intermediate')
output_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/processed')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
glacier_input = os.path.join(input_folder, 'AKVEG_Glacier_Override_3338.shp')

# Define intermediate files
glacier_intermediate = os.path.join(intermediate_folder, 'glacier_correction_int_10m_3338.tif')

# Define output file
glacier_output = os.path.join(output_folder, 'glacier_correction_10m_3338.tif')

#### CONVERT GLACIER TO RASTER
####____________________________________________________

# Read area bounds
area_bounds = raster_bounds(area_input)

# Set output raster options
glacier_options = gdal.RasterizeOptions(
    format='GTiff',
    outputType=gdal.GDT_Int8,
    creationOptions=[
        'COMPRESS=LZW',
        'TILED=YES',
        'BIGTIFF=YES',
        'NUM_THREADS=ALL_CPUS'
    ],
    outputBounds=area_bounds,
    outputSRS='EPSG:3338',
    xRes=10,
    yRes=10,
    initValues=[0],
    burnValues=[1],
    noData= nodata_value,
    allTouched=False
)

# Convert the glacier to raster
if not os.path.exists(glacier_intermediate):
    print('Converting glacier to raster...')
    start_time = time.time()
    gdal.Rasterize(glacier_intermediate, glacier_input, options=glacier_options)
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
gdal.Translate(glacier_output, glacier_intermediate, options=cog_options)
end_timing(start_time)
