import time
import os
from osgeo import ogr

# QGIS
from qgis.core import QgsApplication, QgsProcessingRegistry
from qgis.testing import start_app
from qgis.analysis import QgsNativeAlgorithms
import processing
app = start_app()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

def createFolder(directory):
    import os
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

def copyLayerToMemory(in_lyr):
    import ogr
    """
    Copies a Layer to the memory, returns the copy.
    :param in_lyr: Layer of a shapefile
    :return: Copy of the layer that is stored in memory
    """
    drv_mem = ogr.GetDriverByName('Memory')
    shp_copy = drv_mem.CreateDataSource('temp')
    copy_lyr = shp_copy.CopyLayer(in_lyr, 'lyr_copy')
    in_lyr.ResetReading()
    copy_lyr.ResetReading()
    return shp_copy, copy_lyr

def createEmptyShpWithCopiedLyr(in_lyr, out_pth, geom_type):
    import ogr
    """
    Creates a shapefile (at an user defined path)
    that has the same fields as the input shapefile
    and that has an user defined geometry type
    :param in_lyr: Input layer from which the layer definition is copied
    :param out_pth: Path were copy is stored.
    :param geom_type: Geometry type of the output shapefile, e.g. ogr.wkbPolygon or ogr.wkbMultiPolygon
    :return: Output shapefile, output Layer
    """
    drv_shp = ogr.GetDriverByName('ESRI Shapefile')
    in_sr = in_lyr.GetSpatialRef()
    in_lyr_defn = in_lyr.GetLayerDefn()
    if os.path.exists(out_pth):
        drv_shp.DeleteDataSource(out_pth)
    shp_out = drv_shp.CreateDataSource(out_pth)
    lyr_name = os.path.splitext(os.path.split(out_pth)[1])[0]
    lyr_out = shp_out.CreateLayer(lyr_name, in_sr, geom_type=geom_type)
    for i in range(0, in_lyr_defn.GetFieldCount()):
            field_def = in_lyr_defn.GetFieldDefn(i)
            lyr_out.CreateField(field_def)
    return shp_out, lyr_out

def removeDuplicateFeatures(in_shp_pth, temp_folder, return_duplicates=False):
    createFolder(temp_folder)
    file_name = os.path.basename(in_shp_pth)[:-4]

    in_shp = ogr.Open(in_shp_pth, 0)
    in_lyr = in_shp.GetLayer()

    copy_shp, copy_lyr = copyLayerToMemory(in_lyr)

    nodups_shp_name = temp_folder + r'\\' + file_name + '_no_duplicates.shp'
    nodups_shp, nodups_lyr = createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=nodups_shp_name,
                                                         geom_type=ogr.wkbPolygon)
    nodups_lyr_defn = nodups_lyr.GetLayerDefn()
    dupl_lst = []

    if return_duplicates == True:
        dups_shp_name = temp_folder + r'\\' + file_name + '_duplicates.shp'
        dups_shp, dups_lyr = createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=dups_shp_name,
                                                         geom_type=ogr.wkbPolygon)
        dups_lyr_defn = dups_lyr.GetLayerDefn()
        dupl_lst = []

    num_feat_total = in_lyr.GetFeatureCount()

    for f, feat_curr in enumerate(in_lyr):
        id1 = feat_curr.GetField('ID')
        geom_curr = feat_curr.GetGeometryRef()

        ## set a filter on the copied layer to identify all features that might overlap
        copy_lyr.SetSpatialFilter(geom_curr)
        num_feat_nb = copy_lyr.GetFeatureCount() -1
        progress = round((f / num_feat_total)*100, 2)
        # print("Progress:", progress, "% ID:", id1, "Neighbouring features:", num_feat_nb )
        dupl_check = 0
        for feat_nb in copy_lyr:
            id2 = feat_nb.GetField('ID')
            id_inters = '{0}_{1}'.format(min([id1, id2]), max([id1, id2]))
            geom_nb = feat_nb.geometry()

            ## if both geoms are equal and IDs differ then increase duplicate check by 1
            if geom_curr.Equals(geom_nb) and id1 != id2:
                dupl_lst.append(id_inters)
                dupl_check += 1

        ## if the current feature is not a duplicate or w
        ## if it is a duplicate but the second version of it was net yet recorded in the duplicate list
        ## then add the current feature to the no duplicates layer
        if dupl_check == 0 or dupl_lst.count(id_inters) == 1:
            ouf_feat = ogr.Feature(nodups_lyr_defn)
            for i in range(0, nodups_lyr_defn.GetFieldCount()):
                field_def = nodups_lyr_defn.GetFieldDefn(i)
                field_name = field_def.GetName()
                ouf_feat.SetField(field_name, feat_curr.GetField(i))
            geom_out = geom_curr.Clone()
            geom_out = geom_out.MakeValid()
            ouf_feat.SetGeometry(geom_out)
            nodups_lyr.CreateFeature(ouf_feat)
            ouf_feat = None
        else:
            if return_duplicates == True:
                ouf_feat = ogr.Feature(dups_lyr_defn)
                for i in range(0, dups_lyr_defn.GetFieldCount()):
                    field_def = dups_lyr_defn.GetFieldDefn(i)
                    field_name = field_def.GetName()
                    ouf_feat.SetField(field_name, feat_curr.GetField(i))
                geom_out = geom_curr.Clone()
                geom_out = geom_out.MakeValid()
                ouf_feat.SetGeometry(geom_out)
                dups_lyr.CreateFeature(ouf_feat)
                ouf_feat = None
            else:
                pass

        copy_lyr.SetSpatialFilter(None)
        copy_lyr.ResetReading()
    in_lyr.ResetReading()
    nodups_lyr.ResetReading()

    del copy_shp, copy_lyr
    del nodups_shp, nodups_lyr
    del in_shp, in_lyr
    if return_duplicates == True:
        del dups_lyr, dups_shp

