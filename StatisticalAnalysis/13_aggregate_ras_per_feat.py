# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import numpy as np
import pandas as pd
import math
import gdal

## CJs Repo
import vector
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'BB'
year = 2018
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## Input
shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}.shp".format(bl, year)
ras_pth = r"data\raster\mosaics\Ackerzahl_BB.tif"

shp = ogr.Open(shp_pth,1)
lyr = shp.GetLayer()
sr = lyr.GetSpatialRef()
fname_lst = vector.getFieldNames(shp)

ras = gdal.Open(ras_pth)
arr = ras.ReadAsArray()
gt = ras.GetGeoTransform()
pr = ras.GetProjection()
x_ref = gt[0]
y_ref = gt[3]

## Output
fname_new = 'ACKERZ'

## Create new field in Layer
if fname_new in fname_lst:
    print("The field {0} exists already in the layer.".format(fname_new))
else:
    lyr.CreateField(ogr.FieldDefn(fname_new, ogr.OFTReal))
    fname_lst = vector.getFieldNames(shp)

for f, feat in enumerate(lyr):
    print(f)
    geom = feat.GetGeometryRef()
    geom_wkt = geom.ExportToWkt()

    extent = geom.GetEnvelope()

    x_min_ext = extent[0]
    x_max_ext = extent[1]
    y_min_ext = extent[2]
    y_max_ext = extent[3]

    # # align coordinates to input raster
    dist_x = x_ref - x_min_ext
    steps_x = -(math.floor(dist_x / 5))
    x_min_ali = x_ref + steps_x * 5

    dist_x = x_ref - x_max_ext
    steps_x = -(math.floor(dist_x / 5))
    x_max_ali = x_ref + steps_x * 5

    dist_y = y_ref - y_min_ext
    steps_y = -(math.floor(dist_y / 5))
    y_min_ali = y_ref + steps_y * 5

    dist_y = y_ref - y_max_ext
    steps_y = -(math.floor(dist_y / 5))
    y_max_ali = y_ref + steps_y * 5

    # slice input raster array to common dimensions
    px_min = int((x_min_ali - gt[0]) / gt[1])
    px_max = int((x_max_ali - gt[0]) / gt[1])

    # raster coordinates count from S to N, but array count from Top to Bottum, thus pymax = ymin
    py_max = int((y_min_ali - gt[3]) / gt[5])
    py_min = int((y_max_ali - gt[3]) / gt[5])

    geom_arr = arr[py_min: py_max, px_min: px_max]

    # create memory layer for rasterization
    driver_mem = ogr.GetDriverByName('Memory')
    ogr_ds = driver_mem.CreateDataSource('wrk')
    ogr_lyr = ogr_ds.CreateLayer('poly', srs=sr)

    feat_mem = ogr.Feature(ogr_lyr.GetLayerDefn())
    feat_mem.SetGeometryDirectly(ogr.Geometry(wkt=geom_wkt))

    ogr_lyr.CreateFeature(feat_mem)

    # rasterize geom
    col_sub = px_max - px_min
    row_sub = py_max - py_min
    if col_sub > 0 and row_sub > 0:
        gt_os = (x_min_ali, gt[1], 0, y_max_ali, 0, gt[5])
        target_ds = gdal.GetDriverByName('MEM').Create('', col_sub, row_sub, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform(gt_os)
        band = target_ds.GetRasterBand(1)
        band.SetNoDataValue(255)

        # Calculate polygon coverage of pixels
        gdal.RasterizeLayer(target_ds, [1], ogr_lyr, burn_values=[1])

        os_arr = band.ReadAsArray()
        os_arr[geom_arr == 255] = 0
        geom_mean = np.mean(geom_arr[os_arr == 1])
        del (target_ds)
    # otherwise print warning.
    else:
        geom_mean = 255

    feat.SetField(fname_new, geom_mean)
    lyr.SetFeature(feat)


    del (ogr_lyr)
    del (ogr_ds)

lyr.ResetReading()

del shp, lyr
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


