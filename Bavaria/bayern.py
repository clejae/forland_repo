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

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

####################################################################
## ADD ID column
# sd = r'Daten\vector\InVekos\Bayern\AKTUELL_20200604\\'
# lst = glob.glob(wd + sd + '*.shp')
#
# # for pth in lst:
# def workFunc(pth):
#     year = general.findBetween(pth, 'Nutzung', '.shp')
#     print("\n", year)
#
#     inv_shp = ogr.Open(pth, 1)
#     inv_lyr = inv_shp.GetLayer()
#
#     field_def = ogr.FieldDefn('ID', ogr.OFTInteger64)
#     inv_lyr.CreateField(field_def)
#
#     for f, feat in enumerate(inv_lyr):
#         feat.SetField("ID", f)
#         inv_lyr.SetFeature(feat)
#     inv_lyr.ResetReading()
#
#     print(year, "done")
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=12)(joblib.delayed(workFunc)(pth) for pth in lst)
#
####################################################################
## Extract NU Code
# import ogr
# wd = r'Q:\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\\'
# year = 2017
# # for year in range(2017, 2020):
# def workFunc(year):
#     print("\n############\n{}\n###########".format(year))
#     pth = wd + 'Nutzung{0}.shp'.format(year)
#     shp = ogr.Open(pth)
#     lyr = shp.GetLayer()
#     # vector.printFieldNames(lyr)
#     lst = []
#     for feat in lyr:
#         fid = feat.GetField("nutz_code") #"nutz_c1"
#         if fid not in lst:
#             lst.append(fid)
#     pth = r"Q:\FORLand\Clemens\data\tables\InVekos\BY\NUCodes_{0}.txt".format(year)
#     file = open(pth, "w+")
#     for i in lst:
#         file.write(str(i) + ', ')
#     file.close()
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=3)(joblib.delayed(workFunc)(year) for year in range(2017, 2020))
####################################################################
## Reproject data (VERY SLOW, do it in QGIS!!)

