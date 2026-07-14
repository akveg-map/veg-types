# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Key to tussock types
# Author: Timm Nawrocki
# Last Updated: 2025-07-13
# Usage: Execute in Python 3.9+.
# Description: "Key to tussock types" defines a programmatic key as a function.
# ---------------------------------------------------------------------------

def key_tussock(data, in_block):

    #### BOREAL TYPES
    ####____________________________________________________

    # 205. Alaska-Yukon Tussock Peatland, Ombrotrophic
    out_block = np.where(
        (in_block == 4000) & (data['sphagn'] >= 12) & (np.isin(data['region'], [3, 4, 5, 6, 7, 8])),
        205, in_block)

    #### POLYGONAL COMPLEXES
    ####____________________________________________________

    # 254. Arctic Tussock Tundra Polygonal Complex
    out_block = np.where(
        (out_block == 4000) & (data['wetsed'] >= 8) & (data['slope'] < 3) & (data['polcom'] == 1),
        254, out_block)

    #### ARCTIC TYPES
    ####____________________________________________________

    # 294. Arctic Ericaceous (-Birch) Lichen Tundra
    out_block = np.where(
        (out_block == 4000) & (data['lichen'] >= 25),
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
