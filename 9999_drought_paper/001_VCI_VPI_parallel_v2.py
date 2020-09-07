# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
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
wd = r'\\141.20.140.222\endor\germany-drought\\'
target_year = 2019
min_year = 2005
max_year = 2019
bl = '{0}-{1}'.format(min_year, max_year)
in_sen = 'LNDLG'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# read tiles from text file into a list
with open(r'germany.txt') as file:
    tiles_lst = file.readlines()
tile_lst = [item.strip() for item in tiles_lst]
# tile_lst = ['X0069_Y0037']

def workFunc(tile):
    print('TILE | YEAR | BASELINE | SENSORS \n', tile, target_year, bl, in_sen)

    ## open ndvi rasters of target year and the reference statistics
    curr_ndvi_pth = 'VCI_VPI\{0}\{1}-{1}_001-365_HL_TSA_{2}_NDV_FBM.tif'.format(tile, target_year, in_sen)
    avg_ras_pth = 'VCI_VPI\{0}\{1}_001-365_HL_TSA_{2}_NDV_FBM_AVG.tif'.format(tile, bl, in_sen)
    std_ras_pth = 'VCI_VPI\{0}\{1}_001-365_HL_TSA_{2}_NDV_FBM_STD.tif'.format(tile, bl, in_sen)
    # min_ras_pth = 'VCI_VPI\{0}\{1}_001-365_HL_TSA_LNDLG_NDV_FBM_MIN.tif'.format(tile, bl)
    # max_ras_pth =  'VCI_VPI\{0}\{1}_001-365_HL_TSA_LNDLG_NDV_FBM_MAX.tif'.format(tile, bl)

    ndvi_ras = gdal.Open(curr_ndvi_pth)
    avg_ras = gdal.Open(avg_ras_pth)
    std_ras = gdal.Open(std_ras_pth)
    # min_ras = gdal.Open(min_ras_pth)
    # max_ras = gdal.Open(max_ras_pth)

    ndvi_arr = ndvi_ras.ReadAsArray()
    avg_arr = avg_ras.ReadAsArray()
    std_arr = std_ras.ReadAsArray()
    # min_arr = min_ras.ReadAsArray()
    # max_arr = max_ras.ReadAsArray()

    gt = ndvi_ras.GetGeoTransform()
    pr = ndvi_ras.GetProjection()

    ## the monthly vpi and vci of the target year will be stored in these lists
    vpi_out_lst = []
    # vci_out_lst = []

    # ## Derive statistics (min, max, avg, std) for each month based on reference period
    # ## reference period is stored in arr_lst
    for month in range(0, 12):

        ## create NDVI-array of current month
        ndvi_slice = ndvi_arr[month, :, :]
        ndvi_slice = ndvi_slice + 0.0
        ndvi_slice[ndvi_slice == -9999] = np.nan

        ## Calculate VPI
        avg_curr_month = avg_arr[month, :, :]
        std_curr_month = std_arr[month, :, :]
        vpi_arr = norm.cdf(ndvi_slice, scale=std_curr_month, loc=avg_curr_month)
        vpi_arr = vpi_arr * 100
        ## create a mask where all arrays are no data value
        nan_merge = np.ones(ndvi_slice.shape)
        nan_merge[np.isnan(ndvi_slice)] = -9999
        nan_merge[np.isnan(avg_curr_month)] = -9999
        nan_merge[np.isnan(std_curr_month)] = -9999
        vpi_arr[np.isnan(nan_merge)] = 255
        vpi_out_lst.append(vpi_arr)

        # ## Calculate VCI
        # min_curr_month = min_arr[month, :, :]
        # max_curr_month = max_arr[month, :, :]
        # vci_arr = 100 * (ndvi_slice - min_curr_month) / (max_curr_month - min_curr_month)
        # ## create a mask where all arrays are no data val
        # nan_merge = np.ones(ndvi_slice.shape)
        # nan_merge[np.isnan(ndvi_slice)] = -9999
        # nan_merge[np.isnan(min_curr_month)] = -9999
        # nan_merge[np.isnan(max_curr_month)] = -9999
        # vci_arr[nan_merge == -9999] = -9999
        # vci_arr[np.isinf(vci_arr)] = 255
        # vci_out_lst.append(vci_arr)

    vpi_out_arr = np.array(vpi_out_lst)
    # vci_out_arr = np.array(vci_out_lst)

    ## Write VPI array to disc
    out_pth_vpi = r'VCI_VPI\{0}\{1}_BL-{2}_{3}_VPI_v2.tif'.format(tile, target_year, bl, in_sen)
    raster.writeArrayToRaster(vpi_out_arr, out_pth_vpi, gt, pr, no_data_value=255, type_code = gdal.GDT_Byte, options=[])

    # # write VCI array to disc
    # out_pth_vci = r'VCI_VPI\{0}\{1}_BL-{2}_{3}_VCI_v2.tif'.format(tile, target_year, bl, in_sen)
    # raster.writeArrayToRaster(vci_out_arr, out_pth_vci, gt, pr, no_data_value=255, type_code = gdal.GDT_Byte, options=[])

if __name__ == '__main__':
    joblib.Parallel(n_jobs=30)(joblib.delayed(workFunc)(tile) for tile in tile_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


