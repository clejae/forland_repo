# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import ogr
import joblib
import pandas as pd
import glob
## CJ REPO
import general
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
# wd = r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\\'
# wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
wd = r'C:\Users\Clemens Jänicke\Desktop\FORLAND\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl_lst = ['BB', 'SA']
#
# for bl in bl_lst:
#
#     if bl == 'BB':
#         # pth = r'Crops\AKTUELL_Invekos_20191217\\'
#         pth = r'vector\InvClassified\\'
#         file = 'Inv_NoDups_'
#         min_year = 2005
#         max_year = 2018
#     if bl == 'SA':
#         # pth = r'Sachsen-Anhalt\Shapefiles\AKTUELL_20200404\\'
#         pth = r'vector\InvClassified\\'
#         file = 'Antraege'
#         min_year = 2008
#         max_year = 2018
#     if bl == 'BY':
#         pth = r'Bayern\AKTUELL_20200604\\'
#         file = 'Nutzung'
#         min_year = 2005
#         max_year = 2019
#
#     year_lst = range(min_year, max_year + 1)
#
#     def workFunc(year):
#     # for year in year_lst:
#
#         print(bl, year)
#
#         out_lst = [['BL','Year','FID','CountID','KTYP','Area']]
#
#         shp_pth = pth + file + str(year) + '.shp'
#         shp = ogr.Open(shp_pth)
#         lyr = shp.GetLayer()
#
#         for f, feat in enumerate(lyr):
#
#             fid = feat.GetField("ID")
#             ktyp = feat.GetField("ID_KTYP")
#             geom = feat.GetGeometryRef()
#             if geom != None:
#                 area = geom.Area()
#             else:
#                 area = -9999
#
#             attr_lst = [bl, year, fid, f, ktyp, area]
#             out_lst.append(attr_lst)
#
#         out_pth = r'tables\InVekos\area_stats\area_stats_{}_{}.csv'.format(bl, year)
#         general.writeListToCSV(out_lst, out_pth)
#
#         print(bl, year, "done")
#
#     if __name__ == '__main__':
#         joblib.Parallel(n_jobs=14)(joblib.delayed(workFunc)(year) for year in year_lst)
#
# pth_lst = glob.glob(r'tables\InVekos\area_stats\*.csv')
#
# for csv_pth in pth_lst:
#     df = pd.read_csv(csv_pth)
#     df_lst.append(df)
#
# df = pd.concat(df_lst)
# df.to_csv(r'tables\InVekos\area_stats\area_stats_ALL_20200406.csv', index= False)
df = pd.read_csv(r"tables\InVekos\area_stats\area_stats_ALL_20200406.csv")

## Change data types where necessary
df.info()
df['BL'] = df['BL'].astype('str')
df['Area'] = df['Area'].astype('float')

## Calculate statistics
## first convert sqm to ha
df['Area'] = df['Area'].div(10000)

df_lst = []
for bl in bl_lst:
    df_sub = df[df.BL == bl]

    df1 = df_sub.groupby(['Year'])[['Area']].max()
    df1.columns = ['Max Area']
    df2 = df_sub.groupby(['Year'])[['Area']].min()
    df2.columns = ['Min Area']
    df3 = df_sub.groupby(['Year'])[['Area']].mean()
    df3.columns = ['Mean Area']
    df4 = df_sub.groupby(['Year'])[['Area']].sum()
    df4.columns = ['Sum Area']
    df5 = df_sub.groupby(['Year']).size()
    df5 = pd.DataFrame(df5)
    df5.columns = ['Count']

    df_summ = pd.concat([df1, df2, df3, df4, df5], 1)
    df_lst.append(df_summ)

df_lst2 = []
ct_lst = df['KTYP'].unique()
ct_lst.sort()
for bl in bl_lst:
    df_sub = df[df.BL == bl]

    df1 = df_sub.groupby(['Year','KTYP'])[['Area']].max().unstack()
    df1.columns = ['Max Area' + str(i) for i in ct_lst]
    df2 = df_sub.groupby(['Year','KTYP'])[['Area']].min().unstack()
    df2.columns = ['Min Area' + str(i) for i in ct_lst]
    df3 = df_sub.groupby(['Year','KTYP'])[['Area']].mean().unstack()
    df3.columns = ['Mean Area' + str(i) for i in ct_lst]
    df4 = df_sub.groupby(['Year','KTYP'])[['Area']].sum().unstack()
    df4.columns = ['Sum Area' + str(i) for i in ct_lst]
    df5 = df_sub.groupby(['Year','KTYP']).size().unstack()
    df5.columns = ['Count' + str(i) for i in ct_lst]

    df_summ = pd.concat([df1, df2, df3, df4, df5],1)
    df_lst2.append(df_summ)

