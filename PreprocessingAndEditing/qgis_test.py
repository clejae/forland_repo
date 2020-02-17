import os
import time
from osgeo import ogr

# QGIS
from qgis.core import QgsApplication, QgsProcessingRegistry
from qgis.testing import start_app
from qgis.analysis import QgsNativeAlgorithms
import processing
app = start_app()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#from processing.core.Processing import Processing
#Processing.initialize()

def createFolder(directory):
    import os
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

def removeLooseLines(in_shp_pth, dissolve):
    negbuff_pth = in_shp_pth[:-4] + '_negbuffer.shp'
    processing.run("native:buffer", {'INPUT': in_shp_pth,
                                     'DISTANCE': -.1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 2,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': negbuff_pth})

    posbuff_pth = in_shp_pth[:-4] + '_posbuffer.shp'
    processing.run("native:buffer", {'INPUT': negbuff_pth,
                                     'DISTANCE': .1,
                                     'SEGMENTS': 5,
                                     'DISSOLVE': dissolve,
                                     'END_CAP_STYLE': 2,
                                     'JOIN_STYLE': 1,
                                     'MITER_LIMIT': 2,
                                     'OUTPUT': posbuff_pth})

wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

# for alg in QgsApplication.processingRegistry().algorithms():
#     print(alg.id(), "=", alg.displayName())
#
# processing.algorithmHelp("native:difference")
# processing.algorithmHelp("native:mergevectorlayers")
# processing.algorithmHelp("native:buffer")
# processing.algorithmHelp("native:dissolve")

inters_inters_pth = r"data\vector\repairInvekos\Test_intersection_intersection.shp"
inters_pth = r"data\vector\repairInvekos\Test_intersection.shp"
nudups_pth = r"data\vector\repairInvekos\Test_noDuplicates.shp"
cleaned_pth = r'Q:\FORLand\Clemens\data\vector\repairInvekos\Test_cleaned.shp'

temp_folder = nudups_pth[:-4] + '_temp'
createFolder(temp_folder)

inters_wo_pth = temp_folder + r'\01_intersection_without_overlap.shp'
param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}
processing.run('native:difference', param_dict)

inters_merged_pth = temp_folder + r'\02_merged_intersections.shp'
param_dict = {'LAYERS':[inters_inters_pth, inters_wo_pth], 'CRS':inters_inters_pth, 'OUTPUT': inters_merged_pth}
processing.run('qgis:mergevectorlayers', param_dict)

removeLooseLines(inters_merged_pth, False)
inters_posbuff_pth = inters_merged_pth[:-4] + '_posbuffer.shp'

poly_diff_pth = temp_folder + r'\05_difference_of_polygons.shp'
param_dict = {'INPUT': nudups_pth,'OVERLAY': inters_posbuff_pth,'OUTPUT':poly_diff_pth}
processing.run('native:difference', param_dict)

removeLooseLines(poly_diff_pth, False)
polydiff_posbuff_pth = poly_diff_pth[:-4] + '_posbuffer.shp'

sliced_polys_pth = temp_folder + r'\08_sliced_polygons.shp'
param_dict = {'LAYERS':[polydiff_posbuff_pth, inters_posbuff_pth], 'CRS':polydiff_posbuff_pth, 'OUTPUT': sliced_polys_pth}
processing.run('qgis:mergevectorlayers', param_dict)

# dissolved_polys_pth = temp_folder + r'\09_dissolved_polygons.shp'
param_dict = {'INPUT': sliced_polys_pth, 'FIELD':'ID', 'OUTPUT': cleaned_pth}
processing.run('native:dissolve', param_dict)
