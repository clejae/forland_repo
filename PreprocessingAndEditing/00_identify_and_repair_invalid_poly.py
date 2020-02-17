# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
from osgeo import ogr
import numpy as np

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def printFieldNames(lyr):
    lyr_defn = lyr.GetLayerDefn()
    print("Column name | Field type | Width | Precision")
    print("--------------------------------------------")
    for i in range(lyr_defn.GetFieldCount()):
        field_name = lyr_defn.GetFieldDefn(i).GetName()
        field_type_code = lyr_defn.GetFieldDefn(i).GetType()
        field_type = lyr_defn.GetFieldDefn(i).GetFieldTypeName(field_type_code)
        field_width = lyr_defn.GetFieldDefn(i).GetWidth()
        get_precision = lyr_defn.GetFieldDefn(i).GetPrecision()

        print(field_name + " | " + field_type + " | " + str(field_width) + " | " + str(get_precision))

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

shp = ogr.Open(r'data\vector\repairInvekos\Antraege2008.shp', 0)
lyr = shp.GetLayer()

shp2 = ogr.Open(r'data\vector\repairInvekos\Antraege2008 - Kopie.shp', 0)
lyr2 = shp.GetLayer()


printFieldNames(lyr)

lyr_defn = lyr.GetLayerDefn()
field_lst = [lyr_defn.GetFieldDefn(i).GetName() for i in range(lyr_defn.GetFieldCount())]

# check for invalid polygons
id_lst = []
for feat in lyr:
    geom = feat.GetGeometryRef()
    name = feat.GetField('ID')
    if not geom.IsValid():
        print(name)
        id_lst.append(name)
lyr.ResetReading()
id_lst.sort()

# repair invalid polygons
for feat in lyr:
    geom = feat.GetGeometryRef()
    if not geom.IsValid():
        feat.SetGeometry(geom.Buffer(0))
        lyr.SetFeature(feat)
        assert feat.GetGeometryRef().IsValid()
lyr.ResetReading()

id_lst = []
index_lst = []
check_lst = []
attr_main_lst = []
area_lst = []
peri_lst = []

for f, feat in enumerate(lyr):
    name = feat.GetField('ID')
    peri = feat.GetGeometryRef().Boundary().Length()
    area = feat.GetGeometryRef().GetArea()
    attr_lst = []
    for field in field_lst:
        attr_lst.append(feat.GetField(field))
    geom = feat.GetGeometryRef()
    wkt = geom.ExportToWkt()

    area_lst.append(area)
    peri_lst.append(peri)
    id_lst.append(name)
    index_lst.append(f)
    check_lst.append(wkt)
    attr_main_lst.append(attr_lst)
lyr.ResetReading()

feat = lyr.GetNextFeature()
for feat in lyr:
    geom = feat.GetGeometryRef()

    lyr2.SetSpatialFilter(geom)

    for feat2 in lyr2:
        print(feat2.GetField('ID'))
        intersection = feat2.Intersection(feat)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

# def removeSliver(ds, EPSG):
#     from osgeo import osr, ogr
#     lyr = ds.GetLayer()
#     out_ds = ogr.GetDriverByName('Memory').CreateDataSource('')
#     srs = osr.SpatialReference()
#     srs.ImportFromEPSG(EPSG)
#     out_lyr = out_ds.CreateLayer('', srs)
#     for feature in lyr:
#         geom = feature.GetGeometryRef()
#         perimeter = feature.GetGeometryRef().Boundary().Length()
#         area = feature.GetGeometryRef().GetArea()
#         sliver = float(perimeter/area)
#         if sliver <1:
#             if geom.IsValid() == True:
#                 wkt = geom.ExportToWkt()
#                 new_poly = ogr.CreateGeometryFromWkt(wkt)
#                 new_feat = ogr.Feature(out_lyr.GetLayerDefn())
#                 new_feat.SetGeometry(new_poly)
#                 out_lyr.CreateFeature(new_feat)
#                 new_feat = None
#             else:
#                 new_feat = ogr.Feature(out_lyr.GetLayerDefn())
#                 new_feat.SetGeometry(geom.Buffer(0))
#                 out_lyr.CreateFeature(new_feat)
#                 new_feat = None
#     out_lyr = None
#     return out_ds
#
# def list_duplicates_of(seq,item):
#     start_at = -1
#     locs = []
#     while True:
#         try:
#             loc = seq.index(item,start_at+1)
#         except ValueError:
#             break
#         else:
#             locs.append(loc)
#             start_at = loc
#     return locs

# check_lst = list('ABABCBDEFBABCD')
# dup_lst = []
# i = 0
# item = check_lst[i]
# print(i)
# dup = list_duplicates_of(check_lst, item)
# print(dup)
# if len(dup) > 1:
#     dup_lst.append([item] + dup)
#     print(dup_lst)
# else:
#     print(item, 'not in list')
# i += 1

# tic = time.time()
# dup_lst = []
# for i, item in enumerate(check_lst):
#     dup = list_duplicates_of(check_lst, item)
#
#     if len(dup) > 1:
#         dup_lst.append([item] + dup)
#     else:
#         pass
# toc = time.time()

# arr_area = np.array(area_lst)
# arr_peri = np.array(peri_lst)
#
# for y in range(len(arr_area)):
#     arr_area_check = arr_area / arr_area[y,]
#     arr_area_check[(arr_area_check > .95) & (arr_area_check < 1.05)] = 1
#     arr_area_check[(arr_area_check < .95) | (arr_area_check > 1.05)] = 0
#
#     arr_peri_check = arr_peri / arr_peri[y,]
#     arr_peri_check[(arr_peri_check > .95) & (arr_peri_check < 1.05)] = 1
#     arr_peri_check[(arr_peri_check < .95) | (arr_peri_check > 1.05)] = 0
#
#     arr_area_check[arr_area_check == 1] = 1
#     arr_area_check[arr_area_check != 1] = 0
#
#     # arr_peri_check = arr_peri / arr_peri[y,]
#     # arr_peri_check[arr_peri_check == 1] = 1
#     # arr_peri_check[arr_peri_check != 1] = 0
#
#     check_arr = arr_area_check * arr_peri_check
#
#     print(np.where(check_arr == 1))
#
#
# print(arr_area[291,])
# print(arr_area[6482,])
#
# print(arr_peri[291,])
# print(arr_peri[6482,])
#
# print(arr_area_check[291,])
# print(arr_peri_check[6482,])
#
# print(arr_peri_check[291,])
# print(arr_area_check[6482,])