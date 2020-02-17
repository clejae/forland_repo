# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import ogr
import gdal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def printFieldNames(lyr):
    lyr_defn = lyr.GetLayerDefn()
    print("Column name | Field type | Width | Precision")
    print("--------------------------------------------")
    for i in range(lyr_defn.GetFieldCount()):
        field_name = lyr_defn.GetFieldDefn(i).GetName()
        field_type_code = lyr_defn.GetFieldDefn(i).GetType()
        field_type = lyr_defn.GetFieldDefn(i).GetFieldTypeName(field_type_code)
        field_width = lyr_defn.GetFieldDefn(i).GetWidth()
        get_precision = lyr_defn.GetFieldDefn(i).GetPrecision()

        print(field_name + " | " + field_type + " | " + str(field_width) + " | " + str(get_precision))
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Daten\vector\InVekos\Crops\AKTUELL_Invekos_20191217\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
df_lst = []
area_lst = [["TotalArea","AlArea"]]
for year in range(2005,2017):
    print(year)
    shp_pth = wd + r'Inv_NoDups_{0}.shp'.format(year)
    shp = ogr.Open(shp_pth, 0) # 0=read only, 1=writeabel
    lyr = shp.GetLayer()

    printLayerColumns(lyr)

    area_lst = []
    type_lst = []
    id_lst = []
    for feat in lyr:
        pt_id = feat.GetField('PtID')
        area = feat.GetField('Area_H')
        k_art_n = feat.GetField('K_ART_N')

        id_lst.append(pt_id)
        area_lst.append(area)
        type_lst.append(k_art_n)
    lyr.ResetReading()

    df = pd.DataFrame()
    df["K_ART_N"] = type_lst
    df["Area_H"] = area_lst
    df["ID"] = id_lst

    area_total = df["Area_H"].sum()
    df_kult = df.groupby(['K_ART_N'])[['Area_H']].sum()#.unstack()
    df_lst.append(df_kult)

    if year == 2016:
        area_1 = df_kult.loc['AL',:][0]
        area_2 = df_kult.loc['AI',:][0]
        area_al = area_1 + area_2
    else:
        area_al = df_kult.loc['AL',:][0]

    al_perc = area_al / area_total * 100

    area_al_lst.append([area_total, area_al, al_perc])

area_lst = [["Year","TotalArea","AL-Area","AL-Perc"]]
for i, df in enumerate(df_lst):
    print(i + 2005)
    # ind_names = df.index.values
    # print(ind_names)
    area_total = df["Area_H"].sum()
    if i + 2005 == 2016:
        area_1 = df.loc['AL',:][0]
        area_2 = df.loc['AI',:][0]
        area_al = area_1 + area_2
    else:
        area_al = df.loc['AL',:][0]

    al_perc = round(area_al / area_total * 100,2)

    area_lst.append([i + 2005, round(area_total,2), round(area_al,2), al_perc])

df = pd.DataFrame(area_lst)
df.columns = df.iloc[0]
df = df.drop(df.index[0])
df.to_excel(r'L:\Clemens\data\tables\InVekos\k_art_k_area.xlsx', index=False)


plt.plot(range(2005,2017),area_al_lst)
plt.bar(x= range(2005,2017), height=area_al_lst, width=0.8, align='center')
plt.show()
plt.close()

ras = gdal.Open(r"L:\Clemens\data\raster\grid\2005-2005_Inv_Stack_5m_BIN_mosaic.tif")

with open(r"L:\Clemens\data\raster\grid\folder_list.txt") as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

arr = ras.ReadAsArray()
pix_count = np.sum(arr)
area_m2 = pix_count * 25
area_ha = area_m2 / (100 * 100)


# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#