# sd = r'Daten\vector\InVekos\Bayern\AKTUELL_20200604\\'
# lst = glob.glob(wd + sd + '*shp')
# for pth in lst[:1]:
#     shp = ogr.Open(pth)
#     out_shp_pth = pth[:-3] + 'repr.shp'
#     vector.reprojectShape(shp, out_shp_pth, 25832, geom_type=ogr.wkbPolygon)
#
# ####################################################################
# ## Explore data structure
# sd = r'Daten\vector\InVekos\Niedersachsen\NS_InvekosHarmonised\\'
# # sd = r'Daten\vector\InVekos\Bayern\AKTUELL_20200604\\'
# lst = glob.glob(wd + sd + '*.shp')
#
# for pth in lst:
#     year = general.findBetween(pth, 'Harm_', '.shp')
#     # year = general.findBetween(pth, 'Nutzung', '.shp')
#     print("\n", year)
#
#     inv_shp = ogr.Open(pth)
#     inv_lyr = inv_shp.GetLayer()
#     vector.printFieldNames(inv_lyr)
#     fnames = vector.getFieldNames(inv_shp)
#     print(fnames)
#     for i in range(10):
#         feat = inv_lyr.GetFeature(i)
#         attrs = [feat.GetField(fname) for fname in fnames]
#         print(attrs)
#
# ####################################################################
# ## get a subset of the data
# sd = r'Daten\vector\InVekos\Bayern\AKTUELL_20200604\\'
# lst = glob.glob(wd + sd + '*.shp')
# # for pth in lst:
# def workFunc(pth):
#     grid_pth = r"Clemens\data\vector\grid\Invekos_grid_BY_15km.shp"
#     grid_shp = ogr.Open(grid_pth)
#     grid_lyr = grid_shp.GetLayer()
#
#     grid_sr = grid_lyr.GetSpatialRef()
#
#     tile = '0024_0021' #0027_0013, '0028_0020'
#
#     grid_lyr.SetAttributeFilter("POLYID = '" + tile + "'")
#
#     feat_grid = grid_lyr.GetNextFeature()
#
#     year = general.findBetween(pth, 'Nutzung', '.shp')
#     print(year)
#     print("\n", pth)
#     inv_shp = ogr.Open(pth)
#     inv_lyr = inv_shp.GetLayer()
#     print(year, "Number of features:", inv_lyr.GetFeatureCount())
#     print("Extent:", inv_lyr.GetExtent())
#     inv_sr = inv_lyr.GetSpatialRef()
#     # transform = osr.CoordinateTransformation(grid_sr, inv_sr)
#
#     geom = feat_grid.geometry().Clone()
#     print(year, "Geometry before transformation:\n", geom)
#     # geom.Transform(transform)
#     # print("Geometry after transformation:\n", geom)
#     inv_lyr.SetSpatialFilter(geom)
#
#     print(year, "Number of filtered features:", inv_lyr.GetFeatureCount())
#
#     out_shp_pth = r"Clemens\data\vector\InvClassified\BY\InVekos_BY_{}_{}.shp".format(year, tile)
#
#     drv_shp = ogr.GetDriverByName('ESRI Shapefile')
#
#     inv_lyr_defn = inv_lyr.GetLayerDefn()
#     if os.path.exists(out_shp_pth):
#         drv_shp.DeleteDataSource(out_shp_pth)
#     out_shp = drv_shp.CreateDataSource(out_shp_pth)
#     lyr_name = os.path.splitext(os.path.split(out_shp_pth)[1])[0]
#     geom_type = ogr.wkbPolygon
#     out_lyr = out_shp.CreateLayer(lyr_name, inv_sr, geom_type=geom_type)
#     for i in range(0, inv_lyr_defn.GetFieldCount()):
#         field_def = inv_lyr_defn.GetFieldDefn(i)
#         out_lyr.CreateField(field_def)
#
#     for feat in inv_lyr:
#         out_feat = feat
#         out_lyr.CreateFeature(out_feat)
#         ouf_feat = None
#     inv_lyr.ResetReading()
#
#     del inv_shp, inv_lyr
#     del out_shp, out_lyr
#
#     print(year, "done")
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=12)(joblib.delayed(workFunc)(pth) for pth in lst[:1])
#
# ####################################################################
# ## write tile names to txt file
#
# pth = r"Q:\FORLand\Clemens\data\vector\grid\Invekos_grid_BY-motorways_15km.shp"
# pth = r"Q:\FORLand\Clemens\data\vector\t.shp"
# shp = ogr.Open(pth)
# lyr = shp.GetLayer()
#
# file = open(r"Q:\FORLand\Clemens\data\vector\tile_list_BB_errors.txt", 'w+')
#
# for feat in lyr:
#     fid = feat.GetField("POLYID")
#     file.write(fid + "\n")
# lyr.ResetReading()
# file.close()
#
# with open(r"Q:\FORLand\Clemens\data\vector\tile_list_BB_rivers.txt") as file:
#     tiles_lst1 = file.readlines()
# tiles_lst1 = [item.strip() for item in tiles_lst1]
#
# with open(r"Q:\FORLand\Clemens\data\vector\tile_list_BB_rivers2.txt") as file:
#     tiles_lst2 = file.readlines()
# tiles_lst2 = [item.strip() for item in tiles_lst2]
#
# with open(r"Q:\FORLand\Clemens\data\vector\tile_list_BB_motorways.txt") as file:
#     tiles_lst3 = file.readlines()
# tiles_lst3 = [item.strip() for item in tiles_lst3]
#
# check_lst = tiles_lst1 + tiles_lst2
#
# tiles_lst = []
# for tile in tiles_lst3:
#     if tile not in check_lst:
#         tiles_lst.append(tile)
#
# t = []
# for tile in tiles_lst3:
#     if tile in check_lst:
#         t.append(tile)

####################################################################
## remove none geoms
#
# for year in range(2011, 2012):
#     print('######################\n{0}\n######################'.format(year))
#     in_pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}_buff.shp'.format(year)
#     out_pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}_no_nones.shp'.format(year)
#     forland_wrapper.removingNoneGeoms(in_pth, out_pth)
#     print(year, "done!")
#
# ####################################################################
# ## make geoms valid
# # lst = list(range(2006,2011)) + list(range(2012,2020))
# # lst = [2005, 2018, 2019]
# lst = [2011]
# import forland_wrapper
# for year in lst:
#     print('######################\n{0}\n######################'.format(year))
#     in_pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}_no_nones.shp'.format(year)
#     forland_wrapper.validityChecking(in_shp_pth = in_pth, id_field_name="ID")
#     print(year, "done!\n")

