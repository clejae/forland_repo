# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd

import vector

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# # def workFunc(year):
# for year in range(2016,2017):
#     print(year)
#     if year < 2015:
#         df_m = pd.read_excel(r"Daten\vector\InVekos\Tables\LS_UniqueCropCodes.xlsx", sheet_name='K_ART_UNIQUE_2011-2014')
#     else:
#         df_m = pd.read_excel(r"Daten\vector\InVekos\Tables\LS_UniqueCropCodes.xlsx", sheet_name='K_ART_UNIQUE_2015-2018')
#
#     ## naming convetion: #InVekos_BY_2019_1
#     # in_shp_pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\shp\backup\Schlaege_mitNutzung_{}.shp".format(year)
#     in_shp_pth = r"Clemens\data\vector\IACS\LS\IACS_LS_{0}.shp".format(year)
#     in_shp = ogr.Open(in_shp_pth,1)
#     in_lyr = in_shp.GetLayer()
#
#     ## get list of field names
#     fname_lst = vector.getFieldNames(in_shp)
#
#     ## column name of Kulturtypen
#     fname_organic = "ID_KTYP"
#     fname_ws = "ID_WiSo"
#     fname_cl = "ID_HaBl"
#     fname_kuni = "K_ART_UNI"
#
#     ## check if this column name already exists
#     ## if yes, then no new column will be created
#     ## if not, then the column will be created and the field name list will be updated
#
#     if fname_organic in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_organic))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_organic, ogr.OFTInteger))
#         fname_lst = vector.getFieldNames(in_shp)
#
#     if fname_ws in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_ws))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_ws, ogr.OFTInteger))
#         fname_lst = vector.getFieldNames(in_shp)
#
#     if fname_cl in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_cl))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_cl, ogr.OFTInteger))
#         fname_lst = vector.getFieldNames(in_shp)
#
#     if fname_kuni in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_kuni))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_kuni, ogr.OFTString))
#         fname_lst = vector.getFieldNames(in_shp)
#
#     for feat in in_lyr:
#         # fname_code = 'KULTURARTF'
#         # if year < 2016:
#         #     nu_code = feat.GetField(fname_code)
#         # else:
#         #     nu_code = int(feat.GetField(fname_code))
#
#         if year < 2016:
#             fname_btr = 'KULTURCODE'
#             betr = feat.GetField(fname_btr)
#         elif year == 2016:
#             fname_btr = 'KULTURCODE'
#             betr = int(feat.GetField(fname_btr))
#         else:
#             fname_btr = 'KULTURARTF'
#             betr = int(feat.GetField(fname_btr))
#
#         organic = df_m['ID_KULTURTYP4_FL'].loc[df_m['NUCODE'] == betr]  # returns a pd Series
#         organic = organic.iloc[0]  # extracts value from pd Series
#
#         ws = df_m['ID_WinterSommer'].loc[df_m['NUCODE'] == betr]  # returns a pd Series
#         ws = ws.iloc[0]  # extracts value from pd Series
#
#         cl = df_m['ID_HalmfruchtBlattfrucht'].loc[df_m['NUCODE'] == betr]  # returns a pd Series
#         cl = cl.iloc[0]
#
#         kuni = df_m['K_ART_UNIQUE'].loc[df_m['NUCODE'] == betr]  # returns a pd Series
#         kuni = kuni.iloc[0]
#
#         ind = fname_lst.index(fname_organic)
#         feat.SetField(ind, int(organic))
#
#         ind = fname_lst.index(fname_ws)
#         feat.SetField(ind, int(ws))
#
#         ind = fname_lst.index(fname_cl)
#         feat.SetField(ind, int(cl))
#
#         ind = fname_lst.index(fname_kuni)
#         feat.SetField(ind, kuni)
#
#         in_lyr.SetFeature(feat)
#
#     in_lyr.ResetReading()
#
#     del in_shp, in_lyr
#
#     print(year, "done!")
#
# # if __name__ == '__main__':
#     joblib.Parallel(n_jobs=7)(joblib.delayed(workFunc)(year) for year in range(2015,2019))

## Assign organic/conventional farming to shape in LS
# for year in [2015,2017]:  # range(2016,2017):
def workFunc(year):
    print(year)
    df_m = pd.read_csv(r"Q:\FORLand\Clemens\data\vector\IACS\LS\Betriebe_{0}.csv".format(year), sep = ";")
    df_m["OEKOKONTROLLNUMMER"] = df_m["OEKOKONTROLLNUMMER"].astype(str)
    df_m["OEKOKONTROLLNUMMER"][df_m["OEKOKONTROLLNUMMER"] != 'nan'] = 1
    df_m["OEKOKONTROLLNUMMER"][df_m["OEKOKONTROLLNUMMER"] == 'nan'] = 0
    ## naming convetion: #InVekos_BY_2019_1
    # in_shp_pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\shp\backup\Schlaege_mitNutzung_{}.shp".format(year)
    in_shp_pth = r"Clemens\data\vector\IACS\LS\IACS_LS_{0}.shp".format(year)
    in_shp = ogr.Open(in_shp_pth ,1)
    in_lyr = in_shp.GetLayer()

    ## get list of field names
    fname_lst = vector.getFieldNames(in_shp)

    ## column name of Kulturtypen
    fname_organic = "ORGANIC"

    ## check if this column name already exists
    ## if yes, then no new column will be created
    ## if not, then the column will be created and the field name list will be updated

    if fname_organic in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_organic))
    else:
        in_lyr.CreateField(ogr.FieldDefn(fname_organic, ogr.OFTString))
        fname_lst = vector.getFieldNames(in_shp)

    if year < 2017:
        fname_btr = 'REG_NR'
    else:
        fname_btr = 'REGISTRIER'

    check_lst = list(df_m['REG_NR'])
    for f, feat in enumerate(in_lyr):
    # for i in range(100000):
    #     feat = in_lyr.GetFeature(i)
        betr = feat.GetField(fname_btr)
        if year < 2017:
            betr = '27603' + str(betr)

        if int(betr) in check_lst:
            organic = df_m['OEKOKONTROLLNUMMER'].loc[df_m['REG_NR'] == int(betr)]  # returns a pd Series
            organic = organic.iloc[0]  # extracts value from pd Series
        else:
            organic = 0

        feat.SetField(fname_organic, organic)
        in_lyr.SetFeature(feat)

    in_lyr.ResetReading()
    del in_shp, in_lyr
    print(year, "done!")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=3)(joblib.delayed(workFunc)(year) for year in range(2015,2018))
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#