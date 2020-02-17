# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
from osgeo import ogr


# QGIS
# from qgis.core import QgsApplication, QgsProcessingRegistry
# from qgis.testing import start_app
# from qgis.analysis import QgsNativeAlgorithms
# import processing
# # app = start_app()

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

in_shp_name = r'data\vector\repairInvekos\Antraege2008_sub.shp'

shp = ogr.Open(in_shp_name, 0)
in_lyr = shp.GetLayer()
in_sr = in_lyr.GetSpatialRef()
in_lyr_defn = in_lyr.GetLayerDefn()
num_fields = in_lyr_defn.GetFieldCount()

print(in_lyr.GetFeatureCount())

drv_mem = ogr.GetDriverByName('Memory')
drv_shp = ogr.GetDriverByName('ESRI Shapefile')

## create a copy of the input layer in memory
## needed to loop over in_layer and use the current feat
## to filter all touching features (in copied lyr)
## in the end, reset the layer, because apparently if you copy the layer
## it loops over all features and does not reset them
shp_copy = drv_mem.CreateDataSource('temp')
copy_lyr = shp_copy.CopyLayer(in_lyr, 'lyr_copy')
print(copy_lyr.GetFeatureCount())
in_lyr.ResetReading()

## create a output shapefile in memory into which
## all features that are not duplicates or almost duplicates
## will be written to
clean_shp_name = in_shp_name[:-4] + '_clean.shp'
if os.path.exists(clean_shp_name):
    drv_shp.DeleteDataSource(clean_shp_name)
shp_clean = drv_shp.CreateDataSource(clean_shp_name)
clean_lyr_name = os.path.splitext(os.path.split(clean_shp_name)[1])[0]
clean_lyr = shp_clean.CreateLayer(clean_lyr_name, in_sr, geom_type=ogr.wkbMultiPolygon)
for i in range(0, num_fields):
        field_def = in_lyr_defn.GetFieldDefn(i)
        field_name = field_def.GetName()
        clean_lyr.CreateField(field_def)
clean_lyr_defn = clean_lyr.GetLayerDefn()

## create a output shapefile into which
## all intersections will be written to
inters_shp_name = in_shp_name[:-4] + '_intersection.shp'
if os.path.exists(inters_shp_name):
    drv_shp.DeleteDataSource(inters_shp_name)
shp_inters = drv_shp.CreateDataSource(inters_shp_name)
inters_lyr_name = os.path.splitext(os.path.split(inters_shp_name)[1])[0]
inters_lyr = shp_inters.CreateLayer(inters_lyr_name,in_sr, geom_type=ogr.wkbMultiPolygon)
for i in range(0, num_fields):
    field_def = in_lyr_defn.GetFieldDefn(i)
    field_name = field_def.GetName()
    inters_lyr.CreateField(field_def)

inters_lyr.CreateField(ogr.FieldDefn('ID_INTERS',ogr.OFTString))
inters_lyr_defn = inters_lyr.GetLayerDefn()

## create a output shapefile into which
## all intersections will be written to
clip_shp_name = in_shp_name[:-4] + '_clip.shp'
if os.path.exists(clip_shp_name):
    drv_shp.DeleteDataSource(clip_shp_name)
shp_clip = drv_shp.CreateDataSource(clip_shp_name)
clip_lyr_name = os.path.splitext(os.path.split(clip_shp_name)[1])[0]
clip_lyr = shp_clip.CreateLayer(clip_lyr_name,in_sr, geom_type=ogr.wkbMultiPolygon)
# clip_lyr.CreateField(ogr.FieldDefn('ID',ogr.OFTString))
for i in range(0, num_fields):
    field_def = in_lyr_defn.GetFieldDefn(i)
    field_name = field_def.GetName()
    clip_lyr.CreateField(field_def)
clip_lyr_defn = clip_lyr.GetLayerDefn()

