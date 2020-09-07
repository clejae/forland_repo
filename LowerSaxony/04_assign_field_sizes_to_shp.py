# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import vector

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'LS'
fname_area = 'AREA_ha'

# for year in range(2012,2019):
def workFunc(year):
    print(year)
    pth = 'vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
    shp = ogr.Open(pth, 1)
    lyr = shp.GetLayer()
    fname_lst = vector.getFieldNames(shp)

    if fname_area in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_area))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_area, ogr.OFTReal))
        fname_lst = vector.getFieldNames(shp)

    for f, feat in enumerate(lyr):
        geom = feat.geometry()
        area = geom.Area()
        area = area / 10000
        feat.SetField(fname_area, area)
        lyr.SetFeature(feat)
    lyr.ResetReading()
    print(year, "done")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=7)(joblib.delayed(workFunc)(year) for year in range(2018, 2019))

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
