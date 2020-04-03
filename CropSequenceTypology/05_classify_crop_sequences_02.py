# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import gdal
import numpy as np
import os
import time
import joblib

import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def identifyMainTypes(ts, no_data_value, skip_lst):
    """
    Classifies crop time series over 7 years into crop types based on the sum of transitions between the years
    from one crop to another and on the number of different crops that are in the time series.
    If there are more than two no data values, then the crop type is set to -9999. Crop typification is based on
    Stein & Steinmann 2018 - "Identying crop rotation practice ..."

    :param ts: A time series of crops.
    :param no_data_value: Value indicating that there is no crop in the year of the index.
    :param skip_lst: List of IDs of classes that are not crop types considered in the crop typology.
    :return: Returns crop types in integer values. With 1=A to 9=I and -9999 for not classified.
    """

    ## first set all values in the skip list to the first value of the same list
    ts_calc = ts.copy()
    for value in skip_lst[1:]:
        ts_calc[ts_calc == value] = skip_lst[0]

    ## now count the transitions between values in the time series
    sum_trans = 0
    for i in range(len(ts_calc) - 1):
        if ts_calc[i] != ts_calc[i + 1]:
            sum_trans += 1
        else:
            sum_trans += 0

    ## count the number of crops
    unique, counts = np.unique(ts_calc, return_counts=True)
    sum_crops = len(unique)

    ## last check, whether there are not more than two values of the skip list in the time series
    num_no_data = np.sum(np.where(ts == no_data_value, 1, 0))

    if num_no_data > 2:
        main_type = 255
    elif sum_crops == 1:
        main_type = 1  # A
    elif sum_crops == 2 and (sum_trans == 1 or sum_trans == 2):
        main_type = 2  # B
    elif sum_crops == 3 and sum_trans == 2:
        main_type = 2  # B
    elif sum_crops == 2 and (sum_trans == 3 or sum_trans == 4):
        main_type = 3  # C
    elif sum_crops == 2 and (sum_trans == 5 or sum_trans == 6):
        main_type = 4  # D
    elif sum_crops == 3 and (sum_trans == 3 or sum_trans == 4):
        main_type = 5  # E
    elif sum_crops == 3 and (sum_trans == 5 or sum_trans == 6):
        main_type = 6  # F
    elif sum_crops == 4 and (sum_trans == 3 or sum_trans == 4):
        main_type = 7  # G
    elif sum_crops == 4 and (sum_trans == 5 or sum_trans == 6):
        main_type = 8  # H
    elif sum_crops >= 5:
        main_type = 9  # I
    else:
        main_type = 255

    return main_type

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'SA'

min_year = 2012
max_year = 2018

per = '{0}-{1}'.format(min_year, max_year)

