# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd
import joblib
# import matplotlib.pyplot as plt
import threading

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'LS'
per_lst = ['2012-2018']
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

#################### Crop Type Analysis
cols = ['Tile','1','2','3','4','5','6','7','9','10','12','13','60','70','30','80','99','255']
df_lst = []

# for year in range(2005,2020):
def workFunc(year):
    df = pd.DataFrame(columns=cols)
    for t, tile in enumerate(tiles_lst):
        print(year,tile)
        ras = gdal.Open(r'data\raster\grid_15km\{0}\{1}_CropTypes_{2}.tif'.format(tile, bl, year))
        arr = ras.ReadAsArray()
        arr[ :, :][arr[ :, :] == 14] = 12

        ndval = ras.GetRasterBand(1).GetNoDataValue()

        uniques, counts = np.unique(arr, return_counts=True)

        df.at[t, 'Tile'] = tile
        for c, count in enumerate(counts):
            area = count * 25
            col = str(uniques[c])
            df.at[t, col] = area
    # df_lst.append(df)
    df.to_csv(r"data\tables\InVekos\area_stats\crop_area_stats_{}_{}.csv".format(bl, year), index=False)

if __name__ == '__main__':
    joblib.Parallel(n_jobs=15)(joblib.delayed(workFunc)(year) for year in range(2015,2016))

df_lst = [pd.read_csv(r"data\tables\InVekos\area_stats\crop_area_stats_{}_{}.csv".format(bl, year)) for year in range(2005,2019)]

df_sum_lst = []
for i, df in enumerate(df_lst):
    df_sum = df[cols[1:-1]].sum(0)
    df_sum = pd.DataFrame(df_sum).transpose()
    df_sum = df_sum.rename(index = {0:i+2005})
    df_sum_lst.append(df_sum)
df_sum = pd.concat(df_sum_lst)

df_sum = df_sum / 10000
df_sum.to_excel(r'data\tables\CropRotations\{}_2005-2018_AreaOfCropTypes_ha.xlsx'.format(bl))
df_prop = df_sum.transpose() / df_sum.sum(1) * 100
df_prop = df_prop.transpose()
df_prop.to_excel(r'data\tables\CropRotations\{}_2005-2018_AreaOfCropTypes.xlsx'.format(bl))


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
