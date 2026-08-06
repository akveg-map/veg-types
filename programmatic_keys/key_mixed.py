# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to mixed tree types
# Author: Timm Nawrocki
# Last Updated: 2025-08-04
# Usage: Execute in Python 3.9+.
# Description: "Key to mixed tree types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_mixed(data, in_block):

    # Import packages
    import numpy as np

    #### FLOODPLAIN TYPES
    ####____________________________________________________

    # 21. Alaska Pacific Cottonwood - Sitka Spruce / Western Hemlock Riparian Forest
    out_block = np.where(
        (in_block == 3000) & (np.isin(data['region'], [8, 9]))
        & ((data['fldpln'] == 1) & (data['fldplnex'] != 1))
        & ((data['picsit'] >= 3) | (data['tsuhet'] >= 3) | (data['populbt'] >= 3)),
        21, in_block)

    # 213. Birch (-White Spruce) Active Floodplain
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3) & ((data['fldpln'] == 1) & (data['fldplnex'] != 1))
        & (data['populbt'] < (data['bettre'] * 0.8)) & (data['bettre'] >= data['poptre']),
        213, out_block)

    # 214. Poplar (-White Spruce) Active Floodplain
    out_block = np.where(
        (out_block == 3000) & (data['populbt'] >= 3) & ((data['fldpln'] == 1) & (data['fldplnex'] != 1))
        & (data['populbt'] >= (data['bettre'] * 0.8))  & (data['populbt'] >= data['poptre']),
        214, out_block)

    #### TEMPERATE TYPES
    ####____________________________________________________

    # 2. Alaska Pacific Birch Forest Mesic
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3) & (data['picgla'] < 3) & (np.isin(data['region'], [9, 10]))
        & (data['bettre'] >= data['poptre']) & (data['bettre'] >= data['populbt']),
        2, out_block)

    # 3. Alaska Pacific Sitka Spruce - Cottonwood Forest Mesic
    out_block = np.where(
        (out_block == 3000) & ((data['populbt'] >= 3))
        & (data['tree'] >= 20) & (np.isin(data['region'], [9, 10]))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        3, out_block)

    #### POST-FIRE TYPES
    ####____________________________________________________

    # 163. Alaska-Yukon Post-burn Recovering Aspen Forest Mesic
    out_block = np.where(
        (out_block == 3000) & (data['poptre'] >= 3)
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre'])
        & (data['fire'] >= 1990),
        163, out_block)

    # 116. Alaska-Yukon Post-burn Recovering Birch Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] >= 1990) & (np.isin(data['region'], [1, 2, 3, 4, 5])),
        116, out_block)

    # 137. Alaska-Yukon Post-burn Recovering Birch Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] >= 1990) & (np.isin(data['region'], [6, 7, 8])),
        137, out_block)

    #### BOREAL TYPES
    ####____________________________________________________

    # 113. Alaska-Yukon Black Spruce-Deciduous Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['brotre'] >= 3) & (data['picmar'] >= 3)
        & (data['picratio'] < 40) & (np.isin(data['region'], [1, 2, 3, 4, 5])),
        113, out_block)

    # 133. Alaska-Yukon Black Spruce-Deciduous Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['brotre'] >= 3) & (data['picmar'] >= 3)
        & (data['picratio'] < 40) & (np.isin(data['region'], [6, 7, 8, 9, 10])),
        133, out_block)

    # 115. Alaska-Yukon Mixed Spruce-Deciduous Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['brotre'] >= 3) & (data['picmar'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 40) & (data['picratio'] < 60) & (np.isin(data['region'], [1, 2, 3, 4, 5])),
        115, out_block)

    # 135. Alaska-Yukon Mixed Spruce-Deciduous Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['brotre'] >= 3) & (data['picmar'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 40) & (data['picratio'] < 60) & (np.isin(data['region'], [6, 7, 8, 9, 10])),
        135, out_block)

    # 118. Alaska-Yukon White Spruce-Aspen Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['poptre'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre']),
        118, out_block)

    # 139. Alaska-Yukon White Spruce-Aspen Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['poptre'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre']),
        139, out_block)

    # 120. Alaska-Yukon White Spruce-Poplar Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['populbt'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        120, out_block)

    # 141. Alaska-Yukon White Spruce-Poplar Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['populbt'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        141, out_block)

    # 119. Alaska-Yukon White Spruce-Birch Forest Mesic (Central)
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [1, 2, 3, 4, 5]))
        & (data['bettre'] >= data['poptre']) & (data['bettre'] >= data['populbt']),
        119, out_block)

    # 140. Alaska-Yukon White Spruce-Birch Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 3000) & (data['bettre'] >= 3) & (data['picgla'] >= 3)
        & (data['picratio'] >= 60) & (np.isin(data['region'], [6, 7, 8, 9, 10]))
        & (data['bettre'] >= data['poptre']) & (data['bettre'] >= data['populbt']),
        140, out_block)

    #### APPLY FLOODPLAIN CORRECTIONS
    ####____________________________________________________

    # Apply corrections to cottonwood - spruce floodplain
    out_block = np.where(
        (out_block == 3) & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        21, out_block)

    # Apply corrections to poplar - white spruce floodplain
    out_block = np.where(
        (np.isin(out_block, [120, 141])) & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        214, out_block)

    # Apply corrections to birch - white spruce floodplain
    out_block = np.where(
        (np.isin(out_block, [119, 140])) & ((data['fldpln'] == 1) & (data['fldplnex'] != 1)),
        213, out_block)

    return out_block
