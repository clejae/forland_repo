# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'BB'
per = '2005-2011'
strata = [0, 1]
out_name = '{0}_{1}_AreaOfCSTOeko_v2_clean'.format(bl, per)
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

## Define columns of output dataframe
cst_lst = [(10 * j) + i for j in range(1, 10) for i in range(1, 10)]
cst_lst.append(255)
cols = [str(i) for i in cst_lst]
# cols.insert(0, 'Stratum')
cols.insert(0, 'Tile')

## Since multiple strata are analysed, they will be dumped into a list
df_lst = []

## All further analysis will also be calculated in the loop and dumped into another list
sheet_lst = []

t = 0
tile = tiles_lst[t]
for cl in strata:
    df = pd.DataFrame(columns=cols)
    for t, tile in enumerate(tiles_lst):
    # def workFunc(tile):
        print(tile)

        ## Open stratum raster and cst raster
        msk_pth = r'data\raster\grid_15km\{}\{}_OekoMask_{}.tif'.format(tile, bl, per)
        msk_ras = gdal.Open(msk_pth)
        msk_arr = msk_ras.ReadAsArray()
        nd_val = msk_ras.GetRasterBand(1).GetNoDataValue()

        cst_pth = r'data\raster\grid_15km\{}\{}_{}_CropSeqType_v2_clean.tif'.format(tile, bl, per)
        cst_ras = gdal.Open(cst_pth)
        cst_arr = cst_ras.ReadAsArray()

        ## create mask for current stratum
        msk = msk_arr.copy()
        msk[msk != cl] = nd_val
        msk[msk == cl] = 1
        msk[msk == nd_val] = 0

        ## mask values out that do not fall into current stratum
        curr_cst_arr = cst_arr.copy()
        curr_cst_arr = curr_cst_arr * msk

        ## Analyze distribution
        uniques, counts= np.unique(curr_cst_arr, return_counts=True)

        df.at[t, 'Tile'] = tile
        # df.at[t, 'Stratum'] = cl
        for c, count in enumerate(counts):
            area = count * .0025
            col = str(uniques[c])
            df.at[t, col] = area

        print(tile, cl, "done")

    ## Aggregate over tiles
    df_agg = df[cols[1:-1]].sum(0)
    df_agg = pd.DataFrame(df_agg)
    df_agg.reset_index(inplace=True)
    df_agg.columns = ['CST', 'Area']
    df_agg['Stratum'] = cl
    df_lst.append(df_agg)

    ## Perform analysis on aggregated df
    columns = ['MainType','1','2','3','4','5','6','7','8','9','SUM']
    indeces = ['A','B','C','D','E','F','G','H','I','SUM']
    df_sum = pd.DataFrame(columns=columns)
    for r, i in enumerate(range(0,80,9)):
        print(i, i+9)
        sl = list(df_agg['Area'][i : i+9])
        sl.append(sum(sl))
        row = indeces[r]
        sl.insert(0, row)
        print(sl)
        # pd.concat([df_sum, sl], axis=0)
        # df_sum.append(sl)
        df_sum.loc[r] = sl
    sheet_lst.append(df_sum)

sheet1 = pd.concat(df_lst)

with pd.ExcelWriter(r'data\tables\CropRotations\{0}.xlsx'.format(out_name)) as writer:
    sheet1.to_excel(writer, sheet_name='AreaAggregated', index=False)
    for s, sheet in enumerate(sheet_lst):
        cl = strata[s]
        sheet.to_excel(writer, sheet_name='Collapsed' + str(cl), index=False)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


