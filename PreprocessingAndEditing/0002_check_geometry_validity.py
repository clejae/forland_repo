import os
import time
from osgeo import ogr

def createEmptyShpWithCopiedLyr(in_shp, out_pth, geom_type):
    import ogr
    """
    Creates a shapefile (at an user defined path)
    that has the same fields as the input shapefile
    and that has an user defined geometry type
    :param in_shp: Input shapefile from which the layer definition is copied
    :param out_pth: Path were copy is stored.
    :param geom_type: Geometry type of the output shapefile, e.g. ogr.wkbPolygon or ogr.wkbMultiPolygon
    :return: Output shapefile, output Layer
    """
    drv_shp = ogr.GetDriverByName('ESRI Shapefile')
    in_lyr = in_shp.GetLayer()
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

wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

in_shp_name = r'data\vector\repairInvekos\Test_noDuplicates.shp'
in_shp = ogr.Open(in_shp_name, 0)
in_lyr = in_shp.GetLayer()
# in_sr = in_lyr.GetSpatialReference()
in_lyr_defn = in_lyr.GetLayerDefn()

inter_shp_name = r'data\vector\repairInvekos\Test_intersection.shp'
inter_shp = ogr.Open(inter_shp_name, 0)
inter_lyr = inter_shp.GetLayer()
inter_lyr_defn = inter_lyr.GetLayerDefn()

subtract_shp_name =  in_shp_name[:-4] + '_subtract.shp'
subtract_shp, subtract_lyr = createEmptyShpWithCopiedLyr(in_shp=in_shp, out_pth=subtract_shp_name, geom_type= ogr.wkbPolygon)
subtract_lyr_defn = subtract_lyr.GetLayerDefn()

# inters_lyr.SetAttributeFilter("IDInters = '36362_36363'")

for feat_inter in inter_lyr:
    id_inters = feat_inter.GetField('IDInters')
    difference = feat_inter.GetGeometryRef()
    id_lst = id_inters.split('_')
    # id1 = id_inters.split('_')[0]
    # id2 = id_inters.split('_')[1]
    # print(id1, id2)
    print(id_lst)

    in_lyr.SetAttributeFilter("ID IN {}".format(tuple(id_lst)))

    for feat_curr in in_lyr:
        id_curr = feat_curr.GetField('ID')
        geom_curr = feat_curr.GetGeometryRef()

        difference = geom_curr.Difference(geom_inters)
        if difference != None:
            area = difference.Area()
            # print(id_curr, area)

            ouf_feat = ogr.Feature(subtract_lyr_defn)
            for i in range(0, subtract_lyr_defn.GetFieldCount()):
                field_def = subtract_lyr_defn.GetFieldDefn(i)
                field_name = field_def.GetName()
                ouf_feat.SetField(subtract_lyr_defn.GetFieldDefn(i).GetNameRef(), feat_curr.GetField(i))
            ouf_feat.SetGeometry(difference)
            subtract_lyr.CreateFeature(ouf_feat)
            ouf_feat = None

    in_lyr.SetAttributeFilter(None)
    in_lyr.ResetReading()
inter_lyr.ResetReading()

del in_lyr, in_shp
del inter_shp, inter_lyr
del subtract_shp, subtract_lyr