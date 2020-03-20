# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd
import gdal
import raster
import general
from collections import Counter
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
## INPUT
in_shp_pth = r"data\vector\InvClassified\Inv_NoDups_2011.shp"
cst_ras_name = "2005-2011_CropSeqType_v2.tif"
ct_ras_name = "2005-2011_Inv_CropTypes_5m.tif"

## OUTPUT
out_shp_pth = r"data\vector\InvClassified\Inv_NoDups_2011_centroids.shp"
out_csv_descr = '2005-2011_all_sequences'

#############
with open(r'data\raster\tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

shp = ogr.Open(in_shp_pth)
lyr = shp.GetLayer()
sr = lyr.GetSpatialRef()

shp_tiles = ogr.Open(r"data\vector\grid\Invekos_grid_GER_15km.shp")
lyr_tiles = shp_tiles.GetLayer()

# drv = ogr.GetDriverByName("ESRI Shapefile")
# if os.path.exists(out_shp_pth):
#     drv.DeleteDataSource(out_shp_pth)
# out_shp = drv.CreateDataSource(out_shp_pth)
# lyr_name = os.path.basename(out_shp_pth)
# out_lyr = out_shp.CreateLayer(lyr_name, sr, geom_type=ogr.wkbPoint)
# out_lyr.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger64))
# # out_lyr.CreateField(ogr.FieldDefn("Tile", ogr.OFTString))
# out_defn = out_lyr.GetLayerDefn()
#
# for feat in lyr:
#     fid = feat.GetField("ID")
#     print(fid)
#     geom = feat.GetGeometryRef()
#
#     centroid = geom.Centroid()
#
#     # lyr_tiles.SetSpatialFilter(centroid)
#     # tile = lyr_tiles.GetNextFeature()
#     # tile_name = tile.GetField("POLYID")
#     # print(tile_name)
#
#     out_feat = ogr.Feature(out_defn)  # erzeugt ein leeres dummy-feature
#     out_feat.SetGeometry(centroid)  # packt die polygone in das dummy feature
#     out_lyr.CreateFeature(out_feat)
#     out_feat.SetField(0, fid)
#     # out_feat.SetField(1, tile_name)
#
# lyr.ResetReading()
# out_shp.Destroy()

print("\n######## EXTRACTION ########\n")

def workFunc(tile):
    print(tile)
    ras_cst_pth = r"data\raster\grid_15km\{}\{}".format(tile, cst_ras_name)
    ras_ct_pth = r"data\raster\grid_15km\{}\{}".format(tile, ct_ras_name)

    ras_cst = gdal.Open(ras_cst_pth)
    arr_cst = ras_cst.ReadAsArray()

    ras_ct = gdal.Open(ras_ct_pth)
    arr_ct = ras_ct.ReadAsArray()

    gt = ras_cst.GetGeoTransform()
    minx, miny, maxx, maxy = raster.getCorners(ras_cst_pth)

    out_lst = []

    shp = ogr.Open(out_shp_pth)
    lyr = shp.GetLayer()
    # double minx, double miny, double maxx, double maxy
    lyr.SetSpatialFilterRect(minx, miny, maxx, maxy)

    for feat in lyr:
        geom = feat.GetGeometryRef()
        centroid = geom.Centroid()
        mx, my = centroid.GetX(), centroid.GetY()
        px = int((mx - gt[0]) / gt[1])  # x pixel
        py = int((my - gt[3]) / gt[5])  # y pixel
        cst = arr_cst[ py, px]
        ct = arr_ct[:, py, px]
        ct[ct == 30] = 255
        ct[ct == 80] = 255
        ct[ct == 99] = 255
        ct[ct == 14] = 12

        ct = list(ct)
        ct = [str(id) for id in ct]
        out_str = '_'.join(list(ct))

        out_lst.append([cst, out_str])

    out_pth = r"data\tables\CropRotations\sequences\{}_{}.csv".format(out_csv_descr, tile)
    if len(out_lst) > 0:
        general.writeListToCSV(out_lst, out_pth)
    print(tile, "done")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=17)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

lst = general.getFilesinFolderWithEnding(r'data\tables\CropRotations\sequences', "csv", True)

df = pd.DataFrame(columns=[0,1])
for c, csv_pth in enumerate(lst):
    print(c, csv_pth)
    csv = pd.read_csv(csv_pth, header=None)
    df = df.append(csv)

df = df.reset_index()
df = df.drop(columns=['index'])
df.to_csv(r'data\tables\CropRotations\{}.csv'.format(out_csv_descr))
ind_lst = df.index[df[0] == 255].tolist()
df_clean = df.drop(ind_lst)

seq_lst = df_clean[1].tolist()
seq_count = Counter(seq_lst)

df_out = pd.DataFrame.from_dict(seq_count, orient='index') #, columns=
df_out = df_out.reset_index()
df_out.columns = ['sequence','count']

df_out.to_csv(r'data\tables\CropRotations\{}_counts.csv'.format(out_csv_descr))

mcst_lst = [13, 23, 35, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
for mcst in mcst_lst:
    ind_lst = df_clean.index[df_clean[0] != mcst].tolist()
    df_mcst = df_clean.drop(ind_lst)
    seq_lst = df_mcst[1].tolist()
    seq_count = Counter(seq_lst)

    df_out = pd.DataFrame.from_dict(seq_count, orient='index')  # , columns=
    df_out = df_out.reset_index()
    df_out.columns = ['sequence', 'count']

    df_out.to_csv(r'data\tables\CropRotations\{}_counts_{}.csv'.format(out_csv_descr,mcst), index=False)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