def identifyIntersections(in_shp_pth, temp_folder):
    file_name = os.path.basename(in_shp_pth)[:-4]
    createFolder(temp_folder)

    in_shp = ogr.Open(in_shp_pth, 0)
    in_lyr = in_shp.GetLayer()

    copy_shp, copy_lyr = copyLayerToMemory(in_lyr)

    inters_shp_name = temp_folder + r'\\' + file_name + '_intersection.shp'
    drv_shp = ogr.GetDriverByName('ESRI Shapefile')
    in_sr = in_lyr.GetSpatialRef()
    if os.path.exists(inters_shp_name):
        drv_shp.DeleteDataSource(inters_shp_name)
    inters_shp = drv_shp.CreateDataSource(inters_shp_name)
    lyr_name = os.path.splitext(os.path.split(inters_shp_name)[1])[0]
    geom_type = ogr.wkbPolygon
    inters_lyr = inters_shp.CreateLayer(lyr_name, in_sr, geom_type=geom_type)
    inters_lyr.CreateField(ogr.FieldDefn('ID', ogr.OFTInteger64))
    inters_lyr.CreateField(ogr.FieldDefn('IDInters', ogr.OFTString))

    inters_lyr_defn = inters_lyr.GetLayerDefn()
    num_fields = inters_lyr_defn.GetFieldCount()

    id_inters_lst = []
    for feat_curr in in_lyr:
        id1 = feat_curr.GetField('ID')
        geom_curr = feat_curr.GetGeometryRef()
        copy_lyr.SetSpatialFilter(geom_curr)

        for feat_nb in copy_lyr:
            id2 = feat_nb.GetField('ID')
            id_inters = '{0}_{1}'.format(min([id1, id2]), max([id1, id2]))
            geom_nb = feat_nb.geometry()
            if id1 != id2:
                if geom_nb.Intersects(geom_curr):
                    intersection = geom_nb.Intersection(geom_curr)
                    geom_type = intersection.GetGeometryName()
                    if geom_type in ['MULTILINESTRING', 'POINT', 'LINESTRING','MULTIPOINT']: #alternatively mabye not in ['POLYGON', 'MULTIPOLYGON']
                        intersection = None
                        area_inters = 0
                        # print("Intersection of {} and {} is a {}".format(id1, id2, geom_type))
                    elif intersection != None:
                        area_inters = round(intersection.Area(), 1)
                        print("Intersection of {} and {} is NOT none. Its area is {} and its geom type is {}".format(id1, id2, area_inters, geom_type))
                    else:
                        intersection = None
                        area_inters = 0
                        # print("Intersection of {} and {} is none. Its area is {}".format(id1, id2, area_inters))
                else:
                    intersection = None
                    area_inters = 0
                    # print("{} and {} do not intersect.")

                ## if the id of the intersection is not already in the list and its area is bigger than 0
                ## then add this feature to the intersection layer
                if area_inters > 0.0 and id_inters not in id_inters_lst:
                    intersection = intersection.Buffer(0)
                    intersection = intersection.MakeValid()
                    wkt_inters = intersection.ExportToWkt()
                    poly = ogr.CreateGeometryFromWkt(wkt_inters)
                    out_feat = ogr.Feature(inters_lyr_defn)
                    out_feat.SetGeometry(poly)
                    out_feat.SetField('ID', id1)
                    out_feat.SetField(num_fields - 1, id_inters)
                    inters_lyr.CreateFeature(out_feat)
                    ouf_feat = None

                    id_inters_lst.append(id_inters)
            else:
                pass

        copy_lyr.SetSpatialFilter(None)
        copy_lyr.ResetReading()
    in_lyr.ResetReading()
    inters_lyr.ResetReading()

    del copy_shp, copy_lyr
    del inters_shp, inters_lyr
    del in_shp, in_lyr