####################################################################
## remove loose lines
# lst = [2011]
# import forland_wrapper
# for year in lst:
#     print('######################\n{0}\n######################'.format(year))
#     in_pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}.shp'.format(year)
#     out_pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}_buff.shp'.format(
#         year)
#     forland_wrapper.removeLooseLines(in_shp_pth = in_pth, out_shp_pth=out_pth)
#     print(year, "done!\n")

####################################################################
## subset invekos on TILE basis in parallel for one year
#
# with open(r"Clemens\data\vector\InvClassified\BY\tile_list_BB_errors.txt") as file:
# with open(r"Clemens\data\vector\InvClassified\BY\tile_list_BY_rivers-motorways.txt") as file:
#     tiles_lst = file.readlines()
# tiles_lst = [item.strip() for item in tiles_lst]
# tiles_lst = ['0018_0022']
# lst = list(range(2006,2011)) + list(range(2012,2020))
# for year in range(2005,2020):
#     def workFunc(tile):
# for tile in tiles_lst:
#     def workFunc(year):
#         # year = 2017
#         pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}.shp'.format(year)
#         grid_pth = r"Clemens\data\vector\grid\Invekos_grid_BY_15km.shp"
#         grid_shp = ogr.Open(grid_pth)
#         grid_lyr = grid_shp.GetLayer()
#
#         grid_lyr.SetAttributeFilter("POLYID = '" + tile + "'")
#         feat_grid = grid_lyr.GetNextFeature()
#
#         # year = general.findBetween(pth, 'Nutzung', '.shp')
#         print(year, tile)
#         # print("\n", pth)
#         inv_shp = ogr.Open(pth)
#         inv_lyr = inv_shp.GetLayer()
#         # print(year, "Number of features:", inv_lyr.GetFeatureCount())
#         # print("Extent:", inv_lyr.GetExtent())
#         inv_sr = inv_lyr.GetSpatialRef()
#         # transform = osr.CoordinateTransformation(grid_sr, inv_sr)
#
#         geom = feat_grid.geometry().Clone()
#         # print(year, "Geometry before transformation:\n", geom)
#         # geom.Transform(transform)
#         # print("Geometry after transformation:\n", geom)
#         inv_lyr.SetSpatialFilter(geom)
#
#         out_pth = r"Clemens\data\vector\InvClassified\BY\tiles\{}".format(tile)
#         general.createFolder(out_pth)
#         out_shp_pth = r"Clemens\data\vector\InvClassified\BY\tiles\{1}\InVekos_BY_{0}_{1}.shp".format(year, tile)
#
#         drv_shp = ogr.GetDriverByName('ESRI Shapefile')
#
#         inv_lyr_defn = inv_lyr.GetLayerDefn()
#         if os.path.exists(out_shp_pth):
#             drv_shp.DeleteDataSource(out_shp_pth)
#         out_shp = drv_shp.CreateDataSource(out_shp_pth)
#         lyr_name = os.path.splitext(os.path.split(out_shp_pth)[1])[0]
#         geom_type = ogr.wkbPolygon
#         out_lyr = out_shp.CreateLayer(lyr_name, inv_sr, geom_type=geom_type)
#         for i in range(0, inv_lyr_defn.GetFieldCount()):
#             field_def = inv_lyr_defn.GetFieldDefn(i)
#             out_lyr.CreateField(field_def)
#
#         for feat in inv_lyr:
#             out_feat = feat
#             out_lyr.CreateFeature(out_feat)
#             ouf_feat = None
#         inv_lyr.ResetReading()
#
#         del inv_shp, inv_lyr
#         del out_shp, out_lyr
#
#         print(year, tile, "done")
#
#     # if __name__ == '__main__':
#     #     joblib.Parallel(n_jobs=22)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)
#
#     if __name__ == '__main__':
#         joblib.Parallel(n_jobs=22)(joblib.delayed(workFunc)(year) for year in range(2005,2020))

