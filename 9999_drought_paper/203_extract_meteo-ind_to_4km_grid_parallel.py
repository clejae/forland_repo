import ogr
import gdal
import shutil
import time
import joblib
import os
import glob

## CJ REPO
import general

# #### SET TIME-COUNT #### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)

# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

pth_lst1 = glob.glob(r"Q:\FORLand\Clemens\_temp\00_MA\data\climate\SPI\SPI*4km.tif")
pth_lst2 = glob.glob(r"Q:\FORLand\Clemens\_temp\00_MA\data\climate\SPEI\SPEI*4km.tif")
pth_lst = pth_lst1 + pth_lst2
pth_lst = [r"_temp\00_MA\data\4katja\original_data\UFZ\SMI_2018_Gesamtboden_4km.tif"]
pth_lst = [r"_temp\00_MA\data\climate\dwd_evapo_p\time_series\EVAPO_2018_3035_4km.tif",
r"_temp\00_MA\data\climate\dwd_precipitation\RSMS\time_series\RSMS_01-12_2018-2018_3035_4km.tif",
r"_temp\00_MA\data\climate\dwd_temperature\times_series\TEMP_2018_3035_4km.tif"]

## input files
grid_pth = r"_temp\00_MA\data\vector\miscellaneous\4km_grid.shp"
csvt_pth = r"_temp\00_MA\data\vector\lsp_metrics\grid_cells\VPI_2018_4km_BL_2008-2018.csvt"

def workFunc( in_pth): # i is index of cell
    out_pth = r'_temp\\00_MA\data\vector\lsp_metrics\grid_cells\\' + os.path.basename(in_pth)[:-3] + 'csv'
    out_cvst_pth = r'_temp\\00_MA\data\vector\lsp_metrics\grid_cells\\' + os.path.basename(in_pth)[:-3] + 'csvt'

    col_name_lst = ['ID', '_01', '_02', '_03', '_04', '_05', '_06', '_07', '_08', '_09', '_10', '_11', '_12']
    out_lst = [col_name_lst]

    ras = gdal.Open(in_pth)
    arr = ras.ReadAsArray()
    gt = ras.GetGeoTransform()
    n_months = arr.shape[0]

    x_origin = gt[0]
    y_origin = gt[3]
    pixel_width = gt[1]
    pixel_height = -gt[5]

    ## open grid layer
    grid_shp = ogr.Open(grid_pth)
    grid_lyr = grid_shp.GetLayer()

    ## get current grid cell
    for feat in grid_lyr:
        polyid = feat.GetField('POLYID')
        sub_lst = []
        sub_lst.append(polyid)
        geom = feat.GetGeometryRef()
        centroid = geom.Centroid()
        col = int((centroid.GetPoint()[0] - x_origin) / pixel_width)
        row = int((y_origin - centroid.GetPoint()[1]) / pixel_height)
        for month in range(n_months):
            val = arr[month,row,col]
            if val == -32767 or val == -999:
                val = ''
            sub_lst.append(val)
        out_lst.append(sub_lst)
    grid_lyr.ResetReading()

    general.writeListToCSV(out_lst, out_pth)
    shutil.copyfile(csvt_pth, out_cvst_pth)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(in_pth) for in_pth in pth_lst)

# #### END TIME-COUNT AND PRINT TIME STATS #### #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")