def validitiyCheck(in_shp_pth):

    in_shp = ogr.Open(in_shp_pth)
    in_lyr = in_shp.GetLayer()

    for feat in in_lyr:
        geom = feat.GetGeometryRef()
        fid = feat.GetField("ID")
        if geom.IsValid():
            pass
        else:
            print(in_shp_pth, ':', fid)
    in_lyr.ResetReading()

    del in_shp, in_lyr

def makeGeomsValid(in_shp_pth):
    in_shp = ogr.Open(in_shp_pth, 1)
    in_lyr = in_shp.GetLayer()
    for feat in in_lyr:
        geom = feat.GetGeometryRef()
        fid = feat.GetField("ID")
        if not geom.IsValid():

            print(in_shp_pth, ':', fid)
            print("Geom_in is valid:", geom.IsValid())

            geom_out = geom.MakeValid()
            geom_out.Buffer(0)
            print(geom_out.GetGeometryName())
            print("Geom_out is valid:", geom_out.IsValid())
            # assert feature.GetGeometryRef().IsValid()

            feat.SetGeometry(geom_out.Buffer(0))
            # feat.SetGeometryDirectly(geom_out)

            in_lyr.SetFeature(feat)

        else:
            pass

    in_lyr.ResetReading()

    del in_shp, in_lyr

