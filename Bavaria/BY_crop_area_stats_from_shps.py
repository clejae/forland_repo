# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd
import math

from functools import reduce

import vector
import general


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

ind_lst = [15, 23, 18, 14, 17, 9, 1, 19, 22, 20, 3, 5, 16, 21, 11, 13, 8, 12, 4, 6, 2, 10, 7]
task_lst = [(year, index) for year in range(2014,2015) for index in ind_lst]

###################################################################
# ## Area stats of crop types
#
# # for task in task_lst:
# def workFunc(task):
#
#     area_dict = {0:0,
#             1: 0 ,
#             2: 0 ,
#             3: 0 ,
#             4: 0 ,
#             5: 0 ,
#             6: 0 ,
#             7: 0 ,
#             9: 0 ,
#             10: 0 ,
#             12: 0 ,
#             13: 0 ,
#             60: 0 ,
#             70: 0 ,
#             30: 0 ,
#             80: 0 ,
#             99: 0 ,
#             255:0}
#
#     df_m = pd.read_excel(r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Tables\BY_UniqueCropCodes.xlsx',
#                          sheet_name='CodeNameCombinations')
#
#     year = task[0]
#     index = task[1]
#
#     print(year, index)
#
#     ## naming convetion: #InVekos_BY_2019_1
#     in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(year, index)
#     in_shp = ogr.Open(in_shp_pth)
#     in_lyr = in_shp.GetLayer()
#
#     if year < 2017:
#
#         for feat in in_lyr:
#             use_n = feat.GetField("anz_nutz")
#             if use_n == 1:
#                 fname_code = 'nutz_c1'
#                 fname_area = 'nutz_f1'
#                 nu_code = int(feat.GetField(fname_code))
#                 area = float(feat.GetField(fname_area))
#
#                 ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#                 ktyp = ktyp.iloc[0]  # extracts value from pd Series
#
#                 area_dict[ktyp] = area_dict[ktyp] + area
#
#             elif use_n > 1:
#
#                 for i in range(1, int(use_n) + 1):
#                     fname_code = 'nutz_c' + str(i)
#                     fname_area = 'nutz_f' + str(i)
#
#                     nu_code = feat.GetField(fname_code)
#                     if nu_code == None:
#                         ktyp = 0
#                         area = 0
#                     else:
#                         nu_code = int(nu_code)
#                         area = float(feat.GetField(fname_area))
#
#                         ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#                         ktyp = ktyp.iloc[0]  # extracts value from pd Series
#
#                     area_dict[ktyp] = area_dict[ktyp] + area
#
#             else:
#                 fname_area = 'nutz_f1'
#                 ktyp = 0
#                 area = float(feat.GetField(fname_area))
#                 area_dict[ktyp] = area_dict[ktyp] + area
#         in_lyr.ResetReading()
#     else:
#         for feat in in_lyr:
#             fname_code = 'nutz_code'
#             fname_area = 'flaeche'
#             nu_code = int(feat.GetField(fname_code))
#             area = float(feat.GetField(fname_area))
#
#             ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#             ktyp = ktyp.iloc[0]  # extracts value from pd Series
#
#             area_dict[ktyp] = area_dict[ktyp] + area
#         in_lyr.ResetReading()
#
#     df = pd.DataFrame.from_dict(area_dict, orient='index')
#     df.to_excel(r'data\tables\InVekos\area_stats\BY_slices\{}_AreaOfCropTypes_{}.xlsx'.format(year, index))
#
#     del in_shp, in_lyr
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(task) for task in task_lst)
#
# for year in range(2017,2020):
#     print(year)
#     df_lst = []
#     for ind in range(1,24):
#         pth = r'data\tables\InVekos\area_stats\BY_slices\{}_AreaOfCropTypes_{}.xlsx'.format(year, ind)
#         df = pd.read_excel(pth)
#         df.columns = ['K','AREA' + str(ind)]
#         df_lst.append(df)
#
#     df_final = df_lst[0].merge(df_lst[1],on='K')
#
#     for df in df_lst[2:]:
#         df_final = df_final.merge(df, on='K')
#
#     df_final.to_excel(r'data\tables\InVekos\area_stats\BY_slices\AreaOfCropTypes_{}.xlsx'.format(year))
#
#
# df_lst = [pd.read_excel(r'data\tables\InVekos\area_stats\BY_slices\AreaOfCropTypes_{}.xlsx'.format(year)) for year in range(2005,2020)]
# ct_col = pd.DataFrame(df_lst[0]['K'])
# ct_col.columns = ['CropType']
# cols = ['AREA{}'.format(i) for i in range(1,24)]
# df_lst = [df[cols].sum(axis=1) for df in df_lst]
# df = pd.concat(df_lst, axis=1)
# cols = [str(i) for i in range(2005,2020)]
# df.columns = cols
# df_out = pd.concat([ct_col, df], axis=1)
# df_out.to_excel(r"data\tables\CropRotations\BY\BY_2005-2018_AreaOfCropTypes_ha_from_shp.xlsx", index=False)

###################################################################
## Maximum area

# out_lst1 = []
# out_lst2 = []

