# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import time
import os
from osgeo import ogr
import joblib
import glob

## OWN REPOSITORY
import general
import vector
import forland_wrapper

## QGIS
QgsApplication, QgsProcessingRegistry, start_app,  QgsNativeAlgorithms, processing, app = vector.importQgis()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'

# slice list sorted by feature count
ind_lst = [7,12,8,1,3,5,6,13,11,10,9,4,2]
task_lst = [(year, ind) for year in range(2012,2020) for ind in ind_lst]

done_lst = glob.glob(r"Q:\FORLand\Clemens\data\vector\IACS\LS\progress\*_status_report_last_steps.txt")
done_lst = [os.path.basename(item) for item in done_lst]
done_lst = [(int(item[:4]), int(general.findBetween(item, "_", "_"))) for item in done_lst]

task_lst = []
for year in range(2012,2020): #range(2007, 2020):
    for index in ind_lst:
        if (year, index) not in done_lst:
            task_lst.append((year, index))

task_lst = task_lst[1:]
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# ## first run of making the shapefile valid
#
# for year in range(2012,2020):
#     pth = r"data\vector\IACS\LS\IACS_LS_{0}.shp".format(year)
#     shp = ogr.Open(pth)
#     lyr = shp.GetLayer()
#     # vector.printFieldNames(lyr)
#
#     no_dups_pth = r"data\vector\IACS\LS\IACS_LS_{0}_NoDups.shp".format(year)
#     # forland_wrapper.validityChecking(pth)
#     forland_wrapper.removeDuplicates(pth, no_dups_pth)