dupl_lst = []
covered_lst = []
id_lst = []
id_inters_lst = []
for feat in in_lyr:
    id1 = feat.GetField('ID')
    print(id1)
    geom = feat.GetGeometryRef()
    area1 = geom.Area()
    copy_lyr.SetSpatialFilter(geom)

    checker = 0

    for feat2 in copy_lyr:
        id2 = feat2.GetField('ID')
        id_inters = '{0}_{1}'.format(min([id1, id2]), max([id1, id2]))

        geom2 = feat2.geometry()
        # print(id1, geom.GetGeometryName(), id2, geom2.GetGeometryName())
        area2 = geom2.Area()
        intersection = geom2.Intersection(geom)
        area_inters = intersection.Area()

       ## test if area of intersection is equal to area of polygon1
        ## and if both are
        ## if yes then polygon1 is covered by polygon2
        if area_inters == area1 and area1 == area2 and id1 != id2:
            dupl_lst.append([id1, id2])
            checker += 1
        elif area_inters + .5 >= area1 and area1 != area2 and id1 != id2:
            covered_lst.append([id1, id2])
            checker += 1
        elif id_inters not in id_inters_lst and id1 != id2 and area1 != 0:
            out_feat = ogr.Feature(inters_lyr_defn)
            # for i in range(0, num_fields):
            #     field_def = inters_lyr_defn.GetFieldDefn(i)
            #     field_name = field_def.GetName()
            #     ouf_feat.SetField(inters_lyr_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
            out_feat.SetField(num_fields, id_inters)

            out_feat.SetGeometry(intersection.Buffer(0))
            inters_lyr.CreateFeature(out_feat)

            id_inters_lst.append(id_inters)

            # out_feat = ogr.Feature(clip_lyr_defn)
            # out_feat.SetGeometry(clip)
            #
            # for i in range(0, clip_lyr_defn.GetFieldCount()):
            #     field_def = clip_lyr_defn.GetFieldDefn(i)
            #     field_name = field_def.GetName()
            #     ouf_feat.SetField(clip_lyr_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))

    if checker == 0:
        id_lst.append(id1)
        ouf_feat = ogr.Feature(clean_lyr_defn)

        for i in range(0, num_fields):
            field_def = clean_lyr_defn.GetFieldDefn(i)
            field_name = field_def.GetName()
            ouf_feat.SetField(clean_lyr_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))

        # # Set geometry as centroid
        # geom = feat.GetGeometryRef()
        ouf_feat.SetGeometry(geom.Clone())
        # Add new feature to output Layer
        clean_lyr.CreateFeature(ouf_feat)
        ouf_feat = None

    # print('\n')
    copy_lyr.SetSpatialFilter(None)
    copy_lyr.ResetReading()
in_lyr.ResetReading()
clean_lyr.ResetReading()
clip_lyr.ResetReading()

del shp_copy, copy_lyr

for feat in inters_lyr:
    id1 = feat.GetField('ID_INTERS')
    geom = feat.GetGeometryRef()
    clean_lyr.SetSpatialFilter(geom)

    for feat2 in clean_lyr:

        id2 = feat2.GetField('ID')
        id_inters = '{0}_{1}'.format(id1,id2)

        print(id_inters)
        geom2 = feat2.geometry()
        difference = geom2.Difference(geom)

        out_feat = ogr.Feature(clip_lyr_defn)
        # for i in range(0, clip_lyr_defn.GetFieldCount()):
        #     field_def = clip_lyr_defn.GetFieldDefn(i)
        #     field_name = field_def.GetName()
        #     ouf_feat.SetField(clip_lyr_defn.GetFieldDefn(i).GetNameRef(), feat.GetField(i))
        out_feat.SetField(num_fields-1, id_inters)
        out_feat.SetGeometry(difference.Buffer(0))
        out_feat.SetField(0, id_inters)
        clip_lyr.CreateFeature(out_feat)

    clean_lyr.SetSpatialFilter(None)
    clean_lyr.ResetReading()

inters_lyr.SetSpatialFilter(None)
inters_lyr.ResetReading()
#
# output_lyr = in_shp_name[:-4] + '_difference.shp'
# param_dict = {'INPUT': clean_shp_name,'OVERLAY':inters_shp_name,'OUTPUT':output_lyr}
# processing.run('native:difference', param_dict)


