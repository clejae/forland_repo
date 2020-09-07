import ogr
import gdal
import pandas as pd
import numpy as np
import time
import os

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")

# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)


wuchs_pth = r'_temp\00_MA\data\vector\stratification_germany\wuchsgebiete\wuchsgebiete_germany_3035.shp'
tiles_pth = r'_temp\00_MA\data\vector\miscellaneous\force-tiles_ger_3035.shp'

wuchs_shp = ogr.Open(wuchs_pth)
tiles_shp = ogr.Open(tiles_pth)

wuchs_lyr = wuchs_shp.GetLayer()
tiles_lyr = tiles_shp.GetLayer()

sr = wuchs_lyr.GetSpatialRef()

id_lst = []
for feat in wuchs_lyr:
    wuchs_name = feat.GetField('Name')
    wuchs_id = feat.GetField('ID')
    id_lst.append(wuchs_id)
wuchs_lyr.ResetReading()

for feat in wuchs_lyr:

    wuchs_name = feat.GetField('Name')
    wuchs_name = wuchs_name.replace("/", "-")

    wuchs_id = feat.GetField('ID')
    print(wuchs_id, wuchs_name)

    tiles_lyr.SetSpatialFilter(None)
    geom = feat.GetGeometryRef()
    geom_wkt = geom.ExportToWkt()
    tiles_lyr.SetSpatialFilter(geom)

    tiles_lst = []
    for tile in tiles_lyr:
        tile_name = tile.GetField('Name')
        tiles_lst.append(tile_name)
        print(tile_name)

    tiles_lyr.ResetReading()
    print('\n')

    msk_lst = [r'Z:\germany-drought\masks\{0}\2015_MASK_FOREST-BROADLEAF_UNDISTURBED-2013_BUFF-01.tif'.format(i) for i in tiles_lst]
    vrt_msk_pth = r'Z:\germany-drought\vrt\wuchsgebiete\{0}_{1}_MASK_FOREST-BROADLEAF.vrt'.format(wuchs_id, wuchs_name)
    vrt_msk = gdal.BuildVRT(vrt_msk_pth, msk_lst)

    del vrt_msk
    print(wuchs_id, wuchs_name, 'done')
wuchs_lyr.ResetReading()