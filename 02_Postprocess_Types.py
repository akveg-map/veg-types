# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert raster grids to cloud-optimized geotiff
# Author: Timm Nawrocki
# Last Updated: 2026-08-04
# Usage: Must be executed in a Python 3.11+ installation with GDAL 3.9+.
# Description: 'Convert raster grids to cloud-optimized geotiff' compiles raster grids and creates a cloud-optimized geotiff version.
# ---------------------------------------------------------------------------

# Define model targets
destination = 'rasters_final'
nodata_value = -32768

# Import packages
import glob
import os
import shutil
import time
import collections
import dbf
import numpy as np
import pandas as pd
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

# Define final GCS path for the output
output_name = 'types_10m_3338.tif'
final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define folder structure
schema_folder = os.path.join(drive, root_folder, 'scripts')
input_folder = os.path.join(drive, root_folder, 'Data_Output/rasters_gridded')
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
intermediate_folder = os.path.join(drive, root_folder, f'Data_Output/rasters_intermediate')
output_folder = os.path.join(drive, root_folder, f'Data_Output/rasters_final')

# Make output directories
if os.path.exists(input_folder):
    shutil.rmtree(input_folder)
os.makedirs(input_folder)
if not os.path.exists(intermediate_folder):
    os.makedirs(intermediate_folder)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_CategoricalDomain_v2p1_10m_3338.tif')
schema_input = os.path.join(schema_folder, 'AKVEG_MapClass_Schema.csv')

# Define intermediate files
vrt_intermediate = os.path.join(intermediate_folder, 'types_merged.vrt')
merged_intermediate = os.path.join(intermediate_folder, 'types_merged.tif')

# Define output files
type_output = os.path.join(output_folder, output_name)

# Create cloud-optimized geotiff if it does not already exist
if not os.path.exists(type_output):

    #### DOWNLOAD RASTER TILES
    ####____________________________________________________

    # Identify all raster tiles in target folder on Google Cloud Storage
    raster_tiles = gcs_list_files(f'{gcs_base}/rasters_gridded', storage_client, extension='.tif')

    # Download each raster tile to local folder
    tile_count = 1
    print('Downloading raster tiles...')
    start_time = time.time()
    for raster_uri in raster_tiles:
        if tile_count % 1000 == 0 or tile_count == len(raster_tiles):
            print(f'\tDownloading tile {tile_count} of {len(raster_tiles)}...')
        # Extract filename from uri
        file_name = os.path.split(raster_uri)[1]
        # Define the local download path
        raster_file = os.path.join(input_folder, file_name)
        # Download raster tile
        download_from_gcs(raster_uri, raster_file, storage_client)
        # Check and update nodata value if it does not match the specified nodata value
        with rasterio.open(raster_file, 'r+') as src:
            current_nodata = src.nodata
            if current_nodata != nodata_value:
                # Read the pixel array
                data = src.read(1)
                # Replace erroneous nodata values
                data = np.where(data == current_nodata, nodata_value, data)
                # Write the updated array back to disk
                src.write(data, 1)
                # Update the file's internal metadata
                src.nodata = nodata_value
        # Increase count
        tile_count += 1

    # Report outcome
    end_timing(start_time)

    #### PROCESS CLOUD-OPTIMIZED GEOTIFFS
    ####____________________________________________________

    # Read area bounds
    area_bounds = raster_bounds(area_input)

    # Define input files
    input_files = glob.glob(f'{input_folder}/*.tif')

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
    print(f'Applying study area...')
    start_time = time.time()
    area_raster = rasterio.open(area_input)
    output_profile = area_raster.profile.copy()
    output_profile.update({
        'count': 1,
        'nodata': nodata_value,
        'dtype': 'int16',
        'compress': 'lzw',
        'bigtiff': 'YES',
        'tiled': True,
        'blockxsize': 512,
        'blockysize': 512
    })

    # Prepare raster data
    type_raster = rasterio.open(vrt_intermediate)

    # Post-process floodplain raster
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
            type_block = read_raster_block(type_raster, window_bounds)

            # Set no data to water
            raster_block = np.where(type_block == nodata_value, 998, type_block)

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int16'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)
    end_timing(start_time)

    # Close rasters
    for raster in [area_raster, type_raster]:
        raster.close()

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
            'OVERVIEW_RESAMPLING=MODE'
        ]
    )

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    start_time = time.time()
    gdal.Translate(type_output, merged_intermediate, options=cog_options)
    end_timing(start_time)

    # Upload post-processed raster to GCS
    start_time = time.time()
    print('Uploading cloud-optimized geotiff to Google Cloud...')
    upload_to_gcs(type_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### BUILD RASTER ATTRIBUTE TABLE
####____________________________________________________

# Specify attribute table file path
attribute_output = type_output + '.vat.dbf'
if os.path.exists(attribute_output):
    os.remove(attribute_output)

# Define new collection counter
value_counts = collections.Counter()

# Read raster blocks to build attribute values and counts
print('Building value histogram...')
start_time = time.time()
with rasterio.open(type_output) as type_raster:
    # Find number of raster blocks
    window_list = []
    for block_index, window in type_raster.block_windows(1):
        window_list.append(window)
    # Iterate processing through raster blocks
    count = 1
    progress = 0
    for block_index, window in type_raster.block_windows(1):
        input_block = type_raster.read(1, window=window, masked=True)
        # Use compressed to ignore nodata
        input_data = input_block.compressed()
        if input_data.size == 0:
            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)
        else:
            # Update the histogram incrementally
            value_counts.update(input_data.tolist())
            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

