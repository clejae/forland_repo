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

################## VERSION 02 ##################
# import os
# import gdal
# import ogr
# import glob
# import math
# import osr
#
# ##CJ REPO
# import vector
#
#
# # ------------------------------------------ USER VARIABLES ------------------------------------------------#
# wd = r'L:\Clemens\data\\'
# # ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
# os.chdir(wd)
#
# ras = gdal.Open(r"raster\2005-2005_Inv_Stack_5m_BIN_mosaic.tif")
# gt = ras.GetGeoTransform()
# inv_gt = gdal.InvGeoTransform(gt)
#
# grid_res = 15000
#
# ras_ext = vector.getCorners(r'raster\2005-2005_Inv_Stack_5m_BIN_mosaic.tif')
#
# x_ext = ras_ext[2] - ras_ext[0]
# y_ext = ras_ext[3] - ras_ext[1]
#
# gt = ras.GetGeoTransform()
# pr = ras.GetProjection()
#
# ras_res = gt[1]
#
# grid_col = math.ceil(x_ext / grid_res)
# grid_row = math.ceil(y_ext / grid_res)
#
# # create shapefile
# sr = osr.SpatialReference()
# sr.ImportFromWkt(pr)
# out_shp_name = 'L:/Clemens/data/vector/grid/Invekos_grid_15km.shp'
# drv = ogr.GetDriverByName('ESRI Shapefile')
# if os.path.exists(out_shp_name):
#     drv.DeleteDataSource(out_shp_name)
# lyr_name = 'Invekos_grid_01'
# ds = drv.CreateDataSource(out_shp_name)
# out_polygons = ds.CreateLayer(lyr_name, sr, ogr.wkbPolygon)
# out_polygons.CreateField(ogr.FieldDefn("POLYID", ogr.OFTString))
#
# curr_xmin = ras_ext[0]
# for col in range(0, grid_col):
#     curr_ymin = ras_ext[1]
#
#     for row in range(0, grid_row):
#         poly_id = 'X{0:02d}_Y{1:02d}'.format(col + 1, row + 1)
#         print(poly_id)
#
#         x_min = curr_xmin
#         x_max = curr_xmin + grid_res
#         y_min = curr_ymin
#         y_max = curr_ymin + grid_res
#         print("   Xmin      -      Ymin      -      Xmax       -      Ymax")
#         print(ras_ext[0],ras_ext[1],ras_ext[2],ras_ext[3])
#         print(x_min, y_min, x_max, y_max, "\n")
#
#         out_path = r"raster\grid_15km\{0}\\".format(poly_id)
#         vector.createFolder(out_path)
#         out_name = out_path + '2005-2005_Inv_Stack_5m_BIN.tif'
#
#         # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
#         ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min])# , projWinSRS=sr)
#         ras_cut = None
#
#         ring = ogr.Geometry(ogr.wkbLinearRing)
#         ring.AddPoint(curr_xmin, curr_ymin)
#         ring.AddPoint(curr_xmin + grid_res, curr_ymin)
#         ring.AddPoint(curr_xmin + grid_res, curr_ymin + grid_res)
#         ring.AddPoint(curr_xmin, curr_ymin + grid_res)
#         ring.AddPoint(curr_xmin, curr_ymin)
#
#         poly = ogr.Geometry(ogr.wkbPolygon)
#         poly.AddGeometry(ring)
#         poly.CloseRings()
#
#         out_defn = out_polygons.GetLayerDefn()  # get the layer definition
#         out_feat = ogr.Feature(out_defn)  # erzeugt ein leeres dummy-feature
#         out_feat.SetGeometry(poly)  # packt die polygone in das dummy feature
#         out_polygons.CreateFeature(out_feat)  # fügt das feature zum layer hinzu
#
#         out_feat.SetField(0, poly_id)
#         out_polygons.SetFeature(out_feat)
#
#         curr_ymin += grid_res
#
#     curr_xmin += grid_res
#
# ds = None
#
# # file_list = glob.glob(r'L:\Clemens\data\raster\grid_30km\**\2005-2005_Inv_Stack_5m_BIN.tif')
# # vrt = gdal.BuildVRT(r'L:\Clemens\data\raster\grid_30km\2005-2005_Inv_Stack_5m_BIN.vrt', file_list)
# # del(vrt)
#
# # print(gdal.Info(ras))
# print("Script Done!")