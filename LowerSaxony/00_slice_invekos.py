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
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

###################################################################
## subset invekos on SLICE basis in parallel for one year

index_lst = range(4, 6)

for year in range(2015,2018):
    print('######################\n{0}\n######################'.format(year))
    folder_pth = r"Clemens\data\vector\IACS\LS\slices\{0}".format(year)
    general.createFolder(folder_pth)
    def workFunc(index):
        pth = r'Clemens\data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
        grid_pth = r"Clemens\data\vector\LS slicing\LS_slices_2.shp"
        grid_shp = ogr.Open(grid_pth)
        grid_lyr = grid_shp.GetLayer()

        grid_lyr.SetAttributeFilter("ID = '" + str(index) + "'")
        feat_grid = grid_lyr.GetNextFeature()

        print(year, index)
        inv_shp = ogr.Open(pth)
        inv_lyr = inv_shp.GetLayer()
        inv_sr = inv_lyr.GetSpatialRef()

        geom = feat_grid.geometry().Clone()
        inv_lyr.SetSpatialFilter(geom)

        out_shp_pth = r"Clemens\data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}.shp".format(year, index)
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

        print(year, index, "done")

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=13)(joblib.delayed(workFunc)(index) for index in index_lst)



# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