# Raise error for empty output
if not value_counts:
    raise RuntimeError('Raster contains no valid data.')

# Convert counter to sorted lists
print('Building raster attribute table...')
unique_values = sorted(value_counts.keys())

# Define DBF table fields
attribute_table = dbf.Table(
    attribute_output,
    'VALUE N(10,0); COUNT N(20,0); MAP_CLS C(254); COARSE_CLS C(254); MACRO_CODE C(50); NVC_MACRO C(254); GROUP_CODE C(50); NVC_GROUP C(254)',
    codepage='utf8'
)

# Read the schema data
schema_data = pd.read_csv(schema_input).fillna('')

# Convert the dataframe to a dictionary using 'code' as the key for fast row lookups
schema_dict = schema_data.set_index('code').to_dict(orient='index')

# Write attribute table
attribute_table.open(mode=dbf.READ_WRITE)
for value in unique_values:
    count = value_counts[value]

    # Retrieve the attributes for the current value, defaulting to empty strings if code is missing
    if int(value) in schema_dict:
        row = schema_dict[int(value)]
        map_class = str(row.get('map_class', ''))
        coarse_class = str(row.get('coarse_class', ''))
        macrogroup_code = str(row.get('macrogroup_code', ''))
        macrogroup = str(row.get('macrogroup', ''))
        group_code = str(row.get('group_code', ''))
        group = str(row.get('group', ''))
    else:
        map_class = coarse_class = macrogroup_code = macrogroup = group_code = group = ''

    # Append the row matching the dbf field definition sequence
    attribute_table.append((
        int(value),
        int(count),
        map_class,
        coarse_class,
        macrogroup_code,
        macrogroup,
        group_code,
        group
    ))
attribute_table.close()
end_timing(start_time)

# Upload post-processed attribute table to GCS
start_time = time.time()
print('Uploading attribute table to Google Cloud...')
attribute_gcs_output = f'{gcs_base}/{destination}/{os.path.split(attribute_output)[1]}'
upload_to_gcs(attribute_output, attribute_gcs_output, storage_client)
end_timing(start_time)

# Create a .cpg file to guarantee ArcGIS Pro reads the encoding correctly
cpg_output = type_output + '.vat.cpg'
with open(cpg_output, 'w') as cpg_file:
    cpg_file.write('UTF-8')
cpg_gcs_output = f'{gcs_base}/{destination}/{os.path.split(cpg_output)[1]}'
upload_to_gcs(cpg_output, cpg_gcs_output, storage_client)
