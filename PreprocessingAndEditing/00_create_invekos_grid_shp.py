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

grid_res = 15000

shp = ogr.Open(r"Q:\FORLand\Daten\vector\Administrativ\Deutschlandweit\vg250-ew_3112.utm32s.shape.kompakt\vg250-ew_kompakt\VG250_F.shp")
shp = ogr.Open(r"Q:\FORLand\Clemens\data\vector\grid\force-tiles_ger_25832.shp")
lyr = shp.GetLayer()

ext = lyr.GetExtent()
#xmin, xmax, ymin, ymax

x_ext = ext[1] - ext[0]
y_ext = ext[3] - ext[2]

sr = lyr.GetSpatialRef()

# ras = gdal.Open(r'raster\grid\2005-2005_Inv_Stack_5m_BIN.tif')
# ras_ext = raster.getCorners(r'raster\grid\2005-2005_Inv_Stack_5m_BIN.tif')
#
# x_ext = ras_ext[2] - ras_ext[0]
# y_ext = ras_ext[3] - ras_ext[1]
#
# gt = ras.GetGeoTransform()
# pr = ras.GetProjection()
#
# ras_res = gt[1]
# sr = osr.SpatialReference()
# sr.ImportFromWkt(pr)

grid_col = math.ceil(x_ext / grid_res)
grid_row = math.ceil(y_ext / grid_res)

out_shp_name = 'vector/grid/Invekos_grid_GER_10km2.shp'
drv = ogr.GetDriverByName('ESRI Shapefile')

if os.path.exists(out_shp_name):
    drv.DeleteDataSource(out_shp_name)

lyr_name = 'Invekos_grid_01'
ds = drv.CreateDataSource(out_shp_name)
out_polygons = ds.CreateLayer(lyr_name, sr, ogr.wkbPolygon)

#add fields
out_polygons.CreateField(ogr.FieldDefn("POLYID", ogr.OFTString))

curr_xmin = ext[0]
for col in range(0, grid_col):
    curr_ymin = ext[2]

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