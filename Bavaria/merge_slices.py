# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

def workFunc(year):
# for year in range(2005, 2020):
    print("\nStarting year", year)
    ref_pth = r'Clemens\data\vector\IACS\BV\slices\{0}\InVekos_BY_{0}_1_temp\IACS_BV_{0}_1.shp'.format(year)
    out_pth = r'Clemens\data\vector\IACS\BV\IACS_BV_{0}_ZALF.shp'.format(year)

    ## open reference shape, fetch sr, and lyr def and close
    ref_shp = ogr.Open(ref_pth)
    ref_lyr = ref_shp.GetLayer()
    ref_sr = ogr.osr.SpatialReference()
    ref_sr.ImportFromEPSG(25832)
    ref_lyr_defn = ref_lyr.GetLayerDefn()

    ## create output shp
    drv_shp = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(out_pth):
        drv_shp.DeleteDataSource(out_pth)
    out_shp = drv_shp.CreateDataSource(out_pth)
    lyr_name = os.path.splitext(os.path.split(out_pth)[1])[0]
    geom_type = ogr.wkbPolygon
    out_lyr = out_shp.CreateLayer(lyr_name, ref_sr, geom_type=geom_type)
    for i in range(0, ref_lyr_defn.GetFieldCount()):
        field_def = ref_lyr_defn.GetFieldDefn(i)
        out_lyr.CreateField(field_def)

    del ref_shp, ref_lyr

    ## loop over slices and their features to add them to the output shp
    for index in range(1,24):
        print(year, index)
        sl_pth = r'Clemens\data\vector\IACS\BV\slices\{0}\InVekos_BY_{0}_{1}_temp\IACS_BV_{0}_{1}.shp'.format(
            year, index)

        sl_shp = ogr.Open(sl_pth)
        sl_lyr = sl_shp.GetLayer()

        ## loop over features
        for feat in sl_lyr:
            out_lyr.CreateFeature(feat)
        sl_lyr.ResetReading()

        del sl_shp, sl_lyr

    del out_shp, out_lyr
    print(year, "done!")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=4)(joblib.delayed(workFunc)(year) for year in range(2005, 2008))

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


