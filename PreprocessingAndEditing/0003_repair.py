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
    # in_lyr = in_shp.GetLayer()
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

def identifyIntersections(in_shp_pth, temp_folder):
    file_name = os.path.basename(in_shp_pth)[:-4]
    createFolder(temp_folder)

    in_shp = ogr.Open(in_shp_pth, 0)
    in_lyr = in_shp.GetLayer()
    # in_sr = in_lyr.GetSpatialRef()

    copy_shp, copy_lyr = copyLayerToMemory(in_lyr)

    nodups_shp_name = temp_folder + r'\\' + file_name + '_no_duplicates.shp'
    nodups_shp, nodups_lyr = createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=nodups_shp_name,
                                                         geom_type=ogr.wkbPolygon)
    nodups_lyr_defn = nodups_lyr.GetLayerDefn()

    inters_shp_name = temp_folder + r'\\' + file_name + '_intersection.shp'
    inters_shp, inters_lyr = createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=inters_shp_name,
                                                         geom_type=ogr.wkbPolygon)
    inters_lyr.CreateField(ogr.FieldDefn('IDInters', ogr.OFTString))
    inters_lyr_defn = inters_lyr.GetLayerDefn()
    num_fields = inters_lyr_defn.GetFieldCount()

    dupl_lst = []
    covered_lst = []
    id_inters_lst = []
    for feat_curr in in_lyr:
        id1 = feat_curr.GetField('ID')
        geom_curr = feat_curr.GetGeometryRef()

        ## set a filter on the copied layer to
        ## identify all features that might overlap
        copy_lyr.SetSpatialFilter(geom_curr)

        num_feat = copy_lyr.GetFeatureCount()
        checker = 0
        for feat_nb in copy_lyr:  # feat_nb = neighbouring feature
            id2 = feat_nb.GetField('ID')
            id_inters = '{0}_{1}'.format(min([id1, id2]), max([id1, id2]))
            print(id_inters)
            geom_nb = feat_nb.geometry()


            if geom_nb.Intersects(geom_curr) and geom_nb != None:
                intersection = geom_nb.Intersection(geom_curr)
                geom_type = intersection.GetGeometryName()
                if geom_type == 'MULTILINESTRING' or geom_type == 'POINT' or geom_type == 'LINESTRING':
                    intersection = None
            else:
                intersection = None

            if intersection == None or intersection.IsEmpty():
                area_inters = 0
                # print(id_inters, "is non-surface geometry type")
            else:
                area_inters = intersection.Area()

            ## test for duplicates:
            if geom_curr.Equals(geom_nb) and id1 != id2:
                dupl_lst.append(id_inters)
                checker += 1
                # print(id1, 'and', id2, 'are duplicates!')

            elif geom_nb.Within(geom_curr) and id1 != id2:
                dupl_lst.append(id_inters)
                covered_lst.append(id_inters)
                checker += 1
                # print('OGR Test:', id2, 'is within', id1)
                # print(id2, area_nb, id1,  area_curr)

            ## if the current feat of the copied layer is not a duplicate
            ## and the neighbouring geom is not within the current geom
            ## and the id of the intersection is not already in the list
            ## then add this feature to the intersection layer
            elif area_inters > 0 and id_inters not in id_inters_lst and id1 != id2:
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

                # print(id1, 'and', id2, 'intersect and are NOT (almost) duplicates!')
                id_inters_lst.append(id_inters)

        ## if the current feature is not a duplicate or
        ## if it is a duplicate but the second version of it was net yet recorded in the duplicate list
        ## then add the current feature to the no duplicates layer
        if checker == 0 or dupl_lst.count(id_inters) == 1:
            ouf_feat = ogr.Feature(nodups_lyr_defn)
            for i in range(0, nodups_lyr_defn.GetFieldCount()):
                field_def = nodups_lyr_defn.GetFieldDefn(i)
                field_name = field_def.GetName()
                ouf_feat.SetField(nodups_lyr_defn.GetFieldDefn(i).GetNameRef(), feat_curr.GetField(i))
            geom_out = geom_curr.Clone()
            geom_out = geom_out.MakeValid()
            ouf_feat.SetGeometry(geom_out)
            nodups_lyr.CreateFeature(ouf_feat)
            ouf_feat = None

        copy_lyr.SetSpatialFilter(None)
        copy_lyr.ResetReading()
    in_lyr.ResetReading()
    nodups_lyr.ResetReading()
    inters_lyr.ResetReading()

    del copy_shp, copy_lyr
    del in_shp, in_lyr
    del nodups_shp, nodups_lyr
    del inters_shp, inters_lyr

wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

## INPUT
in_shp_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\sub_case\Antraege2008_sub.shp"

## OUTPUT
cleaned_pth = r"Q:\FORLand\Clemens\data\vector\repairInvekos\sub_case\Antraege2008_sub_cleaned.shp"

## PROCESSING

temp_folder = in_shp_pth[:-4] + '_temp'
identifyIntersections(in_shp_pth, temp_folder)

file_name = os.path.basename(in_shp_pth)[:-4]
nudups_pth = temp_folder + r'\\' + file_name + '_no_duplicates.shp'
inters_pth = temp_folder + r'\\' + file_name + '_intersection.shp'

identifyIntersections(inters_pth, temp_folder)
inters_inters_pth = inters_pth[:-4] + '_intersection.shp'

# createFolder(temp_folder)

inters_wo_pth = temp_folder + r'\03_intersection_without_overlap.shp'
param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}
processing.run('native:difference', param_dict)

inters_merged_pth = temp_folder + r'\04_merged_intersections.shp'
param_dict = {'LAYERS':[inters_inters_pth, inters_wo_pth], 'CRS':inters_inters_pth, 'OUTPUT': inters_merged_pth}
processing.run('qgis:mergevectorlayers', param_dict)

removeLooseLines(inters_merged_pth, False)
inters_posbuff_pth = inters_merged_pth[:-4] + '_posbuffer.shp'

poly_diff_pth = temp_folder + r'\05_difference_of_polygons.shp'
param_dict = {'INPUT': nudups_pth,'OVERLAY': inters_posbuff_pth,'OUTPUT':poly_diff_pth}
processing.run('native:difference', param_dict)

removeLooseLines(poly_diff_pth, False)
polydiff_posbuff_pth = poly_diff_pth[:-4] + '_posbuffer.shp'

sliced_polys_pth = temp_folder + r'\06_sliced_polygons.shp'
param_dict = {'LAYERS':[polydiff_posbuff_pth, inters_posbuff_pth], 'CRS':polydiff_posbuff_pth, 'OUTPUT': sliced_polys_pth}
processing.run('qgis:mergevectorlayers', param_dict)

# dissolved_polys_pth = temp_folder + r'\09_dissolved_polygons.shp'
param_dict = {'INPUT': sliced_polys_pth, 'FIELD':'ID', 'OUTPUT': cleaned_pth}
processing.run('native:dissolve', param_dict)