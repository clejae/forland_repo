# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import gdal
import numpy as np
import os
import time
import joblib
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def writeArrayToRaster(in_array, out_path, gt, pr, no_data_value):

    import gdal
    from osgeo import gdal_array

    # type_code = gdal_array.NumericTypeCodeToGDALTypeCode(in_array.dtype)

    if len(in_array.shape) == 3:
        nbands_out = in_array.shape[0]
        x_res = in_array.shape[2]
        y_res = in_array.shape[1]

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, gdal.GDT_Byte, options = ['COMPRESS=DEFLATE'])
        out_ras.SetGeoTransform(gt)
        out_ras.SetProjection(pr)

        for b in range(0, nbands_out):
            band = out_ras.GetRasterBand(b + 1)
            arr_out = in_array[b, :, :]
            band.WriteArray(arr_out)
            band.SetNoDataValue(no_data_value)
            band.FlushCache()

        del (out_ras)

    if len(in_array.shape) == 2:
        nbands_out = 1
        x_res = in_array.shape[1]
        y_res = in_array.shape[0]

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, gdal.GDT_Byte, options = ['COMPRESS=DEFLATE'])
        out_ras.SetGeoTransform(gt)
        out_ras.SetProjection(pr)

        band = out_ras.GetRasterBand( 1)
        band.WriteArray(in_array)
        band.SetNoDataValue(no_data_value)
        band.FlushCache()

        del (out_ras)

def cleanInvekosRaster(sl, excl_lst, no_data_value):
    """
    Checks whether the sum of  no data values, unkown values and fallow years is more than 2 in the
    time series of a pixel. If yes, then the time series is disregarded, i.e. all values are set to no data.

    :param sl: A time series of crops.
    :param excl_lst: list of all values that indicate non-arable land
    #param no_data_val: no data value to which a time series is set,
    when there are more than 2 occurences of non-arable land
    :return: Either the original Slice, or a Slice full of no data values.
    """

    import numpy as np

    # count occurences of 0 and no_data_value
    unique, counts = np.unique(sl, return_counts=True)
    count_dict = dict(zip(unique, counts))

    num_not_arable = 0 # counter of occurences of not arable land

    # go through list of values that indicate not arable land
    for val in excl_lst:
        # check if current value is in the time series
        # if yes add the number of occurences to the counter
        if val in sl:
            num_not_arable = num_not_arable + count_dict[val]

    # if the sum of all occurenves of not arable land is more then 2, all values are set to the no data value.
    if num_not_arable > 2:
        sl = (sl - sl) + no_data_value

    return sl

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

    ## first exclude all values in ts out that are in the skip list
    ts_mask = ts
    for value in skip_lst:
        ts_mask = ts_mask[ts_mask != value]

    ## now count the transitions between values that are not masked
    sum_trans = 0
    for i in range(len(ts_mask) - 1):
        if ts_mask[i] != ts_mask[i + 1]:
            sum_trans += 1
        else:
            sum_trans += 0

    ## count the number of crops
    unique, counts = np.unique(ts_mask, return_counts=True)
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
wd = r'L:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

per = '2012-2018'

with open(r'L:\Clemens\data\raster\folder_list_20200120.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]


def workFunc(tile):
    print(tile, "Cleaning")
    ## open rasterized kulturtyp raster
    ras = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_Inv_CropTypes_5m.tif'.format(tile, per))
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
        arr_copy[b, :, :][arr_copy[b, :, :] == 255] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 13] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 30] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 80] = 255
        arr_copy[b, :, :][arr_copy[b, :, :] == 99] = 255

        arr_copy[b, :, :][arr_copy[b, :, :] == 60] = 8

    arr_mask = np.sum(arr_copy, axis=0)
    arr_mask[arr_mask > 693] = 0
    arr_mask[arr_mask != 0] = 1

    print(tile, "MainType")
    #### derive main type from kulturtyp raster. If this was alread done, then load the respective raster instead
    arr_mt = np.apply_along_axis(func1d=identifyMainTypes, axis=0, arr=arr, no_data_value = 255, skip_lst = [255, 30, 80, 99])
    arr_mt = arr_mt * arr_mask
    arr_mt[arr_mt == 0] = 255
    writeArrayToRaster(arr_mt, r'L:\Clemens\data\raster\grid_15km\{0}\{1}_MainType.tif'.format(tile, per), gt, pr, no_data_value)
    # arr_mt = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_MainType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "SubType")
    #### derive sub type from cereal leaf raster and winter-summer raster
    arr_cl = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_Inv_CerLeaf_5m.tif'.format(tile, per)).ReadAsArray()
    arr_ws = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_Inv_WinSumm_5m.tif'.format(tile, per)).ReadAsArray()

    ## mask all no data values
    arr_cl_m = np.ma.masked_where(arr_cl == 255, arr_cl)
    arr_ws_m = np.ma.masked_where(arr_ws == 255, arr_ws)

    ## calculate the sum of leaf crop occurences and the sum of spring crop occurences
    ## leaf crop occurences
    arr_cl_sum = np.ma.sum(arr_cl_m, axis=0)
    arr_cl_sum = np.ma.filled(arr_cl_sum, 255)

    ## spring crop occurences
    arr_ws_sum = np.ma.sum(arr_ws_m, axis=0)
    arr_ws_sum = np.ma.filled(arr_ws_sum, 255)

    ## identify sub types
    ## create output array
    arr_st = np.full(arr_ws_sum.shape, 255)

    arr_st[(arr_cl_sum == 0) & (arr_ws_sum == 0)] = 1
    arr_st[(arr_cl_sum == 0) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 2
    arr_st[(arr_cl_sum == 0) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 3
    arr_st[(arr_cl_sum >= 1) & (arr_cl_sum <= 3) & (arr_ws_sum == 0)] = 4
    arr_st[(arr_cl_sum >= 1) & (arr_cl_sum <= 3) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 5
    arr_st[(arr_cl_sum >= 1) & (arr_cl_sum <= 3) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 6
    arr_st[(arr_cl_sum >= 4) & (arr_cl_sum <= 7) & (arr_ws_sum == 0)] = 7
    arr_st[(arr_cl_sum >= 4) & (arr_cl_sum <= 7) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 8
    arr_st[(arr_cl_sum >= 4) & (arr_cl_sum <= 7) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 9

    # writeArrayToRaster(arr_st, r'L:\Clemens\data\raster\grid_15km\{0}\{1}_SubType.tif'.format(tile, per), gt, pr, no_data_value)
    # arr_st = gdal.Open(r'L:\Clemens\data\raster\grid_15km\{0}\{1}_SubType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "Combining")
    arr_mt_m = np.ma.masked_where(arr_mt == 255, arr_mt)
    arr_st_m = np.ma.masked_where(arr_mt == 255, arr_st)
    arr_ct_comb = (arr_mt_m * 10) + arr_st_m
    writeArrayToRaster(arr_ct_comb, r'L:\Clemens\data\raster\grid_15km\{0}\{1}_CropRotType.tif'.format(tile, per), gt, pr, no_data_value)

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
    joblib.Parallel(n_jobs=8)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

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
