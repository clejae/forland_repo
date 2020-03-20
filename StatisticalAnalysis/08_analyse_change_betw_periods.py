# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\raster\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

per_lst = ['2005-2011', '2012-2018']

arr_lst = []
for tile in tiles_lst:
    print(tile)
    # arr_lst.append(gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd,tile,per)).ReadAsArray())

    arr1 = gdal.Open('{0}\grid_15km\{1}\{2}_CropSeqType_v2_clean.tif'.format(wd, tile, per_lst[0])).ReadAsArray()
    arr1 = arr1 + 0.0
    arr2 = gdal.Open('{0}\grid_15km\{1}\{2}_CropSeqType_v2_clean.tif'.format(wd, tile, per_lst[1])).ReadAsArray()
    arr2 = arr2 + 0.0

    gt = gdal.Open('{0}\grid_15km\{1}\{2}_CropSeqType_v2_clean.tif'.format(wd, tile, per_lst[0])).GetGeoTransform()
    pr = gdal.Open('{0}\grid_15km\{1}\{2}_CropSeqType_v2_clean.tif'.format(wd, tile, per_lst[0])).GetProjection()
    nd_val = 255

    arr1[arr2 == 255] = 255
    arr2[arr1 == 255] = 255
    arr1[arr2 == 255] = 255
    arr2[arr1 == 255] = 255

    diff_arr = arr1 - arr2
    diff_arr[arr2 == 255] = 255

    conc_arr = (arr1 * 100) + arr2
    conc_arr[arr2 == 255] = 255

    out_pth = '{0}\grid_15km\{1}\{2}_{3}_CropSeqTypeDiff_v2_clean.tif'.format(wd, tile, per_lst[0], per_lst[1])
    raster.writeArrayToRaster(diff_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)

    out_pth = '{0}\grid_15km\{1}\{2}_{3}_CropSeqTypeConc_v2_clean.tif'.format(wd, tile, per_lst[0], per_lst[1])
    raster.writeArrayToRaster(conc_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


