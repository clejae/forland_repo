# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import gdal
import os
import math
import numpy as np
import ogr, osr

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
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
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

grid_res = 10000

ras = gdal.Open(r'raster\grid\2005-2005_Inv_Stack_5m_BIN.tif')
ras_ext = getCorners(r'raster\grid\2005-2005_Inv_Stack_5m_BIN.tif')

x_ext = ras_ext[2] - ras_ext[0]
y_ext = ras_ext[3] - ras_ext[1]

gt = ras.GetGeoTransform()
pr = ras.GetProjection()

ras_res = gt[1]

grid_col = math.ceil(x_ext / grid_res)
grid_row = math.ceil(y_ext / grid_res)

sr = osr.SpatialReference()
sr.ImportFromWkt(pr)

out_shp_name = 'L:/Clemens/data/vector/grid/Invekos_grid_10km.shp'
drv = ogr.GetDriverByName('ESRI Shapefile')

if os.path.exists(out_shp_name):
    drv.DeleteDataSource(out_shp_name)

lyr_name = 'Invekos_grid_01'
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

        out_defn = out_polygons.GetLayerDefn()  # get the layer definition
        out_feat = ogr.Feature(out_defn)  # erzeugt ein leeres dummy-feature
        out_feat.SetGeometry(poly)  # packt die polygone in das dummy feature
        out_polygons.CreateFeature(out_feat)  # fügt das feature zum layer hinzu

        out_feat.SetField(0, poly_id)
        out_polygons.SetFeature(out_feat)

        curr_ymin += grid_res

    curr_xmin += grid_res

ds = None

# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#