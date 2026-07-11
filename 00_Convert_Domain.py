# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert vector domain to raster
# Author: Timm Nawrocki
# Last Updated: 2026-06-26
# Usage: Must be executed in a Python 3.11+ installation with GDAL 3.9+.
# Description: 'Convert vector domain to raster' creates a raster map domain from a vector map domain.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
import math
import geopandas as gpd
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

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
domain_input = os.path.join(region_folder, 'AlaskaYukon_CategoricalDomain_v2p1_3338.shp')

# Define intermediate files
domain_intermediate = os.path.join(region_folder, 'AlaskaYukon_Intermediate_v2p1_10m_3338.tif')

# Define output files
domain_output = os.path.join(region_folder, 'AlaskaYukon_CategoricalDomain_v2p1_10m_3338.tif')

#### CALCULATE ALIGNED BOUNDS
####____________________________________________________

# Get geotransform from reference raster (area_input)
area_raster = gdal.Open(area_input)
area_transform = area_raster.GetGeoTransform()
ref_x_origin = area_transform[0]
pixel_width = area_transform[1]
ref_y_origin = area_transform[3]
pixel_height = area_transform[5] 
area_raster = None

# Get bounding box of vector domain
vector_data = gpd.read_file(domain_input)
vec_min_x, vec_min_y, vec_max_x, vec_max_y = vector_data.total_bounds

# Snap vector horizontal bounds to reference raster grid
snap_min_x = ref_x_origin + math.floor((vec_min_x - ref_x_origin) / pixel_width) * pixel_width
snap_max_x = ref_x_origin + math.ceil((vec_max_x - ref_x_origin) / pixel_width) * pixel_width

# Snap vector vertical bounds to reference raster grid
snap_min_y = ref_y_origin + math.ceil((vec_min_y - ref_y_origin) / pixel_height) * pixel_height
snap_max_y = ref_y_origin + math.floor((vec_max_y - ref_y_origin) / pixel_height) * pixel_height

# Format for GDAL options
snapped_bounds = [snap_min_x, snap_min_y, snap_max_x, snap_max_y]

#### CONVERT DOMAIN TO RASTER
####____________________________________________________

# Set output raster options
domain_options = gdal.RasterizeOptions(
    format='GTiff',
    outputType=gdal.GDT_Int8,
    creationOptions=[
        'COMPRESS=LZW',
        'TILED=YES',
        'BIGTIFF=YES',
        'NUM_THREADS=ALL_CPUS'
    ],
    outputBounds=snapped_bounds,
    xRes=10,
    yRes=10,
    burnValues=[1],
    noData=-128,
    allTouched=False
)

# Convert the domain to raster
print('Converting domain to raster...')
start_time = time.time()
gdal.Rasterize(domain_intermediate, domain_input, options=domain_options)
end_timing(start_time)

#### PROCESS CLOUD-OPTIMIZED GEOTIFFS
####____________________________________________________

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
print('Creating cloud-optimized raster using GDAL...')
start_time = time.time()
gdal.Translate(domain_output, domain_intermediate, options=cog_options)
end_timing(start_time)

# Clean up intermediate file
if os.path.exists(domain_intermediate):
    os.remove(domain_intermediate)
