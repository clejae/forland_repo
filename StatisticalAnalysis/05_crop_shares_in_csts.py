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

## CJs Repo
import general
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def statistics_task(lock, tile):

    # for t, tile in enumerate(tiles_lst):
    print(tile)

    ## open crop sequence and crop sequence type tiles
    ras_cst = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropSeqType_clean.tif'.format(tile, bl, per))
    arr_cst_bu = ras_cst.ReadAsArray()  # [y1:y2,x1:x2]

    ras_ct = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropTypes.tif'.format(tile, bl, per))
    arr_ct_bu = ras_ct.ReadAsArray()  # [:,y1:y2,x1:x2]

    ## loop over the crop types
    for ct in main_ct:

        ## create a "proportion array" indicating the share of the crop type in the sequence
        arr_ct = arr_ct_bu.copy()
        for band in range(7):
            arr_ct[band, :, :][arr_ct[band, :, :] != ct] = 0
            arr_ct[band, :, :][arr_ct[band, :, :] == ct] = 1

        ## count the occurences of the current ct in each cell
        ## calculate proportion
        arr_ct_sum = np.sum(arr_ct, 0)
        arr_pr = arr_ct_sum / 7

        ## loop over crop sequence type
        for cst in main_csts:
            # print("TILE: {0}, CT: {1}, CST: {2}".format(tile, ct, cst))
            arr_cst = arr_cst_bu.copy()

            ## create a mask array indicating where the current cst is present
            arr_cst[arr_cst != cst] = 0
            arr_cst[arr_cst == cst] = 1

            ## identify cells where current cst is present and where the current crop type is present simultaneously
            arr_pres = np.where(arr_pr > 0, arr_cst, 0)

            ## count the total number of cells where the current cst is present
            ## count number of cells where current cst and the current ct are present
            num_pix_cst = np.sum(arr_cst)
            num_pix_pres = np.sum(arr_pres)

            ## count the occurences of the current ct in the cells of the current cst
            num_occ_ct = np.sum(arr_ct_sum[arr_cst == 1])
            ## calculate the sum of all proportion in the cells of the current cst
            sum_pr = np.sum(arr_pr[arr_cst == 1])

            lock.acquire()
            global out_lst
            out_lst.append([tile, ct, cst, num_pix_cst, num_pix_pres, num_occ_ct, sum_pr])

            lock.release()


def main_task(tiles_lst):

    # creating a lock
    lock = threading.Lock()

    thread_lst = []
    for tile in tiles_lst:
        t = threading.Thread(target=statistics_task, args=(lock, tile,))
        thread_lst.append(t)

    for thread in thread_lst:
        thread.start()

    for thread in thread_lst:
        thread.join()
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl_lst = ['BB','BV','SA','LS']

bl_dict = {'BB':['2005-2011','2008-2014','2012-2018'],
           'SA':['2008-2014','2012-2018'],
           'BV':['2005-2011','2008-2014','2012-2018'],
           'LS':['2012-2018']}
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# ## get all top 10 csts across the federal states
# all_main_csts = []
# for bl in bl_lst:
#     per_lst = bl_dict[bl]
#     for per in per_lst:
#         ## get top 10 of csts of current period
#         main_csts = pd.read_excel(r'data\tables\crop_sequence_types\{0}\{0}_CSTArea2.xlsx'.format(bl),
#                                   sheet_name='Top15CSTs')
#         main_csts = main_csts[main_csts['Period'] == per]
#         main_csts = main_csts[:10]
#         main_csts = list(main_csts['CST'])
#         all_main_csts = all_main_csts + main_csts
# main_csts = list(set(all_main_csts))
#           # old
#           # A3, B2, B3, C5, E2, E4, E5, F2, F4, F5, G5, H2, H4, H5, I5
#           # [13, 22, 23, 35, 52, 54, 55, 62, 64, 65, 75, 82, 84, 85, 95]
#
#           # v1
#           # NS, NS, BB  BB, NS, bo, bo, NS, bo, bo, BB, BB, bo, bo
#           # A3, B3, C2, C4, C5, E4, E5, F2, F4, F5, G5, H4, H5, I5
#           # [13, 23, 32, 34, 35, 54, 55, 62, 64, 65, 75, 84, 85, 95]

#           # v2  - tr=SA+LS+BB, BL=BB+LS, SB=SA+BB
#           # LS, LS, SA, LS, SA, BB, tr, tr, BL, tr, tr, SB, SB, tr, tr
#           # A3, B3, C4, C5, D2, E2, E4, E5, F2, F4, F5, G5, H4, H5, I5
# 13, 23, 34, 35, 42, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
#
#           # Maize, Winter Wheat, Oilseed Rape, Winter Barley, Rye, Fallow
# main_ct = [1, 2, 4, 9, 10, 255]

