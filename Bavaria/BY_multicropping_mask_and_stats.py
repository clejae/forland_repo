# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import joblib
import pandas as pd

## OWN REPOSITORY
import raster

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'BY'

min_year = 2012
max_year = 2018
year_range = range(min_year, max_year + 1)

per = '{0}-{1}'.format(min_year, max_year)

with open(r'raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

def workFunc(tile):
    print(tile)

    ras_ct_lst = [r'raster\grid_15km\{0}\{1}_CropTypes_{2}.tif'.format(tile, bl, year) for year in year_range]
    ras_ct_lst = raster.openRasterFromList(ras_ct_lst)


    out_pth_ct = r'raster\grid_15km\{0}\{1}_{2}_CropTypes.tif'.format(tile, bl, per)
    if os.path.exists(out_pth_ct) == False:
        raster.stackRasterFromList(ras_ct_lst, out_pth_ct, data_type=gdal.GDT_Int16)

    print(tile, "Cleaning")
    ## open rasterized kulturtyp raster
    ras = gdal.Open(out_pth_ct)
    arr = ras.ReadAsArray()

    ## get some arr attributes
    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()
    no_data_value = ras.GetRasterBand(1).GetNoDataValue()
    bands = arr.shape[0]

    #### create a mask array to clean kulturtyp raster in a later step
    ## where 0 indicates time series with more than 2 times of fallow land, grassland, unknown etc.
    ## loop over the years and set all respective classes to no data value
    ## set also class 60 (vegetables) to a lower value
    arr_copy = arr.copy()
    for b in range(bands):
        arr_copy[b, :, :][arr_copy[b, :, :] != 70] = 0
        arr_copy[b, :, :][arr_copy[b, :, :] == 70] = 1

    arr_mask = np.sum(arr_copy, axis=0)

    raster.writeArrayToRaster(arr_mask, r'raster\grid_15km\{0}\{1}_{2}_Multicropping.tif'.format(tile, bl, per), gt, pr,
                             no_data_value, type_code=gdal.GDT_Byte)

# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=15)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)

cols = ['Tile','0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']
df = pd.DataFrame(columns=cols)

for t, tile in enumerate(tiles_lst):

    print(tile, t, 'of', len(tiles_lst))

    pth = r'raster\grid_15km\{0}\{1}_{2}_Multicropping.tif'.format(tile, bl, per)
    ras = gdal.Open(pth)
    arr = ras.ReadAsArray()

    uniques, counts = np.unique(arr, return_counts=True)

    df.at[t, 'Tile'] = tile
    for c, count in enumerate(counts):
        area = count * 25
        col = str(uniques[c])
        df.at[t, col] = area

df.to_csv(r"tables\InVekos\area_stats\mulitcrop_area_stats_{}_{}_v2.csv".format(bl, per), index=False)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# -----------------------