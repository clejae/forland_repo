import time
import os
from osgeo import ogr
import time

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

def validityChecking(in_shp_pth, id_field = "ID"):
    print("Validity check of", in_shp_pth)
    invalid_geoms = vector.countInvalidGeoms(in_shp_pth, id_field)
    if len(invalid_geoms) > 0:
        vector.makeGeomsValid(in_shp_pth)
        invalid_geoms_step2 = vector.countInvalidGeoms(in_shp_pth, id_field)

        if len(invalid_geoms_step2) > 0:
            print(invalid_geoms_step2, "could not be made valid.")
        else:
            print("All invalid geometries were made valid.")
    else:
        print("There are no invalid geometries in shapefile", in_shp_pth)

######## Define wd, input & output folder
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

for year in range(2017,2019):
    tic = time.time()
    print('####################################\n{}\n####################################'.format(year))

    in_shp_pth = r"data\vector\repairInvekos\complete_case\Antraege{}.shp".format(year)
    out_folder = r"data\vector\repairInvekos\complete_case\Antraege{}_temp\\".format(year)

    ######## Processing
    file_name = os.path.basename(in_shp_pth)[:-4]
    general.createFolder(out_folder)

    #### Identify duplicate features
    no_dups_pth = out_folder + '01_noDuplicates.shp'
    inters_pth = out_folder + '02_intersections.shp'

    status_txt = "1. Remove duplicates from Invekos polygons"
    print(status_txt)

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
    #######

    validityChecking(no_dups_pth,"ID")


    status_txt = "\n2. Identify intersections of invekos polygons"
    print(status_txt)
    vector.identifyIntersections(no_dups_pth, inters_pth)
    toc = time.time()
    t = round((toc-tic),1)
    print('####################################\n{}: {} sec\n####################################'.format(year,t))