for task in task_lst:
# def workFunc(task):

    print("Task:", task)
    year = task[0]
    index = task[1]
    stime_func = time.time()

    ## Input shapefile & output folder
    in_shp_pth = r"data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}.shp".format(year, index)
    out_folder = r"data\vector\IACS\LS\slices\{0}\IACS_LS_{0}_{1}_temp\\".format(year, index)

    general.createFolder(out_folder)

    #### Define paths
    no_dups_pth = out_folder + '01_noDuplicates.shp'
    no_dups_pth2 = out_folder + '01_noDuplicates_v02.shp'
    no_dups_pth3 = out_folder + '01_noDuplicates_v03.shp'

    inters_pth = out_folder + '02_intersections.shp'
    inters_sliced_path1 = out_folder + '02_intersections_sliced_01.shp'
    inters_sliced_path2 = out_folder + '02_intersections_sliced_02.shp'
    inters_sliced_path3 = out_folder + '02_intersections_sliced_03.shp'

    inters_pth2 = out_folder + '02_intersections_v02.shp'
    inters_pth3 = out_folder + '02_intersections_v03.shp'

    poly_diff_pth = out_folder + '03_difference.shp'
    polydiff_cleaned_pth1 = out_folder + '03_difference_cleaned_01.shp'
    polydiff_cleaned_pth2 = out_folder + '03_difference_cleaned_02.shp'

    sliced_polys_pth1 = out_folder + r'04_sliced_polygons_01.shp'
    sliced_polys_pth2 =  out_folder + r'04_sliced_polygons_02.shp'
    sliced_polys_pth3 =  out_folder + r'04_sliced_polygons_03.shp'

    cleaned_pth1 = out_folder + r"05_nodups_cleaned_01.shp"
    cleaned_pth2 = out_folder + r"05_nodups_cleaned_02.shp"
    cleaned_pth3 = out_folder + r"05_nodups_cleaned_03.shp"

    # print(year, index, "\nRemove duplicates from Invekos polygons and check and correct for validity of the polygons")
    # forland_wrapper.removeDuplicates(in_shp_pth, no_dups_pth)
    # forland_wrapper.validityChecking(no_dups_pth)
    #
    # print(year, index, "\nIdentify intersections of no duplicates polygons and check and correct for validity of the intersections")
    # vector.identifyIntersections(no_dups_pth, inters_pth)
    # forland_wrapper.validityChecking(inters_pth)
    #
    # print("\n", year, index, "\n Clean no duplicates and intersections for difference calculation")
    # forland_wrapper.removeLooseLines(inters_pth, inters_pth2, False)
    # forland_wrapper.removingNoneGeoms(inters_pth2, inters_pth3)
    if os.path.exists(inters_pth3) == False:
        inters_pth3 = inters_pth2
    # forland_wrapper.validityChecking(inters_pth3)

    # forland_wrapper.removeLooseLines(no_dups_pth, no_dups_pth2, False)
    # forland_wrapper.removingNoneGeoms(no_dups_pth2, no_dups_pth3)
    if os.path.exists(no_dups_pth3) == False:
        no_dups_pth3 = no_dups_pth2
    # forland_wrapper.validityChecking(no_dups_pth3)

    # print("\n", year, index, "\nIdentify possible intersections of intersections and slice them")
    # forland_wrapper.sliceIntersections(inters_pth, inters_sliced_path1)
    if os.path.exists(inters_sliced_path1):
        # forland_wrapper.removeLooseLines(inters_sliced_path1, inters_sliced_path2, False)
        # forland_wrapper.removingNoneGeoms(inters_sliced_path2, inters_sliced_path3)
        if os.path.exists(inters_sliced_path3) == False:
            inters_sliced_path3 = inters_sliced_path2
    else:
        inters_sliced_path3 = inters_pth
    # forland_wrapper.validityChecking(inters_sliced_path3)

    # print("\n", year, index, "\nCalc difference between invekos polygons and final intersections")
    # print("INPUT:", no_dups_pth)
    # print("OVERLAY:", inters_pth)
    # param_dict = {'INPUT': no_dups_pth, 'OVERLAY': inters_pth, 'OUTPUT': poly_diff_pth}
    # processing.run('native:difference', param_dict)

    # print("\n", year, index, "\nClean difference-polygons.")
    # forland_wrapper.removeLooseLines(poly_diff_pth, polydiff_cleaned_pth1, False)
    # forland_wrapper.removingNoneGeoms(polydiff_cleaned_pth1, polydiff_cleaned_pth2) ## --> no feature with null geoms
    if os.path.exists(polydiff_cleaned_pth2) == False:
        polydiff_cleaned_pth2 = polydiff_cleaned_pth1
    # forland_wrapper.validityChecking(polydiff_cleaned_pth2)

    # print("\n", year, index, "\nMerge difference-polygons with final intersections")
    # print("LAYERS1:", polydiff_cleaned_pth2)
    # print("LAYERS2:", inters_sliced_path3)
    # param_dict = {'LAYERS':[polydiff_cleaned_pth2, inters_sliced_path3], 'CRS': polydiff_cleaned_pth2, 'OUTPUT': sliced_polys_pth1}
    # processing.run('native:mergevectorlayers', param_dict)
    #
    # print("\n", year, index, "\nClean sliced polygons")
    forland_wrapper.removeLooseLines(sliced_polys_pth1, sliced_polys_pth2, False)
    forland_wrapper.removingNoneGeoms(sliced_polys_pth2, sliced_polys_pth3) #--> no features with no geometry in the shp
    if os.path.exists(sliced_polys_pth3) == False:
        sliced_polys_pth3 = sliced_polys_pth2
    forland_wrapper.validityChecking(sliced_polys_pth3)

    print("\n", year, index, "\nDissolve polygons and intersections based on ID")
    print("INPUT:", sliced_polys_pth3)
    param_dict = {'INPUT': sliced_polys_pth3, 'FIELD':'ID', 'OUTPUT': cleaned_pth1}
    processing.run('native:dissolve', param_dict)

    print("\n", year, index, "\nRemove loose lines from inside of the polygons")
    forland_wrapper.removeLooseLines(cleaned_pth1, cleaned_pth2, False, dist = 0.01)
    forland_wrapper.removingNoneGeoms(cleaned_pth2, cleaned_pth3)

    etime_func = time.time()
    duration = round((etime_func - stime_func) / 60, 2)
    file = open(r"data\vector\IACS\LS\progress\{0}_{1}_status_report_last_steps.txt".format(year, index), "w+")
    file.write(r"Year: {} Index: {} Duration: {} min".format(year, index, duration))
    file.close()
    print(year, index, "done! Duration:", duration, "min.")

# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=13)(joblib.delayed(workFunc)(task) for task in task_lst)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# import os
# wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# os.chdir(wd)
# import forland_wrapper
# pth = r"data\vector\IACS\LS\slices\2012\IACS_LS_2012_13_temp\\04_sliced_polygons_02.shp"
# forland_wrapper.validityChecking(pth)