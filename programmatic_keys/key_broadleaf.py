# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to broadleaf types
# Author: Timm Nawrocki
# Last Updated: 2025-07-12
# Usage: Execute in Python 3.9+.
# Description: "Key to broadleaf types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_broadleaf(data, in_block):

    # Import packages
    import numpy as np

    #### FLOODPLAIN TYPES
    ####____________________________________________________

    # 22. Alaska Pacific Cottonwood Riparian Forest
    out_block = np.where(
        (in_block == 2000) & (data['populbt'] >= 8) & (data['fldpln'] == 1),
        22, in_block)

    # 213. Birch (-White Spruce) Active Floodplain
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3) & (data['fldpln'] == 1)
        & (data['populbt'] < (data['bettre'] * 0.8)) & (data['bettre'] >= data['poptre']),
        213, out_block)

    # 214. Poplar (-White Spruce) Active Floodplain
    out_block = np.where(
        (out_block == 2000) & (data['populbt'] >= 3) & (data['fldpln'] == 1)
        & (data['populbt'] >= (data['bettre'] * 0.8)) & (data['populbt'] >= data['poptre']),
        214, out_block)

    #### TEMPERATE TYPES
    ####____________________________________________________

    # 2. Alaska Pacific Birch Forest Mesic
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3) & (np.isin(data['region'], [9, 10]))
        & (data['bettre'] >= data['poptre']) & (data['bettre'] >= data['populbt']),
        2, out_block)

    # 3. Alaska Pacific Sitka Spruce - Cottonwood Forest Mesic
    out_block = np.where(
        (out_block == 2000) & (data['populbt'] >= 3)
        & (data['tree'] >= 20) & (np.isin(data['region'], [9, 10]))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        3, out_block)

    #### BOREAL AND BOREAL-TEMPERATE TYPES
    ####____________________________________________________

    # 161. Alaska-Yukon Aspen Dry Woodland / Steppe Bluff
    out_block = np.where(
        (out_block == 2000) & (data['poptre'] >= 3)
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre'])
        & (data['slope'] >= 12) & (data['aspect'] >= 300) & (data['fire'] < 1990),
        161, out_block)

    # 162. Alaska-Yukon Aspen Forest Mesic (Successional)
    out_block = np.where(
        (out_block == 2000) & (data['poptre'] >= 3)
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre'])
        & ((data['slope'] < 12) | (data['aspect'] < 300)) & (data['fire'] < 1990),
        162, out_block)

    # 163. Alaska-Yukon Post-burn Aspen Forest Mesic
    out_block = np.where(
        (out_block == 2000) & (data['poptre'] >= 3)
        & (data['bettre'] < data['poptre']) & (data['populbt'] < data['poptre'])
        & (data['fire'] >= 1990),
        163, out_block)

    # 153. Alaska-Yukon Poplar Woodland Mesic
    out_block = np.where(
        (out_block == 2000) & (data['populbt'] >= 3)
        & ((data['tree'] < 20) | (np.isin(data['region'], [1, 2, 3, 4, 5])))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        153, out_block)

    # 136. Alaska-Yukon Poplar Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 2000) & (data['populbt'] >= 3)
        & (data['tree'] >= 20) & (np.isin(data['region'], [6, 7, 8]))
        & (data['populbt'] >= data['poptre']) & (data['bettre'] < data['populbt']),
        136, out_block)

    # 111. Alaska-Yukon Birch Forest Mesic (Central)
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] < 1990) & (np.isin(data['region'], [1, 2, 3, 4, 5])),
        111, out_block)

    # 116. Alaska-Yukon Post-burn Recovering Birch Forest Mesic (Central)
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] >= 1990) & (np.isin(data['region'], [1, 2, 3, 4, 5])),
        116, out_block)

    # 131. Alaska-Yukon Birch Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] < 1990) & (np.isin(data['region'], [6, 7, 8])),
        131, out_block)

    # 137. Alaska-Yukon Post-burn Recovering Birch Forest Mesic (Southern)
    out_block = np.where(
        (out_block == 2000) & (data['bettre'] >= 3)
        & (data['bettre'] >= data['populbt']) & (data['bettre'] >= data['poptre'])
        & (data['fire'] >= 1990) & (np.isin(data['region'], [6, 7, 8])),
        137, out_block)

    return out_block
