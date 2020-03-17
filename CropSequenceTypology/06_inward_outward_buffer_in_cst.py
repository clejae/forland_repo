# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
from scipy.signal import convolve2d
import numpy as np
import joblib
import glob

## OWN REPOSITORY
import raster

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## !!!! There is a problem with convolve2d-function. Either, it doesn't work in O:  !!!!
## !!!! or it doesn't work with too big raster data  !!!!

print('Buffering\n')

with open(r'data\raster\tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

in_lst = [r'data\raster\grid_15km\\' + item + r'\2005-2011_CropSeqType.tif' for item in tiles_lst]
out_lst = [r'data\raster\grid_15km\\' + item + r'\2005-2011_CropSeqType_clean.tif' for item in tiles_lst]

job_lst = [[in_lst[i], out_lst[i]] for i in range (len(in_lst))]

## Optional check job list
# for i, job in enumerate(job_lst):
#    print(i+1)
#    print(job)

job = job_lst[1]
def workFunc(job):
# for job in job_lst:
    print("Start: " + job[0])
    out_path = job[1]

    ## open raster and get necessary features from it
    ras = gdal.Open(job[0])
    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()
    nd_val = ras.GetRasterBand(1).GetNoDataValue()

    ## read array and create copy for later modifying
    arr = ras.ReadAsArray()
    arr_copy = arr.copy()

    ## get all unique values and delete no data value
    unique = np.unique(arr)
    unique = unique[unique != nd_val]

    arr_out = np.full(arr.shape,0)

    ## loop over unique values, apply first negative then positive buffer
    ## this eliminates the single points and stripes of only 2 pixels
    for num in unique:

        ## the kernel determines how much is buffered
        ## 3,3 == 1; 5,5 == 2
        kernel = np.ones((3, 3))

        ## set current value to 0 and all other values to 1
        ## then apply buffer to all 1s --> inward buffer is applied to current value
        arr_copy[arr != num] = 1
        arr_copy[arr == num] = 0
        arr_buff = np.int64(convolve2d(arr_copy, kernel, mode = 'same') > 0)

        ## set current value to 1 and all other values to 0
        ## then appley buffer to all 1s --> positive buffer is applied to remainings of the current values
        arr_buff[arr_buff == 1] = 2
        arr_buff[arr_buff == 0] = 1
        arr_buff[arr_buff == 2] = 0
        arr_buff = np.int64(convolve2d(arr_buff, kernel, mode='same') > 0)

        ## set all 1s to the current value and pass to list
        arr_buff = arr_buff * num
        arr_out = arr_out + arr_buff

    ## set 0 to no data value
    arr_out[arr_out == 0] = 255

    ## write to disc
    raster.writeArrayToRaster(arr_out, out_path, gt, pr, nd_val, gdal.GDT_Byte)

    print("Done: " + job[0])

if __name__ == '__main__':
    joblib.Parallel(n_jobs=4)(joblib.delayed(workFunc)(i) for i in job_lst)
print("Script done!")
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


