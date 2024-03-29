# Clemens Jänicke
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
# cols = ['Tile','1','2','3','4','5','6','7','9','10','12','13','60','70','30','80','99','255']
# df_lst = []
#
# # for year in range(2005,2020):
# def workFunc(year):
#     df = pd.DataFrame(columns=cols)
#     for t, tile in enumerate(tiles_lst):
#         print(year,tile)
#         ras = gdal.Open(r'data\raster\grid_15km\{0}\{1}_CropTypes_{2}.tif'.format(tile, bl, year))
#         arr = ras.ReadAsArray()
#         arr[ :, :][arr[ :, :] == 14] = 12
#
#         ndval = ras.GetRasterBand(1).GetNoDataValue()
#
#         uniques, counts = np.unique(arr, return_counts=True)
#
#         df.at[t, 'Tile'] = tile
#         for c, count in enumerate(counts):
#             area = count * 25
#             col = str(uniques[c])
#             df.at[t, col] = area
#     # df_lst.append(df)
#     df.to_csv(r"data\tables\InVekos\area_stats\crop_area_stats_{}_{}.csv".format(bl, year), index=False)
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=15)(joblib.delayed(workFunc)(year) for year in range(2015,2016))
#
# df_lst = [pd.read_csv(r"data\tables\InVekos\area_stats\crop_area_stats_{}_{}.csv".format(bl, year)) for year in range(2005,2019)]
#
# df_sum_lst = []
# for i, df in enumerate(df_lst):
#     df_sum = df[cols[1:-1]].sum(0)
#     df_sum = pd.DataFrame(df_sum).transpose()
#     df_sum = df_sum.rename(index = {0:i+2005})
#     df_sum_lst.append(df_sum)
# df_sum = pd.concat(df_sum_lst)
#
# df_sum = df_sum / 10000
# df_sum.to_excel(r'data\tables\CropRotations\{}_2005-2018_AreaOfCropTypes_ha.xlsx'.format(bl))
# df_prop = df_sum.transpose() / df_sum.sum(1) * 100
# df_prop = df_prop.transpose()
# df_prop.to_excel(r'data\tables\CropRotations\{}_2005-2018_AreaOfCropTypes.xlsx'.format(bl))

# ##################### Crop Sequence Type Analysis


df_lst = []
per_df_lst = []

for per in per_lst:
    print('\n########', per, '#######\n')
    cst_lst = [i+j for i in range(10,100,10) for j in range(1,10)]
    cst_lst.append(255)

    cols = [str(i) for i in cst_lst]
    cols.insert(0, 'Tile')

    df = pd.DataFrame(columns=cols)

    for t, tile in enumerate(tiles_lst):
        print(tile, t, 'of', len(tiles_lst))
        ras = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropSeqType_clean.tif'.format(tile, bl, per))
        arr = ras.ReadAsArray()

        ndval = ras.GetRasterBand(1).GetNoDataValue()

        uniques, counts= np.unique(arr, return_counts=True)

        df.at[t, 'Tile'] = tile
        for c, count in enumerate(counts):
            area = count * .0025
            col = str(uniques[c])
            df.at[t, col] = area

    # df_bu = df.copy()
    # df = df_bu.copy()
    # df = df.dropna(axis=1, how='all')

    df_sum = df[cols[1:-1]].sum(0)
    df_sum = pd.DataFrame(df_sum)
    df_sum.reset_index(inplace=True)
    df_sum.columns = ['CST', 'Area']
    df_sum['Period'] = per
    df_lst.append(df_sum)

    ## Perform analysis on aggregated df
    columns = ['MainType', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SUM']
    indeces = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'SUM']
    df_per = pd.DataFrame(columns=columns)

    for r, i in enumerate(range(0, 80, 9)):
        print(i, i + 9)
        sl = list(df_sum['Area'][i: i + 9])
        sl.append(sum(sl))
        row = indeces[r]
        sl.insert(0, row)
        print(sl)
        # pd.concat([df_sum, sl], axis=0)
        # df_sum.append(sl)
        df_per.loc[r] = sl
    per_df_lst.append(df_per)

df_area_aggr = pd.concat(df_lst)
with pd.ExcelWriter(r'data\tables\CropRotations\{0}\{0}_CSTArea.xlsx'.format(bl)) as writer:
    df_area_aggr.to_excel(writer, sheet_name='AreaAggregated', index=False)
    for s, sheet in enumerate(per_df_lst):
        sheet_name = per_lst[s]
        sheet.to_excel(writer, sheet_name = sheet_name, index=False)

