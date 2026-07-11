# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare alkaline data
# Author: Timm Nawrocki
# Last Updated: 2026-07-09
# Usage: Execute in Python 3.9+.
# Description: "Prepare alkaline data" extracts alkaline soil surface polygons from the Alaska SSURGO database and converts them to raster.
# ---------------------------------------------------------------------------

# Set nodata value
nodata_value = -128

# Import packages
import os
import time
import numpy as np
import pandas as pd
from osgeo import gdal
import geopandas as gpd
import rasterio
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
ancillary_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data/processed')
input_folder = os.path.join(drive, root_folder, 'Data_Input/physiography_alkaline')
output_folder = os.path.join(drive, root_folder, 'Data_Output/physiography_data/alkaline_20260709')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
ssurgo_geodatabase = os.path.join(input_folder, 'unprocessed/gSSURGO_AK.gdb')
custom_input = os.path.join(input_folder, 'unprocessed/alkaline_custom_3338.shp')

# Define intermediate files
filter_intermediate = os.path.join(input_folder, 'unprocessed/ssurgo_alkaline.gpkg')
ssurgo_intermediate = os.path.join(input_folder, 'processed/ssurgo_alkaline_10m_3338.tif')
custom_intermediate = os.path.join(input_folder, 'processed/custom_alkaline_10m_3338.tif')
merged_intermediate = os.path.join(output_folder, 'alkaline_merged_10m_3338.tif')

# Define output file
alkaline_output = os.path.join(output_folder, 'alkaline_10m_3338.tif')

#### QUERY ALKALINE MAP UNITS FROM SSURGO
####____________________________________________________

# Read area bounds and exact pixel dimensions to guarantee a perfect match
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Create alkaline geopackage if it does not already exist
if not os.path.exists(filter_intermediate):
    print('Querying alkaline map units from SSURGO...')
    start_time = time.time()

    # Load data from SSURGO
    chorizon_data = gpd.read_file(ssurgo_geodatabase, layer='chorizon', ignore_geometry=True)
    component_data = gpd.read_file(ssurgo_geodatabase, layer='component', ignore_geometry=True)
    mapunit_data = gpd.read_file(ssurgo_geodatabase, layer='MUPOLYGON')

    # Filter where the top 20 cm are alkaline (>= 7.6 pH)
    chorizon_data['ph1to1h2o_r'] = pd.to_numeric(chorizon_data['ph1to1h2o_r'], errors='coerce')
    alkaline_horizons = chorizon_data[
        (chorizon_data['ph1to1h2o_r'] >= 7.6) &
        (chorizon_data['hzdept_r'] <= 20)
    ]

    # Filter for major components only to avoid minor inclusions
    major_components = component_data[component_data['majcompflag'] == 'Yes']

    # Join the filtered horizons to the major components
    alkaline_components = major_components.merge(
        alkaline_horizons,
        on='cokey',
        how='inner'
    )

    # Extract the Map Unit Keys (mukey) that meet all criteria
    target_mukeys = alkaline_components['mukey'].unique()

    # Calculate the maximum pH for each qualifying map unit
    max_ph_summary = alkaline_components.groupby('mukey')['ph1to1h2o_r'].max().reset_index()
    max_ph_summary.rename(columns={'mukey': 'MUKEY', 'ph1to1h2o_r': 'max_pH'}, inplace=True)

    # Filter the map units to target mukeys
    alkaline_polygons = mapunit_data[mapunit_data['MUKEY'].isin(target_mukeys)]

    # Join the max_pH summary back to the spatial polygons
    alkaline_polygons = alkaline_polygons.merge(max_ph_summary, on='MUKEY', how='left')

    # Export results
    alkaline_polygons.to_file(filter_intermediate, driver='GPKG')
    end_timing(start_time)

#### CONVERT SSURGO VECTOR TO RASTER
####____________________________________________________

# Convert SSURGO alkaline vector to raster if it does not already exist
if not os.path.exists(ssurgo_intermediate):
    print('Converting SSURGO alkaline vector to raster...')
    start_time = time.time()

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
        width=target_width,
        height=target_height,
        initValues=[0],
        burnValues=[1],
        noData=nodata_value,
        allTouched=False
    )

    # Convert the override to raster
    gdal.Rasterize(ssurgo_intermediate, filter_intermediate, options=range_options)
    end_timing(start_time)

#### CONVERT CUSTOM VECTOR TO RASTER
####____________________________________________________

# Convert custom alkaline vector to raster if it does not already exist
if not os.path.exists(custom_intermediate):
    print('Converting custom alkaline vector to raster...')
    start_time = time.time()

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
        width=target_width,
        height=target_height,
        initValues=[0],
        burnValues=[1],
        noData=nodata_value,
        allTouched=False
    )

    # Convert the override to raster
    gdal.Rasterize(custom_intermediate, custom_input, options=range_options)
    end_timing(start_time)

#### MERGE ALKALINE ZONES
####____________________________________________________

# Read raster data
area_raster = rasterio.open(area_input)
custom_raster = rasterio.open(custom_intermediate)

# Prepare output profile
output_profile = area_raster.profile.copy()
output_profile.update({
    'height': area_raster.height,
    'width': area_raster.width,
    'transform': area_raster.transform,
    'crs': area_raster.crs,
    'nodata': nodata_value,
    'dtype': 'int8',
    'compress': 'lzw',
    'bigtiff': 'YES'
})

# Extract raster to area
print('Merging alkaline zones...')
start_time = time.time()
with rasterio.open(merged_intermediate, 'w', **output_profile) as dst:
    # Find number of raster blocks
    window_list = []
    for block_index, window in dst.block_windows(1):
        window_list.append(window)
    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in dst.block_windows(1):
        # Load area block
        area_block = area_raster.read(1, window=window, masked=False)

        # Compute bounds of the current output window
        window_bounds = rasterio.windows.bounds(window, area_raster.transform)

        # Load raster blocks
        custom_block = read_raster_block(custom_raster, window_bounds)

        # Perform merge (SSURGO is omitted in this version)
        raster_block = np.where(custom_block == 1, 1, 0)

        # Enforce study area boundary
        raster_block = np.where(area_block == 1, raster_block, nodata_value)

        # Write results
        dst.write(raster_block.astype('int8'), 1, window=window)

        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
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
print(f'Creating cloud-optimized raster using GDAL...')
start_time = time.time()
gdal.Translate(alkaline_output, merged_intermediate, options=cog_options)
end_timing(start_time)
