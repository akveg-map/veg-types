# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Dynamic World
# Author: Timm Nawrocki
# Last Updated: 2026-07-08
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Prepare Dynamic World" prepares the Dynamic World percentages as individual cloud-optimized geotiffs.
# ---------------------------------------------------------------------------

# Set nodata value
nodata_value = -128

# Import packages
import os
import glob
import time
from osgeo import gdal
import rasterio
from google.cloud import storage
from akutils import *

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Initialize GCS Client
storage_client = storage.Client()

# Define GCS base name
gcs_base = 'gs://akveg-data/veg_type_v2p1'
destination = 'ancillary_data'

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define data folder
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
dw_folder = os.path.join(drive, root_folder, 'Data_Input/dw')
output_folder = os.path.join(drive, root_folder, 'Data_Output/rasters_final')

# Define input data
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
input_files = glob.glob(f'{dw_folder}/*.tif')

# Define dictionary of band values
band_dictionary = {'water': 0,
                   'flooded': 3,
                   'barren': 7,
                   'snow': 8}

#### MERGE RASTERS
####____________________________________________________

# Read area bounds and exact pixel dimensions to guarantee a perfect match
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Loop through each band to process output raster
for band, value in band_dictionary.items():
    # Define final GCS path for the output
    output_name = f'dw_{band}_10m_3338.tif'
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    vrt_intermediate = os.path.join(output_folder, f'dw_{band}_10m_3338.vrt')

    # Define output data
    dw_output = os.path.join(output_folder, output_name)

    # Process output raster if it does not already exist
    if not os.path.exists(dw_output):
        print(f'Processing raster conversion for {band}...')
        start_time = time.time()

        # Merge tiles
        print(f'\tMerging {len(input_files)} tiles...')
        # Merge raster tiles
        gdal.BuildVRT(vrt_intermediate,
                      input_files,
                      bandList=[value + 1],
                      outputSRS='EPSG:3338',
                      xRes=10,
                      yRes=10,
                      srcNodata=255,
                      VRTNodata=255,
                      outputBounds=area_bounds)

        # Set Warp options for spatial snapping, data conversion, and COG creation
        warp_options = gdal.WarpOptions(
            format='COG',
            outputBounds=area_bounds,
            width=target_width,
            height=target_height,
            srcSRS='EPSG:3338',
            dstSRS='EPSG:3338',
            srcNodata=255,
            dstNodata=nodata_value,
            outputType=gdal.GDT_Int8,
            resampleAlg=gdal.GRA_Bilinear,
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
        print('\tWarping raster...')
        gdal.Warp(dw_output, vrt_intermediate, options=warp_options)
        end_timing(start_time)

    else:
        print(f'Raster for {band} already exists.')
        print('----------')

    # Upload post-processed raster to GCS
    print('Uploading raster to Google Cloud...')
    upload_to_gcs(dw_output, final_gcs_output, storage_client)

    # Create finished file
    print('Writing final output message...')
    finished_output = os.path.join(output_folder, f'{band}_finished.txt')
    with open(finished_output, "w") as file:
        file.write("finished")
    final_gcs_output = f'{gcs_base}/{destination}/{band}_finished.txt'
    upload_to_gcs(finished_output, final_gcs_output, storage_client)
    print('Processing finished.')
    print('----------')