# ##################### Share of Crops in CST PARALLEL
#
# print('\n######## Share of Crops in CST PARALLEL ########\n')
#
# tic = time.time()
#
# def statistics_task(lock, tile):
#
#     # for t, tile in enumerate(tiles_lst):
#     print(tile)
#
#     ## open tile crop sequence and crop sequence type
#     ras_cst = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropSeqType_v2_clean.tif'.format(tile, bl, per))
#     arr_cst_bu = ras_cst.ReadAsArray()  # [y1:y2,x1:x2]
#
#     ras_ct = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropTypes.tif'.format(tile, bl, per))
#     arr_ct_bu = ras_ct.ReadAsArray()  # [:,y1:y2,x1:x2]
#
#     ## loop over the crop types
#     for ct in main_ct:
#
#         ## create a "proportion array" indicating the share of the crop type in the sequence
#         arr_ct = arr_ct_bu.copy()
#         for band in range(7):
#             arr_ct[band, :, :][arr_ct[band, :, :] != ct] = 0
#             arr_ct[band, :, :][arr_ct[band, :, :] == ct] = 1
#
#         ## count the occurences of the current ct in each cell
#         ## calculate proportion
#         arr_ct_sum = np.sum(arr_ct, 0)
#         arr_pr = arr_ct_sum / 7
#
#         ## loop over crop sequence type
#         for cst in main_cst:
#             # print("TILE: {0}, CT: {1}, CST: {2}".format(tile, ct, cst))
#             arr_cst = arr_cst_bu.copy()
#
#             ## create a mask array indicating where the current cst is present
#             arr_cst[arr_cst != cst] = 0
#             arr_cst[arr_cst == cst] = 1
#
#             ## identify cells where current cst is present and where the current crop type is present simultaneously
#             arr_pres = np.where(arr_pr > 0, arr_cst, 0)
#
#             ## count the total number of cells where the current cst is present
#             ## count number of cells where current cst and the current ct are present
#             num_pix_cst = np.sum(arr_cst)
#             num_pix_pres = np.sum(arr_pres)
#
#             ## count the occurences of the current ct in the cells of the current cst
#             num_occ_ct = np.sum(arr_ct_sum[arr_cst == 1])
#             ## calculate the sum of all proportion in the cells of the current cst
#             sum_pr = np.sum(arr_pr[arr_cst == 1])
#
#             lock.acquire()
#             global out_lst
#             out_lst.append([tile, ct, cst, num_pix_cst, num_pix_pres, num_occ_ct, sum_pr])
#
#             lock.release()
#
# def main_task(tiles_lst):
#
#     # creating a lock
#     lock = threading.Lock()
#
#     thread_lst = []
#     for tile in tiles_lst:
#         t = threading.Thread(target=statistics_task, args=(lock, tile,))
#         thread_lst.append(t)
#
#     for thread in thread_lst:
#         thread.start()
#
#     for thread in thread_lst:
#         thread.join()
#
# #           # old
# #           # A3, B2, B3, C5, E2, E4, E5, F2, F4, F5, G5, H2, H4, H5, I5
# #           # [13, 22, 23, 35, 52, 54, 55, 62, 64, 65, 75, 82, 84, 85, 95]
# #
# #           # v1
# #           # NS, NS, BB  BB, NS, bo, bo, NS, bo, bo, BB, BB, bo, bo
# #           # A3, B3, C2, C4, C5, E4, E5, F2, F4, F5, G5, H4, H5, I5
# #           # [13, 23, 32, 34, 35, 54, 55, 62, 64, 65, 75, 84, 85, 95]
#
# #           # v2  - tr=SA+LS+BB, BL=BB+LS, SB=SA+BB
# #           # LS, LS, SA, LS, SA, BB, tr, tr, BL, tr, tr, SB, SB, tr, tr
# #           # A3, B3, C4, C5, D2, E2, E4, E5, F2, F4, F5, G5, H4, H5, I5
#             # 13, 23, 34, 35, 42, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
# #
# #           # Maize, Winter Wheat, Oilseed Rape, Winter Barley, Rye, Fallow
# # main_ct = [1, 2, 4, 9, 10, 255]
#
# main_cst = [13, 23, 34, 35, 42, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
#
# # Maize, Winter Wheat, Oilseed Rape, Winter Barley, Rye
# main_ct = [1, 2, 4, 9, 10, 30, 80, 99, 255]
#
# cols = ['Tile', 'CT', 'CST', 'NumPixCST', 'NumPixCTinCST', 'NumOccCTinCST', 'SumProp']
#
# global out_lst
# out_lst = [cols]
#
# num_threads = 15
#
# for per in ['2012-2018']:
#     for i in range(0,len(tiles_lst),num_threads):
#         print(tiles_lst[i:i+num_threads])
#         s_tic = time.time()
#         main_task(tiles_lst=tiles_lst[i:i+num_threads])
#         s_toc = time.time()
#         print('Elapsed time of current bundles of threads {:.2f} s'.format(s_toc - s_tic))
#
#     df = pd.DataFrame(out_lst)
#     df.columns = df.iloc[0]
#     df = df.drop(df.index[0])
#
#     df.to_excel(r'data\tables\CropRotations\{0}_{1}_CropTypesInCST_v2_clean.xlsx'.format(bl, per))
#
#     # df = pd.read_excel(r'data\tables\CropRotations\{0}_CropTypesInCST.xlsx'.format(per))
#     # df['Share'] = df['SumProp']/df['NumPixCTinCST']
#
#     df1 = df.groupby(['CT', 'CST'])['NumPixCTinCST'].sum()
#     df1 = df1.unstack()
#
#     # df2 = df.groupby(['CT','CST'])['SumProp'].sum()
#     # df2 = df2.unstack()
#
#     df3 = df.groupby(['CT', 'CST'])['NumPixCST'].sum()
#     df3 = df3.unstack()
#
#     df4 = df.groupby(['CT', 'CST'])['NumOccCTinCST'].sum()
#     df4 = df4.unstack()
#
#     df_prop_area = df1 / df3
#
#     ## there is a logical mistake in the first calculation, which I can't figure out.
#     # df_prop_seq = df2 / df1
#     df_prop_seq = df4 / (df3 * 7)
#
#     # df_prop_seq.sum(0)
#     with pd.ExcelWriter(r'data\tables\CropRotations\{0}_{1}_ShareOfCropTypesInCropSequences_v2_clean.xlsx'.format(bl, per)) as writer:
#         df_prop_area.to_excel(writer, sheet_name='PropOfAreaInCST', index=True)
#         df_prop_seq.to_excel(writer, sheet_name='PropOfOccInCST', index=True)
#
#     toc = time.time()
#
# print('Elapsed time in parallel {:.2f} s'.format(toc- tic))
# ## 15 threads: 2316 sec

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

