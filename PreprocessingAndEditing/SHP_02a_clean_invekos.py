# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import time
import os
from osgeo import ogr
import joblib

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
year_lst = range(2016, 2017) # [2010] #
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#

os.chdir(wd)

for year in year_lst:

    print('################\n{}\n################'.format(year))

    ## Input shapefile & output folder
    in_shp_pth = r"data\vector\InvClassified\Antraege{0}.shp".format(year)
    out_folder = r"data\vector\InvClassified\Antraege{0}_temp\\".format(year)

    # in_shp_pth = r"data\vector\repairInvekos\sub_case\Antraege{0}_sub.shp".format(year)
    # out_folder = r"data\vector\repairInvekos\sub_case\Antraege{0}_sub_temp\\".format(year)
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

#     print("\nRemove duplicates from Invekos polygons and check and correct for validity of the polygons")
#     forland_wrapper.removeDuplicates(in_shp_pth, no_dups_pth)
#     forland_wrapper.validityChecking(no_dups_pth)
#
#     print("\nIdentify intersections of no duplicates polygons and check and correct for validity of the intersections")
#     vector.identifyIntersections(no_dups_pth, inters_pth)
#     forland_wrapper.validityChecking(inters_pth)
    ## 2009 --> Intersection with ID 1143 had to be corrected manually
    ## 2016 --> Intersection with ID 57331 had to be corrected manually
    ## 2017 --> Intersection with ID 93827 had to be corrected manually
    ## 2018 --> no Intersections of intersections

    print("\n Clean no duplicates and intersections for difference calculation")
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

    # print("\nIdentify possible intersections of intersections and slice them")
    # forland_wrapper.sliceIntersections(inters_pth, inters_sliced_path1)
    # forland_wrapper.removeLooseLines(inters_sliced_path1, inters_sliced_path2, False)
    # forland_wrapper.removingNoneGeoms(inters_sliced_path2, inters_sliced_path3)
    if os.path.exists(inters_sliced_path3) == False:
        inters_sliced_path3 = inters_sliced_path2
    # forland_wrapper.validityChecking(inters_sliced_path3)

    print("\nCalc difference between invekos polygons and final intersections")
    param_dict = {'INPUT': no_dups_pth3, 'OVERLAY': inters_pth, 'OUTPUT': poly_diff_pth}
    processing.run('native:difference', param_dict)
    no_dups_pth = no_dups_pth2
    inters_pth = inters_pth3

    print("\nClean difference-polygons.")
    forland_wrapper.removeLooseLines(poly_diff_pth, polydiff_cleaned_pth1, False)
    forland_wrapper.removingNoneGeoms(polydiff_cleaned_pth1, polydiff_cleaned_pth2) ## --> no feature with null geoms
    if os.path.exists(polydiff_cleaned_pth2) == False:
        polydiff_cleaned_pth2 = polydiff_cleaned_pth1
    forland_wrapper.validityChecking(polydiff_cleaned_pth2)

    print("\nMerge difference-polygons with final intersections")
    if year == 2018:
        param_dict = {'LAYERS': [polydiff_cleaned_pth2, inters_pth], 'CRS': polydiff_cleaned_pth2,
                      'OUTPUT': sliced_polys_pth1}
    else:
        param_dict = {'LAYERS':[polydiff_cleaned_pth2, inters_sliced_path3], 'CRS': polydiff_cleaned_pth2, 'OUTPUT': sliced_polys_pth1}
    processing.run('qgis:mergevectorlayers', param_dict)

    print("\nClean sliced polygons")
    forland_wrapper.removeLooseLines(sliced_polys_pth1, sliced_polys_pth2, False)
    forland_wrapper.removingNoneGeoms(sliced_polys_pth2, sliced_polys_pth3) #--> no features with no geometry in the shp
    if os.path.exists(sliced_polys_pth3) == False:
        sliced_polys_pth3 = sliced_polys_pth2
    forland_wrapper.validityChecking(sliced_polys_pth3)

    print("\nDissolve polygons and intersections based on ID")
    param_dict = {'INPUT': sliced_polys_pth3, 'FIELD':'ID', 'OUTPUT': cleaned_pth1}
    processing.run('native:dissolve', param_dict)

    print("\nRemove loose lines from inside of the polygons")
    forland_wrapper.removeLooseLines(cleaned_pth1, cleaned_pth2, False, dist = 0.01)
    forland_wrapper.removingNoneGeoms(cleaned_pth2, cleaned_pth3)

    # print("\nConvert polygons to multipart where necessary")
    # param_dict = {'INPUT': cleaned_pth2, 'OUTPUT': cleaned_pth3}
    # processing.run('native:multiparttosingleparts', param_dict)
    # forland_wrapper.validityChecking(cleaned_pth3)

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