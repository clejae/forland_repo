# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import gdal
import ogr
import glob
import joblib
import time

## Clemens repo
import general
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
min = 2018
max = 2019
bl = 'BB'

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

rastypes = ['CropTypesOeko'] #'CropTypesLeCe', 'CropTypesWiSu', 'CropTypes'
for rastype in rastypes:

    def workFunc(year):
        print(year)
        ras = gdal.Open(r"raster\mosaics\{0}_{1}_{2}.tif".format(rastype, bl, year))
        shp = ogr.Open(r"vector\grid\Invekos_grid_{}_15km.shp".format(bl))
        lyr = shp.GetLayer()
        sr = lyr.GetSpatialRef()

        for feat in lyr:

            name = feat.GetField('POLYID')
            print(name)

            geom = feat.geometry().Clone()
            ext = geom.GetEnvelope()

            x_min = ext[0]
            x_max = ext[1]
            y_min = ext[2]
            y_max = ext[3]

            out_path = r"raster\grid_15km\{0}\\".format(name)
            general.createFolder(out_path)
            out_name = out_path + '{0}_{1}_{2}.tif'.format(bl, rastype, year)

            # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
            ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min], projWinSRS=sr, creationOptions=['COMPRESS=DEFLATE'])
            ras_cut = None

            print(name, "done")
        lyr.ResetReading()

        print(year, "done")

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=15)(joblib.delayed(workFunc)(year) for year in range(min, max))


    # file_list = glob.glob(r'raster\grid_15km\**\Inv_CropTypes_2005_5m.tif')
    # vrt = gdal.BuildVRT(r'raster\Inv_CropTypes_2005_5m.vrt', file_list)
    # del(vrt)

# print(gdal.Info(ras))
print("Script Done!")

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

# ul = gdal.ApplyGeoTransform(inv_gt, x_min, y_max)
# ll = gdal.ApplyGeoTransform(inv_gt, x_min, y_min)
# ur = gdal.ApplyGeoTransform(inv_gt, x_max, y_max)
# lr = gdal.ApplyGeoTransform(inv_gt, x_max, y_min)