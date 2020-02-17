# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def writeArrayToRaster(in_array, out_path, gt, pr, no_data_value):

    import gdal
    from osgeo import gdal_array

    type_code = gdal_array.NumericTypeCodeToGDALTypeCode(in_array.dtype)

    if len(in_array.shape) == 3:
        nbands_out = in_array.shape[0]
        x_res = in_array.shape[2]
        y_res = in_array.shape[1]

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, type_code, options = ['COMPRESS=DEFLATE'])
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

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, type_code, options = ['COMPRESS=DEFLATE'])
        out_ras.SetGeoTransform(gt)
        out_ras.SetProjection(pr)

        band = out_ras.GetRasterBand( 1)
        band.WriteArray(in_array)
        band.SetNoDataValue(no_data_value)
        band.FlushCache()

        del (out_ras)


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\raster\grid_15km'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'L:\Clemens\data\raster\folder_list.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

tile = 'X06_Y08'

per_lst = ['2005-2011','2012-2018']

# arr_lst = []
# for per in per_lst:
#     arr_lst.append(gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd,tile,per)).ReadAsArray())

arr1 = gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd, tile, per_lst[0])).ReadAsArray()
arr1 = arr1 + 0.0
arr2 = gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd, tile, per_lst[1])).ReadAsArray()
arr2 = arr2 + 0.0

gt = gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd, tile, per_lst[0])).GetGeoTransform()
pr = gdal.Open('{0}\{1}\{2}_CropSeqType.tif'.format(wd, tile, per_lst[0])).GetProjection()
nd_val = 255

arr1[arr2 == 255] = 255
arr2[arr1 == 255] = 255
arr1[arr2 == 255] = 255
arr2[arr1 == 255] = 255

diff_arr = arr1 - arr2
diff_arr[arr2 == 255] = 255

conc_arr = (arr1 * 100) + arr2
conc_arr[arr2 == 255] = 255

out_pth = '{0}\{1}\{2}_{3}_CropSeqTypeDiff.tif'.format(wd, tile, per_lst[0], per_lst[1])
writeArrayToRaster(diff_arr, out_pth, gt, pr, nd_val)

out_pth = '{0}\{1}\{2}_{3}_CropSeqTypeConc.tif'.format(wd, tile, per_lst[0], per_lst[1])
writeArrayToRaster(conc_arr, out_pth, gt, pr, nd_val)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


