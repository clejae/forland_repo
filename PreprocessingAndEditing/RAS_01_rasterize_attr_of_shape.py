# Clemens Jänicke
# github Repo: https://github.com/clejae

# --------------------------------------------------------------- LOAD PACKAGES ---------------------------------------------------------------#
import ogr
import os
import time
import joblib
import gdal

## Clemens repo
import vector

stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# --------------------------------------------------------------- USER VARIABLES ---------------------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# --------------------------------------------------------------- LOAD DATA & PROCESSING ---------------------------------------------------------------#
os.chdir(wd)
bl_lst = ['LS']
per_lst = [(2011,2011)]
for bl in bl_lst:
    #### Define extent
    ## Get extent of box of federal state
    shp_pth = wd + r'Clemens\data\vector\grid\Invekos_grid_{0}-Box_15km.shp'.format(bl)
    shp = ogr.Open(shp_pth, 0)
    lyr = shp.GetLayer()
    x_min_ext, x_max_ext, y_min_ext, y_max_ext = lyr.GetExtent()

    #### Rasterize the IACS data
    attr_lst = ["CST USE"]# "ID_KTYP", "ID_WiSo", "ID_HaBl"] #"ID_KTYP", "ID_WiSo", "ID_HaBl", "Oeko", "ORGANIC"
    res = 5
    no_data_val = 255
    for attr in attr_lst:
        for per in per_lst:
            min, max = per[0], per[1] + 1
            def workFunc(year):
                ## input shapefile path
                shp_pth = wd + r'Clemens\data\vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
                shp_pth = r
                ## output raster path
                if attr == 'ID_KTYP': #"ID_KTYP", "ID_WiSo", "ID_HaBl", "Oeko"
                    target_ds_pth = r'Clemens\data\raster\mosaics\CropTypes_{0}_{1}.tif'.format(bl, year)
                elif attr == 'ID_WiSo':
                    target_ds_pth = r'Clemens\data\raster\mosaics\CropTypesWiSu_{0}_{1}.tif'.format(bl,  year)
                elif attr == 'ID_HaBl':
                    target_ds_pth = r'Clemens\data\raster\mosaics\CropTypesLeCe_{0}_{1}.tif'.format(bl,  year)
                else:
                    target_ds_pth = r'raster\mosaics\CropTypes{0}_{1}_{2}.tif'.format(attribute, bl, year)
                vector.rasterizeShape(shp_pth, target_ds_pth, attr, [x_min_ext, x_max_ext, y_min_ext, y_max_ext], res, no_data_val, gdal_dtype=gdal.GDT_Byte)

            if __name__ == '__main__':
                joblib.Parallel(n_jobs=7)(joblib.delayed(workFunc)(year) for year in range(min, max))

    ### Rasterize Field sizes
    # attr_dict = {'BV':"flaeche",
    #              'LS':'AREA',
    #              'SA':'PARZ_FLAE',
    #              'BB':'GROESSE'}
    #
    # attr = attr_dict[bl]
    # res = 5
    # no_data_val = -999
    # for per in per_lst:
    #     min, max = per[0], per[1] + 1
    #
    #     def workFunc(year):
    #         ## open shapefile
    #         shp_pth = r'Clemens\data\vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
    #         target_ds_pth = r'Clemens\data\raster\mosaics\FieldSize_{0}_{1}_test.tif'.format(bl, year)
    #         vector.rasterizeShape(shp_pth, target_ds_pth, attr, [x_min_ext, x_max_ext, y_min_ext, y_max_ext], res,
    #                               no_data_val, gdal_dtype=gdal.GDT_Float32)
    #
    #     if __name__ == '__main__':
    #         joblib.Parallel(n_jobs=1)(joblib.delayed(workFunc)(year) for year in range(min, max))

    # #### Raterize yield values
    # shp_pth = r"Q:\FORLand\Daten\vector\ALKIS\Bodenschätzung_gesamt_BB\bodenschaetzung_bb_gesamt_v2.shp"
    # target_ds_pth = r'Clemens\data\raster\mosaics\Ackerzahl_{0}.tif'.format(bl)
    # attr = 'ACKERZAHLO'
    # res = 5
    # no_data_val = 255
    # vector.rasterizeShape(shp_pth, target_ds_pth, attr, [x_min_ext, x_max_ext, y_min_ext, y_max_ext], res, no_data_val,
    #                       gdal_dtype=gdal.GDT_Byte) # GDT_Float32

    # ## Rasterize Cattle per farm
    # per = per_lst[0]
    # min, max = per[0], per[1] + 1
    # # for attr in ['Cattle','Sheep','Pig']:
    # for year in range(min, max):
    #     def workFunc(attr):
    #         print(attr)
    #         shp_pth = r'Clemens\data\vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
    #         target_ds_pth = r'Clemens\data\raster\mosaics\{0}_{1}_{2}.tif'.format(attr, bl, year)
    #         res = 5
    #         no_data_val = -999
    #         vector.rasterizeShape(shp_pth, target_ds_pth, attr, [x_min_ext, x_max_ext, y_min_ext, y_max_ext], res, no_data_val,
    #                               gdal_dtype=gdal.GDT_Int16) # GDT_Float32
    #
    #         print(attr, 'done!')
    #     if __name__ == '__main__':
    #         joblib.Parallel(n_jobs=3)(joblib.delayed(workFunc)(attr) for attr in ['Cattle','Sheep','Pig'])

print("Script done!")
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

## Get common extent of invekos shapes over the years.
# import gdal
# import math
# x_min_lst = []
# x_max_lst = []
# y_min_lst = []
# y_max_lst = []
### loop over shapefiles and get extent that covers all shapefiles
# for year in range(2005,2019):
#     print('year: {0}'.format(year))
#
#     # shp_pth = wd + r'vector\misc\Inv_NoDups_{0}_testsub.shp'.format(year)
#     shp_pth = wd + r'Inv_NoDups_{}.shp'.format(year)
#     shp = ogr.Open(shp_pth, 0)
#     lyr = shp.GetLayer()
#     x_min_lyr, x_max_lyr, y_min_lyr, y_max_lyr = lyr.GetExtent()
#     x_min_lst.append(x_min_lyr)
#     x_max_lst.append(x_max_lyr)
#     y_min_lst.append(y_min_lyr)
#     y_max_lst.append(y_max_lyr)
#
# x_min_ext = min(x_min_lst)
# x_max_ext = max(x_max_lst)
# y_min_ext = min(y_min_lst)
# y_max_ext = max(y_max_lst)