## Reorder columns in pandas dataframe
# cols = df.columns.tolist()
# cols = cols[-1:] + cols[:-1]
# cols = cols[:-2] + cols[-1:] + cols[-2:-1]
# df = df[cols]

## Plotting of share of crop types over time
# ax = df_prop[:7].plot.line()
# ax.legend(loc='lower left', bbox_to_anchor= (1.01, 0.0), ncol=1,borderaxespad=0, frameon=False)
# ax.set_xlim(left=2005, right=2012)
#
# labels = df_prop.loc[2011] - df_prop.loc[2005]
#
# y_coords = list(df_prop.loc[2011])
#
# x_coords = [2011.1] * len(y_coords)
# for i in range(0, 16, 2):
#     x_coords[i] = x_coords[i] + 0.5
# for i, xy in enumerate(zip(x_coords,y_coords)):
#     ax.annotate(round(labels[i],1), xy = xy)

# ##################### Share of Crops in CST
# tic = time.time()
#           # old
#           # A3, B2, B3, C5, E2, E4, E5, F2, F4, F5, G5, H2, H4, H5, I5
#           # [13, 22, 23, 35, 52, 54, 55, 62, 64, 65, 75, 82, 84, 85, 95]
#
#           # v1
#           # NS, NS, BB  BB, NS, bo, bo, NS, bo, bo, BB, BB, bo, bo
#           # A3, B3, C2, C4, C5, E4, E5, F2, F4, F5, G5, H4, H5, I5
#           # 13, 23, 32, 34, 35, 54, 55, 62, 64, 65, 75, 84, 85, 95
#
#           # v2
#           # NS, NS, NS, BB, bo, bo, bo, bo, bo, BB, BB, bo, bo
#           # A3, B3, C5, E2, E4, E5, F2, F4, F5, G5, H4, H5, I5
# main_cst = [13, 23, 35, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
#
#           # Maize, Winter Wheat, Oilseed Rape, Winter Barley, Rye
# main_ct = [1, 2, 4, 9, 10, 255]
#
# cols = ['Tile', 'CT', 'CST', 'NumPixCST', 'NumPixCTinCST', 'NumOccCTinCST', 'SumProp']
#
# df = pd.DataFrame(columns=cols)
#
# # tile = 'X06_Y08'
# # main_cst = [55,65,75,85]
# # main_ct = [1,4,10,7,12]
# # y1 = 2943
# # y2 = 2951
# # x1 = 1720
# # x2 = 1723
#
# ## crop proportion per sequence list
# r = 0
#
# lt = len(tiles_lst)
# for t, tile in enumerate(tiles_lst):
#     print(t, lt, tile)
#
#     ## open tile crop sequence and crop sequence type
#     ras_cst = gdal.Open(r'data\raster\grid_15km\{0}\{1}_CropSeqType_v2.tif'.format(tile, per))
#     arr_cst_bu = ras_cst.ReadAsArray()#[y1:y2,x1:x2]
#
#     ras_ct = gdal.Open(r'data\raster\grid_15km\{0}\{1}_CropTypes.tif'.format(tile, per))
#     arr_ct_bu =ras_ct.ReadAsArray()#[:,y1:y2,x1:x2]
#
#     bands = arr_ct_bu.shape[0]
#     for b in range(bands):
#         arr_ct_bu[b, :, :][arr_ct_bu[b, :, :] == 30] = 255
#         arr_ct_bu[b, :, :][arr_ct_bu[b, :, :] == 80] = 255
#         arr_ct_bu[b, :, :][arr_ct_bu[b, :, :] == 99] = 255
#
#     # ct = 1
#     # cst = 55
#
#     ## loop over the crop types
#     for ct in main_ct:
#
#         ## create a "proportion array" indicating the share of the crop type in the sequence
#         arr_ct = arr_ct_bu.copy()
#         for band in range(7):
#             arr_ct[band, :, :][arr_ct[band, :, :] != ct] = 0
#             arr_ct[band, :, :][arr_ct[band, :, :] == ct] = 1
#
#         ## count the occurences of the current ct in each cell
#         ## calculate proportion
#         arr_ct_sum = np.sum(arr_ct, 0)
#         arr_pr = arr_ct_sum / 7
#
#         ## loop over crop sequence type
#         for cst in main_cst:
#
#             # print("TILE: {0}, CT: {1}, CST: {2}".format(tile, ct, cst))
#             arr_cst = arr_cst_bu.copy()
#
#             ## create a mask array indicating where the current cst is present
#             arr_cst[arr_cst != cst] = 0
#             arr_cst[arr_cst == cst] = 1
#
#             ## identify cells where current cst is present and where, at the same time, the current crop type is present
#             arr_pres = np.where(arr_pr > 0, arr_cst, 0)
#
#             ## count the total number of cells where the current cst is present
#             ## count number of cells where current cst and the current ct are present
#             num_pix_cst = np.sum(arr_cst)
#             num_pix_pres = np.sum(arr_pres)
#
#             ## count the occurences of the current ct in the cells of the current cst
#             num_occ_ct = np.sum(arr_ct_sum[arr_cst == 1])
#             ## calculate the sum of all proportion in the cells of the current cst
#             sum_pr = np.sum(arr_pr[arr_cst == 1])
#
#             ##cols = ['Tile','CT','CST','NumPixCST','NumPixCTinCST','NumOccCTinCST','SumProp']
#             df.at[r, 'Tile'] = tile
#             df.at[r, 'CT'] = ct
#             df.at[r, 'CST'] = cst
#             df.at[r, 'NumPixCST'] = num_pix_cst
#             df.at[r, 'NumPixCTinCST'] = num_pix_pres
#             df.at[r, 'NumOccCTinCST'] = num_occ_ct
#             df.at[r, 'SumProp'] = sum_pr
#
#             r += 1
#
# toc = time.time()
#
# print('Elapsed time in loop {:.2f} s'.format(toc- tic))
# ## 4921 sec
#
# df.to_excel(r'data\tables\CropRotations\{0}_CropTypesInCST_v2.xlsx'.format(per))
#
# # df = pd.read_excel(r'data\tables\CropRotations\{0}_CropTypesInCST.xlsx'.format(per))
# # df['Share'] = df['SumProp']/df['NumPixCTinCST']
#
# df1 = df.groupby(['CT','CST'])['NumPixCTinCST'].sum()
# df1 = df1.unstack()
#
# # df2 = df.groupby(['CT','CST'])['SumProp'].sum()
# # df2 = df2.unstack()
#
# df3 = df.groupby(['CT','CST'])['NumPixCST'].sum()
# df3 = df3.unstack()
#
# df4 = df.groupby(['CT','CST'])['NumOccCTinCST'].sum()
# df4 = df4.unstack()
#
# df_prop_area = df1 / df3
#
# ## there is a logical mistake in the first calculation, which I can't figure out.
# # df_prop_seq = df2 / df1
# df_prop_seq = df4 / (df3 * 7)
#
# # df_prop_seq.sum(0)
#
# with pd.ExcelWriter(r'data\tables\CropRotations\{0}_ShareOfCropTypesInCropSequences.xlsx'.format(per)) as writer:
#     df_prop_area.to_excel(writer, sheet_name='PropOfAreaInCST', index=True)
#     df_prop_seq.to_excel(writer, sheet_name='PropOfOccInCST', index=True)