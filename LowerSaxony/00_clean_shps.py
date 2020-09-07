# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
##CJs Repo
import vector
import forland_wrapper

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## first run make of making the shapefile valid

for year in range(2012,2020):
    pth = r"data\vector\IACS\LS\IACS_LS_{0}.shp".format(year)
    shp = ogr.Open(pth)
    lyr = shp.GetLayer()
    # vector.printFieldNames(lyr)

    no_dups_pth = r"data\vector\IACS\LS\IACS_LS_{0}_NoDups.shp".format(year)
    # forland_wrapper.validityChecking(pth)
    forland_wrapper.removeDuplicates(pth, no_dups_pth)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


