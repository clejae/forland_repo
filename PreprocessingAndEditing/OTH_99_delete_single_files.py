# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import joblib
import glob
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'Q:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r"Q:\Clemens\data\raster\folder_list.txt") as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

def workFunc(tile):
    print(tile)
    lst = glob.glob(r"L:\Clemens\data\raster\grid_15km\{0}\Inv_CerLeaf*".format(tile))
    for file in lst:
        os.remove(file)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=8)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)


# 30 sec
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