# for year in range(2005,2006):
# def workFunc(task):
# # for task in task_lst:
#
#     classes = [i / 100 for i in range(0, 100, 5)]
#     classes.append(1.0)
#
#     prop_dict = {}
#     area_dict = {}
#     for c in classes:
#         prop_dict[c] = 0
#         area_dict[c] = 0
#
#     df_m = pd.read_excel(r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Tables\BY_UniqueCropCodes.xlsx',
#                             sheet_name='CodeNameCombinations')
#
#     year = task[0]
#     index = task[1]
#
#     print(year, index)
#
#     ## naming convetion: #InVekos_BY_2019_1
#     in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(year, index)
#     in_shp = ogr.Open(in_shp_pth)
#     in_lyr = in_shp.GetLayer()
#
#     for feat in in_lyr:
#         use_n = feat.GetField("anz_nutz")
#         if use_n == 1:
#             fname_code = 'nutz_c1'
#             fname_area = 'nutz_f1'
#             area = feat.GetField(fname_area)
#             if area != None:
#                 area = float(area)
#             else:
#                 area = 0
#             nu_code = int(feat.GetField(fname_code))
#
#             ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#             ktyp = ktyp.iloc[0]  # extracts value from pd Series
#
#             maxclass = 1.00
#             prop_dict[maxclass] = prop_dict[maxclass] + 1
#             area_dict[maxclass] = area_dict[maxclass] + area
#
#         elif use_n > 1:
#
#             ktyp_lst = []
#
#             for i in range(1, int(use_n) + 1):
#                 fname_code = 'nutz_c' + str(i)
#                 fname_area = 'nutz_f' + str(i)
#
#                 nu_code = int(feat.GetField(fname_code))
#                 area = feat.GetField(fname_area)
#                 if area != None:
#                     area = float(area)
#                 else:
#                     area = 0
#
#                 ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#                 ktyp = ktyp.iloc[0]  # extracts value from pd Series
#                 ktyp_lst.append([ktyp, area])
#
#             df = pd.DataFrame(ktyp_lst, columns=['KTYP', 'AREA'])
#             df = df.groupby('KTYP').sum() / df['AREA'].sum()
#             maxclass = df['AREA'].max()
#             df.reset_index(inplace=True)
#             ktyp = df['KTYP'].loc[df['AREA'] == maxclass]
#
#             if math.isnan(maxclass):
#                 maxclass = 0
#             else:
#                 maxclass = round(.05 * round(float(maxclass) / .05), 2)
#
#             prop_dict[maxclass] = prop_dict[maxclass] + 1
#             area_dict[maxclass] = area_dict[maxclass] + area
#
#         else:
#             ktyp = 0
#             maxclass = 0.00
#             area = 0
#
#             prop_dict[maxclass] = prop_dict[maxclass] + 1
#             area_dict[maxclass] = area_dict[maxclass] + area
#
#     in_lyr.ResetReading()
#
#     df = pd.DataFrame.from_dict(prop_dict, orient='index')
#     df.to_excel(r'data\tables\InVekos\multicropping\{}_CountMaxClass_{}.xlsx'.format(year, index))
#
#     df = pd.DataFrame.from_dict(area_dict, orient='index')
#     df.to_excel(r'data\tables\InVekos\multicropping\{}_AreaMaxClass_{}.xlsx'.format(year, index))
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(task) for task in task_lst)

out_lst = []
out_lst2 = []
for year in range(2005,2017):
    print(year)
    df_lst = []
    df_lst2 = []
    for ind in range(1,24):
        pth = r'data\tables\InVekos\multicropping\{}_CountMaxClass_{}.xlsx'.format(year, ind)
        df = pd.read_excel(pth)
        df.columns = ['Class','Count' + str(ind)]
        df_lst.append(df)

        pth2 = r'data\tables\InVekos\multicropping\{}_AreaMaxClass_{}.xlsx'.format(year, ind)
        df = pd.read_excel(pth2)
        df.columns = ['Class', 'Area' + str(ind)]
        df_lst2.append(df)

    df_final = reduce(lambda x, y: pd.merge(x, y, on = 'Class'), df_lst)
    cols = ['Count{}'.format(i) for i in range(1,24)]
    df = df_final[cols].sum(1)
    indeces = pd.DataFrame(df_final['Class'])
    df = pd.concat([indeces, df], axis=1)
    df.columns = ['Class',year]
    out_lst.append(df)

    df_final = reduce(lambda x, y: pd.merge(x, y, on = 'Class'), df_lst2)
    cols = ['Area{}'.format(i) for i in range(1,24)]
    df = df_final[cols].sum(1)
    indeces = pd.DataFrame(df_final['Class'])
    df = pd.concat([indeces, df], axis=1)
    df.columns = ['Class',year]
    out_lst2.append(df)

df_out = reduce(lambda x, y: pd.merge(x, y, on = 'Class'), out_lst)
pth = r'data\tables\InVekos\multicropping\_CountMaxClass.xlsx'
df_out.to_excel(pth)

df_out = reduce(lambda x, y: pd.merge(x, y, on = 'Class'), out_lst2)
pth = r'data\tables\InVekos\multicropping\_AreaMaxClass.xlsx'
df_out.to_excel(pth)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#