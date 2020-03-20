# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd
## CJ REPO
import raster

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'raster\tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

per_lst = ['2005-2011', '2012-2018']


cst_lst = list(range(11, 100))
cst_lst.append(2525)
cols = [str(i) for i in cst_lst]
cols.insert(0, 'Tile')

df = pd.DataFrame(columns=cols)

for t, tile in enumerate(tiles_lst):
    print(tile)

    arr1 = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).ReadAsArray()
    arr1 = arr1 + 0.0
    arr2 = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[1])).ReadAsArray()
    arr2 = arr2 + 0.0

    gt = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).GetGeoTransform()
    pr = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).GetProjection()
    nd_val = 255

    arr1[arr2 == 255] = 255
    arr2[arr1 == 255] = 255
    arr1[arr2 == 255] = 255
    arr2[arr1 == 255] = 255

    ## get the exact difference and the exact concat
    # diff_arr = arr1 - arr2
    # diff_arr[arr2 == 255] = 255
    #
    # conc_arr = (arr1 * 100) + arr2
    # conc_arr[arr2 == 255] = 255
    #
    # out_pth = 'raster\grid_15km\{}\{}_{}_CropSeqTypeDiff_v2_clean.tif'.format(tile, per_lst[0], per_lst[1])
    # raster.writeArrayToRaster(diff_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)
    #
    # out_pth = 'raster\grid_15km\{}\{}_{}_CropSeqTypeConc_v2_clean.tif'.format(tile, per_lst[0], per_lst[1])
    # raster.writeArrayToRaster(conc_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)

    ## get the changes between main types
    arr1 = np.floor(arr1/10)
    arr2 = np.floor(arr2/10)
    conc_arr = (arr1 * 10) + arr2
    conc_arr[arr2 == 25] = 255
    conc_arr = conc_arr.astype(int)
    uniques, counts = np.unique(conc_arr, return_counts=True)
    df.at[t, 'Tile'] = tile
    for c, count in enumerate(counts):
        area = count * 25
        col = str(uniques[c])
        df.at[t, col] = area
    out_pth = r'tables\CropRotations\seq-diff_grid\{0}_{1}_AreaOfChangeInMainTypes_v2_clean_{2}.csv'.format(per_lst[0],
                                                                                                            per_lst[1],
                                                                                                            tile)
    df.to_csv(out_pth, index=False)


df_sum = df[cols[1:-1]].sum(0)
df_sum = pd.DataFrame(df_sum)
df_sum.reset_index(inplace=True)
df_sum.columns = ['CST', 'Area [m²]']
df_sum['Area [ha]'] = df_sum['Area [m²]']/10000
# df_sum = df_sum.sort_values(by=['Area'], ascending =False)

with pd.ExcelWriter(r'tables\CropRotations\{0}_{1}_AreaOfChangeInMainTypes_v2_clean.xlsx'.format(per_lst[0],
                                                                                                 per_lst[1])) as writer:
    df.to_excel(writer, sheet_name='AreaPerTile', index=False)
    df_sum.to_excel(writer, sheet_name='AreaAggregated', index=False)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


