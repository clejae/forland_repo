# Clemens Jänicke
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
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
min_year = 2012
max_year = 2018
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

###################################################################
## Area stats of crop types

def workFunc(year):
    print(year)
    area_dict = {0:0,
            1: 0 ,
            2: 0 ,
            3: 0 ,
            4: 0 ,
            5: 0 ,
            6: 0 ,
            7: 0 ,
            9: 0 ,
            10: 0 ,
            12: 0 ,
            13: 0 ,
            60: 0 ,
            70: 0 ,
            30: 0 ,
            80: 0 ,
            99: 0 ,
            255:0}

    in_shp_pth = r"Daten\vector\InVekos\Niedersachsen\NS_OriginalData\NI_Schlag_KC_20_12\shp\Schlaege_mitNutzung_{}.shp".format(
        year)
    in_shp = ogr.Open(in_shp_pth)
    in_lyr = in_shp.GetLayer()

    for feat in in_lyr:
        fname_ktyp = 'ID_KTYP'
        if year < 2017:
            fname_area = 'Area_m2'
        else:
            fname_area = 'GEOMETRIE1' # GEOMETRIE_ == ShapeLength; GEOMETRIE1 == ShapeArea

        ktyp = int(feat.GetField(fname_ktyp))
        if ktyp == 14:
            ktyp = 12

        area = float(feat.GetField(fname_area))

        area_dict[ktyp] = area_dict[ktyp] + area
    in_lyr.ResetReading()

    df = pd.DataFrame.from_dict(area_dict, orient='index')
    df.to_excel(r'Clemens\data\tables\InVekos\LS\{}_AreaOfCropTypes.xlsx'.format(year))

    del in_shp, in_lyr

if __name__ == '__main__':
    joblib.Parallel(n_jobs=7)(joblib.delayed(workFunc)(year) for year in range(min_year, max_year+1))

df_lst = [pd.read_excel(r'Clemens\data\tables\InVekos\LS\{}_AreaOfCropTypes.xlsx'.format(year)) for year in range(min_year, max_year+1)]
df = pd.concat(df_lst, axis=1)
cols = []
for i in range(min_year, max_year+1):
    cols.append('CropClass'+str(i))
    cols.append('Area' + str(i))
df.columns = cols
df = df.drop(columns=['CropClass'+str(i) for i in range(min_year+1, max_year+1)])
df.to_excel(r"Clemens\data\tables\CropRotations\LS_{}-{}_AreaOfCropTypes_m2_from_shp_v02.xlsx".format(min_year, max_year), index=False)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#