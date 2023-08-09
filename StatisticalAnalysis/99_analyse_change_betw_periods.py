# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd
import string

## CJ REPO
import raster

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'

bl_lst = ['BB'] #,'LS', 'BV'
per_lst = ['2005-2011', '2012-2018']
name_lst = ['Brandenburg'] #,'Lower-Saxony', 'Bavaria'

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
bl = 'BB'
per1 = '2005-2011'
per2 = '2012-2018'

#### PART 1: Derive CSTs with largest changes between two periods

## define list of all possible crop sequence types
## these will be the column names
cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
cst_lst.append(255)
cols = [str(i) for i in cst_lst]
cols.insert(0, 'Tile')

## load the data
pth1 = r"tables\crop_sequence_types\{0}\{0}_{1}_AreaOfCropSequenceTypes_clean.xlsx".format(bl, per1)
df_per1 = pd.read_excel(pth1, sheet_name='AreaPerTile')
pth2 = r"tables\crop_sequence_types\{0}\{0}_{1}_AreaOfCropSequenceTypes_clean.xlsx".format(bl, per2)
df_per2 = pd.read_excel(pth2, sheet_name='AreaPerTile')

## period 1
## aggregate the areas over all tiles
df_sum1 = round(df_per1[cols[1:-1]].sum(0), 3)
df_sum1 = pd.DataFrame(df_sum1)
df_sum1.reset_index(inplace=True)
df_sum1.columns = ['CST', 'Area']

## calculate share of all csts
total_area = df_sum1['Area'].sum()
df_sum1['Share'] = round(df_sum1['Area'] / total_area * 100, 5)

## period 2
## aggregate the areas over all tiles,
df_sum2 = round(df_per2[cols[1:-1]].sum(0), 3)
df_sum2 = pd.DataFrame(df_sum2)
df_sum2.reset_index(inplace=True)
df_sum2.columns = ['CST', 'Area']

## calculate share of all csts
total_area = df_sum2['Area'].sum()
df_sum2['Share'] = round(df_sum2['Area'] / total_area * 100, 5)

## calculate changes
df_change = pd.merge(df_sum1, df_sum2, how='inner', on='CST')
df_change.columns = ['cst', 'area_{0}'.format(per1),'share_{0}'.format(per1),'area_{0}'.format(per2),'share_{0}'.format(per2)]
## calculate the change (newer period - older period)
df_change['area_change'] = df_change['area_{0}'.format(per2)] - df_change['area_{0}'.format(per1)]
df_change['share_change'] = df_change['share_{0}'.format(per2)] - df_change['share_{0}'.format(per1)]
# df_change['proportional change'] = (df_change['change in area']/df_change['Area_{0}'.format(per1)])*100

## derive csts with largest changes
df_change = df_change.sort_values(by='share_change', ascending=False)
top_csts = list(df_change[:5]['cst'])
top_csts = [[cst,'increasing'] for cst in top_csts]
df_change = df_change.sort_values(by='share_change', ascending=True)
top_csts = top_csts + [[cst,'decreasing'] for cst in list(df_change[:5]['cst'])]
df_top_csts = pd.DataFrame(top_csts, columns=['CST','Direction'])

#### PART 2: Calculating the change in the area of the top CSTs
df_tiles = pd.DataFrame(df_per1['Tile'])
for cst in cols[1:]:
    df_tiles[cst] = df_per2[cst] - df_per1[cst]

pth = r"tables\crop_sequence_types\{0}\{0}_Change_In_Area_Of_CSTs.xlsx".format(bl)
with pd.ExcelWriter(pth) as writer:
    df_change.to_excel(writer, sheet_name='ChangeTotal', index=False)
    df_tiles.to_excel(writer, sheet_name='ChangePerTile', index=False)
    df_top_csts.to_excel(writer, sheet_name='Top5Changes', index=False)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)

# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
#
# all_dfs = []
# for b,bl in enumerate(bl_lst):
#     df_pth = r"tables\crop_sequence_types\{0}\{0}_CSTArea.xlsx".format(bl)
#     df_lst = []
#
#     ## load cst shares of the specified periods for each federal state into a list
#     for per in per_lst:
#         df = pd.read_excel(df_pth, per)
#         t_area = df['SUM'].sum()
#         for i in range(1, 10):
#             df[str(i)] = round(df[str(i)] / t_area * 100, 2)
#         df_lst.append(df)
#
#     all_dfs.append(df_lst)
#
# ## sum the shares
# sub_types = [str(i) for i in range(1, 10)]
# df_per_new = all_dfs[0][1][sub_types] + all_dfs[1][1][sub_types] + all_dfs[2][1][sub_types]
# df_per_old = all_dfs[0][0][sub_types] + all_dfs[1][0][sub_types] + all_dfs[2][0][sub_types]
#
#
# ## calculate the change (newer period - older period)
#
# df_change = df_lst[1][sub_types] - df_lst[0][sub_types]
#
# ## make change df more readable
# ## add column names and names of main types
# main_types = list(string.ascii_uppercase[:9])
# cols = sub_types.copy()
# cols.insert(0, 'MainType')
# df_change.insert(0, 'MainType', main_types)
# df_change.columns = cols
#
# ## identify largest changes
# ## --> wide to long format, calculate absolute values, sort by absolut values
# df_change = pd.melt(df_change, id_vars=['MainType'], value_vars=sub_types)
# df_change['abs_value'] = abs(df_change['value'])
# df_change = df_change.sort_values(by='abs_value', ascending=False)

#############################################
#
# with open(r'raster\tile_list_BB.txt') as file:
#     tiles_lst = file.readlines()
# tiles_lst = [item.strip() for item in tiles_lst]
#
# per_lst = ['2005-2011', '2012-2018']
#
#
# cst_lst = list(range(11, 100))
# cst_lst.append(2525)
# cols = [str(i) for i in cst_lst]
# cols.insert(0, 'Tile')
#
# df = pd.DataFrame(columns=cols)
#
# for t, tile in enumerate(tiles_lst):
#     print(tile)
#
#     arr1 = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).ReadAsArray()
#     arr1 = arr1 + 0.0
#     arr2 = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[1])).ReadAsArray()
#     arr2 = arr2 + 0.0
#
#     gt = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).GetGeoTransform()
#     pr = gdal.Open('raster\grid_15km\{}\{}_CropSeqType_v2_clean.tif'.format(tile, per_lst[0])).GetProjection()
#     nd_val = 255
#
#     arr1[arr2 == 255] = 255
#     arr2[arr1 == 255] = 255
#     arr1[arr2 == 255] = 255
#     arr2[arr1 == 255] = 255
#
#     ## get the exact difference and the exact concat
#     # diff_arr = arr1 - arr2
#     # diff_arr[arr2 == 255] = 255
#     #
#     # conc_arr = (arr1 * 100) + arr2
#     # conc_arr[arr2 == 255] = 255
#     #
#     # out_pth = 'raster\grid_15km\{}\{}_{}_CropSeqTypeDiff_v2_clean.tif'.format(tile, per_lst[0], per_lst[1])
#     # raster.writeArrayToRaster(diff_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)
#     #
#     # out_pth = 'raster\grid_15km\{}\{}_{}_CropSeqTypeConc_v2_clean.tif'.format(tile, per_lst[0], per_lst[1])
#     # raster.writeArrayToRaster(conc_arr, out_pth, gt, pr, nd_val, gdal.GDT_Int16)
#
#     ## get the changes between main types
#     arr1 = np.floor(arr1/10)
#     arr2 = np.floor(arr2/10)
#     conc_arr = (arr1 * 10) + arr2
#     conc_arr[arr2 == 25] = 255
#     conc_arr = conc_arr.astype(int)
#     uniques, counts = np.unique(conc_arr, return_counts=True)
#     df.at[t, 'Tile'] = tile
#     for c, count in enumerate(counts):
#         area = count * 25
#         col = str(uniques[c])
#         df.at[t, col] = area
#     out_pth = r'tables\CropRotations\seq-diff_grid\{0}_{1}_AreaOfChangeInMainTypes_v2_clean_{2}.csv'.format(per_lst[0],
#                                                                                                             per_lst[1],
#                                                                                                             tile)
#     df.to_csv(out_pth, index=False)
#
#
# df_sum = df[cols[1:-1]].sum(0)
# df_sum = pd.DataFrame(df_sum)
# df_sum.reset_index(inplace=True)
# df_sum.columns = ['CST', 'Area [m²]']
# df_sum['Area [ha]'] = df_sum['Area [m²]']/10000
# # df_sum = df_sum.sort_values(by=['Area'], ascending =False)
#
# with pd.ExcelWriter(r'tables\CropRotations\{0}_{1}_AreaOfChangeInMainTypes_v2_clean.xlsx'.format(per_lst[0],
#                                                                                                  per_lst[1])) as writer:
#     df.to_excel(writer, sheet_name='AreaPerTile', index=False)
#     df_sum.to_excel(writer, sheet_name='AreaAggregated', index=False)