# clip_lyr = clean_lyr.Erase(inters_lyr, clip_lyr)

del shp_clip, clip_lyr
del shp_inters, inters_lyr

print(len(id_lst))
print(clean_lyr.GetFeatureCount())

del_lst = [sub_lst[:2] for sub_lst in dupl_lst]
for s, sub_lst in enumerate(del_lst):
    sub_lst.sort()
    del_lst[s] = '{0},{1}'.format(sub_lst[0],sub_lst[1])
del_lst = list(set(del_lst))
for s, string in enumerate(del_lst):
    del_lst[s] = string.split(',')
for sub_lst in covered_lst:
    del_lst.append(sub_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# sr = lyr.GetSpatialRef()
# driver_mem = ogr.GetDriverByName('Memory')
# ogr_ds = driver_mem.CreateDataSource('wrk')
# out_lyr = ogr_ds.CreateLayer('poly', srs=sr)
#
# feat_mem = ogr.Feature(out_lyr.GetLayerDefn())
# sr = lyr.GetSpatialRef()
# lyr_def = lyr.GetLayerDefn()
# for i in range(lyr_def.GetFieldCount()):
#     out_lyr.CreateField (lyr_def.GetFieldDefn(i))
#
# feat_mem.SetGeometryDirectly(ogr.Geometry(wkt = geom_wkt))
#
# lyr_def = in_lyr.GetLayerDefn ()
# for i in range(lyr_def.GetFieldCount()):
#     out_lyr.CreateField ( lyr_def.GetFieldDefn(i) )
#
# ##Writing the features
# for feat in selection:
#     out_lyr.CreateFeature(feat)
#
# ogr_lyr.CreateFeature(feat_mem)
#####
# memory_driver = ogr.GetDriverByName ('memory')
# memory_ds = memory_driver.CreateDataSource ('temp')
# result_layer = memory_ds.CreateLayer('result')

# feat = lyr.GetNextFeature()

# lyr.SetAttributeFilter("ID = '291'") # 98772-98772   ##291-64481
# feat = lyr.GetNextFeature()
# geom = feat.geometry()
# area = geom.Area()
# print(area)
# lyr.SetAttributeFilter(None) # 98772
#
# lyr2.SetAttributeFilter("ID = '64481'") # 98772-98772   ##291-64481
# feat2 = lyr2.GetNextFeature()
# geom2 = feat2.geometry()
# area2 = geom2.Area()
# print(area2)
# lyr2.SetAttributeFilter(None) # 98772
#
# intersection = geom2.Intersection(geom)
# area_inters = intersection.Area()
# print(area, area2, area_inters)

# drv_mem = ogr.GetDriverByName('Memory')
# shp_out = drv_mem.CreateDataSource('temp')
# out_lyr = shp_out.CreateLayer('polygons', geom_type=ogr.wkbMultiPolygon)
# for i in range(0, in_lyr_defn.GetFieldCount()):
#         field_def = in_lyr_defn.GetFieldDefn(i)
#         field_name = field_def.GetName()
#         out_lyr.CreateField(field_def)
# out_lyr_defn = out_lyr.GetLayerDefn()
# lyr.SetAttributeFilter("ID IN {0}".format(tuple(id_lst)))  # 98772-98772   ##291-64481
# for feat in lyr:
#     ouf_feat = ogr.Feature(out_lyr_defn)
#
#     for i in range(0, out_lyr_defn.GetFieldCount()):
#         field_def = out_lyr_defn.GetFieldDefn(i)
#         field_name = field_def.GetName()
#         ouf_feat.SetField(out_lyr_defn.GetFieldDefn(i).GetNameRef(),feat.GetField(i))
#
#     # Set geometry as centroid
#     geom = feat.GetGeometryRef()
#     ouf_feat.SetGeometry(geom.Clone())
#     # Add new feature to output Layer
#     out_lyr.CreateFeature(ouf_feat)
#     ouf_feat = None
# lyr.ResetReading()
# lyr.SetAttributeFilter(None)