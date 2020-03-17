# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import time
import os
from osgeo import ogr

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
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## Input shapefile & output folder
in_shp_pth = r"data\vector\repairInvekos\complete_case\Antraege2008.shp"
out_folder = r"data\vector\repairInvekos\complete_case\Antraege2008_temp\\"
general.createFolder(out_folder)

#### Define paths
no_dups_pth = out_folder + '01_noDuplicates.shp'

inters_pth = out_folder + '02_intersections.shp'
inters_sliced_path1 = out_folder + '02_intersections_sliced_01.shp'
inters_sliced_path2 = out_folder + '02_intersections_sliced_02.shp'
inters_sliced_path3 = out_folder + '02_intersections_sliced_03.shp'

poly_diff_pth = out_folder + '03_difference.shp'
polydiff_cleaned_pth1 = out_folder + '03_difference_cleaned_01.shp'
polydiff_cleaned_pth2 = out_folder + '03_difference_cleaned_02.shp'

sliced_polys_pth1 = out_folder + r'\04_sliced_polygons_01.shp'
sliced_polys_pth2 =  out_folder + r'\04_sliced_polygons_02.shp'
sliced_polys_pth3 =  out_folder + r'\04_sliced_polygons_03.shp'

cleaned_pth1 = out_folder + r"\05_nodups_cleaned_01.shp"
cleaned_pth2 = out_folder + r"\05_nodups_cleaned_02.shp"
cleaned_pth3 = out_folder + r"\05_nodups_cleaned_03.shp"

print("\nRemove duplicates from Invekos polygons and check and correct for validity of the polygons")
forland_wrapper.removeDuplicates(in_shp_pth, no_dups_pth)
forland_wrapper.validityChecking(no_dups_pth)

print("\nIdentify intersections of no duplicates polygons and check and correct for validity of the intersections")
vector.identifyIntersections(no_dups_pth, inters_pth)
forland_wrapper.validityChecking(inters_pth)

print("\nIdentify possible intersections and slice intersections")
forland_wrapper.sliceIntersections(inters_pth, inters_sliced_path1)
forland_wrapper.removeLooseLines(inters_sliced_path1, inters_sliced_path2, False)
forland_wrapper.removingNoneGeoms(inters_sliced_path2, inters_sliced_path3)
forland_wrapper.validityChecking(inters_sliced_path3)

print("\nCalc difference between invekos polygons and final intersections")
param_dict = {'INPUT': no_dups_pth, 'OVERLAY': inters_pth, 'OUTPUT': poly_diff_pth}
processing.run('native:difference', param_dict)

print("\nClean difference-polygons.")
forland_wrapper.removeLooseLines(poly_diff_pth, polydiff_cleaned_pth1, False)
forland_wrapper.removingNoneGeoms(polydiff_cleaned_pth1, polydiff_cleaned_pth2) ## --> no feature with null geoms
forland_wrapper.validityChecking(polydiff_cleaned_pth2)

print("\nMerge difference-polygons with final intersections")
param_dict = {'LAYERS':[polydiff_cleaned_pth2, inters_sliced_path3], 'CRS': polydiff_cleaned_pth2, 'OUTPUT': sliced_polys_pth1}
processing.run('qgis:mergevectorlayers', param_dict)

print("\nClean sliced polygons")
forland_wrapper.removeLooseLines(sliced_polys_pth1, sliced_polys_pth2, False)
forland_wrapper.removingNoneGeoms(sliced_polys_pth2, sliced_polys_pth3) #--> no features with no geometry in the shp
forland_wrapper.validityChecking(sliced_polys_pth2)

print("\nDissolve polygons and intersections based on ID")
param_dict = {'INPUT': sliced_polys_pth2, 'FIELD':'ID', 'OUTPUT': cleaned_pth1}
processing.run('native:dissolve', param_dict)

print("\nRemove loose lines from inside of the polygons")
forland_wrapper.removeLooseLines(cleaned_pth1, cleaned_pth2, False, dist = 0.01)

print("\nConvert polygons to multipart where necessary")
param_dict = {'INPUT': cleaned_pth2, 'OUTPUT': cleaned_pth3}
processing.run('native:multiparttosingleparts', param_dict)
forland_wrapper.validityChecking(cleaned_pth3)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#