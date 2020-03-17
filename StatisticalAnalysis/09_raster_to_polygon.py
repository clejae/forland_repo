# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import osr
import gdal


# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'data\raster\tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]
tiles_lst = [r'data\raster\grid_15km\{0}\2005-2011_CropSeqType_v2.tif'.format(t) for t in tiles_lst]

## actually a vrt, I called it ras, because of the line below
ras = gdal.BuildVRT(r'data\raster\2005-2011_CropSeqType_v2.vrt', tiles_lst)

# ras = gdal.Open(r'data\raster\grid_15km\{0}\2005-2011_CropSeqType_v2.tif'.format(tile))
pr = ras.GetProjection()
band = ras.GetRasterBand(1)

srs = osr.SpatialReference()
srs.ImportFromWkt(pr)

out_shp_name = "cst_fields"
drv = ogr.GetDriverByName("ESRI Shapefile")
out_shp = drv.CreateDataSource(r"data\vector\cst_fields\{0}.shp".format(out_shp_name))
out_lyr = out_shp.CreateLayer(out_shp_name, srs = srs)
field = ogr.FieldDefn("ID", ogr.OFTInteger)
out_lyr.CreateField(field)

gdal.Polygonize(band, None, out_lyr, 0, [], callback = None)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


