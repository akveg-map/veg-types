# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to herbaceous types
# Author: Timm Nawrocki
# Last Updated: 2025-08-05
# Usage: Execute in Python 3.9+.
# Description: "Key to herbaceous types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_herbaceous(data, in_block):
    # Import packages
    import numpy as np

    # 6001. Herbaceous Mesic
    out_block = np.where(
        (in_block == 6000) & (data['wetind'] < 15) & (data['wetsed'] < 10)
        & (data['wetforb'] < 20) & (data['wetgram'] < 50) & (data['water'] < 10)
        & (data['sphagn'] < 18) & (((data['peat'] < 50) & ((data['soil'] != 4) | (data['wetind'] < 8)))
                                   | ((data['fldpln'] == 1) & (data['fldplnex'] != 1))),
        6001, in_block)

    # 6002. Herbaceous Wet
    out_block = np.where(
        (out_block == 6000) & ((data['wetind'] >= 15) | (data['wetsed'] >= 10) | (data['wetforb'] >= 20)
                               | (data['wetgram'] >= 50) | (data['water'] >= 10))
        & (data['sphagn'] < 18) & (((data['peat'] < 50) & ((data['soil'] != 4) | (data['wetind'] < 8)))
                                   | ((data['fldpln'] == 1) & (data['fldplnex'] != 1))),
        6002, out_block)

    # 6003. Herbaceous Peat
    out_block = np.where(
        (out_block == 6000)
        & ((data['sphagn'] >= 18) | (data['peat'] >= 50) | ((data['soil'] == 4) & (data['wetind'] >= 8))),
        6003, out_block)

    #### PRIORITY TYPES
    ####____________________________________________________

    # 294. Arctic Ericaceous (-Birch) Lichen Tundra
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7, 8])) & (data['alpine'] == 0)
        & (((data['lichen'] >= 35) & (data['fire'] < 1980))
           | ((data['lichen'] >= 45) & (data['fire'] < 2019))),
        294, out_block)

    # 252. Arctic Non-tussock Polygonal Complex
    out_block = np.where(
        (np.isin(out_block, [6001, 6002, 6003])) & (data['slope'] < 3) & (data['polcom'] == 1)
        & ((data['wetsed'] >= 8) | (data['water'] >= 5))
        & (data['wetsed'] < 30) & (data['sphagn'] < 20) & (data['wetgram'] < 55) & (data['water'] < 18)
        & ((((data['wetsed'] / (data['gramin'] + 0.1)) < 0.8) & ((data['wetsed'] / (data['gramin'] + 0.1)) >= 0.2))
           | ((data['ndshrub'] < 20) & ((data['dryas'] + data['eridwarf'] + data['dsalix']) >= 15))),
        252, out_block)

    #### ALPINE MESIC TYPES
    ####____________________________________________________

    # 52. Alaska Pacific Alpine Mesic Meadow
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [9, 10]))
        & (data['alpine'] == 2) & ((data['fldpln'] == 0) | (data['fldplnex'] == 1)),
        52, out_block)

    # 175. Alaska-Yukon Alpine Meadow Mesic
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['alpine'] == 2) & ((data['fldpln'] == 0) | (data['fldplnex'] == 1)),
        175, out_block)

    #### FLOODPLAIN MESIC TYPES
    ####____________________________________________________

    # 87. Alaska Pacific Forb-Graminoid Active Floodplain
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [9, 10]))
        & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        87, out_block)

    # 105. Aleutian-Kamchatka Forb-Graminoid Active Floodplain
    out_block = np.where(
        (out_block == 6001) & (data['region'] == 8)
        & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        105, out_block)

    # 223. Alaska-Yukon Herbaceous Active Floodplain
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        223, out_block)

    # 314. Arctic Herbaceous Active Floodplain
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [1, 2]))
        & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        314, out_block)

    #### TEMPERATE-SUBPOLAR OCEANIC MESIC TYPES
    ####____________________________________________________

    # 71. Alaska Pacific Calamagrostis - Forb Herbaceous Mesic
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [9, 10])) & (data['mwcalama'] >= 15),
        71, out_block)

    # 72. Alaska Pacific Forb (-Fern) Herbaceous Mesic
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [9, 10])) & (data['mwcalama'] < 15),
        72, out_block)

    # 103. Aleutian-Kamchatka Graminoid - Forb Mesic
    out_block = np.where(
        (out_block == 6001) & (data['region'] == 8),
        103, out_block)

    #### ARCTIC-BOREAL MESIC TYPES
    ####____________________________________________________

    # 193. Alaska-Yukon Forb-Graminoid Meadow Mesic Alkaline
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['alkaline'] == 1),
        193, out_block)

    # 191. Alaska-Yukon Calamagrostis-Forb Meadow Mesic
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['alkaline'] == 0) & (data['mwcalama'] >= 15),
        191, out_block)

    # 192. Alaska-Yukon Forb-Graminoid Meadow Mesic Acidic
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['alkaline'] == 0) & (data['mwcalama'] < 15),
        192, out_block)

    # 276. Arctic Herbaceous Non-Tussock Tundra
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [1, 2])),
        276, out_block)

    #### TEMPERATE-SUBPOLAR OCEANIC WET TYPES
    ####____________________________________________________

    # 73. Alaska Pacific Calamagrostis - Sedge Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [8, 9, 10])) & (data['mwcalama'] >= 15),
        73, out_block)

    # 76. Alaska Pacific Sedge Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [8, 9, 10]))
        & (data['mwcalama'] < 15) & (data['wetsed'] >= 8),
        76, out_block)

    # 74. Alaska Pacific Forb - Graminoid Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [8, 9, 10]))
        & (data['mwcalama'] < 15) & (data['wetsed'] < 8),
        74, out_block)

    #### ARCTIC-BOREAL WET TYPES
    ####____________________________________________________

    # 226. Alaska-Yukon Sedge-Calamagrostis Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['mwcalama'] >= 20),
        226, out_block)

    # 225. Alaska-Yukon Sedge Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['mwcalama'] < 20) & (data['wetsed'] >= 15),
        225, out_block)

    # 227. Alaska-Yukon Forb-Graminoid Meadow Wet (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['mwcalama'] < 20) & (data['wetsed'] < 15),
        227, out_block)

    # 321. Arctic Wet Meadow (Mineral/Riverine)
    out_block = np.where(
        (out_block == 6002) & (np.isin(data['region'], [1, 2])),
        321, out_block)

    #### TEMPERATE-SUBPOLAR OCEANIC PEAT TYPES
    ####____________________________________________________

    # 91. Alaska Pacific (Dwarf Shrub) Sedge-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [8, 9, 10])) & (data['sphagn'] >= 15),
        91, out_block)

    # 94. Alaska Pacific Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [8, 9, 10])) & (data['sphagn'] < 15),
        94, out_block)

    #### ARCTIC-BOREAL PEAT TYPES
    ####____________________________________________________

    # 201. Alaska-Yukon (Dwarf Shrub) Sedge-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['sphagn'] >= 15),
        201, out_block)

    # 206. Alaska-Yukon Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['sphagn'] < 15),
        206, out_block)

    # 262. Arctic Sphagnum-Sedge Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [1, 2])) & (data['sphagn'] >= 15),
        262, out_block)

    # 263. Arctic Brown Moss-Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 6003) & (np.isin(data['region'], [1, 2])) & (data['sphagn'] < 15),
        263, out_block)

    #### APPLY MINEROTROPHIC PEATLAND CORRECTIONS
    ####____________________________________________________

    # Correct Alaska Pacific Sedge Peatland, Minerotrophic
    out_block = np.where(
        (np.isin(out_block, [74, 76])) & ((data['peat'] >= 25) | (data['bromos'] >= 30) | (data['sphagnum'] >= 5))
        & (np.isin(data['region'], [8, 9, 10])),
        94, out_block)

    # Correct Alaska-Yukon Sedge Peatland, Minerotrophic
    out_block = np.where(
        (np.isin(out_block, [225, 227])) & ((data['peat'] >= 40) | (data['bromos'] >= 60) | (data['sphagnum'] >= 5))
        & (np.isin(data['region'], [3, 4, 5, 6, 7])) & ((data['fldpln'] == 0) | (data['fldplnex'] == 1)),
        206, out_block)

    return out_block
