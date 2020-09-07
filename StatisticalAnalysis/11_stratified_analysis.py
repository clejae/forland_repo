# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)
bl_lst = ['LS','BB']#,'SA','BV','LS']

# for bl in bl_lst:
def workFunc(bl):
    print(bl)
    per = '2012-2018'

    ## Cattle
    # strata = [[0, 1], [1, 100], [100, 20000]] # Cattle
    # out_name = '{0}_{1}_CSTArea-CattleNumbers'.format(bl, per)

    ## Pig
    strata = [[0, 1], [1, 1000], [1000, 25000]] # Pig
    out_name = '{0}_{1}_CSTArea-PigNumbers'.format(bl, per)

    ## Organic vs conventional
    # strata = [[0, 1],[1, 7],[7, 8]]
    # strata= [[0, 1],[1, 4],[4, 8]]
    # out_name = '{0}_{1}_CSTArea-Oeko'.format(bl, per)

    ## Field sizes
    # strata = [[0,25],[25,50],[50,100],[100,250],[250,500],[500,1000],[1000,2000],[2000,4000],[4000,6000]]
    # out_name = '{0}_{1}_CSTArea-FieldSize_BMEL'.format(bl, per)

   # ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#

    with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
        tiles_lst = file.readlines()
    tiles_lst = [item.strip() for item in tiles_lst]

    ## Define columns of output dataframe
    cst_lst = [i+j for i in range(10,100,10) for j in range(1,10)]
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
            # msk_pth = r'data\raster\grid_15km\{0}\{1}_FieldSize_2018.tif'.format(tile, bl)
            # msk_pth = r'data\raster\grid_15km\{0}\{1}_OekoMaskSum_2015-2018.tif'.format(tile, bl)  ## change years BB/LS
            # msk_pth = r'data\raster\grid_15km\{0}\{1}_Cattle_2018.tif'.format(tile, bl)
            msk_pth = r'data\raster\grid_15km\{0}\{1}_Pig_2018.tif'.format(tile, bl)

            ## r'data\raster\grid_15km\{}\{}_OekoMask_{}.tif'.format(tile, bl, per)
            msk_ras = gdal.Open(msk_pth)
            msk_arr = msk_ras.ReadAsArray()
            nd_val = msk_ras.GetRasterBand(1).GetNoDataValue()

            cst_pth = r'data\raster\grid_15km\{}\{}_{}_CropSeqType_clean.tif'.format(tile, bl, per)
            cst_ras = gdal.Open(cst_pth)
            cst_arr = cst_ras.ReadAsArray()

            ## create mask for current stratum
            msk = msk_arr.copy()
            ## farm sizes
            min_val = cl[0]
            max_val = cl[1]
            msk[msk == nd_val] = -255
            ## 2030,2488
            msk = np.where(np.logical_or(msk < min_val, msk >= max_val), 0, 1)
            # ## oeko
            # msk[msk != cl] = nd_val
            # msk[msk == cl] = 1
            # msk[msk == nd_val] = 0

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
        df_agg['Stratum'] = '>={}<{}'.format(min_val, max_val)
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

    df_area_aggr = pd.concat(df_lst)

    with pd.ExcelWriter(r'data\tables\CropRotations\{0}\{1}.xlsx'.format(bl,out_name)) as writer:
        df_area_aggr.to_excel(writer, sheet_name='AreaAggregated', index=False)
        for s, sheet in enumerate(sheet_lst):
            min_val = strata[s][0]
            max_val = strata[s][1]
            sheet_name = 'Collapsed>={}<{}'.format(min_val, max_val) #strata[s]
            sheet.to_excel(writer, sheet_name=sheet_name, index=False)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=4)(joblib.delayed(workFunc)(bl) for bl in bl_lst)

# ## Create stacked bar graphs
# sheet1['MainType'] = sheet1.CST.str.slice(0, 1)
# sheet1['SubType'] = sheet1.CST.str.slice(1, 3)
#
# c = ["blue", "purple", "red", "green", "pink","black","white","grey","brown"]
# for i, g in enumerate(sheet1.groupby("SubType")):
#     ax = sns.barplot(data=g[1],
#                      x="MainType",
#                      y="Area",
#                      hue="Stratum",
#                      color=c[i],
#                      zorder=-i, # so first bars stay on top
#                      edgecolor="k")
# ax.legend_.remove() # remove the redundant legends
#
# p1 = plt.bar(sheet1['MainType'], sheet1['SubType'][sheet1['Stratum']=='>=0<532'], 0.35)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


