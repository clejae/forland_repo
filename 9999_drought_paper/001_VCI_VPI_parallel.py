# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import glob
import time
import gdal
import numpy as np
import joblib
from scipy.stats import norm

## CJ Repo
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
target_year = 2018
min_year = 2005
max_year = 2019
bl = '{0}-{1}'.format(min_year, max_year)
in_sen = 'SEN2L'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# read tiles from text file into a list
with open(r'\\141.20.140.222\endor\germany-drought\germany.txt') as file:
    tiles_lst = file.readlines()
tile_lst = [item.strip() for item in tiles_lst]

tile_lst = ['X0069_Y0037']

def workFunc(tile):
    print('TILE | YEAR | BASELINE | SENSORS \n', tile, target_year, bl, in_sen)

    ## open ndvi raster of target year
    # curr_pth = glob.glob(r'\\141.20.140.222\endor\germany-drought\VCI_VPI\{0}\{1}-{1}*NDV*.tif'.format(tile,curr_year))[0]
    curr_pth = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}-{1}_001-365_HL_TSA_{2}_NDV_FBM.tif'.format(tile, target_year, in_sen)
    ndvi_ras = gdal.Open(curr_pth)
    ndvi_arr = ndvi_ras.ReadAsArray()
    gt = ndvi_ras.GetGeoTransform()
    pr = ndvi_ras.GetProjection()

    # ## open ndvi rasters of reference period and save to a list
    arr_lst = []
    for year in range(min_year, max_year + 1):
        pth = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}-{1}_001-365_HL_TSA_LNDLG_NDV_FBM.tif'.format(tile,year)
        ras = gdal.Open(pth)
        arr = ras.ReadAsArray()
        gt = ras.GetGeoTransform()
        pr = ras.GetProjection()
        arr_lst.append(arr)
    #
    # ## the monthly vpi and vci of the target year will be stored in these lists
    # vpi_out_lst = []
    # vci_out_lst = []
    #
    # ## the monthly min, max, mean and std of the ref-period will be stored in these lists
    # min_lst = []
    # max_lst = []
    mean_lst = []
    # std_lst = []
    #
    # ## Derive statistics (min, max, avg, std) for each month based on reference period
    # ## reference period is stored in arr_lst
    for month in range(0, 12):
        monthly_lst = []
        for arr in arr_lst:
            monthly_arr = arr[month, :, :]
            monthly_arr = monthly_arr + 0.0
            monthly_arr[monthly_arr == -9999] = np.nan
            monthly_lst.append(monthly_arr)
        monthly_stack = np.array(monthly_lst)
    #
    #     ## create NDVI-array of current month
    #     ndvi_slice = ndvi_arr[month, :, :]
    #     ndvi_slice = ndvi_slice + 0.0
    #     ndvi_slice[ndvi_slice == -9999] = np.nan
    #
    #     ## Calculate VPI
        mean_curr_month = np.nanmean(monthly_stack, axis=0)
    #     std_curr_month = np.nanstd(monthly_stack, axis=0, ddof=1)
    #     vpi_arr = norm.cdf(ndvi_slice, scale=std_curr_month, loc=mean_curr_month)
    #     vpi_arr = vpi_arr * 100
    #     vpi_arr[np.isnan(ndvi_slice)] = -9999
    #     vpi_out_lst.append(vpi_arr)
    #
    #     ## Calculate VCI
    #     min_curr_month = np.nanmin(monthly_stack, axis=0)
    #     max_curr_month = np.nanmax(monthly_stack, axis=0)
    #     vci_arr = 100 * (ndvi_slice - min_curr_month) / (max_curr_month - min_curr_month)
    #     ## create a mask where all arrays are no data val
    #     nan_merge = np.ones(ndvi_slice.shape)
    #     nan_merge[np.isnan(ndvi_slice)] = -9999
    #     nan_merge[np.isnan(min_curr_month)] = -9999
    #     nan_merge[np.isnan(max_curr_month)] = -9999
    #     vci_arr[nan_merge == -9999] = -9999
    #     vci_arr[np.isinf(vci_arr)] = -9999
    #     vci_out_lst.append(vci_arr)
    #
    #     ## save statistics derived for the current month in a list
    #     min_lst.append(min_curr_month)
    #     max_lst.append(max_curr_month)
        mean_lst.append(mean_curr_month)
    #     std_lst.append(std_curr_month)
    #
    # ## convert lists to array
    # min_arr = np.array(min_lst)
    # max_arr = np.array(max_lst)
    mean_arr = np.array(mean_lst)
    # std_arr = np.array(std_lst)
    #
    # vpi_out_arr = np.array(vpi_out_lst)
    # vci_out_arr = np.array(vci_out_lst)

    ## Calc ratios
    ratio_arr1 = ndvi_arr[7,:,:] / ndvi_arr[6,:,:]
    ratio_arr2 = ndvi_arr[7, :, :] / ndvi_arr[5, :, :]

    ## write VCI array to disc
    # out_pth_vci = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_BL-{2}_{3}_VCI.tif'.format(tile, target_year, bl, in_sen)
    # raster.writeArrayToRaster(vci_out_arr, out_pth_vci, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])
    #
    # ## Write VPI array to disc
    # out_pth_vpi = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_BL-{2}_{3}_VPI.tif'.format(tile, target_year, bl, in_sen)
    # raster.writeArrayToRaster(vpi_out_arr, out_pth_vpi, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])

    ## Write statistic arrays to disc
    # out_pth_min = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_MIN.tif'.format(tile, bl, in_sen)
    # raster.writeArrayToRaster(min_arr, out_pth_min, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])
    # out_pth_max = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_MAX.tif'.format(tile, bl, in_sen)
    # raster.writeArrayToRaster(max_arr, out_pth_max, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])
    # out_pth_std = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_STD.tif'.format(tile, bl, in_sen)
    # raster.writeArrayToRaster(std_arr, out_pth_std, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])
    out_pth_mean = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_AVG.tif'.format(tile, bl, in_sen)
    raster.writeArrayToRaster(mean_arr, out_pth_mean, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Int16, options=[])

    ## Write ratio array to disc
    out_pth_ratio = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_RATIO-AUG-JUL.tif'.format(tile,
                                                                                                            target_year,
                                                                                                            in_sen)
    raster.writeArrayToRaster(ratio_arr1, out_pth_ratio, gt, pr, no_data_value=-9999, type_code = gdal.GDT_Float32, options=[])

    out_pth_ratio = r'\\141.20.140.222\endor\germany-drought\SPJ\{0}\{1}_{2}_NDVI_RATIO-AUG-JUN.tif'.format(tile,
                                                                                                            target_year,
                                                                                                            in_sen)
    raster.writeArrayToRaster(ratio_arr2, out_pth_ratio, gt, pr, no_data_value=-9999, type_code=gdal.GDT_Float32,
                              options=[])

for target_year in range(2016,2020):
    if __name__ == '__main__':
        joblib.Parallel(n_jobs=1)(joblib.delayed(workFunc)(tile) for tile in tile_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


