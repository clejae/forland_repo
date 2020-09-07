# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import numpy as np
import gdal
import math
# import matplotlib.pyplot as plt
from pyproj import Proj, transform
from scipy.interpolate import griddata

##CJ REPO
import raster

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

ref_pth = r'\\141.20.140.222\endor\germany-drought\vrt\masks\2015_MASK_FOREST-BROADLEAF_BUFF-01.vrt'
netcdf_pth = r"_temp\00_MA\data\climate\SMI\SMI_Lall_Gesamtboden_monatlich_1951_2018_inv.nc"
out_pth = r'_temp\00_MA\data\climate\SMI\SMI_2018_Gesamtboden.tif'

print('opening input')
## open a reference raster
ref_ras = gdal.Open(ref_pth)
gt = ref_ras.GetGeoTransform()
pr = ref_ras.GetProjection()
ref_arr = ref_ras.ReadAsArray()

## get Info about netcdf File
print(gdal.Info(netcdf_pth))

## open netcdf file, load subds and read them as arrays
ds = gdal.Open(netcdf_pth)
subds_lst = ds.GetSubDatasets()
## SMI
ds_smi = gdal.Open(ds.GetSubDatasets()[0][0])
smi_arr = ds_smi.ReadAsArray()
## kernel width
ds_kw = gdal.Open(ds.GetSubDatasets()[1][0])
kw_arr = ds_kw.ReadAsArray()
## latitude
ds_lat = gdal.Open(ds.GetSubDatasets()[2][0])
lat_arr = ds_lat.ReadAsArray()
## longtitude
ds_lon = gdal.Open(ds.GetSubDatasets()[3][0])
lon_arr = ds_lon.ReadAsArray()

## lat, lon values are in EPSG 4326, this transfroms them into EPSG 3035
proj = '3035'
in_proj = Proj('epsg:4326')
out_proj = Proj('epsg:'+proj)
x_arr, y_arr = transform(in_proj, out_proj, lon_arr, lat_arr)

## get extent of reference raster
## Format is: [[UpperLeft],[LowerLeft],[LowerRight],[UpperRight]]
extent = raster.getExtent(gt, ref_ras.RasterXSize, ref_ras.RasterYSize)
min_x = min([i[0] for i in extent])
max_x = max([i[0] for i in extent])
min_y = min([i[1] for i in extent])
max_y = max([i[1] for i in extent])

## optional: create gt for output, but in this case it should be the same as the reference gt
pixel_x_size = 4000 #(max_x - min_x)/ref_ras.RasterXSize
pixel_y_size = 4000 #(max_y - min_y)/ref_ras.RasterYSize
gt_out = (min_x, pixel_x_size, 0, max_y, 0, -pixel_y_size)

cols = int((max_x - min_x)/4000)
rows = int(math.ceil((max_y - min_y)/4000))

## create two grids of lat/lon values representing the reference raster
## the interpolation-function does not take a pre-created tuple of both grid as input
## the tuple needs to be created on the function (see below for clarification)
xi = np.linspace(min_x, min_x + (cols*4000), cols)
yi = np.linspace(max_y - (rows*4000), max_y, rows)
grid = np.meshgrid(xi, yi)
grid_x = grid[0]
grid_y = grid[1]

## optional: get sub_arr of smi_arr
## for example the last 12 bands, i.e. jan-dec 2018
arr_sub = smi_arr[-12:,:,:]

## optional: flip array upside-down, because values are stored upside-down
## but not necessary since lat/lon values are stored up-down as well
# arr_sub = np.flip(arr_sub, axis=1)

## create list to store all interpolated bands in:
#out_lst = []

for i in range(12):
    print(i)
    ## Get input for interpolation from netcdf arrays
    ## These are the SMI values with corresponding lat/lon values
    arr = arr_sub[i,:,:]
    values = arr.flatten(order='F')
    x_arr_f = x_arr.flatten(order='F')
    y_arr_f = y_arr.flatten(order='F')

    ## Drop no-data values. In this case -9999
    values[values == -9999] = np.nan
    x_arr_f[np.isnan(values)] = np.nan
    y_arr_f[np.isnan(values)] = np.nan
    values = values[np.logical_not(np.isnan(values))]
    x_arr_f = x_arr_f[np.logical_not(np.isnan(x_arr_f))]
    y_arr_f = y_arr_f[np.logical_not(np.isnan(y_arr_f))]
    points = np.array([x_arr_f, y_arr_f])
    points = points.T

    ## Interpolate
    grid_int = griddata(points, values, (grid_x, grid_y), method='linear')

    ## ! Do this only, if the netcdf arrays wasnt flipped before !
    ## Optional: flip the interpolated grid
    int_arr = np.flip(grid_int, axis=0)

    ## Set the extrapolated areas to nodata value
    # int_arr[ref_arr == -999] = -999

    ## Optional: plot the array
    # cmap = plt.cm.RdYlGn
    # cmap.set_bad('white')
    # fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    # ax.imshow(out_arr)
    # fig.show()

    out_pth = r'_temp\00_MA\data\climate\SMI\SMI_2018_Gesamtboden_' + str(i) + '_4km.tif'
    ## Write raster to disc
    raster.writeArrayToRaster(int_arr, out_pth, gt_out, pr, -999,options=['COMPRESS=DEFLATE', 'PREDICTOR=3'])

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

