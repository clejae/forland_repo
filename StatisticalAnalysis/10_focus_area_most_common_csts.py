# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import ogr
import vector
import pandas as pd
import numpy as np
import general
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def cstNumToStr(cst_value):
    import string
    if cst_value < 100:
        cst_value = str(int(cst_value))
        alphabet = string.ascii_uppercase
        cst_str = alphabet[int(cst_value[0])-1] + str(cst_value[1])
    else:
        cst_str = 'NA'

    return cst_str

def convertSequnceNumsToStrs(str):
    ct_dict = {1 : 'MA',
               2 : 'WW',
               3 : 'SB',
               4 : 'OR',
               5 : 'PO',
               6 : 'SC',
               7 : 'TR',
               9 : 'WB',
               10: 'RY',
               12: 'LE',
               13: 'GR',
               14: 'LE',
               60: 'VE',
               30: 'FA',
               80: 'UN',
               70: 'MC',
               99: 'OT',
               255: 'FA'
               }

    ct_lst = str.split('_')
    ct_lst = [ct_dict[int(i)] for i in ct_lst]
    ct_str = '-'.join(ct_lst)
    return ct_str
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'C:\Users\Clemens Jänicke\Desktop\FORLAND\\'
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl_lst = ['SA','LS','BV']
# bl_lst = ['BB']

bl_dict = {'BB':['2005-2011','2008-2014','2012-2018'], #
           'SA':['2008-2014','2012-2018'], #,'2012-2018'
           'BV':['2005-2011','2008-2014','2012-2018'], #,'2012-2018'
           'LS':['2012-2018']}

fname_dict = {'BB':['BNR_ZD','GROESSE','ACKERZ'],
              'SA':['btnr','PARZ_FLAE'],
              'LS':['REGISTRIER','AREA_ha'],
              'BV':['bnrhash','flaeche']}
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
## open df with extents
df = pd.read_csv(r"data\tables\focus_areas\focus_areas_extents.txt")

###### Derive most common CSTs from Shapes (Field based) ######
## loop over federal states
for bl in bl_lst:
    print(bl)

    ## subset df for federal state
    df_fs = df[df['federal state'] == bl]

    df_seq = pd.read_csv(r"data\tables\FarmSize-CSTs\{0}_2012-2018_sequences_farm-size.csv".format(bl))
    df_seq['ID'] = df_seq['ID'].astype(str)

    for row in range(df_fs.shape[0]):

        ## open shapefile
        pth = r"data\vector\IACS\{0}\IACS_{0}_2018_centroids.shp".format(bl)
        shp = ogr.Open(pth)
        lyr = shp.GetLayer()

        ## get ID of current focus area
        fid = df_fs['ID'].iloc[row]

        ## get field name of farm identifier
        fname_field = 'ID'

        ## get extent of current focus area
        xmin = df_fs['xmin'].iloc[row]
        ymin = df_fs['ymin'].iloc[row]
        xmax = df_fs['xmax'].iloc[row]
        ymax = df_fs['ymax'].iloc[row]

        ## filter layer by focus area extent
        ## collect field ids in lst
        lyr.SetSpatialFilterRect(xmin, ymin, xmax, ymax)
        field_lst = []
        for feat in lyr:
            field_id = feat.GetField(fname_field)
            field_lst.append(str(int(field_id)))
        lyr.ResetReading()
        del shp, lyr

        ## filter sequences by field ids
        df_ana = df_seq[df_seq['ID'].isin(field_lst)]
        df_ana['Sequence'] = df_ana['Sequence'].map(convertSequnceNumsToStrs)
        df_ana = df_ana[df_ana['CST'] != 255]

        ## count unique CST-Sequence combinations
        df_uni = df_ana.groupby(['CST', 'Sequence'])    # groups CST and Sequences where they are the same
        df_uni = df_uni.size()                          # returns size of unique groups
        df_uni = df_uni.reset_index()                   # resets the columns
        df_uni = df_uni.rename(columns={0: 'count'})    # provides a meaningfull name to last col
        df_uni = df_uni.sort_values('count', ascending=False)

        ## count occurences of CSTs
        df_cst_count = df_uni.groupby(['CST'])['count'].agg('sum')
        df_cst_count = df_cst_count.reset_index()
        df_cst_count = df_cst_count.sort_values('count', ascending=False)

        with pd.ExcelWriter(r'data\tables\focus_areas\{0}_focus_area_{0}.xlsx'.format(fid)) as writer:
            sheet_name = 'CSTCount'
            df_cst_count.to_excel(writer, sheet_name=sheet_name, index=True)
            sheet_name = 'TypicalSequence'
            df_uni.to_excel(writer, sheet_name=sheet_name, index=True)

        print('Focus Area', fid, 'in', bl, 'done!')

###### Derive most common CSTs from Array (Area based) ######
## loop over federal states
# out_lst = [['ID','CST1','CST2','CST3','CST4','CST5','CST6','Area1','Area2','Area3','Area4','Area5','Area6']]
# for bl in bl_lst:
#     print(bl)
#     ## subset df for federal state
#     df_fs = df[df['federal state'] == bl]
#
#     ## open raster
#     pth = r"data\raster\{0}_2012-2018_CropSeqType_clean.tif".format(bl)
#     ras = gdal.Open(pth)
#     arr = ras.ReadAsArray()
#     gt = ras.GetGeoTransform()
#
#     for row in range(df_fs.shape[0]):
#
#         ## get ID of current focus area
#         fid = df_fs['ID'].iloc[row]
#
#         ## get extent of current focus area
#         xmin = df_fs['xmin'].iloc[row]
#         ymin = df_fs['ymin'].iloc[row]
#         xmax = df_fs['xmax'].iloc[row]
#         ymax = df_fs['ymax'].iloc[row]
#         pxmin = int((xmin - gt[0]) / gt[1])
#         pymax = int((ymin - gt[3]) / gt[5])
#         pxmax = int((xmax - gt[0]) / gt[1])
#         pymin = int((ymax - gt[3]) / gt[5])
#
#         ## subset array to current focus area
#         arr_focus = arr[pymin:pymax, pxmin:pxmax]
#
#         ## get unique values and their counts
#         uniques, count = np.unique(arr_focus, return_counts=True)
#
#         ## delete no data
#         uniques_sub = uniques[uniques != 255]
#         count = count[uniques != 255]
#
#         ## order both arrays by count
#         count_inds = count.argsort()
#         sorted_count = count[count_inds[::-1]]
#         sorted_uniques = uniques[count_inds[::-1]]
#
#         ## identify top 3 csts, calculate area of top 3 csts
#         sorted_count = sorted_count * 0.0025
#         sorted_count = np.around(sorted_count,1)
#         top3_csts = list(sorted_uniques[:20])
#         top3_csts = [convertCSTs(cst) for cst in top3_csts]
#         top3_areas = list(sorted_count[:20])
#
#         lst = [fid]+top3_csts+ top3_areas
#         out_lst.append(lst)
#
# general.writeListToCSV(out_lst, out_pth=r"data\raster\focus_area_BV_14_csts.txt")
# ------------------------------------------ END TIME --------------------------------------------------------#

##
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