df_lst3 = []
for bl in bl_lst:
    df_sub = df[df.BL == bl]
    df_sub = df_sub[(df_sub.KTYP != 30) & (df_sub.KTYP != 80) & (df_sub.KTYP != 99)]

    df1 = df_sub.groupby(['Year'])[['Area']].max()
    df1.columns = ['Max Area']
    df2 = df_sub.groupby(['Year'])[['Area']].min()
    df2.columns = ['Min Area']
    df3 = df_sub.groupby(['Year'])[['Area']].mean()
    df3.columns = ['Mean Area']
    df4 = df_sub.groupby(['Year'])[['Area']].sum()
    df4.columns = ['Sum Area']
    df5 = df_sub.groupby(['Year'])[['CountID']].size()
    df5.columns = ['Count']

    df_summ = pd.concat([df1, df2, df3, df4, df5],1)
    df_lst3.append(df_summ)

with pd.ExcelWriter(r'tables\InVekos\area_stats\area_statistics_ALL.xlsx') as writer:
    for d, df_out in enumerate(df_lst):
        bl = bl_lst[d]
        df_out.to_excel(writer, sheet_name = bl + 'TotalStatistics')
    for d, df_out in enumerate(df_lst2):
        bl = bl_lst[d]
        df_out.to_excel(writer, sheet_name=bl + 'CropTypeStatistics')
    for d, df_out in enumerate(df_lst3):
        bl = bl_lst[d]
        df_out.to_excel(writer, sheet_name=bl + 'TotalALStatistics')


# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# import vector
# import forland_wrapper
# cleaned_pth2 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege2018.shp"
# cleaned_pth3 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege2018_v02.shp"
# forland_wrapper.removingNoneGeoms(cleaned_pth2, cleaned_pth3)

# df_lst = []
# area_lst = [["TotalArea","AlArea"]]
# for year in range(2005,2017):
#     print(year)
#     shp_pth = wd + r'Inv_NoDups_{0}.shp'.format(year)
#     shp = ogr.Open(shp_pth, 0) # 0=read only, 1=writeabel
#     lyr = shp.GetLayer()
#
#     printLayerColumns(lyr)
#
#     area_lst = []
#     type_lst = []
#     id_lst = []
#     for feat in lyr:
#         pt_id = feat.GetField('PtID')
#         area = feat.GetField('Area_H')
#         k_art_n = feat.GetField('K_ART_N')
#
#         id_lst.append(pt_id)
#         area_lst.append(area)
#         type_lst.append(k_art_n)
#     lyr.ResetReading()
#
#     df = pd.DataFrame()
#     df["K_ART_N"] = type_lst
#     df["Area_H"] = area_lst
#     df["ID"] = id_lst
#
#     area_total = df["Area_H"].sum()
#     df_kult = df.groupby(['K_ART_N'])[['Area_H']].sum()#.unstack()
#     df_lst.append(df_kult)
#
#     if year == 2016:
#         area_1 = df_kult.loc['AL',:][0]
#         area_2 = df_kult.loc['AI',:][0]
#         area_al = area_1 + area_2
#     else:
#         area_al = df_kult.loc['AL',:][0]
#
#     al_perc = area_al / area_total * 100
#
#     area_al_lst.append([area_total, area_al, al_perc])
#
# area_lst = [["Year","TotalArea","AL-Area","AL-Perc"]]
# for i, df in enumerate(df_lst):
#     print(i + 2005)
#     # ind_names = df.index.values
#     # print(ind_names)
#     area_total = df["Area_H"].sum()
#     if i + 2005 == 2016:
#         area_1 = df.loc['AL',:][0]
#         area_2 = df.loc['AI',:][0]
#         area_al = area_1 + area_2
#     else:
#         area_al = df.loc['AL',:][0]
#
#     al_perc = round(area_al / area_total * 100,2)
#
#     area_lst.append([i + 2005, round(area_total,2), round(area_al,2), al_perc])
#
# df = pd.DataFrame(area_lst)
# df.columns = df.iloc[0]
# df = df.drop(df.index[0])
# df.to_excel(r'L:\Clemens\data\tables\InVekos\k_art_k_area.xlsx', index=False)
#
#
# plt.plot(range(2005,2017),area_al_lst)
# plt.bar(x= range(2005,2017), height=area_al_lst, width=0.8, align='center')
# plt.show()
# plt.close()
#
# ras = gdal.Open(r"L:\Clemens\data\raster\grid\2005-2005_Inv_Stack_5m_BIN_mosaic.tif")
#
# with open(r"L:\Clemens\data\raster\grid\folder_list.txt") as file:
#     tiles_lst = file.readlines()
# tiles_lst = [item.strip() for item in tiles_lst]
#
# arr = ras.ReadAsArray()
# pix_count = np.sum(arr)
# area_m2 = pix_count * 25
# area_ha = area_m2 / (100 * 100)
