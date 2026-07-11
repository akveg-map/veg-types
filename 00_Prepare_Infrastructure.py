# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare infrastructure data
# Author: Timm Nawrocki
# Last Updated: 2026-07-08
# Usage: Execute in Python 3.9+.
# Description: "Prepare infrastructure data" extracts infrastructure from the North Slope Science Initiative vector dataset and the LANDFIRE 2023 EVT raster.
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
from rasterio.windows import from_bounds
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
input_folder = os.path.join(drive, root_folder, 'Data_Input/surficial_infrastructure')
output_folder = os.path.join(drive, root_folder, 'Data_Output/surficial/infrastructure_20260708')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
infrastructure_geodatabase = os.path.join(input_folder, 'unprocessed/NSInfra_V13_geodatabase.gdb')
landfire_input = os.path.join(ancillary_folder, 'LA23_EVT_240.tif')
impervious_input = os.path.join(input_folder, 'processed/impervious_ccap_10m_3338.tif')
delete_input = os.path.join(input_folder, 'unprocessed/override_delete_3338.shp')

# Define intermediate files
vector_intermediate = os.path.join(input_folder, 'unprocessed/NSInfra_V13_vector.gpkg')
ns_intermediate = os.path.join(input_folder, 'processed/NSInfra_V13_intermediate.tif')
landfire_intermediate = os.path.join(input_folder, 'processed/landfire_evt_2023_10m_3338.tif')
delete_intermediate = os.path.join(input_folder, 'processed/override_delete_10m_3338.tif')
merged_intermediate = os.path.join(output_folder, 'infrastructure_merged_10m_3338.tif')

# Define output file
infra_output = os.path.join(output_folder, 'infrastructure_10m_3338.tif')

#### CONVERT NORTH SLOPE VECTOR DATA TO RASTER
####____________________________________________________

# Read area bounds and exact pixel dimensions to guarantee a perfect match
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Convert Northern Alaska Infrastructure to raster if it does not already exist
if not os.path.exists(ns_intermediate):
    print('Converting north slope infrastructure to raster...')
    start_time = time.time()

    # Read vector data
    nsroads_data = (gpd.read_file(infrastructure_geodatabase, layer='NSRoads_V13')
                    .to_crs('EPSG:3338')
                    .buffer(20))
    nspipelines_data = (gpd.read_file(infrastructure_geodatabase, layer='NSPipelines_V13')
                        .to_crs('EPSG:3338')
                        .buffer(10))
    nsdev_data = (gpd.read_file(infrastructure_geodatabase, layer='NSDevAreas_V13')
                  .to_crs('EPSG:3338')
                  .buffer(15))

    # Merge the vectors into a single multipolygon (Returns a GeoSeries)
    ns_data = pd.concat([nsroads_data, nspipelines_data, nsdev_data], ignore_index=True)

    # Re-cast the GeoSeries as a GeoDataFrame
    ns_data = gpd.GeoDataFrame(geometry=ns_data, crs='EPSG:3338')
    ns_data['infra_val'] = 1

    # Export the merged vector to an intermediate GeoPackage
    ns_data.to_file(vector_intermediate, driver='GPKG')

    # Set Rasterize options for a standard GeoTIFF intermediate
    rasterize_options = gdal.RasterizeOptions(
        format='GTiff',
        outputBounds=area_bounds,
        width=target_width,
        height=target_height,
        attribute='infra_val',
        noData=nodata_value,
        outputType=gdal.GDT_Int8,
        creationOptions=['COMPRESS=DEFLATE']
    )

    # Rasterize the intermediate vector directly to the grid
    gdal.Rasterize(ns_intermediate, vector_intermediate, options=rasterize_options)

    # Clean up the intermediate vector file to save drive space
    if os.path.exists(vector_intermediate):
        os.remove(vector_intermediate)
    end_timing(start_time)

#### CONVERT OVERRIDE DATA TO RASTER
####____________________________________________________

# Convert override delete to raster if it does not already exist
if not os.path.exists(delete_intermediate):
    print('Converting override delete to raster...')
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
        xRes=10,
        yRes=10,
        initValues=[0],
        burnValues=[1],
        noData=nodata_value,
        allTouched=False
    )

    # Convert the override to raster
    gdal.Rasterize(delete_intermediate, delete_input, options=range_options)
    end_timing(start_time)

#### RESAMPLE LANDFIRE DATA
####____________________________________________________

# Resample Landfire EVT if it does not already exist
if not os.path.exists(landfire_intermediate):
    # Set Warp options for spatial snapping, data conversion, and COG creation
    warp_options = gdal.WarpOptions(
        format='COG',
        outputBounds=area_bounds,
        width=target_width,
        height=target_height,
        srcSRS='EPSG:3338',
        dstSRS='EPSG:3338',
        srcNodata=32767,
        dstNodata=-32768,
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
    print('Warping Landfire to cloud-optimized raster using GDAL...')
    start_time = time.time()
    gdal.Warp(landfire_intermediate, landfire_input, options=warp_options)
    end_timing(start_time)

#### PROCESS RASTER EXTRACTION
####____________________________________________________

# Read input rasters
area_raster = rasterio.open(area_input)
ns_raster = rasterio.open(ns_intermediate)
imper_raster = rasterio.open(impervious_input)
lf_raster = rasterio.open(landfire_intermediate)
delete_raster = rasterio.open(delete_intermediate)

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
print(f'Extracting raster to area...')
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
        ns_block = read_raster_block(ns_raster, window_bounds)
        imper_block = read_raster_block(imper_raster, window_bounds)
        lf_block = read_raster_block(lf_raster, window_bounds)
        delete_block = read_raster_block(delete_raster, window_bounds)

        # Set developed areas to value of 1
        developed_lf = np.isin(lf_block, [7295, 7296, 7297, 7298, 7299, 7300])
        raster_block = np.where((ns_block == 1) | (imper_block == 1) | developed_lf, 1, 0)

        # Set agricultural areas to value of 2
        agriculture_lf = np.isin(lf_block, [7754, 7755])
        raster_block = np.where(agriculture_lf, 2, raster_block)

        # Enforce override
        raster_block = np.where(delete_block == 1, 0, raster_block)

        # Enforce study area boundary
        raster_block = np.where(area_block == 1, raster_block, nodata_value)

        # Write results
        dst.write(raster_block.astype('int8'), 1, window=window)

        # Report progress
        count, progress = raster_block_progress(100, len(window_list), count, progress)
    end_timing(start_time)

# Close rasters
for raster in [area_raster, ns_raster, imper_raster, lf_raster, delete_raster]:
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
gdal.Translate(infra_output, merged_intermediate, options=cog_options)
end_timing(start_time)
