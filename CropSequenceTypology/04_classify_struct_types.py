# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import joblib

## Clemens repo
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'

cl_dict = {
        1: 0,
        2: 0,
        3: 1,
        4: 1,
        5: 1,
        6: 0,
        7: 0,
        9: 0,
        10: 0,
        12: 0,
        13: 0,
        14: 0,
        30: 255,
        60: 0,
        80: 255,
        99: 255
    }

sw_dict = {
        1: 1,
        2: 0,
        3: 0,
        4: 0,
        5: 1,
        6: 1,
        7: 0,
        9: 0,
        10: 0,
        12: 1,
        13: 0,
        14: 1,
        30: 255,
        60: 1,
        80: 255,
        99: 255
    }
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
os.chdir(wd)

with open(r"raster\folder_list.txt") as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

per_lst = [(2009,2015)]

for item in per_lst:
    min_year = item[0]
    max_year = item[1] + 1
    per = '{0}-{1}'.format(item[0], item[1])
    print(per)
    # for tile in tiles_lst:
    def workFunc(tile):
        print(tile)

        cl_arr = np.full((7, 3000, 3000),255)
        sw_arr = np.full((7, 3000, 3000),255)
        ct_arr = np.full((7, 3000, 3000),255)
        for y, year in enumerate(range(min_year, max_year)):

            ras_pth = r"raster\grid_15km\{0}\Inv_CropTypes_{1}_5m.tif".format(tile, year)
            ras = gdal.Open(ras_pth)

            gt = ras.GetGeoTransform()
            pr = ras.GetProjection()

            arr = ras.ReadAsArray()
            ct_arr[y,:,:] = arr

            out_arr1 = np.full(arr.shape, 255)
            for k in cl_dict:
                v = cl_dict[k]
                out_arr1[arr == k] = v

            cl_arr[y,:,:] = out_arr1

            out_arr2 = np.full(arr.shape, 255)
            for k in sw_dict:
                v = sw_dict[k]
                out_arr2[arr == k] = v

            sw_arr[y, :, :] = out_arr2


        pth = r"raster\grid_15km\{0}\{1}_Inv_CropTypes_5m.tif".format(tile, per)
        raster.writeArrayToRaster(ct_arr, pth, gt, pr, 255)

        pth = r"raster\grid_15km\{0}\{1}_Inv_CerLeaf_5m.tif".format(tile, per)
        raster.writeArrayToRaster(cl_arr, pth, gt, pr, 255)

        pth = r"raster\grid_15km\{0}\{1}_Inv_WinSumm_5m.tif".format(tile, per)
        raster.writeArrayToRaster(sw_arr, pth, gt, pr, 255)

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=4)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

# 2005-2019; 7 jobs = 13.42 min
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# bands = arr.shape(0)
#
# for b in range(bands):
#
#     for k, v in d.iteritems():
#         out_arr[b,:,:][theArray[b,:,:]==k] = v

# def workFunc(year):
# # for year in range(2005, 2006):
#     print(year)
#     with open(r"L:\Clemens\data\raster\folder_list.txt") as file:
#         tiles_lst = file.readlines()
#     tiles_lst = [item.strip() for item in tiles_lst]
#
#     for tile in tiles_lst:
#         # print(year, tile)
#         #tile = 'X10_Y08'
#         ras_pth = r"L:\Clemens\data\raster\grid_15km\{0}\Inv_CropTypes_{1}_5m.tif".format(tile, year)
#         ras = gdal.Open(ras_pth)
#
#         gt = ras.GetGeoTransform()
#         pr = ras.GetProjection()
#
#         arr = ras.ReadAsArray()
#
#         out_arr1 = np.full(arr.shape, 255)
#         for k in cl_dict:
#             v = cl_dict[k]
#             out_arr1[arr==k] = v
#
#         out_arr2 = np.full(arr.shape, 255)
#         for k in sw_dict:
#             v = sw_dict[k]
#             out_arr2[arr == k] = v
#
#         pth = r"L:\Clemens\data\raster\grid_15km\{0}\Inv_CerLeaf_{1}_5m.tif".format(tile,year)
#         writeArrayToRaster(out_arr1, pth, gt, pr, 255)
#
#         pth = r"L:\Clemens\data\raster\grid_15km\{0}\Inv_WinSumm_{1}_5m.tif".format(tile, year)
#         writeArrayToRaster(out_arr2, pth, gt, pr, 255)
#     print(year, "done")
#
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=7)(joblib.delayed(workFunc)(year) for year in range(2005,2012))