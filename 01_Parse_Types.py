# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Parse vegetation types
# Author: Timm Nawrocki
# Last Updated: 2026-08-02
# Usage: Must be executed in a Python 3.12+ installation.
# Description: "Parse vegetation types" runs a programmatic key to the AKVEG map classes using foliar cover and surficial features maps, as well as additional ancillary data.
# ---------------------------------------------------------------------------

# Set execution parameters
processors = 1
processor = 1
nodata_value = -32768

# Import packages
import os
import time
import math
import numpy as np
from osgeo import gdal
import geopandas as gpd
import rasterio
from rasterio import features
from google.cloud import storage
from akutils import *
from programmatic_keys.key_needleleaf import key_needleleaf
from programmatic_keys.key_broadleaf import key_broadleaf
from programmatic_keys.key_mixed import key_mixed
from programmatic_keys.key_tussock import key_tussock
from programmatic_keys.key_shrub import key_shrub
from programmatic_keys.key_herbaceous import key_herbaceous

# Initialize GCS Client
storage_client = storage.Client()

# Configure GDAL
gdal.UseExceptions()

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = '/home'
root_folder = 'twnawrocki'

# Define folder structure
region_folder = os.path.join(drive, root_folder, 'Data_Input/region_data')
ancillary_folder = os.path.join(drive, root_folder, 'Data_Input/ancillary_data')
foliar_folder = os.path.join(drive, root_folder, 'Data_Input/rasters_foliar')
summary_folder = os.path.join(drive, root_folder, 'Data_Input/rasters_summary')
output_folder = os.path.join(drive, root_folder, 'Data_Output/rasters_gridded')

# Define input files
area_input = os.path.join(region_folder, 'AlaskaYukon_CategoricalDomain_v2p1_10m_3338.tif')
grid_input = os.path.join(region_folder, 'AlaskaYukon_CategoricalTiles_010_v2p1_3338.shp')
region_input = os.path.join(ancillary_folder, 'AlaskaYukon_VegetationRegions_10m_3338.tif')

# Define physiography and surficial features inputs
esa_input = os.path.join(ancillary_folder, 'esa_worldcover2_10m_3338.tif')
fire_input = os.path.join(ancillary_folder, 'fire_year_10m_3338.tif')
coast_input = os.path.join(ancillary_folder, 'range_coast_10m_3338.tif')
alpine_input = os.path.join(ancillary_folder, 'alpine_dst_10m_3338.tif')
alkaline_input = os.path.join(ancillary_folder, 'alkaline_10m_3338.tif')
infra_input = os.path.join(ancillary_folder, 'infrastructure_10m_3338.tif')
imper_input = os.path.join(ancillary_folder, 'impervious_ccap_10m_3338.tif')
fldpln_input = os.path.join(ancillary_folder, 'fldpln_dst_10m_3338.tif')
dune_input = os.path.join(ancillary_folder, 'dunes_dst_10m_3338.tif')
bluff_input = os.path.join(ancillary_folder, 'stpblf_dst_10m_3338.tif')
water_input = os.path.join(foliar_folder, 'water_cvr_10m_3338.tif')
peat_input = os.path.join(ancillary_folder, 'peat_dst_10m_3338.tif')
soil_input = os.path.join(ancillary_folder, 'soil_order_10m_3338.tif')
slope_input = os.path.join(ancillary_folder, 'slope_10m_3338.tif')
aspect_input = os.path.join(ancillary_folder, 'aspect_10m_3338.tif')
polcom_input = os.path.join(ancillary_folder, 'range_polygonalcomplex_10m_3338.tif')
subzoneC_input = os.path.join(ancillary_folder, 'subzoneC_10m_3338.tif')
snowex_input = os.path.join(ancillary_folder, 'snow_exclusion_10m_3338.tif')
watercor_input = os.path.join(ancillary_folder, 'water_correction_10m_3338.tif')

# Define Dynamic World inputs
dwwater_input = os.path.join(ancillary_folder, 'dw_water_10m_3338.tif')
dwsnow_input = os.path.join(ancillary_folder, 'dw_snow_10m_3338.tif')
dwflood_input = os.path.join(ancillary_folder, 'dw_flooded_10m_3338.tif')
dwbarren_input = os.path.join(ancillary_folder, 'dw_barren_10m_3338.tif')

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

