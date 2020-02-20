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

## CLEMENS REPOSITORY
import general
import vector

######## Define wd, input & output folder
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

in_shp_pth = r"data\vector\repairInvekos\complete_case\Antraege2008.shp"
out_folder = r"data\vector\repairInvekos\complete_case\Antraege2008_temp\\"

######## Processing
file_name = os.path.basename(in_shp_pth)[:-4]
general.createFolder(out_folder)

#### Identify duplicate features
print("Identifying duplicates")
id_lst, area_lst, centroid_lst = vector.extractGeomCharacteristics(in_shp_pth, 'ID')

## look for identical areas and centroids
## the area and centroid indices indicate the occurence of possible duplicates (only the second occurence)
area_duplicates, area_indices = general.findDuplicatesInList(area_lst)
centroid_duplicates, centroid_indices = general.findDuplicatesInList(centroid_lst)

## check for indices that indicate duplicates in areas and centroids
identical_indices = []
for index in area_indices:
    if index in centroid_duplicates:
        identical_indices.append(index)

## remove all second occurences from the total ID list
id_rem_lst = [id_lst[i] for i in identical_indices]
id_unique_lst = [item for item in id_lst if item not in id_rem_lst]

## write the features that are indicated by the cleaned ID list to a new shapefile
print("Writing cleaned shapefile")
in_shp = ogr.Open(in_shp_pth, 0)
in_lyr = in_shp.GetLayer()

out_shp_name = out_folder + file_name + '_noDuplicates.shp'
out_shp, out_lyr = vector.createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=out_shp_name, geom_type=ogr.wkbPolygon)

tic = time.time()
for id in id_unique_lst:
    in_lyr.SetAttributeFilter("ID = '" + str(id) + "'")
    feat = in_lyr.GetNextFeature()
    out_lyr.CreateFeature(feat)
    in_lyr.SetAttributeFilter(None)
toc = time.time()
print("Version mit SetAttributeFiler:", toc-tic)

out_shp_name = out_folder + file_name + '_noDuplicates2.shp'
out_shp, out_lyr = vector.createEmptyShpWithCopiedLyr(in_lyr=in_lyr, out_pth=out_shp_name, geom_type=ogr.wkbPolygon)

tic = time.time()
for id in id_unique_lst:
    feat = in_lyr.GetFeature(id)
    out_lyr.CreateFeature(feat)
toc = time.time()
print("Version mit GetFeature:", toc-tic)

# ExecuteSQL(DataSource self, char const * statement, Geometry spatialFilter=None, char const * dialect) -> Layer
# yourdatasource.ExecuteSQL('repack yourlayername')

# for area in area_duplicates:
#     indexes_area = [i for i, item in enumerate(area_lst) if item == area]
#     print(indexes_area)
# print("")
# for centroid in centroid_duplicates:
#     indexes_centroid = [i for i, item in enumerate(centroid_lst) if item == centroid]
#     print(indexes_centroid)