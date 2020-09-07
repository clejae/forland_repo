import ogr
import gdal
import numpy as np
import time
import threading
import os
import shutil

## CJ REPO
import general

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)

# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
## Input
mask_lst = ["BROADLEAF", "CONIFER"]
year_lst = [2018, 2019]
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## input files
grid_pth = r"_temp\00_MA\data\vector\miscellaneous\4km_grid.shp"
tiles_pth = r'_temp\00_MA\data\vector\miscellaneous\force-tiles_ger_3035.shp'
csvt_pth = r"_temp\00_MA\data\vector\lsp_metrics\grid_cells\VPI_2018_4km_BL_2008-2018.csvt"

def statistics_task(lock, cell_ind): # i is index of cell
    ## open grid layer
    grid_shp = ogr.Open(grid_pth)
    grid_lyr = grid_shp.GetLayer()
    sr = grid_lyr.GetSpatialRef()

    ## open FORCE tile layer
    tiles_shp = ogr.Open(tiles_pth)
    tiles_lyr = tiles_shp.GetLayer()

    ## get current grid cell
    feat = grid_lyr.GetFeature(cell_ind)
    polyid = feat.GetField('POLYID')

    ## filter FORCE tiles by grid cell
    tiles_lyr.SetSpatialFilter(None)
    geom = feat.GetGeometryRef()
    geom_wkt = geom.ExportToWkt()
    tiles_lyr.SetSpatialFilter(geom)

    ## create list of filtered tiles
    tiles_lst = []
    for tile in tiles_lyr:
        tile_name = tile.GetField('Name')
        tiles_lst.append(tile_name)
    tiles_lyr.ResetReading()
    print(polyid, tiles_lst)

    ## create forest mask vrt of the filtered tiles
    vrt_msk_lst = [r'\\141.20.140.222\endor\germany-drought\masks\{0}\2015_MASK_FOREST-{1}_UNDISTURBED-2013_BUFF-01.tif'.format(
        tile, mask
    ) for tile in tiles_lst]
    vrt_msk_pth = r'\\141.20.140.222\endor\germany-drought\vrt\grid_cells\{0}_2015_MASK_FOREST-{1}.vrt'.format(polyid, mask)
    vrt_msk = gdal.BuildVRT(vrt_msk_pth, vrt_msk_lst)
    arr_msk = vrt_msk.ReadAsArray()

    # create memory layer of the current grid cell for rasterization
    driver_mem = ogr.GetDriverByName('Memory')
    ogr_ds = driver_mem.CreateDataSource('wrk')
    ogr_lyr = ogr_ds.CreateLayer('poly', srs=sr)
    feat_mem = ogr.Feature(ogr_lyr.GetLayerDefn())
    feat_mem.SetGeometryDirectly(ogr.Geometry(wkt=geom_wkt))
    ogr_lyr.CreateFeature(feat_mem)

    ## rasterize geom
    col = vrt_msk.RasterXSize
    row = vrt_msk.RasterYSize
    gt = vrt_msk.GetGeoTransform()
    target_ds = gdal.GetDriverByName('MEM').Create('', col, row, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform(gt)
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(-9999)
    gdal.RasterizeLayer(target_ds, [1], ogr_lyr, burn_values=[1])
    arr_geom = target_ds.ReadAsArray()

    ## mask geom with forest mask
    arr_msk_geom = arr_msk * arr_geom

    ## open array that will be aggregated
    file_lst = [
        r'\\141.20.140.222\endor\germany-drought\VCI_VPI\{0}\{1}_BL-2005-2019_VPI.tif'.format(tile, year)
        for tile in tiles_lst]
    vrt_ind_pth = r'_temp\00_MA\data\vrt\grid_cells\VPI\{0}_VPI_{1}_BL-2005-2019.vrt'.format(polyid, year)
    vrt_ind = gdal.BuildVRT(vrt_ind_pth, file_lst)
    arr_ind = vrt_ind.ReadAsArray()
    n_months = arr_ind.shape[0]

    ## aggregate all bands of the input array
    sub_lst = []
    sub_lst.append(polyid)
    for month in range(n_months):
        arr_sub = arr_ind[month, :, :]

        arr_sub = arr_sub + 0.0
        arr_sub[arr_msk_geom == 0] = -32767  # no data value FORCE -32767
        arr_sub[arr_sub == -32767] = np.nan

        mean_st = np.nanmean(arr_sub)
        sub_lst.append(mean_st)

    lock.acquire()
    global out_lst
    out_lst.append(sub_lst)
    lock.release()

    del (vrt_ind)
    del (vrt_msk)

    print(polyid, 'done.')

def main_task(cell_ind_lst):
    lock = threading.Lock()
    thread_lst = []
    for cell_ind in cell_ind_lst:
        t = threading.Thread(target=statistics_task, args=(lock, cell_ind,))
        thread_lst.append(t)
    for thread in thread_lst:
        thread.start()
    for thread in thread_lst:
        thread.join()

col_name_lst = ['ID', '_01', '_02', '_03', '_04', '_05', '_06', '_07', '_08', '_09', '_10', '_11', '_12']
num_threads = 30

grid_shp_outer = ogr.Open(grid_pth)
grid_lyr_outer = grid_shp_outer.GetLayer()
feat_count = grid_lyr_outer.GetFeatureCount()
cell_ind_lst = list(range(feat_count))

lock = threading.Lock()
for mask in mask_lst:
    for year in year_lst:
        global out_lst
        out_lst = [col_name_lst]
        for cell_ind in cell_ind_lst:
            print(mask, year, cell_ind, "/", len(cell_ind_lst))
            statistics_task(lock, cell_ind)
        out_pth = r'_temp\\00_MA\data\vector\lsp_metrics\grid_cells\VPI_{0}_4km_BL_2005-2019.csv'.format(year)
        general.writeListToCSV(out_lst, out_pth)
        shutil.copyfile(csvt_pth, out_pth[:-3] + "csvt")

        # s_tic = time.time()
        #
        # for i in range(0, feat_count, num_threads):
        #     print(cell_ind_lst[i:i + num_threads])
        #     main_task(cell_ind_lst=cell_ind_lst[i:i + num_threads])
        # ## Output
        #
        # del out_lst
        # s_toc = time.time()
        # print('Elapsed time of {0} - {1} is {2:.2f} s'.format(mask, year, s_toc - s_tic))

# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")