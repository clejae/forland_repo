# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd
from functools import reduce

## CJ Repo
import vector

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# ## derive all nu-codes
# def workFunc(year):
#     print(year)
#
#     lst = []
#
    shp_pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\shp\Schlaege_mitNutzung_{}.shp".format(
        year)
    shp = ogr.Open(shp_pth)
    lyr = shp.GetLayer()

    vector.printFieldNames(lyr)
#
#     for feat in lyr:
#         nu_code = feat.GetField("KC")
#
#         if nu_code not in lst:
#             lst.append(nu_code)
#     lyr.ResetReading()
#
#     pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\Kulturcode_Listen\nu_codes_in_shp_{0}.txt".format(
#         year)
#     file = open(pth, "w+")
#     for i in lst:
#         file.write(str(i) + '\n')
#     file.close()
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=5)(joblib.delayed(workFunc)(year) for year in range(2012,2021))

## concat the codes
id_lst = []
df_shp_lst = []
for year in range(2012,2021):
    pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\Kulturcode_Listen\nu_codes_in_shp_{0}.txt".format(
        year)
    df = pd.read_csv(pth, header=None)
    df.columns = ['NUCODE']
    df['IN_SHP_' + str(year)] = df['NUCODE']
    for i in df['NUCODE']:
        if i not in id_lst:
            id_lst.append(i)
    df_shp_lst.append(df)

df_pdf_lst = []
for year in range(2014,2021):
    pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\Kulturcode_Listen\Kulturcodes_BNK_{0}.xlsx".format(
        year)
    df = pd.read_excel(pth)
    df = df[['Code', 'CODE_ART']]
    df.columns = ['Code', 'IN_PDF_' + str(year)]
    for i in df['Code']:
        if i not in id_lst:
            id_lst.append(i)
    df_pdf_lst.append(df)

    fname_ktyp = "ID_KTYP"
    fname_ws = "ID_WiSo"
    fname_cl = "ID_HaBl"
    fname_maxclass = "MAXCL_AREA"

df_ls = pd.read_excel(r"Daten\vector\InVekos\Tables\LS_CropClassification_SteinSteinmann2018.xlsx", sheet_name = 'Kulturenschlüssel')
df_ls.columns = ['ID','NU_CODE_2011','KULTUR_TXT_2011','ID_KTYP','WiSo_TXT','ID_WiSo','HaBl_TXT']
for i in df_ls['NU_CODE_2011']:
    if i not in id_lst:
        id_lst.append(i)

id_lst.sort()
df_final = pd.DataFrame(id_lst)
df_final.columns = ['NUCODE']
df_shp_lst.insert(0, df_final)
df_merge = reduce(lambda x, y: pd.merge(x, y, on = 'NUCODE', how='outer'), df_shp_lst)
df_pdf_lst.insert(0, df_merge)
df_merge = reduce(lambda x, y: pd.merge(x, y, left_on = 'NUCODE', right_on='Code', how='outer'), df_pdf_lst)

df_merge = pd.merge(df_merge, df_ls, left_on='NUCODE', right_on='NU_CODE_2011', how='outer')

cols = list(df_merge.columns)
cols = [cols[i] for i in [10,12,14,16,18,20,22,24]]
df_merge.drop(cols, axis=1, inplace=True)

col_lst = ['IN_PDF_{}'.format(year) for year in range(2014,2021)]
col_lst.append('KULTUR_TXT_2011')
for col in col_lst:
    df_merge[col] = df_merge[col].str.replace('Ö', 'Oe')
    df_merge[col] = df_merge[col].str.replace('ö', 'oe')
    df_merge[col] = df_merge[col].str.replace('Ü', 'Ue')
    df_merge[col] = df_merge[col].str.replace('ü', 'ue')
    df_merge[col] = df_merge[col].str.replace('Ä', 'Ae')
    df_merge[col] = df_merge[col].str.replace('ä', 'ae')
    df_merge[col] = df_merge[col].str.replace('ß', 'ss')
    df_merge[col] = df_merge[col].str.replace('  ', ' ')
    df_merge[col] = df_merge[col].str.replace('\n', ' ')

df_merge.to_excel(r"Daten\vector\InVekos\Tables\LS_UniqueCropCodes.xlsx", index=False)

## After manual editing:
df_ref = pd.read_excel(r"Daten\vector\InVekos\Tables\UniqueCropCodes_AllYrsAndBundeslaender.xlsx", sheet_name='UniqueCodes')
df_ref = df_ref[['K_ART_UNIQUE_noUmlaute','ID_KULTURTYP4_FL','ID_WinterSommer','ID_HalmfruchtBlattfrucht']]
df = pd.read_excel(r"Daten\vector\InVekos\Tables\LS_UniqueCropCodes_Preparation.xlsx", sheet_name='IDENT_UNIQUE')

df_per1 = df[['NUCODE','IN_SHPS_2011-2014','K_ART_UNIQUE_2011-2014']]
df_per1= df_per1.dropna()
df_per2 = df[['NUCODE','IN_SHPS_2015-2018','K_ART_UNIQUE_2015-2018']]
df_per2= df_per2.dropna()

df_merge1 = pd.merge(df_per1, df_ref, left_on='K_ART_UNIQUE_2011-2014', right_on='K_ART_UNIQUE_noUmlaute', how='left')
df_merge2 = pd.merge(df_per2, df_ref, left_on='K_ART_UNIQUE_2015-2018', right_on='K_ART_UNIQUE_noUmlaute', how='left')

with pd.ExcelWriter(r'Daten\vector\InVekos\Tables\LS_UniqueCropCodes.xlsx') as writer:
    df_merge1.to_excel(writer, sheet_name='K_ART_UNIQUE_2011-2014', index=False)
    df_merge2.to_excel(writer, sheet_name='K_ART_UNIQUE_2015-2018', index=False)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

