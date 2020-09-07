# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import time
import os
from osgeo import ogr
import joblib
import glob

## CJs REPOSITORY
import forland_wrapper

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#

## Parralelize over years (for federeal states where no slicing was needed, e.g. Saxony-Anhalt)
bl = 'SA'
def workFunc(year):
    print('################\n{0}'.format(year))

    ## Input shapefile & output folder
    in_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}.shp".format(bl, year)
    out_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}_v2.shp".format(bl, year)

    forland_wrapper.removeUnusedCols(in_shp_pth, out_shp_pth, ['IDInters','path','layer'])

if __name__ == '__main__':
    joblib.Parallel(n_jobs=5)(joblib.delayed(workFunc)(year) for year in range(2009,2019))

# ## Parralelize over years AND indices (for federeal states which needed slicing, e.g. Bavaria)
# bl = 'BV'
#
# ind_lst = [15, 23, 18, 14, 17, 9, 1, 19, 22, 20, 3, 5, 16, 21, 11, 13, 8, 12, 4, 6, 2, 10, 7]#[1]#  # sorted by feature count
# task_lst = []
# for year in range(2015,2020):#[2005, 2006, 2015, 2016]: #range(2007, 2020):
#     for index in ind_lst:
#         task_lst.append((year, index))
# print(len(task_lst), task_lst)
#
# def workFunc(task):
#     year = task[0]
#     index = task[1]
#     stime_func = time.time()
#     print('################\n{0}, {1}'.format(year, index))
#
#     ## Input shapefile & output folder
#     in_shp_pth = r"data\vector\IACS\BV\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(year, index)
#     out_shp_pth = r"data\vector\IACS\BV\slices\{0}\InVekos_BY_{0}_{1}_temp\IACS_BV_{0}_{1}.shp".format(year, index)
#
#     forland_wrapper.removeUnusedCols(in_shp_pth, out_shp_pth, ['IDInters','path','layer'])
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(task) for task in task_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
