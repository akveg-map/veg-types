# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to needleleaf types
# Author: Timm Nawrocki
# Last Updated: 2025-07-12
# Usage: Execute in Python 3.9+.
# Description: "Key to needleleaf types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_needleleaf(data, in_block):

    # Import packages
    import numpy as np

    # 24. Alaska Pacific Sitka Spruce Riparian Forest
    out_block = np.where(
        (in_block == 1000) & (data['picsit'] >= 8) & (data['fldpln'] == 1),
        24, in_block)

    # 1001. Needleleaf Mesic
    out_block = np.where(
        (out_block == 1000)
        & (data['wetind'] < 8) & (data['wetforb'] < 20) & (data['erivag'] < 12)
        & (data['wetgram'] < 50) & (data['water'] < 10) & (data['pinus'] < 99),
        1001, out_block)

    # 1002. Needleleaf Wet
    out_block = np.where(
        (out_block == 1000)
        & ((data['wetind'] >= 8) | (data['wetforb'] >= 20) | (data['erivag'] >= 12)
           | (data['wetgram'] >= 50) | (data['water'] >= 10) | (data['pinus'] >= 99)),
        1002, out_block)

    #### TEMPERATE MESIC
    ####____________________________________________________

    # 15. Alaska Pacific Subalpine Fir (-Mountain Hemlock) Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['abies'] >= 55) & (data['alpine'] == 0),
        15, out_block)

    # 16. Alaska Pacific Subalpine Fir Subalpine Woodland Mesic
    out_block = np.where(
        (out_block == 1001) & (data['abies'] >= 55) & (np.isin(data['alpine'], [1, 2])),
        16, out_block)

    # 7. Alaska Pacific Yellow Cedar (-Western Hemlock) Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['calnoo'] >= 99)  & (data['alpine'] == 0),
        7, out_block)

    # 4. Alaska Pacific Sitka Spruce Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['picsit'] >= 5) & (data['alpine'] == 0)
        & (data['picsit'] >= (data['picgla'] + data['picmar']))
        & (data['tsumer'] < (data['picsit'] * 0.5))
        & (data['tsuhet'] < (data['picsit'] * 0.8)),
        4, out_block)

    # 5. Alaska Pacific Western Hemlock (-Sitka Spruce) Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['tsuhet'] >= 5) & (data['alpine'] == 0)
        & (data['tsuhet'] >= (data['picsit'] * 0.8))
        & (data['tsuhet'] >= data['tsumer']),
        5, out_block)

    # 11. Alaska Pacific Mountain Hemlock - Sitka/Lutz Spruce Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['tsumer'] > 5) & (data['alpine'] == 0)
        & (data['tsumer'] >= (data['picsit'] * 0.5))
        & (data['tsumer'] < (data['picsit'] * 1.5))
        & (data['tsuhet'] < data['tsumer']),
        11, out_block)

    # 12. Alaska Pacific Mountain Hemlock Forest Mesic
    out_block = np.where(
        (out_block == 1001) & (data['tsumer'] > 5) & (data['alpine'] == 0)
        & (data['tsumer'] >= (data['picsit'] * 1.5))
        & (data['tsuhet'] < data['tsumer']),
        12, out_block)

    #### TEMPERATE WET
    ####____________________________________________________

    # 34. Alaska Pacific Yellow Cedar (-Western Hemlock / Mountain Hemlock) Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['calnoo'] >= 99) & (data['alpine'] == 0),
        34, out_block)

    # 93. Alaska Pacific Sitka Spruce (-Shore Pine) Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 1002) & ((data['sphagn'] >= 12) | (data['wetsed'] >= 10) | (data['peat'] >= 35))
        & ((data['picsit'] >= 3) | (data['pinus'] >= 99)),
        93, out_block)

    # 32. Alaska Pacific Sitka Spruce Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['picsit'] >= 5) & (data['alpine'] == 0)
        & (data['picsit'] >= (data['picgla'] + data['picmar']))
        & (data['tsumer'] < (data['picsit'] * 0.5))
        & (data['tsuhet'] < (data['picsit'] * 0.8)),
        32, out_block)

    # 33. Alaska Pacific Western Hemlock (-Sitka Spruce) Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['tsuhet'] >= 5) & (data['alpine'] == 0)
        & (data['tsuhet'] >= (data['picsit'] * 0.8))
        & (data['tsuhet'] >= data['tsumer']),
        33, out_block)

    # 31. Alaska Pacific Sitka Spruce - Mountain Hemlock Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['tsumer'] > 5) & (data['alpine'] == 0)
        & (data['tsumer'] >= (data['picsit'] * 0.5))
        & (data['tsuhet'] < data['tsumer']),
        31, out_block)

    #### TEMPERATE SUBALPINE
    ####____________________________________________________

    # 13. Alaska Pacific Mountain Hemlock Subalpine Woodland Mesic
    out_block = np.where(
        (np.isin(out_block, [1001, 1002])) & (data['tsumer'] >= 3) & (np.isin(data['alpine'], [1, 2]))
        & (data['tsumer'] >= data['picsit']),
        13, out_block)

    # 14. Alaska Pacific Sitka Spruce Subalpine Woodland Mesic
    out_block = np.where(
        (np.isin(out_block, [1001, 1002])) & (data['picsit'] >= 3) & (np.isin(data['alpine'], [1, 2]))
        & (data['tsumer'] < data['picsit']),
        14, out_block)

    #### BOREAL MESIC
    ####____________________________________________________

    # 212. Alaska-Yukon White Spruce Active Floodplain
    out_block = np.where(
        (out_block == 1001) & (data['picgla'] >= 8) & (data['picratio'] >= 40) & (data['fldpln'] == 1),
        212, out_block)

    # 154. Alaska-Yukon Spruce-Lichen Woodland Mesic
    out_block = np.where(
        (out_block == 1001) & (data['lichen'] >= 25) & ((data['picgla'] >= 3) | (data['picmar'] >= 3)),
        154, out_block)

    # 155. Alaska-Yukon White Spruce Woodland Mesic
    out_block = np.where(
        (out_block == 1001) & (data['neetre'] < 20) & (data['picratio'] >= 60),
        155, out_block)

    # 151. Alaska-Yukon Black Spruce Woodland Mesic
    out_block = np.where(
        (out_block == 1001)  & (data['neetre'] < 20) & (data['picratio'] < 40),
        151, out_block)

    # 152. Alaska-Yukon Mixed Spruce Woodland Mesic
    out_block = np.where(
        (out_block == 1001) & (data['neetre'] < 20) & (data['picratio'] >= 40) & (data['picratio'] < 60),
        152, out_block)

    # 117. Alaska-Yukon White Spruce Forest Mesic (Central)
    out_block = np.where(
        (out_block == 1001) & (data['picgla'] >= 3) & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['neetre'] >= 20) & (data['picratio'] >= 60),
        117, out_block)

    # 138. Alaska-Yukon White Spruce Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 1001) & (data['picgla'] >= 3) & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['neetre'] >= 20) & (data['picratio'] >= 60),
        138, out_block)

    # 112. Alaska-Yukon Black Spruce Forest Mesic (Central)
    out_block = np.where(
        (out_block == 1001) & (data['picmar'] >= 3) & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['neetre'] >= 20) & (data['picratio'] < 40),
        112, out_block)

    # 132. Alaska-Yukon Black Spruce Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 1001) & (data['picmar'] >= 3) & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['neetre'] >= 20) & (data['picratio'] < 40),
        132, out_block)

    # 114. Alaska-Yukon Mixed Spruce Forest Mesic (Central)
    out_block = np.where(
        (out_block == 1001) & (data['picmar'] >= 3) & (data['picgla'] >= 3)
        & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['neetre'] >= 20) & (data['picratio'] >= 40) & (data['picratio'] < 60),
        114, out_block)

    # 134. Alaska-Yukon Mixed Spruce Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 1001) & (data['picmar'] >= 3) & (data['picgla'] >= 3)
        & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['neetre'] >= 20) & (data['picratio'] >= 40) & (data['picratio'] < 60),
        134, out_block)

    #### BOREAL WET
    ####____________________________________________________

    # 203. Alaska-Yukon Black Spruce-Tussock Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 1002) & (data['picmar'] >= 3) & (data['picratio'] < 40) & (data['erivag'] >= 8),
        203, out_block)

    # 217. Alaska-Yukon Tamarack (-Black Spruce) Peatland
    out_block = np.where(
        (out_block == 1002) & ((data['sphagn'] >= 12) | (data['wetsed'] >= 10) | (data['peat'] >= 35))
        & (data['larlar'] >= 90),
        217, out_block)

    # 202. Alaska-Yukon Black Spruce Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 1002) & ((data['sphagn'] >= 12) | (data['wetsed'] >= 10) | (data['peat'] >= 35))
        & (data['picmar'] >= 3) & (data['picratio'] < 60),
        202, out_block)

    # 216. Alaska-Yukon White Spruce Peatland, Ombrotrophic
    out_block = np.where(
        (out_block == 1002) & ((data['sphagn'] >= 12) | (data['wetsed'] >= 10) | (data['peat'] >= 35))
        & (data['picgla'] >= 3) & (data['picratio'] >= 60),
        216, out_block)

    # 211. Alaska-Yukon Black Spruce Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['sphagn'] < 12) & (data['wetsed'] < 10)
        & (data['picmar'] >= 3) & (data['picratio'] < 60),
        211, out_block)

    # 215. Alaska-Yukon White Spruce Forest Wet
    out_block = np.where(
        (out_block == 1002) & (data['sphagn'] < 12) & (data['wetsed'] < 10)
        & (data['picgla'] >= 3) & (data['picratio'] >= 60),
        215, out_block)

    return out_block
