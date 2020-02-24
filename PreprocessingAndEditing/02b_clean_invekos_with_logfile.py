import time
import os
from osgeo import ogr

## QGIS
from qgis.core import QgsApplication, QgsProcessingRegistry
from qgis.testing import start_app
from qgis.analysis import QgsNativeAlgorithms
import processing
app = start_app()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

## OWN REPOSITORY
import general
import vector

def removeLooseLines(in_shp_pth, out_shp_pth, dissolve=False):
    negbuff_pth = out_shp_pth[:-4] + '_negbuff.shp'
    processing.run("native:buffer", {'INPUT': in_shp_pth,
                                     'DISTANCE': -.1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 2,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': negbuff_pth})

    processing.run("native:buffer", {'INPUT': negbuff_pth,
                                     'DISTANCE': .1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 1,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': out_shp_pth})

######## Define wd, input & output folder
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

in_shp_pth = r"data\vector\repairInvekos\complete_case\Antraege2009.shp"
out_folder = r"data\vector\repairInvekos\complete_case\Antraege2009_temp\\"

######## Processing
file_name = os.path.basename(in_shp_pth)[:-4]
general.createFolder(out_folder)

logfile_pth = out_folder + '00_logfile.txt'
logfile = open(logfile_pth, "w+")

#### Identify duplicate features
no_dups_pth = out_folder + '01_noDuplicates.shp'
status_txt = "1. Remove duplicates from Invekos polygons"
print(status_txt)
tic = time.time()

id_lst, area_lst, centroid_lst = vector.extractGeomCharacteristics(in_shp_pth)

## look for identical areas and centroids
## the area and centroid indices indicate the occurence of possible duplicates (only the second occurence)
area_duplicates, area_indices = general.findDuplicatesInList(area_lst)
centroid_duplicates, centroid_indices = general.findDuplicatesInList(centroid_lst)

## check for indices that indicate duplicates in areas and centroids
identical_indices = []
for index in area_indices:
    if index in centroid_indices:
        identical_indices.append(index)

## remove all second occurences from the total ID list
id_rem_lst = [id_lst[i] for i in identical_indices]
id_unique_lst = [item for item in id_lst if item not in id_rem_lst]

## write the features that are indicated by the cleaned ID list to a new shapefile
print("1.1 Writing cleaned shapefile")
in_shp = ogr.Open(in_shp_pth, 0)
in_lyr = in_shp.GetLayer()

out_shp, out_lyr = vector.createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=no_dups_pth, geom_type=ogr.wkbPolygon)

if len(id_unique_lst) > 0:
    for id in id_unique_lst:
        feat = in_lyr.GetFeature(id)
        out_lyr.CreateFeature(feat)
    del out_shp, out_lyr
else:
    print("There are not duplicates in", in_shp_pth)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

inters_pth = out_folder + '02_intersections.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n2. Identify intersections of invekos polygons"
print(status_txt)
tic = time.time()
vector.identifyIntersections(no_dups_pth, inters_pth)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

status_txt = "\n2.1 Make unvalid intersections valid"
print(status_txt)
vector.validitiyCheck(inters_pth, "ID")
vector.makeGeomsValid(inters_pth)

inters_inters_pth = out_folder + '03_intersections_of_intersections.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n3. Identify intersections of intersections"
print(status_txt)
tic = time.time()
vector.identifyIntersections(inters_pth, inters_inters_pth)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

vector.validitiyCheck(inters_inters_pth, "ID")

inters_wo_pth = out_folder + '04_intersection_without_overlap.shp'
logfile = open(logfile_pth, "a+")
status_txt ="\n4. Calc difference between intersections and intersections 2 "
print(status_txt)
tic = time.time()
param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}
processing.run('native:difference', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

inters_merged_pth = out_folder + '05_merged_intersections.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n5. Merge intersections"
print(status_txt)
tic = time.time()
param_dict = {'LAYERS':[inters_inters_pth, inters_wo_pth], 'CRS':inters_inters_pth, 'OUTPUT': inters_merged_pth}
processing.run('qgis:mergevectorlayers', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

inters_cleaned_pth = out_folder + '06_intersections_cleaned.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n6. Remove loose lines of merged intersections"
print(status_txt)
tic = time.time()
removeLooseLines(inters_merged_pth, inters_cleaned_pth, False)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

inters_cleaned_pth2 = out_folder + '06_intersections_cleaned_step2.shp'
status_txt = "\n6.1 Remove geometries that are none"
print(status_txt)
vector.removeNoneGeoms(inters_cleaned_pth, inters_cleaned_pth2)

poly_diff_pth = out_folder + '07_difference_polygons-intersections.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n7. Calc difference between invekos polygons and final intersections"
print(status_txt)
tic = time.time()
param_dict = {'INPUT': no_dups_pth,'OVERLAY': inters_pth,'OUTPUT':poly_diff_pth}
processing.run('native:difference', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

polydiff_cleaned_pth = out_folder + '08_difference_cleaned.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n8. Remove loose lines of subtracted invekos polygons"
print(status_txt)
tic = time.time()
removeLooseLines(poly_diff_pth, polydiff_cleaned_pth, False)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

#status_txt = "\n8.1 Remove geometries that are none"
#print(status_txt)
#polydiff_cleaned_pth2 = out_folder + '06_intersections_cleaned_step2.shp'
#vector.removeNoneGeoms(polydiff_cleaned_pth, polydiff_cleaned_pth2)

## --> Use feat to write new shapefile instead of creating it from the geometries, see makeValid()

sliced_polys_pth = out_folder + r'\09_sliced_polygons.shp'
logfile = open(logfile_pth, "a+")
status_txt = "\n9. Merge subtracted polygons with final intersections"
print(status_txt)
tic = time.time()
param_dict = {'LAYERS':[polydiff_cleaned_pth, inters_cleaned_pth2], 'CRS':polydiff_cleaned_pth, 'OUTPUT': sliced_polys_pth}
processing.run('qgis:mergevectorlayers', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

cleaned_pth = r"data\vector\repairInvekos\complete_case\Antraege2008_cleaned.shp"
logfile = open(logfile_pth, "a+")
status_txt = "\n10. Dissolve polygons and intersections based on ID"
print(status_txt)
tic = time.time()
param_dict = {'INPUT': sliced_polys_pth, 'FIELD':'ID', 'OUTPUT': cleaned_pth}
processing.run('native:dissolve', param_dict)
toc = time.time()
logfile.write(status_txt + ": " + str(toc-tic) + " sec")
logfile.close()

print("Done!")

# ExecuteSQL(DataSource self, char const * statement, Geometry spatialFilter=None, char const * dialect) -> Layer
# yourdatasource.ExecuteSQL('repack yourlayername')

# for area in area_duplicates:
#     indexes_area = [i for i, item in enumerate(area_lst) if item == area]
#     print(indexes_area)
# print("")
# for centroid in centroid_duplicates:
#     indexes_centroid = [i for i, item in enumerate(centroid_lst) if item == centroid]
#     print(indexes_centroid)