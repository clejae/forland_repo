# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import gdal
import ogr
import glob
import joblib
import time

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def createFolder(directory):
    import os
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

def getCorners(path):
    ds = gdal.Open(path)
    gt = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize
    minx = gt[0]
    maxy = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    miny = gt[3]
    return [minx, miny, maxx, maxy]
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'

per_lst = [(2005,2011),(2012,2018)]
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

for per in per_lst:
    print(per)
    min = per[0]
    max = per[1] + 1

    # for year in range(2005,2012):
    def workFunc(year):
        print(year)

        shp = ogr.Open(r"L:\Clemens\data\vector\grid\Invekos_grid_BB_15km.shp")
        lyr = shp.GetLayer()

        sr = lyr.GetSpatialRef()

        ras = gdal.Open(r"L:\Clemens\data\raster\Inv_CropTypes_{0}_5m.tif".format(year))

        for feat in lyr:

            name = feat.GetField('POLYID')
            print(name)

            geom = feat.geometry().Clone()
            ext = geom.GetEnvelope()

            x_min = ext[0]
            x_max = ext[1]
            y_min = ext[2]
            y_max = ext[3]

            out_path = r"L:\Clemens\data\raster\grid_15km\{0}\\".format(name)
            createFolder(out_path)
            out_name = out_path + 'Inv_CropTypes_{0}_5m.tif'.format(year)

            # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
            ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min], projWinSRS=sr)
            ras_cut = None

            print(name, "done")
        lyr.ResetReading()

        print(year, "done")

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=8)(joblib.delayed(workFunc)(year) for year in range(min, max))

    print(per, "done")
# file_list = glob.glob(r'L:\Clemens\data\raster\grid_15km\**\Inv_CropTypes_2005_5m.tif')
# vrt = gdal.BuildVRT(r'L:\Clemens\data\raster\Inv_CropTypes_2005_5m.vrt', file_list)
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