# for bl in bl_lst:
#
#     with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
#         tiles_lst = file.readlines()
#     tiles_lst = [item.strip() for item in tiles_lst]
#
#     ## get periods for which the csts are available for the current federal state
#     per_lst = bl_dict[bl]
#
#     ## set number of threads for parallization
#     num_threads = 15
#
#     df_area_lst = []
#     df_seq_lst = []
#
#     ## loop over periods
#     for per in per_lst:
#
#         # ## get top 10 of csts of current period
#         # main_csts = pd.read_excel(r'data\tables\crop_sequence_types\{0}\{0}_CSTArea2.xlsx'.format(bl),
#         #                           sheet_name='Top15CSTs')
#         # main_csts = main_csts[main_csts['Period'] == per]
#         # main_csts = main_csts[:10]
#         # main_csts = list(main_csts['CST'])
#         # main_cst = [13, 23, 34, 35, 42, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
#
#         ## define target crop types
#         ## 1-Maize, 2-Winter Wheat, 4-Oilseed Rape, 9-Winter Barley, 10-Rye
#         main_ct = [1, 2, 4, 9, 10, 30, 99]
#
#         ## create a global output list, which will be transformed to output df
#         ## results will be written during parallel processing
#         global out_lst
#         cols = ['Tile', 'CT', 'CST', 'NumPixCST', 'NumPixCTinCST', 'NumOccCTinCST', 'SumProp']
#         out_lst = [cols]
#
#         ## run analysis in parallel over all tiles
#         for i in range(0,len(tiles_lst),num_threads):
#             print(tiles_lst[i:i+num_threads])
#             s_tic = time.time()
#             main_task(tiles_lst=tiles_lst[i:i+num_threads])
#             s_toc = time.time()
#             print('Elapsed time of current bundles of threads {:.2f} s'.format(s_toc - s_tic))
#
#         ## transform output list to output df
#         df = pd.DataFrame(out_lst)
#         df.columns = df.iloc[0]
#         df = df.drop(df.index[0])
#
#         # df = pd.read_excel(r'data\tables\crop_sequence_types\{0}_CropTypesInCST.xlsx'.format(per))
#         # df['Share'] = df['SumProp']/df['NumPixCTinCST']
#
#         ## calculate the total area of a cst
#         df_cst_area = df.groupby(['CT', 'CST'])['NumPixCST'].sum()
#         df_cst_area = df_cst_area.unstack()
#
#         ## calculate the total area of a crop type in a cst
#         df_ct_area = df.groupby(['CT', 'CST'])['NumPixCTinCST'].sum()
#         df_ct_area = df_ct_area.unstack()
#
#         ## calculate the total temporal occurence of a crop type in cst
#         df_ct_occ = df.groupby(['CT', 'CST'])['NumOccCTinCST'].sum()
#         df_ct_occ = df_ct_occ.unstack()
#
#         ## calculate the proportion of the area of a crop type in a cst
#         df_prop_area = df_ct_area / df_cst_area
#
#         ## calculate the proportion of the temporal occurence of a crop type in a cst
#         ## there is a logical mistake in the first calculation, which I can't figure out.
#         # df_prop_seq = df2 / df1
#         df_prop_seq = df_ct_occ / (df_cst_area * 7) #7 because period length is 7
#
#         ## dump into output lists
#         df_area_lst.append(df_prop_area)
#         df_seq_lst.append(df_prop_seq)
#
#     ## write to disc
#     with pd.ExcelWriter(r'data\tables\crop_sequence_types\{0}\{0}_ShareCTinCSTs.xlsx'.format(bl)) as writer:
#         for d, df_area in enumerate(df_area_lst):
#             sheet_name = 'CTShareOfCSTArea_{0}'.format(per_lst[d])
#             df_area.to_excel(writer, sheet_name=sheet_name, index=True)
#         for d, df_seq in enumerate(df_seq_lst):
#             sheet_name = 'CTShareOfCSTSeq_{0}'.format(per_lst[d])
#             df_seq.to_excel(writer, sheet_name=sheet_name, index=True)
#
#     print('\n########', bl, 'done', '#######\n')


#### Brandenburg and Bavaria combined
bl_lst = ['BB','BV']
per_lst = ['2005-2011','2008-2014','2012-2018']

## The then largest CSTs by area
cst_lst = [85,95,65,55,64,75,62,84,23,13] #85,95,62,65,82,42,55,75,23,13,64,33,53,86,56,84,28,54,32]
## The five main crop classes
ct_lst =  ['MA','WW','OR','WB','RY'] #['MA','WW','SB','OR','PO','SC','TR','WB','RY','LE','GR','LE','VE','FA','UN','MC','OT']

out_lst = [['Period','CST','CT','Mean Frequency']]
for per in per_lst:
    df_lst = []
    for bl in bl_lst:
        pth = r"data\tables\FarmSize-CSTs\{0}_{1}_sequences_freq.csv".format(bl, per)
        df = pd.read_csv(pth)
        df_lst.append(df)

    df = pd.concat(df_lst)
    for cst in cst_lst:
        df_sub = df[df['CST']==cst]
        for ct in ct_lst:

            df_sub_ct = df_sub[df_sub['Freq_{0}'.format(ct)] != 0.0]
            mean_freq = df_sub_ct['Freq_{0}'.format(ct)].mean()
            out_lst.append([per, cst, ct, mean_freq])

df = pd.DataFrame(out_lst)
df.columns = df.iloc[0]
df = df.drop(df.index[0])
df['Mean Frequency'] = df['Mean Frequency'].astype(float)

df = df.pivot_table(index="CST",
                    columns=['CT','Period'],
                    values='Mean Frequency',
                    fill_value='nan')

pth = r"Q:\FORLand\Clemens\data\tables\most_common_sequences\10_most_common_sequences_vs_crop_class_frequencies_BB_BV_2.csv"
df.to_csv(pth, index=True)
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