# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import gdal

## CJs REPO
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

grid_pth = r"_temp\00_MA\data\vector\miscellaneous\4km_grid.shp"
grid_shp = ogr.Open(grid_pth)
grid_lyr = grid_shp.GetLayer()
extent = grid_lyr.GetExtent()
sr = grid_lyr.GetSpatialRef()
res = 4000

width = (extent[1]-extent[0])/res
height = (extent[3]-extent[2])/res
projWin = [extent[0],extent[3],extent[1],extent[2]]

options = gdal.TranslateOptions(width=width, height=height, projWin=projWin, projWinSRS=sr )
# ## SPI
# spi_lst = [1,3,6,12,24]
# for spi in spi_lst:
#     for month in range(1,13):
#
#         out_pth = r"_temp\00_MA\data\climate\SPI\SPI_{0:02d}\SPI_{1:02d}2018_{0:02d}_3035_4km.tif".format(spi, month)
#         ras_pth = r"_temp\00_MA\data\climate\SPI\SPI_{0:02d}\SPI_{1:02d}2018_{0:02d}_3035.tif".format(spi, month)
#         ras = gdal.Open(ras_pth)
#         out_ras = gdal.Translate(out_pth, ras, options=options)
## Stack SPIS
# for spi in spi_lst:
#     lst = []
#     for month in range(1,13):
#         ras_pth = r"_temp\00_MA\data\climate\SPI\SPI_{0:02d}\SPI_{1:02d}2018_{0:02d}_3035_4km.tif".format(spi, month)
#         ras = gdal.Open(ras_pth)
#         lst.append(ras)
#     raster.stackRasterFromList(lst,r"_temp\00_MA\data\climate\SPI\SPI{0:02d}-2018_4km.tif".format(spi))
#
# -------------------------------
#
# ## SPEI
# spei_lst = [3,6,12,24]
# for spei in spei_lst:
#     out_pth = r"_temp\00_MA\data\climate\SPEI\SPEI{0:02d}-2018_4km.tif".format(spei)
#     ras_pth = r"_temp\00_MA\data\climate\SPEI\SPEI{0:02d}-2018.tif".format(spei)
#     ras = gdal.Open(ras_pth)
#     out_ras = gdal.Translate(out_pth, ras, options=options)
# del out_ras
#
# ## SMI
# out_pth = r"_temp\00_MA\data\4katja\original_data\UFZ\SMI_2018_Gesamtboden_4km.tif"
# ras_pth = r"_temp\00_MA\data\4katja\original_data\UFZ\SMI_2018_Gesamtboden_1km.tif"
# ras = gdal.Open(ras_pth)
# out_ras = gdal.Translate(out_pth, ras, options=options)

## EVAPO
out_pth = r"_temp\00_MA\data\climate\dwd_evapo_p\time_series\EVAPO_2018_3035_4km.tif"
ras_pth = r"_temp\00_MA\data\climate\dwd_evapo_p\time_series\EVAPO_2018_3035.tif"
ras = gdal.Open(ras_pth)
out_ras = gdal.Translate(out_pth, ras, options=options)

## PRECIP
out_pth = r"_temp\00_MA\data\climate\dwd_precipitation\RSMS\time_series\RSMS_01-12_2018-2018_3035_4km.tif"
ras_pth = r"_temp\00_MA\data\climate\dwd_precipitation\RSMS\time_series\RSMS_01-12_2018-2018_3035.tif"
ras = gdal.Open(ras_pth)
options = gdal.TranslateOptions(width=width, height=height, projWin=projWin, projWinSRS=sr)
out_ras = gdal.Translate(out_pth, ras, options=options)

## TEMP
out_pth = r"_temp\00_MA\data\climate\dwd_temperature\times_series\TEMP_2018_3035_4km.tif"
ras_pth = r"_temp\00_MA\data\climate\dwd_temperature\times_series\TEMP_2018_3035.tif"
ras = gdal.Open(ras_pth)
options = gdal.TranslateOptions(width=width, height=height, projWin=projWin, projWinSRS=sr)
out_ras = gdal.Translate(out_pth, ras, options=options)

#----------- END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#