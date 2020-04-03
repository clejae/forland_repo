# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import joblib

## CJ REPO
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'BB'
min = 2012
max = 2018
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

x = 3000
y = 3000
z = (max + 1) - min

with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

# for tile in tiles_lst:
def workFunc(tile):
    print(tile)
    fill_arr = np.full(shape=(z,y,x), fill_value= 0)

    for i, year in enumerate(range(min, max+1)):
        pth = r'data\raster\grid_15km\{}\{}_CropTypesOeko_{}.tif'.format(tile, bl, year)
        ras = gdal.Open(pth)
        arr = ras.ReadAsArray()
        fill_arr[i, :, :] = arr
    msk_arr = np.prod(fill_arr, 0)

    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()

    out_pth = r'data\raster\grid_15km\{}\{}_OekoMask_{}-{}.tif'.format(tile, bl, min, max)

    raster.writeArrayToRaster(msk_arr, out_pth, gt, pr, 255, type_code = gdal.GDT_Byte)
    print(tile, "done")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=11)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


