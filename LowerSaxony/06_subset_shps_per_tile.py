# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import glob
from osgeo import ogr, osr
import joblib

## CJ REPO
import vector
import forland_wrapper
import general

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

####################################################################
## ADD ID column

# for pth in lst:
def workFunc(year):
    pth = r'data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
    print("\n", year)

    inv_shp = ogr.Open(pth, 1)
    inv_lyr = inv_shp.GetLayer()

    field_def = ogr.FieldDefn('ID', ogr.OFTInteger64)
    inv_lyr.CreateField(field_def)

    for f, feat in enumerate(inv_lyr):
        feat.SetField("ID", f)
        inv_lyr.SetFeature(feat)
    inv_lyr.ResetReading()

    print(year, "done")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=12)(joblib.delayed(workFunc)(year) for year in range(2019,2020))

####################################################################
## write tile names to txt file

# for i in range(1,4):
#     pth = r"data\vector\grid\LS\Invekos_grid_LS_15km_sub{}.shp".format(i)
#     shp = ogr.Open(pth)
#     lyr = shp.GetLayer()
#
#     file = open(r"data\vector\tile_list_LS_sub{}.txt".format(i), 'w+')
#
#     for feat in lyr:
#         fid = feat.GetField("POLYID")
#         file.write(fid + "\n")
#     lyr.ResetReading()
#     file.close()

# ####################################################################
## Explore data structure

for year in range(2019, 2020):
    pth = r'data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
    print("\n", year)

    inv_shp = ogr.Open(pth)
    inv_lyr = inv_shp.GetLayer()
    vector.printFieldNames(inv_lyr)
    fnames = vector.getFieldNames(inv_shp)
    print(fnames)
    for i in range(10):
        feat = inv_lyr.GetFeature(i)
        attrs = [feat.GetField(fname) for fname in fnames]
        print(attrs)

####################################################################
# remove none geoms

for year in range(2019, 2020):
    print('######################\n{0}\n######################'.format(year))
    in_pth = r'data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
    out_pth = r'data\vector\IACS\LS\IACS_LS_{0}_no_nones.shp'.format(year)
    forland_wrapper.removingNoneGeoms(in_pth, out_pth)
    print(year, "done!")
## ALL Shapes don't have none geometries
## NAMING stays the same
####################################################################
## make geoms valid
# lst = list(range(2006,2011)) + list(range(2012,2020))
# lst = [2005, 2018, 2019]
lst = list(range(2011,2020))
import forland_wrapper
for year in lst:
    print('######################\n{0}\n######################'.format(year))
    in_pth = r'data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
    forland_wrapper.validityChecking(in_shp_pth = in_pth, id_field_name="ID")
    print(year, "done!\n")

####################################################################
## subset invekos on TILE basis in parallel for one year
for i in range(1,4):
    with open(r"data\vector\tile_list_LS_sub{}.txt".format(i)) as file:
        tiles_lst = file.readlines()
    tiles_lst = [item.strip() for item in tiles_lst]

    for tile in tiles_lst:
        def workFunc(year):
            # year = 2017
            pth = r'data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
            grid_pth = r'data\vector\grid\Invekos_grid_LS_15km.shp'
            grid_shp = ogr.Open(grid_pth)
            grid_lyr = grid_shp.GetLayer()

            grid_lyr.SetAttributeFilter("POLYID = '" + tile + "'")
            feat_grid = grid_lyr.GetNextFeature()

            # year = general.findBetween(pth, 'Nutzung', '.shp')
            print(year, tile)
            # print("\n", pth)
            inv_shp = ogr.Open(pth)
            inv_lyr = inv_shp.GetLayer()
            # print(year, "Number of features:", inv_lyr.GetFeatureCount())
            # print("Extent:", inv_lyr.GetExtent())
            inv_sr = inv_lyr.GetSpatialRef()
            # transform = osr.CoordinateTransformation(grid_sr, inv_sr)

            geom = feat_grid.geometry().Clone()
            # print(year, "Geometry before transformation:\n", geom)
            # geom.Transform(transform)
            # print("Geometry after transformation:\n", geom)
            inv_lyr.SetSpatialFilter(geom)

            out_pth = r"data\vector\IACS\LS\tiles\{}".format(tile)
            general.createFolder(out_pth)
            out_shp_pth = r"data\vector\IACS\LS\tiles\{1}\IACS_{0}_{1}.shp".format(year, tile)

            drv_shp = ogr.GetDriverByName('ESRI Shapefile')

            inv_lyr_defn = inv_lyr.GetLayerDefn()
            if os.path.exists(out_shp_pth):
                drv_shp.DeleteDataSource(out_shp_pth)
            out_shp = drv_shp.CreateDataSource(out_shp_pth)
            lyr_name = os.path.splitext(os.path.split(out_shp_pth)[1])[0]
            geom_type = ogr.wkbPolygon
            out_lyr = out_shp.CreateLayer(lyr_name, inv_sr, geom_type=geom_type)
            for i in range(0, inv_lyr_defn.GetFieldCount()):
                field_def = inv_lyr_defn.GetFieldDefn(i)
                out_lyr.CreateField(field_def)

            for feat in inv_lyr:
                out_feat = feat
                out_lyr.CreateFeature(out_feat)
                ouf_feat = None
            inv_lyr.ResetReading()

            del inv_shp, inv_lyr
            del out_shp, out_lyr

            print(year, tile, "done")

        # if __name__ == '__main__':
        #     joblib.Parallel(n_jobs=22)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

        if __name__ == '__main__':
            joblib.Parallel(n_jobs=1)(joblib.delayed(workFunc)(year) for year in range(2011,2020))

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


