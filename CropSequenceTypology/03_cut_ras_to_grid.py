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

per_lst = [(2017,2018)]
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
per = per_lst[0]

rastypes = ['Inv_CropTypesLeCe', 'Inv_CropTypesWiSu', 'Inv_CropTypes']
for rastype in rastypes:
    for per in per_lst:
        print(per)
        min = per[0]
        max = per[1] + 1

        year = 2005
        for year in range(min,max):
        # def workFunc(year):
            print(year)

            shp = ogr.Open(r"vector\grid\Invekos_grid_BB_15km.shp")
            lyr = shp.GetLayer()

            sr = lyr.GetSpatialRef()

            ras = gdal.Open(r"raster\{0}_BB_{1}_5m.tif".format(rastype, year))

            feat = lyr.GetFeature(0)

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
                out_name = out_path + '{0}_{1}_5m.tif'.format(rastype, year)

                # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
                ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min], projWinSRS=sr, creationOptions=['COMPRESS=DEFLATE'])
                ras_cut = None

                print(name, "done")
            lyr.ResetReading()

            print(year, "done")

        # if __name__ == '__main__':
        #     joblib.Parallel(n_jobs=8)(joblib.delayed(workFunc)(year) for year in range(min, max))

        print(per, "done")
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