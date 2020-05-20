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

def identifyMainTypes(ts, no_data_value, arable_grass_value, skip_lst):
    """
    Classifies crop time series over 7 years into crop sequence types based on the sum of transitions
    from one crop to another and on the number of different crops that are in the time series.
    If there are more than two years no data, arable grass or any class from the skip list, then the crop type is set to 255.
    Crop typification is based on Stein & Steinmann 2018 - "Identying crop rotation practice ..."

    :param ts: A time series of crops.
    :param no_data_value: Value indicating that there is not any crop class.
    :param arable_grass_value: Value indicating arable grass.
    :param skip_lst: List of IDs of classes that are "fallow", "unknown" or "others".
    :return: Returns crop sequence main types in integer values. With 1=A to 9=I and 255 for not classified.
    """

    ## first set all values in the sequence that also occur in the skip list to the no data value
    ts_calc = ts.copy()
    for value in skip_lst:
        ts_calc[ts_calc == value] = no_data_value

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

    ## lastly, count the occurences of temporary grass, fallow, others, unkown or no data
    ## for that, set the occurecences of arable grass also to no data
    ts_calc[ts_calc == arable_grass_value] = no_data_value
    num_no_data = np.sum(np.where(ts_calc == no_data_value, 1, 0))

    ## determine the main type of the crop sequence on the following rule set
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

bl = 'BB'

min_year = 2008
max_year = 2014
year_range = range(min_year, max_year + 1)

per = '{0}-{1}'.format(min_year, max_year)

with open(r'raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]
def workFunc(tile):
    print("Starting", tile)

    dc_pth = r'raster\grid_15km'

    ras_ct_lst = [r'raster\grid_15km\{0}\{1}_CropTypes_{2}.tif'.format(tile, bl, year) for year in year_range]
    ras_ct_lst = raster.openRasterFromList(ras_ct_lst)
    ras_lc_lst = [r'raster\grid_15km\{0}\{1}_CropTypesLeCe_{2}.tif'.format(tile, bl, year) for year in year_range]
    ras_lc_lst = raster.openRasterFromList(ras_lc_lst)
    ras_ws_lst = [r'raster\grid_15km\{0}\{1}_CropTypesWiSu_{2}.tif'.format(tile, bl, year) for year in year_range]
    ras_ws_lst = raster.openRasterFromList(ras_ws_lst)

    out_pth_ct = r'raster\grid_15km\{0}\{1}_{2}_CropTypes.tif'.format(tile, bl, per)
    if os.path.exists(out_pth_ct) == False:
        raster.stackRasterFromList(ras_ct_lst, out_pth_ct, data_type=gdal.GDT_Int16)
    out_pth_lc = r'raster\grid_15km\{0}\{1}_{2}_CropTypesLeCe.tif'.format(tile, bl, per)
    if os.path.exists(out_pth_lc) == False:
        raster.stackRasterFromList(ras_lc_lst, out_pth_lc, data_type=gdal.GDT_Byte)
    out_pth_ws = r'raster\grid_15km\{0}\{1}_{2}_CropTypesWiSu.tif'.format(tile, bl, per)
    if os.path.exists(out_pth_ws) == False:
        raster.stackRasterFromList(ras_ws_lst, out_pth_ws, data_type=gdal.GDT_Byte)

    print(tile, "Cleaning")
    ## open rasterized kulturtyp raster
    ras = gdal.Open(out_pth_ct)
    arr = ras.ReadAsArray()

    ## get some arr_copy
    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()
    no_data_value = ras.GetRasterBand(1).GetNoDataValue()

    #### create a mask array to clean kulturtyp raster in a later step
    ## where 0 indicates time series with more than 2 times of fallow land, grassland, unknown etc.
    ## loop over the years and set all respective classes to no data value
    ## set also class 60 (vegetables) to a lower value
    # arr_copy = arr.copy()
    # bands = arr.shape[0]
    # for b in range(bands):
    #     arr_copy[b, :, :][arr_copy[b, :, :] == 13] = 255
    #     arr_copy[b, :, :][arr_copy[b, :, :] == 30] = 255
    #     arr_copy[b, :, :][arr_copy[b, :, :] == 80] = 255
    #     arr_copy[b, :, :][arr_copy[b, :, :] == 99] = 255
    #
    #     ## set the vegetables class (id=60) to 8, so that the following step works
    #     arr_copy[b, :, :][arr_copy[b, :, :] == 60] = 8
    #
    # arr_mask = np.sum(arr_copy, axis=0)
    # arr_mask[arr_mask > 693] = 0
    # arr_mask[arr_mask != 0] = 1
    #
    # raster.writeArrayToRaster(arr_mask, r'raster\grid_15km\{0}\{1}_{2}_Mask.tif'.format(tile, bl, per), gt, pr,
    #                          no_data_value, type_code=gdal.GDT_Byte)

    ## combine the two legumes classes to one by setting class 14 to class 12
    for b in range(bands):
        arr[b, :, :][arr[b, :, :] == 14] = 12

    print(tile, "MainType")
    #### derive main type from kulturtyp raster. If this was alread done, then load the respective raster instead
    arr_mt = np.apply_along_axis(func1d=identifyMainTypes, axis=0, arr=arr, no_data_value = 255, arable_grass_value = 13, skip_lst = [30, 80, 99])
    # arr_mt = arr_mt * arr_mask
    # arr_mt[arr_mt == 0] = 255
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
    raster.writeArrayToRaster(arr_ct_comb, r'raster\grid_15km\{0}\{1}_{2}_CropSeqType.tif'.format(tile, bl, per), gt, pr, no_data_value, type_code=gdal.GDT_Byte)

    print(tile, "done!\n")

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
