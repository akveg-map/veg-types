# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to tussock types
# Author: Timm Nawrocki
# Last Updated: 2025-08-03
# Usage: Execute in Python 3.9+.
# Description: "Key to tussock types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_tussock(data, in_block):

    # Import packages
    import numpy as np

    #### BOREAL TYPES
    ####____________________________________________________

    # 205. Alaska-Yukon Tussock Peatland, Ombrotrophic
    out_block = np.where(
        (in_block == 4000) & (data['sphagn'] >= 20),
        205, in_block)

    #### POLYGONAL COMPLEXES
    ####____________________________________________________

    # 252. Arctic Non-tussock Polygonal Complex
    out_block = np.where(
        (out_block == 4000) & (data['slope'] < 3) & (data['polcom'] == 1)
        & ((data['wetsed'] >= 8) | (data['water'] >= 5))
        & (data['subzoneC'] == 1) & (data['erivag'] < 25),
        252, out_block)

    # 254. Arctic Tussock Tundra Polygonal Complex
    out_block = np.where(
        (out_block == 4000) & (data['slope'] < 3) & (data['polcom'] == 1)
        & ((data['wetsed'] >= 8) | (data['water'] >= 5)),
        254, out_block)

    #### ARCTIC TYPES
    ####____________________________________________________

    # 294. Arctic Ericaceous (-Birch) Lichen Tundra
    out_block = np.where(
        (out_block == 6001) & (np.isin(data['region'], [1, 2, 3, 4, 5, 6, 7, 8])) & (data['alpine'] == 0)
        & (((data['lichen'] >= 35) & (data['fire'] < 1980))
           | ((data['lichen'] >= 45) & (data['fire'] < 2019))),
        294, out_block)

    # 272. Arctic Tussock Dwarf Shrub Tundra
    out_block = np.where(
        (out_block == 4000) & (data['ndshrub'] < 15),
        272, out_block)

    # 274. Arctic Tussock Low Shrub Tundra
    out_block = np.where(
        (out_block == 4000) & (data['ndshrub'] >= 15),
        274, out_block)

    return out_block
