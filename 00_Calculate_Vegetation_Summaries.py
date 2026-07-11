# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate vegetation summaries
# Author: Timm Nawrocki
# Last Updated: 2026-07-09
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Calculate vegetation summaries" contacts a server to download a series of tiles containing high-resolution impervious surface data.
# ---------------------------------------------------------------------------

# Set nodata value
nodata_value = -128

# Import packages
import os
import time
import numpy as np
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
gcs_base = 'gs://akveg-data/foliar_cover_v2p1'
destination = 'rasters_summary'

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define data folder
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
foliar_folder = os.path.join(drive, root_folder, 'Data_Input/rasters_foliar')
intermediate_folder = os.path.join(drive, root_folder, 'Data_Input/rasters_intermediate')
output_folder = os.path.join(drive, root_folder, 'Data_Input/rasters_summary')

# Define input data
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')

# Define coniferous tree inputs
neetre_input = os.path.join(foliar_folder, 'neetre_cvr_10m_3338.tif')
picgla_input = os.path.join(foliar_folder, 'picgla_cvr_10m_3338.tif')
picmar_input = os.path.join(foliar_folder, 'picmar_cvr_10m_3338.tif')
picsit_input = os.path.join(foliar_folder, 'picsit_cvr_10m_3338.tif')
tsumer_input = os.path.join(foliar_folder, 'tsumer_cvr_10m_3338.tif')
tsuhet_input = os.path.join(foliar_folder, 'tsuhet_cvr_10m_3338.tif')
abies_input = os.path.join(foliar_folder, 'abies_dst_10m_3338.tif')
calnoo_input = os.path.join(foliar_folder, 'calnoo_dst_10m_3338.tif')
larlar_input = os.path.join(foliar_folder, 'larlar_dst_10m_3338.tif')
pinus_input = os.path.join(foliar_folder, 'pinus_dst_10m_3338.tif')

# Define broadleaf tree inputs
brotre_input = os.path.join(foliar_folder, 'brotre_cvr_10m_3338.tif')
bettre_input = os.path.join(foliar_folder, 'bettre_cvr_10m_3338.tif')
poptre_input = os.path.join(foliar_folder, 'poptre_cvr_10m_3338.tif')
populbt_input = os.path.join(foliar_folder, 'populbt_cvr_10m_3338.tif')

# Define shrub inputs
alnus_input = os.path.join(foliar_folder, 'alnus_cvr_10m_3338.tif')
betshr_input = os.path.join(foliar_folder, 'betshr_cvr_10m_3338.tif')
ndsalix_input = os.path.join(foliar_folder, 'ndsalix_cvr_10m_3338.tif')
rubspe_input = os.path.join(foliar_folder, 'rubspe_cvr_10m_3338.tif')
bderishr_input = os.path.join(foliar_folder, 'bderishr_cvr_10m_3338.tif')
rhoshr_input = os.path.join(foliar_folder, 'rhoshr_cvr_10m_3338.tif')
vaculi_input = os.path.join(foliar_folder, 'vaculi_cvr_10m_3338.tif')

# Define dwarf shrub inputs
dryas_input = os.path.join(foliar_folder, 'dryas_cvr_10m_3338.tif')
dsalix_input = os.path.join(foliar_folder, 'dsalix_cvr_10m_3338.tif')
empnig_input = os.path.join(foliar_folder, 'empnig_cvr_10m_3338.tif')
nerishr_input = os.path.join(foliar_folder, 'nerishr_cvr_10m_3338.tif')
vacvit_input = os.path.join(foliar_folder, 'vacvit_cvr_10m_3338.tif')

# Define herbaceous inputs
forb_input = os.path.join(foliar_folder, 'forb_cvr_10m_3338.tif')
wetforb_input = os.path.join(foliar_folder, 'wetforb_cvr_10m_3338.tif')
gramin_input = os.path.join(foliar_folder, 'gramin_cvr_10m_3338.tif')
beach_input = os.path.join(foliar_folder, 'beach_cvr_10m_3338.tif')
halgra_input = os.path.join(foliar_folder, 'halgra_cvr_10m_3338.tif')
erivag_input = os.path.join(foliar_folder, 'erivag_cvr_10m_3338.tif')
mwcalama_input = os.path.join(foliar_folder, 'mwcalama_cvr_10m_3338.tif')
wetsed_input = os.path.join(foliar_folder, 'wetsed_cvr_10m_3338.tif')
wetgram_input = os.path.join(foliar_folder, 'wetgram_dst_10m_3338.tif')

# Define moss and lichen inputs
bromos_input = os.path.join(foliar_folder, 'bromos_dst_10m_3338.tif')
feather_input  = os.path.join(foliar_folder, 'feather_cvr_10m_3338.tif')
sphagn_input = os.path.join(foliar_folder, 'sphagn_cvr_10m_3338.tif')
lichen_input = os.path.join(foliar_folder, 'lichen_cvr_10m_3338.tif')

