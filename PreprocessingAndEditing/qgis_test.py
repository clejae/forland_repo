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

wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "=", alg.displayName())

processing.algorithmHelp("native:difference")
processing.algorithmHelp("native:mergevectorlayers")
processing.algorithmHelp("native:buffer")
processing.algorithmHelp("native:dissolve")
processing.algorithmHelp("native:multiparttosingleparts")

inters_inters_pth = r"data\vector\repairInvekos\Test_intersection_intersection.shp"
inters_pth = r"data\vector\repairInvekos\Test_intersection.shp"

temp_folder = nudups_pth[:-4] + '_temp'
createFolder(temp_folder)

inters_wo_pth = temp_folder + r'\01_intersection_without_overlap.shp'
param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}
processing.run('native:difference', param_dict)
