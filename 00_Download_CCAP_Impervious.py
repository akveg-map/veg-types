# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Download CCAP impervious data
# Author: Timm Nawrocki
# Last Updated: 2026-07-07
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Download CCAP impervious data" contacts a server to download a series of tiles containing high-resolution impervious surface data.
# ---------------------------------------------------------------------------

# Set nodata value
nodata_value = -128

# Import packages
import os
import glob
import time
import math
import numpy as np
import requests
import geopandas as gpd
from osgeo import gdal
import rasterio
from rasterio.warp import transform_bounds
from google.cloud import storage
from tqdm import tqdm
from akutils import *

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Initialize GCS Client
storage_client = storage.Client()

# Define GCS base name
gcs_base = 'gs://akveg-data/foliar_cover_v2p1'
destination = 'rasters_final'

# Define final GCS path for the output
output_name = f'impervious_ccap_10m_3338.tif'
final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define data folder
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
infra_folder = os.path.join(drive, root_folder, 'Data_Input/infrastructure')
download_folder = os.path.join(infra_folder, 'unprocessed')
resample_folder = os.path.join(infra_folder, 'processed')

# Define input data
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
tile_input = os.path.join(infra_folder, 'tiles/Alaska_Tiles_Regions.shp')

# Define intermediate data
vrt_intermediate = os.path.join(infra_folder, 'impervious_ccap_int_10m_3338.vrt')
merged_intermediate = os.path.join(infra_folder, 'impervious_ccap_int_10m_3338_merged.tif')

# Define output data
imper_output = os.path.join(infra_folder, 'impervious_ccap_10m_3338.tif')

# Define base url
base_url = 'https://ocmgeodatastor1.blob.core.windows.net/ccap/bulk_download/C-CAP_High-Resolution_Data/Initial_C-CAP_High-Resolution_Land_Cover_Layers/Impervious/Alaska'

#### PROCESS DATA DOWNLOADS
####____________________________________________________

# Read area bounds and exact pixel dimensions to guarantee a perfect match
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height
    area_transform = ref.transform
    align_x = area_transform[2]
    align_y = area_transform[5]
    res_x = area_transform[0]
    res_y = abs(area_transform[4])

# Read tile data
tile_data = gpd.read_file(tile_input).sort_values('Tile')