# Define output data
trees_output = os.path.join(output_folder, 'trees_cvr_10m_3338.tif')
decratio_output = os.path.join(output_folder, 'deciduous_ratio_10m_3338.tif')
picratio_output = os.path.join(output_folder, 'picea_ratio_10m_3338.tif')
shrub_output = os.path.join(output_folder, 'shrub_cvr_10m_3338.tif')
ndshrub_output = os.path.join(output_folder, 'ndshrub_cvr_10m_3338.tif')
erishrub_output = os.path.join(output_folder, 'erishrub_cvr_10m_3338.tif')
eridwarf_output = os.path.join(output_folder, 'eridwarf_cvr_10m_3338.tif')
wetind_output = os.path.join(output_folder, 'wetind_cvr_10m_3338.tif')
tusratio_output = os.path.join(output_folder, 'tussock_ratio_10m_3338.tif')
herbaceous_output = os.path.join(output_folder, 'herbac_cvr_10m_3338.tif')

#### PREPARE DATA
####____________________________________________________

# Read area bounds and exact pixel dimensions to guarantee a perfect match
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Create a dictionary of input names and paths
raster_paths = {
    'neetre': neetre_input,
    'picgla': picgla_input,
    'picmar': picmar_input,
    'picsit': picsit_input,
    'tsumer': tsumer_input,
    'tsuhet': tsuhet_input,
    'abies': abies_input,
    'calnoo': calnoo_input,
    'larlar': larlar_input,
    'pinus': pinus_input,
    'brotre': brotre_input,
    'bettre': bettre_input,
    'poptre': poptre_input,
    'populbt': populbt_input,
    'alnus': alnus_input,
    'betshr': betshr_input,
    'ndsalix': ndsalix_input,
    'rubspe': rubspe_input,
    'bderishr': bderishr_input,
    'rhoshr': rhoshr_input,
    'vaculi': vaculi_input,
    'dryas': dryas_input,
    'dsalix': dsalix_input,
    'empnig': empnig_input,
    'nerishr': nerishr_input,
    'vacvit': vacvit_input,
    'forb': forb_input,
    'wetforb': wetforb_input,
    'gramin': gramin_input,
    'beach': beach_input,
    'halgra': halgra_input,
    'erivag': erivag_input,
    'mwcalama': mwcalama_input,
    'wetsed': wetsed_input,
    'wetgram': wetgram_input,
    'bromos': bromos_input,
    'feather': feather_input,
    'sphagn': sphagn_input,
    'lichen': lichen_input
}

# Open area raster
area_raster = rasterio.open(area_input)

# Iterate through input paths to open them into a dictionary
raster_sources = {}
for name, path in raster_paths.items():
    raster_sources[name] = rasterio.open(path)

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

