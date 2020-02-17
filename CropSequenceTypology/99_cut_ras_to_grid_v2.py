# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import gdal
import ogr
import glob
import math
import osr
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
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    return [minx, miny, maxx, maxy]
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

ras = gdal.Open(r"raster\2005-2005_Inv_Stack_5m_BIN_mosaic.tif")
gt = ras.GetGeoTransform()
inv_gt = gdal.InvGeoTransform(gt)

grid_res = 15000

ras_ext = getCorners(r'raster\2005-2005_Inv_Stack_5m_BIN_mosaic.tif')

x_ext = ras_ext[2] - ras_ext[0]
y_ext = ras_ext[3] - ras_ext[1]

gt = ras.GetGeoTransform()
pr = ras.GetProjection()

ras_res = gt[1]

grid_col = math.ceil(x_ext / grid_res)
grid_row = math.ceil(y_ext / grid_res)

# create shapefile
sr = osr.SpatialReference()
sr.ImportFromWkt(pr)
out_shp_name = 'L:/Clemens/data/vector/grid/Invekos_grid_15km.shp'
drv = ogr.GetDriverByName('ESRI Shapefile')
if os.path.exists(out_shp_name):
    drv.DeleteDataSource(out_shp_name)
lyr_name = 'Invekos_grid_01'
ds = drv.CreateDataSource(out_shp_name)
out_polygons = ds.CreateLayer(lyr_name, sr, ogr.wkbPolygon)
out_polygons.CreateField(ogr.FieldDefn("POLYID", ogr.OFTString))

curr_xmin = ras_ext[0]
for col in range(0, grid_col):
    curr_ymin = ras_ext[1]

    for row in range(0, grid_row):
        poly_id = 'X{0:02d}_Y{1:02d}'.format(col + 1, row + 1)
        print(poly_id)

        x_min = curr_xmin
        x_max = curr_xmin + grid_res
        y_min = curr_ymin
        y_max = curr_ymin + grid_res
        print("   Xmin      -      Ymin      -      Xmax       -      Ymax")
        print(ras_ext[0],ras_ext[1],ras_ext[2],ras_ext[3])
        print(x_min, y_min, x_max, y_max, "\n")

        out_path = r"raster\grid_15km\{0}\\".format(poly_id)
        createFolder(out_path)
        out_name = out_path + '2005-2005_Inv_Stack_5m_BIN.tif'

        # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
        ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min])# , projWinSRS=sr)
        ras_cut = None

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(curr_xmin, curr_ymin)
        ring.AddPoint(curr_xmin + grid_res, curr_ymin)
        ring.AddPoint(curr_xmin + grid_res, curr_ymin + grid_res)
        ring.AddPoint(curr_xmin, curr_ymin + grid_res)
        ring.AddPoint(curr_xmin, curr_ymin)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        poly.CloseRings()

        out_defn = out_polygons.GetLayerDefn()  # get the layer definition
        out_feat = ogr.Feature(out_defn)  # erzeugt ein leeres dummy-feature
        out_feat.SetGeometry(poly)  # packt die polygone in das dummy feature
        out_polygons.CreateFeature(out_feat)  # fügt das feature zum layer hinzu

        out_feat.SetField(0, poly_id)
        out_polygons.SetFeature(out_feat)

        curr_ymin += grid_res

    curr_xmin += grid_res

ds = None

# file_list = glob.glob(r'L:\Clemens\data\raster\grid_30km\**\2005-2005_Inv_Stack_5m_BIN.tif')
# vrt = gdal.BuildVRT(r'L:\Clemens\data\raster\grid_30km\2005-2005_Inv_Stack_5m_BIN.vrt', file_list)
# del(vrt)

# print(gdal.Info(ras))
print("Script Done!")
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#