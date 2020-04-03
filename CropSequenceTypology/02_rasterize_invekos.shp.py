# Clemens Jänicke
# github Repo: https://github.com/clejae

# --------------------------------------------------------------- LOAD PACKAGES ---------------------------------------------------------------#
import gdal
import math
import ogr
import os
import time
import joblib

## Clemens repo
# import raster
# import vector
# --------------------------------------------------------------- DEFINE FUNCTIONS ---------------------------------------------------------------#

# --------------------------------------------------------------- USER VARIABLES ---------------------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'

## Federal state
bl = 'BB'

## Attribute to rasterize; attribute options: "ID_KTYP", "ID_WiSo", "ID_HaBl", "Oeko"
attribute = "Oeko"

## List of periods
per_lst = [(2005,2018)]
# --------------------------------------------------------------- LOAD DATA & PROCESSING ---------------------------------------------------------------#
os.chdir(wd)

#### 1. Define extent
## Get extent of box of federal state
shp_pth = wd + r'vector\grid\Invekos_grid_{0}-Box_15km.shp'.format(bl)
shp = ogr.Open(shp_pth, 0)
lyr = shp.GetLayer()
x_min_ext, x_max_ext, y_min_ext, y_max_ext = lyr.GetExtent()

#### 2. Define output raster characteristics
## upper left corner
x_min = x_min_ext
y_max = y_max_ext

## number of cols and rows and bottom right corner
res = 5
cols = math.ceil((x_max_ext - x_min_ext) / res)
rows = math.ceil((y_max_ext - y_min_ext) / res)
x_max = x_min + cols * res
y_min = y_max - rows * res

## no data value
no_data_val = 255

#### 3. Rasterize the vector
for per in per_lst:
    min = per[0]
    max = per[1] + 1
    # ras_lst = []

    def workFunc(year):
    # for year in range(min,max):
        print('Rasterization year: {0}'.format(year))

        ## open shapefile
        if bl == "BB":
            shp_pth = wd + r'vector\InvClassified\Inv_NoDups_{0}.shp'.format(year)
        if bl == "SA":
            shp_pth = wd + r'vector\InvClassified\Antraege{0}_cleaned.shp'.format(year)

        # shp_pth = wd + r'Inv_NoDups_2005.shp'.format(year)
        if os.path.exists(shp_pth):
            shp = ogr.Open(shp_pth, 0) # 0=read only, 1=writeabel
            lyr = shp.GetLayer()
            print(year)
            #printFieldNames(lyr)

            #### 3a. Transform spatial reference of shapefiles into projection of raster
            sr = lyr.GetSpatialRef()
            pr = sr.ExportToWkt()

            #### 3b. Create output raster
            ## if it is needed to write the rasters per year out, then uncomment the next two lines and comment the third line
            target_ds_pth = r'raster\mosaics\{0}_CropTypes{1}_{2}.tif'.format(bl, attribute, year)
            target_ds = gdal.GetDriverByName('GTiff').Create(target_ds_pth, cols, rows, 1, gdal.GDT_Byte, options = ['COMPRESS=DEFLATE'])# gdal.GDT_Int16)#
            # target_ds = gdal.GetDriverByName('MEM').Create('', cols, rows, 1,gdal.GDT_Byte) # gdal.GDT_Int16)  #
            target_ds.SetGeoTransform((x_min, res, 0, y_max, 0, -res))
            target_ds.SetProjection(pr)
            band = target_ds.GetRasterBand(1)
            band.Fill(no_data_val)
            band.SetNoDataValue(no_data_val)
            band.FlushCache()

            option_str = "ATTRIBUTE=" + attribute
            gdal.RasterizeLayer(target_ds, [1], lyr, options=[option_str]) #burn_values=[1])#burn_values=[1])#

            # ras_lst.append(target_ds)
            del target_ds
        else:
            print(shp_pth, "doesn't exist.")

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=11)(joblib.delayed(workFunc)(year) for year in range(min, max))

    ## stack rasters
    # print("Stacking started!")
    # raster.StackRasterFromList(ras_lst, r'L:\Clemens\data\raster\{0}-{1}_Inv_Stack_5m.tif'.format(min, max-1))
    # print("Stacking done!")
    # del ras_lst

print("Script done!")

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

## Get common extent of invekos shapes over the years.
# x_min_lst = []
# x_max_lst = []
# y_min_lst = []
# y_max_lst = []
### loop over shapefiles and get extent that covers all shapefiles
# for year in range(2005,2019):
#     print('year: {0}'.format(year))
#
#     # shp_pth = wd + r'vector\misc\Inv_NoDups_{0}_testsub.shp'.format(year)
#     shp_pth = wd + r'Inv_NoDups_{}.shp'.format(year)
#     shp = ogr.Open(shp_pth, 0)
#     lyr = shp.GetLayer()
#     x_min_lyr, x_max_lyr, y_min_lyr, y_max_lyr = lyr.GetExtent()
#     x_min_lst.append(x_min_lyr)
#     x_max_lst.append(x_max_lyr)
#     y_min_lst.append(y_min_lyr)
#     y_max_lst.append(y_max_lyr)
#
# x_min_ext = min(x_min_lst)
# x_max_ext = max(x_max_lst)
# y_min_ext = min(y_min_lst)
# y_max_ext = max(y_max_lst)