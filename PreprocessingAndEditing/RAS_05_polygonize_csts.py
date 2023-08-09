# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import joblib
import glob
import ogr
import osr

## OWN REPOSITORY
import forland_wrapper
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'SA'
per = '2012-2018'

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]
tiles_lst = ['0029_0036']

in_lst = [r'data\raster\grid_15km\\' + tile + r'\{}_{}_CropSeqType_clean.tif'.format(bl,per) for tile in tiles_lst]
out_lst = [r'data\vector\cst_fields\SA\{}_{}_CropSeqType_fields_{}'.format(bl, per, tile) for tile in tiles_lst]

job_lst = [[in_lst[i], out_lst[i]] for i in range (len(in_lst))]

def workFunc(job):
    print("start:", job)
    ras_pth = job[0]
    out_shp_pth = job[1]

    # open raster and band
    ras = gdal.Open(ras_pth)
    band = ras.GetRasterBand(1)
    pr = ras.GetProjection()

    # create shapefile
    srs = osr.SpatialReference(wkt=pr)
    # srs = ogr.osr.SpatialReference()
    # srs.ImportFromEPSG(25832)
    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(out_shp_pth + ".shp"):
        drv.DeleteDataSource(out_shp_pth + ".shp")
    out_shp = drv.CreateDataSource(out_shp_pth + ".shp")
    out_lyr = out_shp.CreateLayer("Polygonized", srs=srs)
    field = ogr.FieldDefn('CST', ogr.OFTInteger)
    out_lyr.CreateField(field)

    # polygonize raster into shapefile
    gdal.Polygonize(band, None, out_lyr, 0, [], callback=None )

    out_shp.Destroy()
    ras = None

    print("done:", job)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(i) for i in job_lst)

#

shp_lst = glob.glob(r"Q:\FORLand\Clemens\data\vector\cst_fields\SA\*.shp")

shp = ogr.Open(shp_lst[0])
lyr = shp.GetLayer()

out_shp_pth = r"Q:\FORLand\Clemens\data\vector\cst_fields\SA_2012-2018_no_csts.shp"
drv_shp = ogr.GetDriverByName('ESRI Shapefile')
in_sr = lyr.GetSpatialRef()
in_lyr_defn = lyr.GetLayerDefn()
if os.path.exists(out_shp_pth):
    drv_shp.DeleteDataSource(out_shp_pth)
out_shp = drv_shp.CreateDataSource(out_shp_pth)
lyr_name = os.path.splitext(os.path.split(out_shp_pth)[1])[0]
geom_type = ogr.wkbPolygon
out_lyr = out_shp.CreateLayer(lyr_name, in_sr, geom_type=geom_type)
for i in range(0, in_lyr_defn.GetFieldCount()):
    field_def = in_lyr_defn.GetFieldDefn(i)
    out_lyr.CreateField(field_def)

del shp, lyr

for pth in shp_lst:

    shp = ogr.Open(pth)
    lyr = shp.GetLayer()

    for feat in lyr:
        cst = int(feat.GetField('CST'))
        if cst == 255:
            out_lyr.CreateFeature(feat)
    lyr.ResetReading()

    del shp, lyr

del out_shp, out_lyr

forland_wrapper.removeLooseLines(out_shp_pth,
                                 out_shp_pth[:-4] + "dissolved.shp",
                                 dissolve=True,
                                 dist=-1)

QgsApplication, QgsProcessingRegistry, start_app, QgsNativeAlgorithms, processing, app = vector.importQgis()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

buff_pth = out_shp_pth[:-4] + '_buff.shp'
processing.run("native:buffer", {'INPUT': out_shp_pth[:-4] + "dissolved.shp",
                                 'DISTANCE': -30,
                                 'SEGMENTS': 5,
                                 'DISSOLVE': dissolve,
                                 'END_CAP_STYLE': 2,
                                 'JOIN_STYLE': 2,
                                 'MITER_LIMIT': 2,
                                 'OUTPUT': buff_pth})