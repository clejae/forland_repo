import os
import general

## import all necessary QGIS modules
from qgis.core import QgsApplication, QgsProcessingRegistry
from qgis.testing import start_app
from qgis.analysis import QgsNativeAlgorithms
import processing
app = start_app()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#from processing.core.Processing import Processing
#Processing.initialize()

## change wd
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)

## print available QGIS algorithms
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "=", alg.displayName())

## Look at the instructions for some algorithms
processing.algorithmHelp("native:difference")
processing.algorithmHelp("native:mergevectorlayers")
processing.algorithmHelp("native:buffer")
processing.algorithmHelp("native:dissolve")
processing.algorithmHelp("native:multiparttosingleparts")
processing.algorithmHelp("native:deleteholes")

## define some paths
temp_folder = nudups_pth[:-4] + '_temp'
general.createFolder(temp_folder)
inters_inters_pth = r"data\vector\repairInvekos\Test_intersection_intersection.shp" # input 1
inters_pth = r"data\vector\repairInvekos\Test_intersection.shp"	# input 2
inters_wo_pth =  r'\01_intersection_without_overlap.shp' # output

## define input parameter dictionary
param_dict = {'INPUT' : inters_pth,'OVERLAY' : inters_inters_pth,'OUTPUT' : inters_wo_pth}

## run an example algorithm
processing.run('native:difference', param_dict)