# Define vegetation summary inputs
tree_input = os.path.join(summary_folder, 'trees_cvr_10m_3338.tif')
decratio_input = os.path.join(summary_folder, 'deciduous_ratio_10m_3338.tif')
picratio_input = os.path.join(summary_folder, 'picea_ratio_10m_3338.tif')
shrub_input = os.path.join(summary_folder, 'shrub_cvr_10m_3338.tif')
ndshrub_input = os.path.join(summary_folder, 'ndshrub_cvr_10m_3338.tif')
erishrub_input = os.path.join(summary_folder, 'erishrub_cvr_10m_3338.tif')
eridwarf_input = os.path.join(summary_folder, 'eridwarf_cvr_10m_3338.tif')
tussock_input = os.path.join(summary_folder, 'tussock_ratio_10m_3338.tif')
wetind_input = os.path.join(summary_folder, 'wetind_cvr_10m_3338.tif')
herbac_input = os.path.join(summary_folder, 'herbac_cvr_10m_3338.tif')

#### IDENTIFY PREDICTION GRIDS
####____________________________________________________

# Read grid data
grid_data = gpd.read_file(grid_input)

# Define grid list
grid_list = grid_data['grid_code'].tolist()

# Override grid list for test purposes (uncomment lines below)
target_grids = ['AK010H211V124', 'AK010H223V014', 'AK010H231V014', 'AK010H219V146', 'AK010H220V146',
                'AK010H190V013', 'AK010H233V013', 'AK010H236V126', 'AK010H253V055', 'AK010H244V121',
                'AK010H195V139']
grid_list = [code for code in grid_list if code in target_grids]

# Partition grid list for spatially parallel processing
#grid_chunks = np.array_split(grid_list, processors)
#grid_list = grid_chunks[processor - 1].tolist()

# Create final grid data
grid_data = grid_data[grid_data['grid_code'].isin(grid_list)]
print(f'Predicting {len(grid_data)} grids...')

#### PARSE VEGETATION TYPES
####____________________________________________________

# Create a dictionary of input names and paths
raster_paths = {
    'area': area_input,
    'region': region_input,
    'esa': esa_input,
    'fire': fire_input,
    'coast': coast_input,
    'alpine': alpine_input,
    'alkaline': alkaline_input,
    'infra': infra_input,
    'imper': imper_input,
    'fldpln': fldpln_input,
    'dune': dune_input,
    'bluff': bluff_input,
    'water': water_input,
    'peat': peat_input,
    'soil': soil_input,
    'slope': slope_input,
    'aspect': aspect_input,
    'polcom': polcom_input,
    'subzoneC': subzoneC_input,
    'snowex': snowex_input,
    'watercor': watercor_input,
    'dwwater': dwwater_input,
    'dwsnow': dwsnow_input,
    'dwflood': dwflood_input,
    'dwbarren': dwbarren_input,
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
    'lichen': lichen_input,
    'tree': tree_input,
    'decratio': decratio_input,
    'picratio': picratio_input,
    'shrub': shrub_input,
    'ndshrub': ndshrub_input,
    'erishrub': erishrub_input,
    'eridwarf': eridwarf_input,
    'tussock': tussock_input,
    'wetind': wetind_input,
    'herbac': herbac_input
}

# Iterate through input paths to open them into a dictionary
raster_sources = {}
for name, path in raster_paths.items():
    raster_sources[name] = rasterio.open(path)

# Define grid alignment from area_input
area_transform = raster_sources['area'].transform
align_x = area_transform[2]
align_y = area_transform[5]
res_x = area_transform[0]
res_y = abs(area_transform[4])

