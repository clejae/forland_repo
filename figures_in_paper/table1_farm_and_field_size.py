# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import vector
import ogr
import pandas as pd
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'Q:\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl_lst = ['SA','BB','BV','LS']
# fname_dict = {'BB':['BNR_ZD','GROESSE'],
#               'SA':['btnr','PARZ_FLAE'],
#               'LS':['REGISTRIER','AREA_ha'],
#               'BV':['bnrhash','flaeche']}
#
# col_names = ['Betrieb','Area','BL']
# df_lst = [col_names]
# for bl in bl_lst:
#     print(bl)
#     pth = r'vector\IACS\{0}\IACS_{0}_2018.shp'.format(bl)
#     shp = ogr.Open(pth)
#     lyr = shp.GetLayer()
#     # vector.printFieldNames(lyr)
#     lst = []
#
#     fname_btr = fname_dict[bl][0]
#     fname_area = fname_dict[bl][1]
#     for feat in lyr:
#         betr = str(feat.GetField(fname_btr))
#         area = float(feat.GetField(fname_area))
#         lst.append([betr, area, bl])
#     lyr.ResetReading()
#
#     df = pd.DataFrame(lst)
#     df.columns = col_names
#     df2 = df.groupby(['Betrieb', 'BL'])[['Area']].sum()
#     df2 = df2.reset_index()
#
#     df_lst.append(df)
#     df_lst.append(df2)
#     # df_pth = r'tables\FarmSizes\{0}_farm_and_field_sizes_2018.xlsx'.format(bl)
#     # with pd.ExcelWriter(df_pth) as writer:
#     #     df.to_excel(writer, sheet_name ='{0}_2018_FieldSizes'.format(bl), index=False)
#     #     df2.to_excel(writer, sheet_name = '{0}_2018_FarmSizes'.format(bl), index=False)
#     df.to_csv(r'tables\FarmSizes\{0}_field_sizes_2018.csv'.format(bl), index=False)
#     df2.to_csv(r'tables\FarmSizes\{0}_farm_sizes_2018.csv'.format(bl), index=False)
#     del shp, lyr

table = [['Federal State', 'Field Mean [ha]', 'Field Median [ha]', 'Farm Mean [ha]', 'Farm Median [ha]']]
b = 0
for bl in bl_lst:
    # df1 = df_lst[b]
    # df2 = df_lst[b+1]
    df1 = pd.read_csv(r'tables\FarmSizes\{0}_field_sizes_2018.csv'.format(bl))
    df2 = pd.read_csv(r'tables\FarmSizes\{0}_farm_sizes_2018.csv'.format(bl))

    field_mean = df1['Area'].mean()
    field_median = df1['Area'].median()
    farm_mean = df2['Area'].mean()
    farm_median = df2['Area'].median()
    table.append([bl, field_mean, field_median, farm_mean, farm_median])
    b += 2

table = pd.DataFrame(table)

df_bb = pd.read_csv(r'tables\FarmSizes\BB_farm_sizes_2018.csv')
df_sa = pd.read_csv(r'tables\FarmSizes\SA_farm_sizes_2018.csv')
df_bv = pd.read_csv(r'tables\FarmSizes\BV_farm_sizes_2018.csv')
df_ls = pd.read_csv(r'tables\FarmSizes\LS_farm_sizes_2018.csv')

table.to_csv(r'tables\FarmSizes\Table01_farm_and_field_sizes_2018.csv', index=False)
df_east = pd.concat([df_bb, df_sa])
df_west = pd.concat([df_bv, df_ls])

mean_east = df_east['Area'].mean()
mean_west = df_west['Area'].mean()
mean_east - mean_west
median_east = df_east['Area'].median()
median_west = df_west['Area'].median()
median_east - mean_west
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


