# Clemens Jänicke
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

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

ind_lst = [15, 23, 18, 14, 17, 9, 1, 19, 22, 20, 3, 5, 16, 21, 11, 13, 8, 12, 4, 6, 2, 10, 7] # sorted by feature count
# task_lst = [(year, ind) for year in range(2009,2020) for ind in ind_lst]
done_lst = glob.glob(r"data\vector\InvClassified\BY\progress\*.txt")
done_lst = [os.path.basename(item) for item in done_lst]
done_lst = [(int(item[:4]), int(general.findBetween(item, "_", "_"))) for item in done_lst]

task_lst = []
for year in range(2007, 2020):
    for index in ind_lst:
        if (year, index) not in done_lst:
            task_lst.append((year, index))

task_lst = [(2013,5)]
print(len(task_lst), task_lst)
# task_lst = list(set(task_lst) - set(done_lst))
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
# task_lst = [(2017,16)]
# for task in task_lst:
def workFunc(task):

    year = task[0]
    index = task[1]
    stime_func = time.time()
    # print('################\n{}\n################'.format(year))

    ## Input shapefile & output folder
    in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}.shp".format(year, index)
    out_folder = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\\".format(year, index)

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

    print(year, index, "\nRemove duplicates from Invekos polygons and check and correct for validity of the polygons")
    forland_wrapper.removeDuplicates(in_shp_pth, no_dups_pth)
    forland_wrapper.validityChecking(no_dups_pth)

    # print(year, index, "\nIdentify intersections of no duplicates polygons and check and correct for validity of the intersections")
    # vector.identifyIntersections(no_dups_pth, inters_pth)
    # forland_wrapper.validityChecking(inters_pth)

    print("\n", year, index, "\n Clean no duplicates and intersections for difference calculation")
    forland_wrapper.removeLooseLines(inters_pth, inters_pth2, False)
    forland_wrapper.removingNoneGeoms(inters_pth2, inters_pth3)
    if os.path.exists(inters_pth3) == False:
        inters_pth3 = inters_pth2
    forland_wrapper.validityChecking(inters_pth3)

    # forland_wrapper.removeLooseLines(no_dups_pth, no_dups_pth2, False)
    # forland_wrapper.removingNoneGeoms(no_dups_pth2, no_dups_pth3)
    # if os.path.exists(no_dups_pth3) == False:
    #     no_dups_pth3 = no_dups_pth2
    # forland_wrapper.validityChecking(no_dups_pth3)

    print("\n", year, index, "\nIdentify possible intersections of intersections and slice them")
    forland_wrapper.sliceIntersections(inters_pth, inters_sliced_path1)
    if os.path.exists(inters_sliced_path1):
        forland_wrapper.removeLooseLines(inters_sliced_path1, inters_sliced_path2, False)
        forland_wrapper.removingNoneGeoms(inters_sliced_path2, inters_sliced_path3)
        if os.path.exists(inters_sliced_path3) == False:
            inters_sliced_path3 = inters_sliced_path2
    else:
        inters_sliced_path3 = inters_pth
    forland_wrapper.validityChecking(inters_sliced_path3)

    print("\n", year, index, "\nCalc difference between invekos polygons and final intersections")
    print("INPUT:", no_dups_pth)
    print("OVERLAY:", inters_sliced_path3)
    param_dict = {'INPUT': no_dups_pth, 'OVERLAY': inters_sliced_path3, 'OUTPUT': poly_diff_pth}
    processing.run('native:difference', param_dict)

    print("\n", year, index, "\nClean difference-polygons.")
    forland_wrapper.removeLooseLines(poly_diff_pth, polydiff_cleaned_pth1, False)
    forland_wrapper.removingNoneGeoms(polydiff_cleaned_pth1, polydiff_cleaned_pth2) ## --> no feature with null geoms
    if os.path.exists(polydiff_cleaned_pth2) == False:
        polydiff_cleaned_pth2 = polydiff_cleaned_pth1
    forland_wrapper.validityChecking(polydiff_cleaned_pth2)

    print("\n", year, index, "\nMerge difference-polygons with final intersections")
    print("LAYERS1:", polydiff_cleaned_pth2)
    print("LAYERS2:", inters_sliced_path3)
    param_dict = {'LAYERS':[polydiff_cleaned_pth2, inters_sliced_path3], 'CRS': polydiff_cleaned_pth2, 'OUTPUT': sliced_polys_pth1}
    processing.run('qgis:mergevectorlayers', param_dict)

    print("\n", year, index, "\nClean sliced polygons")
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

    ## print("\nConvert polygons to multipart where necessary")
    ## param_dict = {'INPUT': cleaned_pth2, 'OUTPUT': cleaned_pth3}
    ## processing.run('native:multiparttosingleparts', param_dict)
    ## forland_wrapper.validityChecking(cleaned_pth3)

    etime_func = time.time()
    duration = round((etime_func - stime_func) / 60, 2)
    file = open(r"data\vector\InvClassified\BY\progress\{0}_{1}_status_report.txt".format(year, index), "w+")
    file.write(r"Year: {} Index: {} Duration: {} min".format(year, index, duration))
    file.close()
    print(year, index, "done! Duration:", duration, "min.")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=1)(joblib.delayed(workFunc)(task) for task in task_lst)

#
# stime_sub = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
# print('################\n', year, "start: " + stime_sub, '\n################')

# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=12)(joblib.delayed(workFunc)(year) for year in range(2008,2020))

# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(ind) for ind in ind_lst)

# etime_sub = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
# print(year, "start: " + stime_sub)
# print(year, "end: " + etime_sub)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

# def workFunc(year):
#     print(year)
#
#     ## Input shapefile & output folder
#     in_shp_pth = r"data\vector\InvClassified\Antraege{0}.shp".format(year)
#     out_folder = r"data\vector\InvClassified\Antraege{0}_temp\\".format(year)
#
#     general.createFolder(out_folder)
#
#     #### Define paths
#     no_dups_pth = out_folder + '01_noDuplicates.shp'
#     inters_pth = out_folder + '02_intersections.shp'
#
#     print("\nRemove duplicates from Invekos polygons and check and correct for validity of the polygons")
#     forland_wrapper.removeDuplicates(in_shp_pth, no_dups_pth)
#     forland_wrapper.validityChecking(no_dups_pth)
#
#     print("\nIdentify intersections of no duplicates polygons and check and correct for validity of the intersections")
#     vector.identifyIntersections(no_dups_pth, inters_pth)
#     forland_wrapper.validityChecking(inters_pth)
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=11)(joblib.delayed(workFunc)(year) for year in year_lst)

# 387.61 + 324.92 + 256.22 + 225.93 + 216.08 + 185.23 + 168.92 + 127.71 + 110.22 + 106.78 + 88.76 + 84.95 + 84.2 + 37.26 + 36.07 + 19.96 + 17.36 + 14.28 + 9.84 + 6.09 + 5.27 + 4.02