# ---------------------------------------------------------------------------
# Prepare regions
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2026-07-06
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Prepare regions" converts the USNVC vegetation regions feature class to a raster.
# ---------------------------------------------------------------------------

# Set execution parameters
nodata_value = -128

# Import libraries
import os
import time
import geopandas as gpd
import rasterio
from osgeo import gdal
from akutils import *

# Enable GDAL exceptions to catch errors natively
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
region_folder = os.path.join(project_folder, 'Data_Input/region_data')
intermediate_folder = os.path.join(project_folder, 'Data_Input/ancillary_data/intermediate')
ancillary_folder = os.path.join(project_folder, 'Data_Input/ancillary_data/processed')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_MapDomain_v2p1_10m_3338.tif')
region_input = os.path.join(region_folder, 'AlaskaYukon_USNVC_ZonesRegions_v2p1_3338.shp')

# Define intermediate files
vector_intermediate = os.path.join(intermediate_folder, 'AlaskaYukon_USNVC_ZonesRegions_v2p1_3338.gpkg')
raster_intermediate = os.path.join(intermediate_folder, 'AlaskaYukon_VegetationRegions_10m_3338.tif')

# Define output files
region_output = os.path.join(ancillary_folder, 'AlaskaYukon_VegetationRegions_10m_3338.tif')

#### CONVERT VEGETATION REGIONS TO RASTER
####____________________________________________________

# Read area bounds
area_bounds = raster_bounds(area_input)
with rasterio.open(area_input) as ref:
    target_width = ref.width
    target_height = ref.height

# Define index values
region_dictionary = {'Arctic Northern': 1,
                     'Arctic Western': 2,
                     'Alaska-Yukon Northern': 3,
                     'Alaska Western': 4,
                     'Alaska-Yukon Central': 5,
                     'Alaska-Yukon Southern': 6,
                     'Alaska Southwest': 7,
                     'Aleutian-Kamchatka': 8,
                     'Alaska Pacific': 9,
                     'North Pacific': 10}

# Extract bioclimatic zone and vegetation region
print('Converting regions vector to raster...')
start_time = time.time()
region_data = gpd.read_file(region_input)[['geometry', 'region']].reset_index()
region_data['region_id'] = region_data['region'].map(region_dictionary)

# Export intermediate geopackage
region_data.to_file(vector_intermediate, driver='GPKG')

# Set rasterize options
rasterize_options = gdal.RasterizeOptions(
    format='GTiff',
    outputBounds=area_bounds,
    width=target_width,
    height=target_height,
    attribute='region_id',
    noData=nodata_value,
    outputType=gdal.GDT_Int8,
    creationOptions=['COMPRESS=DEFLATE']
)

# Rasterize the intermediate vector
gdal.Rasterize(raster_intermediate, vector_intermediate, options=rasterize_options)
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
gdal.Translate(region_output, raster_intermediate, options=cog_options)

# Remove intermediate files
if os.path.exists(vector_intermediate):
    os.remove(vector_intermediate)
if os.path.exists(raster_intermediate):
    os.remove(raster_intermediate)
end_timing(start_time)
