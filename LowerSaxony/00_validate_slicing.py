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
## check if features were missed or got duplicated during slicing

for year in range(2015,2018):
    print(year)

    pth =  r'Clemens\data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)

    inv_shp = ogr.Open(pth)
    inv_lyr = inv_shp.GetLayer()
    print( "Number of features in original shape:", inv_lyr.GetFeatureCount())

    s = 0
    for i in range(1,14):
        sub_pth = r"Clemens\data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}.shp".format(year, i)
        shp = ogr.Open(sub_pth)
        lyr = shp.GetLayer()
        s2 = lyr.GetFeatureCount()
        # print(i, s2)
        s = s + s2
        del shp, lyr
    print("Number of features in sliced shape:", s)

###################################################################
## get missing features that were missed during the slicing
# for year in [2015, 2016, 2017]: #range(2005, 2020):
def workFunc(year):
    print(year)

    pth = r'Clemens\data\vector\IACS\LS\IACS_LS_{0}.shp'.format(year)
    inv_shp = ogr.Open(pth)
    inv_lyr = inv_shp.GetLayer()

    id_lst = []
    for feat in inv_lyr:
        fid = feat.GetField("ID")
        id_lst.append(fid)
    inv_lyr.ResetReading()

    id_lst2 = []
    for i in range(1,14):
        # print(i)
        sub_pth = r"Clemens\data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}.shp".format(year, i)
        shp = ogr.Open(sub_pth)
        lyr = shp.GetLayer()
        for feat in lyr:
            fid = feat.GetField("ID")
            id_lst2.append(fid)
            # if fid not in id_lst:
            #     m_lst.append(fid)
        lyr.ResetReading()
        del shp, lyr

    s = set(id_lst2)
    miss_lst = [fid for fid in id_lst if fid not in s]
    len(set(miss_lst))

    import collections
    dups = [item for item, count in collections.Counter(id_lst2).items() if count > 1]

    file = open(r"Clemens\data\vector\IACS\LS\id_lst_{0}.txt".format(year), "w+")
    for i in id_lst:
        file.write(str(i) + "\n")
    file.close()

    file = open(r"Clemens\data\vector\IACS\LS\id_lst2_{0}.txt".format(year), "w+")
    for i in id_lst2:
        file.write(str(i) + "\n")
    file.close()

    file = open(r"Clemens\data\vector\IACS\LS\miss_lst_{0}.txt".format(year), "w+")
    for i in miss_lst:
        file.write(str(i) + "\n")
    file.close()

    file = open(r"Clemens\data\vector\IACS\LS\dups_lst_{0}.txt".format(year), "w+")
    for i in dups:
        file.write(str(i) + ", ")
    file.close()


if __name__ == '__main__':
    joblib.Parallel(n_jobs=3)(joblib.delayed(workFunc)(year) for year in [2015])


for year in [2016, 2017]:

    with open(r"Clemens\data\vector\IACS\LS\dups_lst_{0}.txt".format(year)) as file:
        dups = file.readlines()
    dups = dups[0].split(',')

    for i in range(1,14):
        # print(i)
        sub_pth = r"Clemens\data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}.shp".format(year, i)
        shp = ogr.Open(sub_pth)
        lyr = shp.GetLayer()

        for dup in dups:
            lyr.SetAttributeFilter("ID = '" + str(dup) + "'")
            print("year:", year, "duplicate:", dup, "slice:", i, "count:", lyr.GetFeatureCount())
            lyr.SetAttributeFilter(None)
        lyr.ResetReading()
        del shp, lyr





# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


