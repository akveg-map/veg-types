# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to shrub types
# Author: Timm Nawrocki
# Last Updated: 2025-08-03
# Usage: Execute in Python 3.9+.
# Description: "Key to shrub types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_shrub(data, in_block):

    # Import packages
    import numpy as np

    # 5001. Shrub Mesic
    out_block = np.where(
        (in_block == 5000) & (data['wetind'] < 15) & (data['wetforb'] < 20)
        & (data['wetgram'] < 50) & (data['water'] < 10)
        & (data['sphagn'] < 20) & (((data['peat'] < 50) & (data['soil'] != 4)) | (data['fldpln'] == 1)),
        5001, in_block)

    # 5002. Shrub Wet
    out_block = np.where(
        (out_block == 5000) & ((data['wetind'] >= 15) | (data['wetforb'] >= 20)
                               | (data['wetgram'] >= 50) | (data['water'] >= 10))
        & (data['sphagn'] < 20) & (((data['peat'] < 50) & (data['soil'] != 4)) | (data['fldpln'] == 1)),
        5002, out_block)

    # 5003. Shrub Peat
    out_block = np.where(
        (out_block == 5000)
        & ((data['sphagn'] >= 20) | (data['peat'] >= 50) | (data['soil'] == 4)),
        5003, out_block)

    #### PRIORITY TYPES
    ####____________________________________________________

    # 294. Arctic Ericaceous (-Birch) Lichen Tundra
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7, 8])) & (data['alpine'] == 0)
        & (((data['lichen'] >= 35) & (data['fire'] < 1980))
           | ((data['lichen'] >= 45) & (data['fire'] < 2019))),
        294, out_block)

    # 173. Alaska-Yukon Dwarf Shrub-Lichen
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (np.isin(data['alpine'], [1, 2])) & (data['ndshrub'] < 15) & (data['lichen'] >= 35),
        173, out_block)

    # 252. Arctic Non-tussock Polygonal Complex
    out_block = np.where(
        (np.isin(out_block, [5001, 5002, 5003])) & (data['slope'] < 3) & (data['polcom'] == 1)
        & ((data['wetsed'] >= 8) | (data['water'] >= 5))
        & (data['wetsed'] < 30) & (data['sphagn'] < 20) & (data['wetgram'] < 55)
        & ((((data['wetsed'] / (data['gramin'] + 0.1)) < 0.8) & ((data['wetsed'] / (data['gramin'] + 0.1)) >= 0.2))
           | ((data['ndshrub'] < 15) & ((data['dryas'] + data['eridwarf'] + data['dsalix']) >= 8))),
        252, out_block)

    # 185. Alaska-Yukon Post-burn Birch-Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (data['fire'] >= 1990) & ((data['ndsalix'] + data['betshr']) >= 5),
        185, out_block)

    # 244. Alaska-Yukon Post-Burn Recovering Birch-Willow Wet
    out_block = np.where(
        (out_block == 5002) & (data['fire'] >= 1990) & ((data['ndsalix'] + data['betshr']) >= 5),
        244, out_block)

    #### TEMPERATE ALPINE
    ####____________________________________________________

    # 54. Alaska Pacific Alpine Ericaceous Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [8, 9, 10])) & (np.isin(data['alpine'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] < 15) & (data['eridwarf'] >= 5)
        & ((data['dryas'] + data['dsalix']) < data['eridwarf']),
        54, out_block)

    # 55. Alaska Pacific Alpine Willow (-Dryas) Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [8, 9, 10])) & (np.isin(data['alpine'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] < 15) & (data['dsalix'] >= 5)
        & ((data['dryas'] + data['dsalix']) >= data['eridwarf']) & (data['dsalix'] >= (data['dryas'] * 0.5)),
        55, out_block)

    # 53. Alaska Pacific Alpine Dryas Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [8, 9, 10])) & (np.isin(data['alpine'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] < 15) & (data['dryas'] >= 5)
        & ((data['dryas'] + data['dsalix']) >= data['eridwarf']) & (data['dsalix'] < (data['dryas'] * 0.5)) ,
        53, out_block)

    #### TEMPERATE FLOODPLAIN
    ####____________________________________________________

    # 84. Alaska Pacific Alder-Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        84, out_block)

    # 88. Alaska Pacific Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)),
        88, out_block)

    # 86. Alaska Pacific Dryas Dwarf Shrub Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 1) & (data['ndshrub'] < 15) & (data['dryas'] >= 5),
        86, out_block)

    #### TEMPERATE MESIC
    ####____________________________________________________

    # 64. Alaska Pacific Salmonberry Mesic
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (data['ndshrub'] >= 15)
        & (data['rubspe'] > ((data['alnus']) + data['ndsalix']) * 0.8) & (data['rubspe'] >= 8),
        64, out_block)

    # 61. Alaska Pacific Alder Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 1.5)),
        61, out_block)

    # 62. Alaska Pacific Alder-Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 1.5)) & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        62, out_block)

    # 65. Alaska Pacific Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [9, 10]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5))
        & (data['ndsalix'] >= ((data['betshr'] + data['erishrub']) * 0.8)),
        65, out_block)

    # 63. Alaska Pacific Ericaceous (-Birch) Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [9, 10]))
        & (data['ndshrub'] >= 15)  & ((data['erishrub'] >= 5) | (data['betshr'] >= 5))
        & ((data['bderishr'] + data['rhoshr'] + data['vaculi'] + data['betshr']) >= 5)
        & (data['ndsalix'] < ((data['betshr'] + data['erishrub']) * 0.8)),
        63, out_block)

    #### TEMPERATE WET
    ####____________________________________________________

    # 81. Alaska Pacific Alder-Willow Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [8, 9, 10]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        81, out_block)

    # 83. Alaska Pacific Willow Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [8, 9, 10]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5))
        & (data['ndsalix'] >= ((data['betshr'] + data['erishrub']) * 0.8)),
        83, out_block)

    # 82. Alaska Pacific Ericaceous (-Birch) Shrub Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [8, 9, 10]))
        & (data['ndshrub'] >= 15) & ((data['erishrub'] >= 5) | (data['betshr'] >= 5))
        & ((data['bderishr'] + data['rhoshr'] + data['vaculi'] + data['betshr']) >= 5)
        & (data['ndsalix'] < ((data['betshr'] + data['erishrub']) * 0.8)),
        82, out_block)

    #### TEMPERATE PEAT
    ####____________________________________________________

    # 92. Alaska Pacific Shrub-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [8, 9, 10])) & (data['sphagn'] >= 15)
        & (data['ndshrub'] >= 15),
        92, out_block)

    # 91. Alaska Pacific (Dwarf Shrub) Sedge-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [8, 9, 10])) & (data['sphagn'] >= 15)
        & (data['ndshrub'] < 15),
        91, out_block)

    # 95. Alaska Pacific Shrub-Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [8, 9, 10])) & (data['sphagn'] < 15),
        95, out_block)

    #### ALEUTIAN-KAMCHATKA TYPES
    ####____________________________________________________

    # 101. Aleutian-Kamchatka Ericaceous (-Willow) Dwarf Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (data['region'] == 8)
        & (data['fldpln'] == 0) & (data['ndshrub'] < 15) & ((data['eridwarf'] >= 5) | (data['dsalix'] >= 5))
        & (data['dryas'] < (data['dsalix'] + data['eridwarf'])),
        101, out_block)

    # 102. Aleutian-Kamchatka Willow Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (data['region'] == 8)
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)),
        102, out_block)

    # 106. Aleutian-Kamchatka Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (data['region'] == 8)
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)),
        106, out_block)

    #### BOREAL FLOODPLAIN
    ####____________________________________________________

    # 221. Alaska-Yukon Alder-Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        221, out_block)

    # 222. Alaska-Yukon Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)),
        222, out_block)

    #### BOREAL DWARF SHRUB
    ####____________________________________________________

    # 172. Alaska-Yukon Dryas-Willow Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['ndshrub'] < 15) & ((data['dryas'] >= 3) | (data['dsalix'] >= 3))
        & ((data['eridwarf'] < data['dsalix']) | (data['eridwarf'] < (data['dryas'] * 0.5))),
        172, out_block)

    # 171. Alaska-Yukon Dryas-Ericaceous Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['ndshrub'] < 15) & (data['dryas'] >= 3) & (data['eridwarf'] >= 3)
        & (data['eridwarf'] >= data['dsalix']) & (data['dryas'] >= (data['eridwarf'] * 0.5)),
        171, out_block)

    # 174. Alaska-Yukon Ericaceous Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['ndshrub'] < 15) & ((data['dryas'] >= 3) | (data['eridwarf'] >= 3))
        & (data['eridwarf'] >= data['dsalix']) & (data['dryas'] < (data['eridwarf'] * 0.5)),
        174, out_block)

    #### BOREAL MESIC
    ####____________________________________________________

    # 181. Alaska-Yukon Alder Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 1.5)),
        181, out_block)

    # 182. Alaska-Yukon Alder-Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 1.5)) & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        182, out_block)

    # 186. Alaska-Yukon Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)) & (data['ndsalix'] >= (data['betshr'] * 1.5)),
        186, out_block)

    # 184. Alaska-Yukon Birch-Willow Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['betshr'] >= 5)
        & (data['ndsalix'] >= (data['erishrub'] * 0.8)) & (data['ndsalix'] < (data['betshr'] * 1.5)),
        184, out_block)

    # 183. Alaska-Yukon Ericaceous (-Birch) Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['erishrub'] >= 5)
        & (data['ndsalix'] < (data['erishrub'] * 0.8)),
        183, out_block)

    #### ARCTIC-BOREAL WET
    ####____________________________________________________

    # 243. Alaska-Yukon Alder-Willow Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        243, out_block)

    # 242. Alaska-Yukon Willow Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)) & (data['ndsalix'] >= (data['betshr'] * 1.5)),
        242, out_block)

    # 241. Alaska-Yukon Birch-Willow Wet
    out_block = np.where(
        (out_block == 5002) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7]))
        & (data['ndshrub'] >= 15) & (data['betshr'] >= 5)
        & (data['ndsalix'] < (data['betshr'] * 1.5)),
        241, out_block)

    #### BOREAL PEAT
    ####____________________________________________________

    # 204. Alaska-Yukon Shrub-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['sphagn'] >= 15)
        & (data['ndshrub'] >= 15) & (data['erivag'] < 15),
        204, out_block)

    # 201. Alaska-Yukon (Dwarf Shrub) Sedge-Sphagnum Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['sphagn'] >= 15)
        & (data['ndshrub'] < 15) & (data['erivag'] < 15),
        201, out_block)

    # 205. Alaska-Yukon Tussock Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['erivag'] >= 15),
        205, out_block)

    # 207. Alaska-Yukon Shrub-Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [3, 4, 5, 6, 7])) & (data['sphagn'] < 15)
        & (data['erivag'] < 15),
        207, out_block)

    #### ARCTIC FLOODPLAIN
    ####____________________________________________________

    # 311. Arctic Alder (-Willow) Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        311, out_block)

    # 312. Arctic Willow Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 1) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)),
        312, out_block)

    # 313. Arctic Dryas (-Willow-Ericaceous) Active Floodplain
    out_block = np.where(
        (np.isin(out_block, [5001, 5002])) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 1) & (data['ndshrub'] < 15)
        & ((data['dryas'] >= 5) | (data['dsalix'] >= 5) | (data['eridwarf'] >= 5))
        & (data['nerishr'] < 15),
        313, out_block)

    #### ARCTIC MESIC
    ####____________________________________________________

    # 291. Arctic Alder (-Willow) Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['alnus'] >= 5)
        & (data['alnus'] >= (data['ndsalix'] * 0.5)),
        291, out_block)

    # 293. Arctic Willow Low Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['ndsalix'] >= 5)
        & (data['alnus'] < (data['ndsalix'] * 0.5)) & (data['ndsalix'] >= (data['betshr'] * 1.5)),
        293, out_block)

    # 292. Arctic Birch (-Willow) Shrub Mesic
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [1, 2]))
        & (data['fldpln'] == 0) & (data['ndshrub'] >= 15) & (data['betshr'] >= 5)
        & (data['ndsalix'] < (data['betshr'] * 1.5)),
        292, out_block)

    # 284. Arctic Ericaceous (-Dryas) Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [1, 2]))
        & (data['erishrub'] >= 5) & (data['erishrub'] >= (data['dryas'] * 0.5))
        & (data['erishrub'] >= (data['dsalix'] + 0.1)),
        284, out_block)

    # 283. Arctic Dryas (-Willow) Dwarf Shrub
    out_block = np.where(
        (out_block == 5001) & (np.isin(data['region'], [1, 2]))
        & ((data['dryas'] >= 5) | (data['dsalix'] >= 5))
        & ((data['erishrub'] < (data['dryas'] * 0.5)) | (data['erishrub'] < (data['dsalix'] + 0.1))),
        283, out_block)

    #### ARCTIC PEAT
    ####____________________________________________________

    # 261. Arctic Shrub-Sedge Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [1, 2]))
        & ((data['sphagn'] >= 15) | ((data['betshr'] / (data['betshr'] + data['ndsalix'] + 0.1)) >= 0.2)),
        261, out_block)

    # 264. Arctic Shrub-Sedge Peatland, Minerotrophic
    out_block = np.where(
        (out_block == 5003) & (np.isin(data['region'], [1, 2]))
        & ((data['sphagn'] < 15) & ((data['betshr'] / (data['betshr'] + data['ndsalix'] + 0.1)) < 0.2)),
        264, out_block)

    return out_block
