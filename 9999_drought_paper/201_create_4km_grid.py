# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import gdal
import os
import math
import numpy as np
import ogr, osr

## Clemens repo
import raster
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

grid_res = 4000

ras = gdal.Open(r"Q:\FORLand\Clemens\_temp\00_MA\data\4katja\original_data\UFZ\SMI_2018_Gesamtboden_1km.tif")
ras_ext = raster.getCorners(r"Q:\FORLand\Clemens\_temp\00_MA\data\4katja\original_data\UFZ\SMI_2018_Gesamtboden_1km.tif")

x_ext = ras_ext[2] - ras_ext[0]
y_ext = ras_ext[3] - ras_ext[1]

gt = ras.GetGeoTransform()
pr = ras.GetProjection()

ras_res = gt[1]
sr = osr.SpatialReference()
sr.ImportFromWkt(pr)

grid_col = math.ceil(x_ext / grid_res)
grid_row = math.ceil(y_ext / grid_res)

out_shp_name = r'Q:\FORLand\Clemens\_temp\00_MA\data\vector\miscellaneous\4km_grid.shp'
drv = ogr.GetDriverByName('ESRI Shapefile')

if os.path.exists(out_shp_name):
    drv.DeleteDataSource(out_shp_name)

lyr_name = '4km_grid'
ds = drv.CreateDataSource(out_shp_name)
out_polygons = ds.CreateLayer(lyr_name, sr, ogr.wkbPolygon)

#add fields
out_polygons.CreateField(ogr.FieldDefn("POLYID", ogr.OFTString))

curr_xmin = ras_ext[0]
for col in range(0, grid_col):
    curr_ymin = ras_ext[1]

    for row in range(0, grid_row):

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(curr_xmin, curr_ymin)
        ring.AddPoint(curr_xmin + grid_res, curr_ymin)
        ring.AddPoint(curr_xmin + grid_res, curr_ymin + grid_res)
        ring.AddPoint(curr_xmin, curr_ymin + grid_res)
        ring.AddPoint(curr_xmin, curr_ymin)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        poly.CloseRings()

        poly_id = '{0:04d}_{1:04d}'.format(col+1, row+1)

        out_defn = out_polygons.GetLayerDefn()
        out_feat = ogr.Feature(out_defn)
        out_feat.SetGeometry(poly)
        out_polygons.CreateFeature(out_feat)

        out_feat.SetField(0, poly_id)
        out_polygons.SetFeature(out_feat)

        curr_ymin += grid_res

    curr_xmin += grid_res

ds = None

# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#