####################################################################
## subset invekos on SLICE basis in parallel for one year
#
# index_lst = range(1, 24)
#
# for year in range(2005,2007):
#     print('######################\n{0}\n######################'.format(year))
#     folder_pth = r"Clemens\data\vector\InvClassified\BY\slices\{0}".format(year)
#     general.createFolder(folder_pth)
#     def workFunc(index):
#         pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}.shp'.format(year)
#         grid_pth = r"Clemens\data\vector\OSM\BY_sliced.shp"
#         grid_shp = ogr.Open(grid_pth)
#         grid_lyr = grid_shp.GetLayer()
#
#         grid_lyr.SetAttributeFilter("ID = '" + str(index) + "'")
#         feat_grid = grid_lyr.GetNextFeature()
#
#         print(year, index)
#         inv_shp = ogr.Open(pth)
#         inv_lyr = inv_shp.GetLayer()
#         inv_sr = inv_lyr.GetSpatialRef()
#
#         geom = feat_grid.geometry().Clone()
#         inv_lyr.SetSpatialFilter(geom)
#
#         out_shp_pth = r"Clemens\data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}.shp".format(year, index)
#         drv_shp = ogr.GetDriverByName('ESRI Shapefile')
#
#         inv_lyr_defn = inv_lyr.GetLayerDefn()
#         if os.path.exists(out_shp_pth):
#             drv_shp.DeleteDataSource(out_shp_pth)
#         out_shp = drv_shp.CreateDataSource(out_shp_pth)
#         lyr_name = os.path.splitext(os.path.split(out_shp_pth)[1])[0]
#         geom_type = ogr.wkbPolygon
#         out_lyr = out_shp.CreateLayer(lyr_name, inv_sr, geom_type=geom_type)
#         for i in range(0, inv_lyr_defn.GetFieldCount()):
#             field_def = inv_lyr_defn.GetFieldDefn(i)
#             out_lyr.CreateField(field_def)
#
#         for feat in inv_lyr:
#             out_feat = feat
#             out_lyr.CreateFeature(out_feat)
#             ouf_feat = None
#         inv_lyr.ResetReading()
#
#         del inv_shp, inv_lyr
#         del out_shp, out_lyr
#
#         print(year, index, "done")
#
#     if __name__ == '__main__':
#         joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(index) for index in index_lst)

###################################################################
## check if features were missed or got duplicated during slicing

for year in range(2005,2020):
    print(year)

    pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}.shp'.format(year)

    inv_shp = ogr.Open(pth)
    inv_lyr = inv_shp.GetLayer()
    print( "Number of features in original shape:", inv_lyr.GetFeatureCount())

    s = 0
    for i in range(1,24):
        sub_pth = r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}.shp".format(year, i)
        shp = ogr.Open(sub_pth)
        lyr = shp.GetLayer()
        s2 = lyr.GetFeatureCount()
        # print(i, s2)
        s = s + s2
        del shp, lyr
    print("Number of features in sliced shape:", s)

###################################################################
## get missing features that were missed during the slicing
# for year in [2005, 2006]: #range(2005, 2020):
# def workFunc(year):
#     print(year)
#
#     pth = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Bayern\AKTUELL_20200604\Nutzung{}.shp'.format(year)
#
#     inv_shp = ogr.Open(pth)
#     inv_lyr = inv_shp.GetLayer()
#
#     id_lst = []
#     for feat in inv_lyr:
#         fid = feat.GetField("ID")
#         id_lst.append(fid)
#     inv_lyr.ResetReading()
#
#     id_lst2 = []
#     for i in range(1,24):
#         # print(i)
#         sub_pth = r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}.shp".format(year, i)
#         shp = ogr.Open(sub_pth)
#         lyr = shp.GetLayer()
#         for feat in lyr:
#             fid = feat.GetField("ID")
#             id_lst2.append(fid)
#             # if fid not in id_lst:
#             #     m_lst.append(fid)
#         lyr.ResetReading()
#         del shp, lyr
#
#     s = set(id_lst2)
#     miss_lst = [fid for fid in id_lst if fid not in s]
#     len(set(miss_lst))
#
#     import collections
#     dups = [item for item, count in collections.Counter(id_lst2).items() if count > 1]
#
#     file = open(r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\id_lst_{0}.txt".format(year), "w+")
#     for i in id_lst:
#         file.write(str(i) + "\n")
#     file.close()
#
#     file = open(r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\id_lst2_{0}.txt".format(year), "w+")
#     for i in id_lst2:
#         file.write(str(i) + "\n")
#     file.close()
#
#     file = open(r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\miss_lst_{0}.txt".format(year), "w+")
#     for i in miss_lst:
#         file.write(str(i) + "\n")
#     file.close()
#
#     file = open(r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\dups_lst_{0}.txt".format(year), "w+")
#     for i in dups:
#         file.write(str(i) + ", ")
#     file.close()
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=2)(joblib.delayed(workFunc)(year) for year in [2005,2006])

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