# Download and resample each file if it has not already been downloaded
count = 1
for index, row in tile_data.iterrows():
    # Create download file name
    file_name = f'ak_{row['Region'].lower()}_2020_ccap_v2_hires_impervious_tile{row['Tile']}.tif'
    xml_name = f'{file_name}.aux.xml'

    # Create download url and file path
    download_url = f'{base_url}/{file_name}'
    download_file = os.path.join(download_folder, file_name)
    xml_url = f'{base_url}/{xml_name}'
    xml_file = os.path.join(download_folder, xml_name)

    # Create resample file
    resample_intermediate = os.path.join(resample_folder,
                                         f'impervious_ccap_{row['Tile']:02d}_10m_3338.tif')

    # Download xml file
    if not os.path.exists(xml_file):
        response_xml = requests.get(xml_url, stream=False)
        if response_xml.status_code == 200:
            with open(xml_file, 'wb') as file:
                file.write(response_xml.content)

    # Download file if it does not exist
    download_success = True
    if not os.path.exists(download_file):
        print(f'Downloading file {count} of {len(tile_data)}...')
        try:
            # Initiate download
            start_time = time.time()
            response = requests.get(download_url, stream=True)

            # Force an exception if the file does not exist on the server
            response.raise_for_status()

            # Determine download size
            total_bytes = int(response.headers.get('content-length', 0))
            total_mb = round((total_bytes / (1024 * 1024)), 0)

            # Print download size
            if total_bytes == 0:
                print('\tCould not determine file size.')
            elif total_mb == 0:
                print(f'\tDownload size is {total_bytes} bytes.')
            else:
                print(f'\tDownload size is {total_mb} mb.')

            # Download file
            block_size = 4096
            progress_bar = tqdm(total=total_bytes, unit='iB', unit_scale=True)
            with open(download_file, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            end_timing(start_time)
        except Exception as e:
            download_success = False
            print(f'File {count} of {len(tile_data)} not available for download. Check url.')
            print(f'Error Details: {e}')
            print('----------')
    else:
        print(f'File {count} of {len(tile_data)} already exists.')
        print('----------')

    # Resample raster if the download was successful (or already existed)
    if download_success and not os.path.exists(resample_intermediate):
        print('Resampling raster to 10m grid...')
        start_time = time.time()

        # Read the exact bounds and CRS of the downloaded raster
        with rasterio.open(download_file) as src:
            src_bounds = src.bounds
            source_nodata = src.nodata

        # Manually define the source projection using the provided Albers parameters
        conus_albers_proj = (
            '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23.0 +lon_0=-96.0 '
            '+x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'
        )

        # Transform the bounds from CONUS Albers to EPSG:3338 before snapping
        dst_left, dst_bottom, dst_right, dst_top = transform_bounds(
            conus_albers_proj,
            'EPSG:3338',
            src_bounds.left,
            src_bounds.bottom,
            src_bounds.right,
            src_bounds.top
        )

        # Snap the transformed bounds to the area_input reference grid
        left_snap = align_x + math.floor((dst_left - align_x) / res_x) * res_x
        bottom_snap = align_y + math.floor((dst_bottom - align_y) / res_y) * res_y
        right_snap = align_x + math.ceil((dst_right - align_x) / res_x) * res_x
        top_snap = align_y + math.ceil((dst_top - align_y) / res_y) * res_y

        # Build kwargs for gdal.WarpOptions
        warp_kwargs = {
            'format': 'GTiff',
            'xRes': res_x,
            'yRes': res_y,
            'outputBounds': (left_snap, bottom_snap, right_snap, top_snap),
            'srcSRS': conus_albers_proj,
            'dstSRS': 'EPSG:3338',
            'resampleAlg': gdal.GRA_Max,
            'outputType': gdal.GDT_Int8,
            'dstNodata': nodata_value,
            'creationOptions': ['COMPRESS=DEFLATE', 'TILED=YES', 'BIGTIFF=YES']
        }

        # Apply srcNodata if it exists in the metadata
        if source_nodata is not None:
            warp_kwargs['srcNodata'] = source_nodata

        # Execute resampling
        warp_options = gdal.WarpOptions(**warp_kwargs)
        gdal.Warp(resample_intermediate, download_file, options=warp_options)
        end_timing(start_time)

    # Increase count
    count += 1

#### MERGE RASTERS
####____________________________________________________

# Define input files
input_files = glob.glob(f'{resample_folder}/*.tif')

# Merge tiles
print(f'Merging {len(input_files)} tiles...')
start_time = time.time()
# Merge raster tiles
gdal.BuildVRT(vrt_intermediate,
              input_files,
              outputSRS='EPSG:3338',
              xRes=10,
              yRes=10,
              srcNodata=nodata_value,
              VRTNodata=nodata_value,
              outputBounds=area_bounds)
end_timing(start_time)

# Prepare output data profile
print(f'Applying post-processing corrections...')
start_time = time.time()
area_raster = rasterio.open(area_input)
output_profile = area_raster.profile.copy()
output_profile.update({
    'count': 1,
    'nodata': nodata_value,
    'dtype': 'int8',
    'compress': 'lzw',
    'bigtiff': 'YES',
    'tiled': True,
    'blockxsize': 512,
    'blockysize': 512
})

# Prepare raster data
dist_raster = rasterio.open(vrt_intermediate)

# Post-process impervious raster
with rasterio.open(merged_intermediate, 'w', **output_profile) as dst:
    # Find number of raster blocks
    window_list = []
    for block_index, window in area_raster.block_windows(1):
        window_list.append(window)
    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in area_raster.block_windows(1):

        # Load area block
        area_block = area_raster.read(1, window=window, masked=False)

        # Compute bounds of the current output window
        window_bounds = rasterio.windows.bounds(window, area_raster.transform)

        # Load raster blocks
        dist_block = read_raster_block(dist_raster, window_bounds)

        # Set no data to zero
        raster_block = np.where(dist_block == nodata_value, 0, dist_block)

        # Enforce study area boundary
        raster_block = np.where(area_block == 1, raster_block, nodata_value)

        # Write results
        dst.write(raster_block.astype('int8'), 1, window=window)

        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
end_timing(start_time)

# Close rasters
for raster in [area_raster, dist_raster]:
    raster.close()

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
gdal.Translate(imper_output, merged_intermediate, options=cog_options)
end_timing(start_time)

# Upload post-processed raster to GCS
upload_to_gcs(imper_output, final_gcs_output, storage_client)

# Create finished file
print('Writing final output message...')
finished_output = os.path.join(infra_folder, f'Imper_Finished.txt')
with open(finished_output, "w") as file:
    file.write("finished")
final_gcs_output = f'{gcs_base}/{destination}/Imper_Finished.txt'
upload_to_gcs(finished_output, final_gcs_output, storage_client)
print('Processing finished.')