# Export covariate raster for each grid in grid list
grid_count = 1
for index, row in grid_data.iterrows():
    # Define grid code
    grid = row['grid_code']

    # Define output paths
    type_output = os.path.join(output_folder, f'type_{grid}_10m_3338.tif')
    gcs_output = f'gs://akveg-data/veg_type_v2p1/rasters_gridded/type_{grid}_10m_3338.tif'

    # Create output raster if it does not already exist in GCS
    if not gcs_blob_exists(gcs_output, storage_client):
        print(f'Compiling raster for {grid} ({grid_count} of {len(grid_list)})...')
        start_time = time.time()

        # Define processing geometry
        geometry_processing = row['geometry'].buffer(2000)
        left_processing, bottom_processing, right_processing, top_processing = geometry_processing.bounds
        left_processing = align_x + math.floor((left_processing - align_x) / res_x) * res_x
        bottom_processing = align_y + math.floor((bottom_processing - align_y) / res_y) * res_y
        right_processing = align_x + math.ceil((right_processing - align_x) / res_x) * res_x
        top_processing = align_y + math.ceil((top_processing - align_y) / res_y) * res_y

        # Define window bounds for processing
        window_processing = (left_processing, bottom_processing, right_processing, top_processing)

        # Define export geometry
        geometry_export = row['geometry'].buffer(20)
        left_export, bottom_export, right_export, top_export = geometry_export.bounds
        left_export = align_x + math.floor((left_export - align_x) / res_x) * res_x
        bottom_export = align_y + math.floor((bottom_export - align_y) / res_y) * res_y
        right_export = align_x + math.ceil((right_export - align_x) / res_x) * res_x
        top_export = align_y + math.ceil((top_export - align_y) / res_y) * res_y

        # Define the output profile by the export geometry
        dst_transform = rasterio.transform.from_origin(left_export, top_export, res_x, res_y)
        dst_width = int(round((right_export - left_export) / res_x))
        dst_height = int(round((top_export - bottom_export) / res_y))

        # Calculate offsets to slice the processing buffer to the export buffer
        col_offset = int(round((left_export - left_processing) / res_x))
        row_offset = int(round((top_processing - top_export) / res_y))

        # Define output profile
        output_profile = {
            'driver': 'GTiff',
            'height': dst_height,
            'width': dst_width,
            'count': 1,
            'dtype': 'int16',
            'crs': 'EPSG:3338',
            'transform': dst_transform,
            'nodata': -32768,
            'compress': 'lzw',
            'tiled': True,
            'blockxsize': 512,
            'blockysize': 512
        }

        # Parse types
        with (rasterio.open(type_output, 'w', **output_profile) as dst):
            # Load raster data
            data = {}
            for name, src in raster_sources.items():
                data[name] = read_raster_block(src, window_processing)

            # Initialize empty arrays for the vegetation types
            base_data = np.zeros_like(data['area'], dtype=np.int16)

            #### KEY THE LAND COVER TYPES
            ####____________________________________________________

            # 1000. needleleaf trees
            base_data = np.where(
                (((data['neetre'] >= 8) & (np.isin(data['alpine'], [0, 1])))
                 | ((data['neetre'] >= 20) & (data['alpine'] == 2))
                 | ((data['neetre'] >= 5) & (data['esa'] == 10))
                 | ((data['neetre'] >= 5) & (data['fire'] >= 1980)))
                & (data['decratio'] < 40),
                1000, base_data)

            # 2000. broadleaf trees
            base_data = np.where(
                (base_data == 0)
                & ((data['brotre'] >= 10)
                   | ((data['brotre'] >= 5) & (data['fire'] >= 1980)))
                & (data['decratio'] >= 85) & (data['brotre'] >= (data['ndshrub'] * 0.5)),
                2000, base_data)

            # 3000. mixed trees
            base_data = np.where(
                (base_data == 0)
                & ((data['tree'] >= 10)
                   | ((data['tree'] >= 5) & (data['fire'] >= 1980)))
                & ((data['decratio'] >= 40) & (data['decratio'] < 85))
                & (data['tree'] >= (data['ndshrub'] * 0.5)),
                3000, base_data)

            # 4000. tussock
            base_data = np.where(
                (base_data == 0)
                & ((data['erivag'] >= 20)
                   | ((data['erivag'] >= 10) & (data['ndshrub'] < 40))
                   | ((data['erivag'] >= 8) & (data['ndshrub'] < 25) & (data['tussock'] >= 30))
                   | ((data['erivag'] >= 8) & (data['ndshrub'] < 25) & (data['polcom'] == 1) & (data['wetsed'] < 35))),
                4000, base_data)

            # 5000. shrub
            base_data = np.where(
                ((base_data == 0) & (data['shrub'] >= 20))
                | ((base_data == 0) & (data['shrub'] >= 12) & (data['fire'] >= 1980))
                | ((np.isin(base_data, [0, 4000])) & (data['region'] == 1) & (data['nerishr'] >= 15)),
                5000, base_data)

            # 6000. herbaceous
            base_data = np.where(
                (base_data == 0)
                & ((data['herbac'] >= 20) | (data['sphagn'] >= 8)
                   | ((data['peat'] >= 35) & (~np.isin(data['esa'], [60, 70, 80]))
                      & (data['dwwater'] < 85) & (data['dwsnow'] < 90) & (data['dwbarren'] < 85))),
                6000, base_data)

            # 994. agriculture
            base_data = np.where(
                (data['infra'] == 2) & (data['tree'] < 10) & (data['shrub'] < 20),
                994, base_data)

            # 995. disturbed vegetation
            base_data = np.where(
                (data['dwwater'] < 95)
                & (((data['infra'] == 1) & (data['tree'] < 10) & (data['shrub'] < 20) & (data['herbac'] >= 20))
                   | ((data['imper'] == 1) & ((data['tree'] + data['shrub'] + data['herbac']) >= 50))),
                995, base_data)

            # 996. infrastructure
            base_data = np.where(
                (data['dwwater'] < 95)
                & (((data['infra'] == 1) & (data['tree'] < 10) & (data['shrub'] < 20) & (data['herbac'] < 20))
                   | ((data['imper'] == 1) & ((data['tree'] + data['shrub'] + data['herbac']) < 50))),
                996, base_data)

            # 997. snow/ice
            base_data = np.where(
                (base_data == 0) & ((data['dwsnow'] >= 90) | (data['esa'] == 70)) & (data['snowex'] != 1)
                & (data['dwbarren'] < 85),
                997, base_data)

            # 998. water
            base_data = np.where(
                (~np.isin(base_data, [995, 996, 997]))
                & ((((data['esa'] == 80) | (data['dwwater'] >= 90)) & (data['coast'] != 1) & (data['slope'] < 5))
                   | ((data['dwwater'] >= 85) & (data['coast'] == 1) & (data['slope'] < 5))),
                998, base_data)

            # 999. recently burned
            base_data = np.where(
                (~np.isin(base_data, [996, 997, 998])) & (data['fire'] >= 2019),
                999, base_data)

            # 990. barren
            base_data = np.where(
                (base_data == 0)
                & (((data['dwbarren'] >= 50) | (np.isin(data['esa'], [60, 100])))
                   | ((data['coast'] == 1) & (data['esa'] == 80))),
                990, base_data)

            # Apply water correction
            base_data = np.where(data['watercor'] == 1, 998, base_data)

            #### KEY THE BARREN TYPES
            ####____________________________________________________

            # 194. Alaska-Yukon Herbaceous Steppe Bluff
            base_data = np.where(
                (data['bluff'] == 1) & (data['tree'] < 10) & (data['shrub'] < 20),
                194, base_data)

            # 195. Alaska-Yukon Inland Dune
            base_data = np.where(
                (data['dune'] == 1) & (~np.isin(data['region'], [1, 2])),
                195, base_data)

            # 281. Arctic Willow Inland Dune
            base_data = np.where(
                (data['dune'] == 1) & (np.isin(data['region'], [1, 2]))
                & (data['ndsalix'] >= 5),
                281, base_data)

            # 282. Arctic Willow Herbaceous Dune
            base_data = np.where(
                (data['dune'] == 1) & (np.isin(data['region'], [1, 2]))
                & (data['ndsalix'] < 5),
                282, base_data)

            # 51. Alaska Pacific Alpine Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (np.isin(data['alpine'], [1, 2])) & (data['fldpln'] != 1)
                & (np.isin(data['region'], [9, 10])),
                51, base_data)

            # 176. Alaska-Yukon Alpine Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (np.isin(data['alpine'], [1, 2])) & (data['fldpln'] != 1)
                & (np.isin(data['region'], [3, 4, 5, 6, 7])),
                176, base_data)

            # 85. Alaska Pacific Barren & Sparsely Vegetated Active Floodplain
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] == 1) & (data['coast'] != 1)
                & (np.isin(data['region'], [9, 10])),
                85, base_data)

            # 104. Aleutian-Kamchatka Barren & Sparsely Vegetated Active Floodplain
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] == 1) & (data['coast'] != 1)
                & (data['region'] == 8),
                104, base_data)

            # 224. Alaska-Yukon Barren & Sparsely Vegetated Active Floodplain
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] == 1) & (data['coast'] != 1)
                & (np.isin(data['region'], [3, 4, 5, 6, 7])),
                224, base_data)

            # 315. Arctic Barren & Sparsely Vegetated Active Floodplain
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] == 1) & (data['coast'] != 1)
                & (np.isin(data['region'], [1, 2])),
                315, base_data)

            # 100. Alaska Pacific Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] != 1) & (data['coast'] != 1) & (data['alpine'] == 0)
                & (np.isin(data['region'], [9, 10])),
                100, base_data)

            # 110. Aleutian-Kamchatka Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] != 1) & (data['coast'] != 1)
                & (data['region'] == 8),
                110, base_data)

            # 250. Alaska-Yukon Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] != 1) & (data['coast'] != 1) & (data['alpine'] == 0)
                & (np.isin(data['region'], [3, 4, 5, 6, 7])),
                250, base_data)

            # 330. Arctic Barren & Sparsely Vegetated
            base_data = np.where(
                (base_data == 990)
                & (data['fldpln'] != 1) & (data['coast'] != 1)
                & (np.isin(data['region'], [1, 2])),
                330, base_data)

            #### KEY THE COASTAL TYPES
            ####____________________________________________________

            # 41. Alaska Pacific Coastal & Estuarine Barren
            base_data = np.where(
                (base_data == 990) & (data['coast'] == 1) & (np.isin(data['region'], [7, 8, 9, 10])),
                41, base_data)

            # 42. Alaska Pacific Herbaceous Coastal Dune & Beach
            base_data = np.where(
                (~np.isin(base_data, [994, 996, 997, 998]))
                & (data['coast'] == 1) & (np.isin(data['region'], [7, 8, 9, 10]))
                & (((data['herbac'] >= 8) & (data['beach'] >= 3))
                   | ((base_data == 6000)  & (data['beach'] >= 3))),
                42, base_data)

            # 43. Alaska Pacific Coastal Salt Marsh
            base_data = np.where(
                (~np.isin(base_data, [994, 996, 997, 998]))
                & (data['coast'] == 1) & (np.isin(data['region'], [7, 8, 9, 10]))
                & (data['gramin'] >= 10) & (data['halgra'] >= 5),
                43, base_data)

            # 302. Arctic Coastal & Estuarine Barren
            base_data = np.where(
                (base_data == 990) & (data['coast'] == 1) & (np.isin(data['region'], [1, 2])),
                302, base_data)

            # 303. Arctic Herbaceous Coastal Dune & Beach
            base_data = np.where(
                (~np.isin(base_data, [994, 996, 997, 998]))
                & (data['coast'] == 1) & (np.isin(data['region'], [1, 2]))
                & (((data['herbac'] >= 8) & (data['beach'] >= 3))
                   | ((base_data == 6000) & (data['beach'] >= 3))),
                303, base_data)

            # 305. Arctic Coastal Dwarf Willow Graminoid
            base_data = np.where(
                (~np.isin(base_data, [994, 996, 997, 998]))
                & (data['coast'] == 1) & (np.isin(data['region'], [1, 2]))
                & (data['gramin'] >= 10) & (data['halgra'] >= 5) & (data['dsalix'] >= 8),
                305, base_data)

            # 306. Arctic Coastal Salt Marsh
            base_data = np.where(
                (~np.isin(base_data, [994, 996, 997, 998]))
                & (data['coast'] == 1) & (np.isin(data['region'], [1, 2]))
                & (data['gramin'] >= 10) & (data['halgra'] >= 5) & (data['dsalix'] < 8),
                306, base_data)

            #### KEY THE FRESHWATER MARSH TYPES
            ####____________________________________________________

            # 75. Alaska Pacific Freshwater Marsh
            base_data = np.where(
                (data['coast'] != 1)
                & (np.isin(data['region'], [8, 9, 10]))
                & (data['bromos'] < 70) & (data['sphagn'] < 3) & (data['erivag'] < 3)
                & (data['tree'] < 5) & (data['shrub'] < 5)
                & ((data['dwwater'] >= 30) | (data['water'] >= 20)) & (data['slope'] < 2)
                & (data['dwwater'] < 85) & (data['wetgram'] >= 50),
                75, base_data)

            # 228. Alaska-Yukon Freshwater Marsh
            base_data = np.where(
                (data['coast'] != 1)
                & (np.isin(data['region'], [3, 4, 5, 6, 7]))
                & (data['bromos'] < 70) & (data['sphagn'] < 3)  & (data['erivag'] < 3)
                & (data['tree'] < 5) & (data['shrub'] < 5)
                & ((data['dwwater'] >= 30) | (data['water'] >= 20)) & (data['slope'] < 2)
                & (data['dwwater'] < 85) & (data['wetgram'] >= 55),
                228, base_data)

            # 322. Arctic Freshwater Marsh
            base_data = np.where(
                (data['coast'] != 1)
                & (np.isin(data['region'], [1, 2]))
                & (data['bromos'] < 70) & (data['sphagn'] < 3) & (data['erivag'] < 3) & (data['wetsed'] < 20)
                & (data['tree'] < 5) & (data['shrub'] < 5)
                & ((data['dwwater'] >= 30) | (data['water'] >= 30)) & (data['slope'] < 2)
                & (data['dwwater'] < 85) & ((data['wetgram'] >= 50) | (data['wetsed'] >= 8)),
                322, base_data)

            #### APPLY CORRECTIONS
            ####____________________________________________________

            # If no other base type assigned, assign herbaceous type from ESA
            base_data = np.where((base_data == 0) & (np.isin(data['esa'], [30, 90, 100])),
                                 6000, base_data)

            # If no other base type assigned, assign water type from ESA
            base_data = np.where((base_data == 0) & (data['esa'] == 80),
                                 998, base_data)

            #### RUN REGULAR PROGRAMMATIC KEYS
            ####____________________________________________________

            # Key for needleleaf forest
            type_data = key_needleleaf(data, base_data)

            # Key for broadleaf forest
            type_data = key_broadleaf(data, type_data)

            # Key for mixed forest
            type_data = key_mixed(data, type_data)

            # Key for tussock tundra
            type_data = key_tussock(data, type_data)

            # Key for shrub
            type_data = key_shrub(data, type_data)

            # Key for herbaceous
            type_data = key_herbaceous(data, type_data)

            #### POST-PROCESSING
            ####____________________________________________________

            # Create post-processing mask
            omitted_mask = np.isin(type_data, [994, 995, 996, 998])
            target_mask = ~(omitted_mask | (type_data == nodata_value))
            
            # Isolate target data
            isolated_data = np.where(target_mask, type_data, nodata_value)

            # Apply incremental sieve
            print('\tApplying size threshold...')
            sieve_data = features.sieve(isolated_data.astype('int16'), size=20, connectivity=4)

            # Fill no data using a categorical nibble
            print('\tFilling no data...')
            sieve_data = np.where(
                (sieve_data == 0) | (sieve_data == 990) | (sieve_data >= 1000),
                nodata_value, sieve_data)
            nibble_data = categorical_nibble(sieve_data, nodata_value)

            # Generalize the raster shapes with majority filter
            print('\tApplying majority filter...')
            filter_data = apply_smoothing_filter(nibble_data, window_size=3, iterations=2)

            # Apply sieve
            print('\tApplying size threshold...')
            sieve_data = features.sieve(filter_data.astype('int16'), size=20, connectivity=4)
            sieve_data = features.sieve(sieve_data.astype('int16'), size=30, connectivity=4)
            sieve_data = features.sieve(sieve_data.astype('int16'), size=30, connectivity=4)

            # Add omitted data into final raster
            print('\tAdding omitted data...')
            combine_data = np.where(omitted_mask, type_data, sieve_data)

            # Generalize the raster shapes with majority filter
            print('\tApplying majority filter...')
            filter_data = apply_smoothing_filter(combine_data, window_size=3, iterations=1)

            # Extract to study area
            print('\tExtracting to study area...')
            export_data = np.where(data['area'] == 1, filter_data, nodata_value)

            # Crop the export data to the export extent
            export_data = export_data[
                row_offset: row_offset + dst_height,
                col_offset: col_offset + dst_width
            ]

            # Write results
            dst.write(export_data.astype('int16'), 1)

        # Upload and Clean Up
        print('Uploading raster dataset to Google Cloud Storage...')
        upload_to_gcs(type_output, gcs_output, storage_client)
        os.remove(type_output)
        end_timing(start_time)
    else:
        print(f'{grid} already exists.')

    # Increase count
    grid_count += 1

# Close all raster connections
for src in raster_sources.values():
    src.close()

# Create finished file
print('Writing final output message...')
finished_output = os.path.join(output_folder, f'{processor:02d}_Finished.txt')
with open(finished_output, "w") as file:
    file.write("finished")
gcs_output = f'gs://akveg-data/veg_type_v2p1/rasters_gridded/{processor:02d}_Finished.txt'
upload_to_gcs(finished_output, gcs_output, storage_client)
print('Processing finished.')