#### CALCULATE TREE TOTAL
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = trees_output
if not os.path.exists(summary_output):
    print('Calculating trees summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            neetre_block = read_raster_block(raster_sources['neetre'], window_bounds)
            brotre_block = read_raster_block(raster_sources['brotre'], window_bounds)

            # Perform calculation
            raster_block = neetre_block + brotre_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE DECIDUOUS RATIO
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = decratio_output
if not os.path.exists(summary_output):
    print('Calculating deciduous ratio summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            neetre_block = read_raster_block(raster_sources['neetre'], window_bounds)
            brotre_block = read_raster_block(raster_sources['brotre'], window_bounds)

            # Perform calculation
            raster_block = (brotre_block / (neetre_block + brotre_block + 0.01)) * 100

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE PICEA RATIO
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = picratio_output
if not os.path.exists(summary_output):
    print('Calculating picea ratio summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            picgla_block = read_raster_block(raster_sources['picgla'], window_bounds)
            picmar_block = read_raster_block(raster_sources['picmar'], window_bounds)

            # Perform calculation
            raster_block = (picgla_block / (picgla_block + picmar_block + 0.01)) * 100

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE SHRUB SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = shrub_output
if not os.path.exists(summary_output):
    print('Calculating shrub summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            alnus_block = read_raster_block(raster_sources['alnus'], window_bounds)
            bderishr_block = read_raster_block(raster_sources['bderishr'], window_bounds)
            betshr_block = read_raster_block(raster_sources['betshr'], window_bounds)
            ndsalix_block = read_raster_block(raster_sources['ndsalix'], window_bounds)
            rubspe_block = read_raster_block(raster_sources['rubspe'], window_bounds)
            rhoshr_block = read_raster_block(raster_sources['rhoshr'], window_bounds)
            vaculi_block = read_raster_block(raster_sources['vaculi'], window_bounds)
            vacvit_block = read_raster_block(raster_sources['vacvit'], window_bounds)
            nerishr_block = read_raster_block(raster_sources['nerishr'], window_bounds)
            dryas_block = read_raster_block(raster_sources['dryas'], window_bounds)
            dsalix_block = read_raster_block(raster_sources['dsalix'], window_bounds)

            # Perform calculation
            raster_block = (alnus_block + bderishr_block + betshr_block + ndsalix_block + rubspe_block
                            + rhoshr_block + vaculi_block + vacvit_block + nerishr_block
                            + dryas_block + dsalix_block)

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE NON-DWARF SHRUB SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = ndshrub_output
if not os.path.exists(summary_output):
    print('Calculating non-dwarf shrub summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            alnus_block = read_raster_block(raster_sources['alnus'], window_bounds)
            bderishr_block = read_raster_block(raster_sources['bderishr'], window_bounds)
            betshr_block = read_raster_block(raster_sources['betshr'], window_bounds)
            ndsalix_block = read_raster_block(raster_sources['ndsalix'], window_bounds)
            rubspe_block = read_raster_block(raster_sources['rubspe'], window_bounds)

            # Perform calculation
            raster_block = alnus_block + bderishr_block + betshr_block + ndsalix_block + rubspe_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE ERICACEOUS SHRUB SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = erishrub_output
if not os.path.exists(summary_output):
    print('Calculating ericaceous shrub summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            bderishr_block = read_raster_block(raster_sources['bderishr'], window_bounds)
            nerishr_block = read_raster_block(raster_sources['nerishr'], window_bounds)
            rhoshr_block = read_raster_block(raster_sources['rhoshr'], window_bounds)
            vaculi_block = read_raster_block(raster_sources['vaculi'], window_bounds)
            vacvit_block = read_raster_block(raster_sources['vacvit'], window_bounds)

            # Perform calculation
            raster_block = bderishr_block + nerishr_block + rhoshr_block + vaculi_block + vacvit_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE ERICACEOUS DWARF SHRUB SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = eridwarf_output
if not os.path.exists(summary_output):
    print('Calculating ericaceous dwarf shrub summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            nerishr_block = read_raster_block(raster_sources['nerishr'], window_bounds)
            rhoshr_block = read_raster_block(raster_sources['rhoshr'], window_bounds)
            vacvit_block = read_raster_block(raster_sources['vacvit'], window_bounds)

            # Perform calculation
            raster_block = nerishr_block + rhoshr_block + vacvit_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE WETLAND INDICATOR SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = wetind_output
if not os.path.exists(summary_output):
    print('Calculating wetland indicator summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            wetsed_block = read_raster_block(raster_sources['wetsed'], window_bounds)
            sphagn_block = read_raster_block(raster_sources['sphagn'], window_bounds)

            # Perform calculation
            raster_block = wetsed_block + sphagn_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE TUSSOCK RATIO SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = tusratio_output
if not os.path.exists(summary_output):
    print('Calculating tussock ratio summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            wetsed_block = read_raster_block(raster_sources['wetsed'], window_bounds)
            sphagn_block = read_raster_block(raster_sources['sphagn'], window_bounds)
            erivag_block = read_raster_block(raster_sources['erivag'], window_bounds)

            # Perform calculation
            raster_block = (erivag_block / (wetsed_block + sphagn_block + 0.01)) * 100

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)

#### CALCULATE HERBACEOUS SUMMARY
####____________________________________________________

# Calculate vegetation summary if it does not already exist
summary_output = herbaceous_output
if not os.path.exists(summary_output):
    print('Calculating herbaceous summary...')
    start_time = time.time()

    # Define final GCS path for the output
    output_name = os.path.split(summary_output)[1]
    final_gcs_output = f'{gcs_base}/{destination}/{output_name}'

    # Define intermediate data
    merged_intermediate = os.path.join(intermediate_folder, output_name)

    # Extract raster to area
    print('Performing block calculations...')
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
            gramin_block = read_raster_block(raster_sources['gramin'], window_bounds)
            forb_block = read_raster_block(raster_sources['forb'], window_bounds)

            # Perform calculation
            raster_block = gramin_block + forb_block

            # Enforce study area boundary
            raster_block = np.where(area_block == 1, raster_block, nodata_value)

            # Write results
            dst.write(raster_block.astype('int8'), 1, window=window)

            # Report progress
            count, progress = raster_block_progress(100, len(window_list), count, progress)

    # Translate raster to cloud-optimized geotiff
    print('Converting to cloud-optimized geotiff...')
    gdal.Translate(summary_output, merged_intermediate, options=cog_options)

    # Upload post-processed raster to GCS
    print('Uploading to Google Cloud Storage...')
    upload_to_gcs(summary_output, final_gcs_output, storage_client)
    end_timing(start_time)