with open(r'raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

# tile = tiles_lst[0] # 0031_0040 done!
# tiles_lst = ['0026_0044']
def workFunc(tile):
# for tile in tiles_lst[56:]:
    print(tile)

    dc_pth = r'raster\grid_15km'

    ras_ct_lst = [wd + '{0}\{1}\{2}_CropTypes_{3}.tif'.format(dc_pth, tile, bl, year) for year in range(min_year, max_year + 1)]
    ras_ct_lst = raster.openRasterFromList(ras_ct_lst)
    ras_lc_lst = [wd + '{0}\{1}\{2}_CropTypesLeCe_{3}.tif'.format(dc_pth, tile, bl, year) for year in range(min_year, max_year + 1)]
    ras_lc_lst = raster.openRasterFromList(ras_lc_lst)
    ras_ws_lst = [wd + '{0}\{1}\{2}_CropTypesWiSu_{3}.tif'.format(dc_pth, tile, bl, year) for year in range(min_year, max_year + 1)]
    ras_ws_lst = raster.openRasterFromList(ras_ws_lst)

    out_pth_ct = '{0}\{1}\{2}_{3}_CropTypes.tif'.format(dc_pth, tile, bl, per)
    raster.stackRasterFromList(ras_ct_lst, out_pth_ct, data_type=gdal.GDT_Int16)
    out_pth_lc = '{0}\{1}\{2}_{3}_CropTypesLeCe.tif'.format(dc_pth, tile, bl, per)
    raster.stackRasterFromList(ras_lc_lst, out_pth_lc, data_type=gdal.GDT_Byte)
    out_pth_ws = '{0}\{1}\{2}_{3}_CropTypesWiSu.tif'.format(dc_pth, tile, bl, per)
    raster.stackRasterFromList(ras_ws_lst, out_pth_ws, data_type=gdal.GDT_Byte)

    print(tile, "Cleaning")
    ## open rasterized kulturtyp raster
    ras = gdal.Open(out_pth_ct)
    arr = ras.ReadAsArray()

    ## get some arr_copy
    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()
    no_data_value = ras.GetRasterBand(1).GetNoDataValue()

    #### clean kulturtyp raster. If cleaned version exists, then load the respective raster instead instead
    # arr_clean = np.apply_along_axis(func1d=cleanInvekosRaster, axis=0, arr=arr, excl_lst=[255, 13, 30, 80, 99], no_data_value = 255)
    # writeArrayToRaster(arr_clean, r'L:\Clemens\data\raster\grid_15km\{0}\{1}_Inv_CropTypesClean_5m.tif'.format(tile, per), gt, pr, no_data_value)
    # arr_clean = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_Inv_CropTypesClean_5m.tif'.format(tile, per)).ReadAsArray()

    #### create a mask array to clean kulturtyp raster in a later step
    ## where 0 indicates time series with more than 2 times of fallow land, grassland, unknown etc.
    ## loop over the years and set all respective classes to no data value
    ## set also class 30 to a lower value
    arr_copy = arr.copy()
    bands = arr.shape[0]
    for b in range(bands):
        arr_copy[b, :, :][arr_copy[b, :, :] == 13] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 30] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 80] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 99] = 255

        ## set the vegetables class (id=60) to 8, so that the following step works
        arr_copy[b, :, :][arr_copy[b, :, :] == 60] = 8

    arr_mask = np.sum(arr_copy, axis=0)
    arr_mask[arr_mask > 693] = 0
    arr_mask[arr_mask != 0] = 1

    ## combine the two legumes classes to one by setting class 14 to class 12
    for b in range(bands):
        arr[b, :, :][arr[b, :, :] == 14] = 12

    print(tile, "MainType")
    #### derive main type from kulturtyp raster. If this was alread done, then load the respective raster instead
    arr_mt = np.apply_along_axis(func1d=identifyMainTypes, axis=0, arr=arr, no_data_value = 255, skip_lst = [255, 30, 80, 99])
    arr_mt = arr_mt * arr_mask
    arr_mt[arr_mt == 0] = 255
    # raster.writeArrayToRaster(arr_mt, r'raster\grid_15km\{0}\{1}_MainType_v2.tif'.format(tile, per), gt, pr, no_data_value, type_code = gdal.GDT_Byte)
    # arr_mt = gdal.Open(r'raster\grid_15km\{0}\{1}_MainType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "SubType")
    #### derive sub type from cereal leaf raster and winter-summer raster
    arr_lc = gdal.Open(out_pth_lc).ReadAsArray()
    arr_ws = gdal.Open(out_pth_ws).ReadAsArray()

    ## where both arrays of the structural types are 99, set them to 255
    bands = arr_lc.shape[0]
    for b in range(bands):
        arr_lc[b, :, :][arr_lc[b, :, :] == 99] = 255

    bands = arr_ws.shape[0]
    for b in range(bands):
        arr_ws[b, :, :][arr_ws[b, :, :] == 99] = 255

    ## mask all no data values
    arr_lc_m = np.ma.masked_where(arr_lc == 255, arr_lc)
    arr_ws_m = np.ma.masked_where(arr_ws == 255, arr_ws)

    ## calculate the sum of leaf crop occurences and the sum of spring crop occurences
    ## leaf crop occurences
    arr_lc_sum = np.ma.sum(arr_lc_m, axis=0)
    arr_lc_sum = np.ma.filled(arr_lc_sum, 255)

    ## spring crop occurences
    arr_ws_sum = np.ma.sum(arr_ws_m, axis=0)
    arr_ws_sum = np.ma.filled(arr_ws_sum, 255)

    ## identify sub types
    ## create output array
    arr_st = np.full(arr_ws_sum.shape, 255)

    arr_st[(arr_lc_sum == 0) & (arr_ws_sum == 0)] = 1
    arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 2
    arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 3
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum == 0)] = 4
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 5
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 6
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum == 0)] = 7
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 8
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 9

    # raster.writeArrayToRaster(arr_st, r'raster\grid_15km\{0}\{1}_SubType_v2.tif'.format(tile, per), gt, pr, no_data_value, type_code=gdal.GDT_Byte)
    # arr_st = gdal.Open(r'raster\grid_15km\{0}\{1}_SubType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "Combining")
    arr_mt_m = np.ma.masked_where(arr_mt == 255, arr_mt)
    arr_st_m = np.ma.masked_where(arr_mt == 255, arr_st)
    arr_ct_comb = (arr_mt_m * 10) + arr_st_m
    raster.writeArrayToRaster(arr_ct_comb, r'raster\grid_15km\{0}\{1}_{2}_CropSeqType_v2.tif'.format(tile, bl, per), gt, pr, no_data_value, type_code=gdal.GDT_Byte)

    print(tile, "done!")

    # arr_1 = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_CropRotType.tif'.format(tile, per)).ReadAsArray()
    # arr_2 = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_CropRotType.tif'.format(tile, per)).ReadAsArray()
    #
    # arr_1[arr_2 == 255] = 255
    # arr_2[arr_1 == 255] = 255
    # arr_1[arr_2 == 255] = 255
    # arr_2[arr_1 == 255] = 255
    #
    # writeArrayToRaster(arr_1, r'L:\Clemens\data\raster\grid_15km\{0}\{1}_CropRotTypeSteadyArea.tif'.format(tile, per), gt, pr, no_data_value)
    # writeArrayToRaster(arr_2, r'L:\Clemens\data\raster\temp\2012-2018_CropRotTypeSteadyArea.tif'.format(tile, per), gt, pr, no_data_value)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# a = arr_clean[:,530:550,510:550]
# ts = arr[:,0,0]
# ts = np.array([60,80,4,10,1,10,10])
#
# t = identifyMainTypes(ts, -9999.0)
#
# t_arr = np.apply_along_axis(func1d=identifyMainTypes, axis=0, arr=a, no_data_value = -9999.0)
#
#######
# import matplotlib.pyplot as plt
# arr_cl_sub = arr_clean[:,1400:2000,291:800]
#
# plt.imshow(arr_cl_sub[0,:,:], vmin=-1, vmax=16, cmap=plt.cm.get_cmap("tab20c", 17))
# plt.colorbar(ticks=range(-1,16))
# ts = np.array([99,3,13,4,80,4,4,])