def removeLooseLines(in_shp_pth, dissolve):
    negbuff_pth = in_shp_pth[:-4] + '_negbuffer.shp'
    processing.run("native:buffer", {'INPUT': in_shp_pth,
                                     'DISTANCE': -.1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 2,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': negbuff_pth})

    posbuff_pth = in_shp_pth[:-4] + '_posbuffer.shp'
    processing.run("native:buffer", {'INPUT': negbuff_pth,
                                     'DISTANCE': .1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 1,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': posbuff_pth})

def removeNoneGeoms(in_shp_pth):
    file_name = os.path.basename(in_shp_pth)[:-4]

    in_shp = ogr.Open(in_shp_pth, 0)
    in_lyr = in_shp.GetLayer()

    nonones_shp_name = temp_folder + r'\\' + file_name + '_no_nones.shp'
    nonones_shp, nonones_lyr = createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=nonones_shp_name,
                                                         geom_type=ogr.wkbPolygon)
    nonones_lyr_defn = nonones_lyr.GetLayerDefn()

    num_feat_total = in_lyr.GetFeatureCount()

    for f, feat in enumerate(in_lyr):

        geom = feat.GetGeometryRef()

        if not geom == None:
            ouf_feat = ogr.Feature(nonones_lyr_defn)
            for i in range(0, nonones_lyr_defn.GetFieldCount()):
                field_def = nonones_lyr_defn.GetFieldDefn(i)
                field_name = field_def.GetName()
                ouf_feat.SetField(field_name, feat.GetField(i))
            ouf_feat.SetGeometry(geom)
            nonones_lyr.CreateFeature(ouf_feat)
            ouf_feat = None
            # print(geom)
        else:
            pass
    in_lyr.ResetReading()

    del in_shp, in_lyr
    del nonones_shp, nonones_lyr


wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

## INPUT
in_shp_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\complete_case\Antraege2008.shp"
# in_shp_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\sub_case2\Antraege2008_sub.shp"

## OUTPUT
# cleaned_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\sub_case2\Antraege2008_sub_cleaned.shp"
cleaned_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\complete_case\Antraege2008_cleaned.shp"
temp_folder = in_shp_pth[:-4] + '_temp'
file_name = os.path.basename(in_shp_pth)[:-4]

logfile_pth = in_shp_pth[:-4] + '_logfile.txt'
# logfile = open(logfile_pth, "w+")

# status_txt = "0. Remove duplicates from Invekos polygons"
# print(status_txt)
# tic = time.time()
# removeDuplicateFeatures(in_shp_pth, temp_folder, return_duplicates=True)
nodups_pth = temp_folder + r'\\' + file_name + '_no_duplicates.shp'
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# logfile = open(logfile_pth, "a+")
# status_txt = "\n1. Identify intersections of invekos polygons"
# print(status_txt)
# tic = time.time()
# identifyIntersections(nodups_pth, temp_folder)
inters_pth = nodups_pth[:-4] + '_intersection.shp'
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# print('MAKE GEOMS VALID')
# makeGeomsValid(inters_pth)
#
# # valid_pth = inters_pth[:-4] + 'valid.shp'
#
# print('CHECK FOR VALIDITY')
# validitiyCheck(inters_pth)

# logfile = open(logfile_pth, "a+")
# status_txt = "\n2. Identify intersections of intersections"
# print(status_txt)
# tic = time.time()
# identifyIntersections(inters_pth, temp_folder)
inters_inters_pth = inters_pth[:-4] + '_intersection.shp'
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# print('MAKE GEOMS VALID')
# makeGeomsValid(inters_inters_pth)
#
# print('CHECK FOR VALIDITY')
# validitiyCheck(inters_inters_pth)

# logfile = open(logfile_pth, "a+")
# status_txt ="\n3. Calc difference between intersections and intersections 2 "
# print(status_txt)
# tic = time.time()
inters_wo_pth = temp_folder + r'\03_intersection_without_overlap.shp'
# param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}
# processing.run('native:difference', param_dict)
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# logfile = open(logfile_pth, "a+")
# status_txt = "\n4. Merge intersections"
# print(status_txt)
# tic = time.time()
inters_merged_pth = temp_folder + r'\04_merged_intersections.shp'
# param_dict = {'LAYERS':[inters_inters_pth, inters_wo_pth], 'CRS':inters_inters_pth, 'OUTPUT': inters_merged_pth}
# processing.run('qgis:mergevectorlayers', param_dict)
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# logfile = open(logfile_pth, "a+")
# status_txt = "\n5. Remove loose lines of merged intersections"
# print(status_txt)
# tic = time.time()
# removeLooseLines(inters_merged_pth, False)
inters_posbuff_pth = inters_merged_pth[:-4] + '_posbuffer.shp'
# toc = time.time()
# logfile.write(status_txt + ": " + str(toc-tic) + " sec")
# logfile.close()

# print('CHECK FOR VALIDITY',nodups_pth)
# validitiyCheck(nodups_pth)
# removeNoneGeoms(inters_posbuff_pth)
inters_no_nones = inters_posbuff_pth[:-4] + '_no_nones.shp'

print('CHECK FOR VALIDITY', inters_posbuff_pth)
validitiyCheck(inters_no_nones)

logfile = open(logfile_pth, "a+")
status_txt = "\n6. Calc difference between invekos polygons and final intersections"
print(status_txt)
tic = time.time()
poly_diff_pth = temp_folder + r'\05_difference_of_polygons.shp'
param_dict = {'INPUT': nodups_pth,'OVERLAY': inters_no_nones,'OUTPUT':poly_diff_pth}
processing.run('native:difference', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

logfile = open(logfile_pth, "a+")
status_txt = "\n7. Remove loose lines of subtracted invekos polygons"
print(status_txt)
tic = time.time()
removeLooseLines(poly_diff_pth, False)
polydiff_posbuff_pth = poly_diff_pth[:-4] + '_posbuffer.shp'
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

removeNoneGeoms(polydiff_posbuff_pth)
polydiff_no_nones = polydiff_posbuff_pth[:-4] + '_no_nones.shp'

logfile = open(logfile_pth, "a+")
status_txt = "\n8. Merge subtracted polygons with final intersections"
print(status_txt)
tic = time.time()
sliced_polys_pth = temp_folder + r'\06_sliced_polygons.shp'
param_dict = {'LAYERS':[polydiff_posbuff_pth, inters_posbuff_pth], 'CRS':polydiff_no_nones, 'OUTPUT': sliced_polys_pth}
processing.run('qgis:mergevectorlayers', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

logfile = open(logfile_pth, "a+")
status_txt = "\n9. Dissolve polygons and intersections based on ID"
print(status_txt)
tic = time.time()
# dissolved_polys_pth = temp_folder + r'\09_dissolved_polygons.shp'
param_dict = {'INPUT': sliced_polys_pth, 'FIELD':'ID', 'OUTPUT': cleaned_pth}
processing.run('native:dissolve', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()