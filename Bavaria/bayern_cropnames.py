# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd

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
# ind_lst = [5, 16, 21, 11, 13, 8, 12, 4, 6, 2, 10, 7]# sorted by feature count
task_lst = [(year, index) for year in range(2005,2008) for index in ind_lst]

###################################################################
## divide single-cropping and multi-cropping plots

## for task in task_lst:
# def workFunc(task):
#     year = task[0]
#     ind = task[1]
#
#     print(year, ind)
#
#     ## naming convetion: #InVekos_BY_2019_1
#     in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(year, ind)
#     out_shp_pth1 = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\InVekos_BY_{0}_{1}_single_cropping.shp".format(
#         year, ind)
#     out_shp_pth2 = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\InVekos_BY_{0}_{1}_multi_cropping.shp".format(
#         year, ind)
#
#     in_shp = ogr.Open(in_shp_pth)
#     in_lyr = in_shp.GetLayer()
#     in_sr = in_lyr.GetSpatialRef()
#     in_lyr_defn = in_lyr.GetLayerDefn()
#     drv_shp = ogr.GetDriverByName('ESRI Shapefile')
#
#     geom_type = ogr.wkbPolygon
#
#     if os.path.exists(out_shp_pth1):
#         drv_shp.DeleteDataSource(out_shp_pth1)
#     out_shp1 = drv_shp.CreateDataSource(out_shp_pth1)
#     lyr_name1 = os.path.splitext(os.path.split(out_shp_pth1)[1])[0]
#     out_lyr1 = out_shp1.CreateLayer(lyr_name1, in_sr, geom_type=geom_type)
#     for i in range(0, in_lyr_defn.GetFieldCount()):
#         field_def = in_lyr_defn.GetFieldDefn(i)
#         out_lyr1.CreateField(field_def)
#
#     if os.path.exists(out_shp_pth2):
#         drv_shp.DeleteDataSource(out_shp_pth2)
#     out_shp2 = drv_shp.CreateDataSource(out_shp_pth2)
#     lyr_name2 = os.path.splitext(os.path.split(out_shp_pth2)[1])[0]
#     out_lyr2 = out_shp2.CreateLayer(lyr_name2, in_sr, geom_type=geom_type)
#     for i in range(0, in_lyr_defn.GetFieldCount()):
#         field_def = in_lyr_defn.GetFieldDefn(i)
#         out_lyr2.CreateField(field_def)
#
#     for feat in in_lyr:
#         anz = feat.GetField('anz_nutz')
#         if anz <= 1:
#             out_lyr1.CreateFeature(feat)
#         else:
#             out_lyr2.CreateFeature(feat)
#     in_lyr.ResetReading()
#
#     del out_shp1, out_shp2, in_shp
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=20)(joblib.delayed(workFunc)(task) for task in task_lst)
#

# ###################################################################
# ## derive all nu-code and nu-bez combinations 2017-2020
#
# for year in range(2017,2020):
#
#     lst = []
#
#     for ind in range(1,24):
#         print(year, ind)
#         in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(
#             year, ind)
#
#         in_shp = ogr.Open(in_shp_pth)
#         in_lyr = in_shp.GetLayer()
#
#         for feat in in_lyr:
#             nu_code = feat.GetField("nutz_code")
#             nu_name = feat.GetField("beschreibu")
#
#             conc = str(nu_code) + '_' + nu_name
#             if conc not in lst:
#                 lst.append(conc)
#
#         in_lyr.ResetReading()
#
#     pth = r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\nu_code_names_{0}.txt".format(year)
#
#     file = open(pth, "w+")
#
#     for i in lst:
#         file.write(i + '\n')
#     file.close()
#
# ###################################################################
## derive crop codes from years 2005 - 2016

# lst = [0]
#
# for year in range(2007,2008):
#     for ind in range(1,24):
#         print(year, ind)
#         in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(
#             year, ind)
#
#         in_shp = ogr.Open(in_shp_pth)
#         in_lyr = in_shp.GetLayer()
#
#         for feat in in_lyr:
#             use_n = feat.GetField("anz_nutz")
#             if use_n != 0:
#                 for i in range(int(use_n), int(use_n) + 1):
#                     field_name = 'nutz_c' + str(i)
#                     nu_code = feat.GetField(field_name)
#
#                     if nu_code not in lst:
#                         lst.append(nu_code)
#         in_lyr.ResetReading()
#
# pth = r"Q:\FORLand\Clemens\data\vector\InvClassified\BY\nu_code_2007.txt"
#
# file = open(pth, "w+")
#
# for i in lst:
#     file.write(str(i) + '\n')
# file.close()

# year = 2015
# for index in range(1,24):
#     print('\n', index)
#     in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\05_nodups_cleaned_02.shp".format(
#         year, index)
#     shp = ogr.Open(in_shp_pth)
#     lyr = shp.GetLayer()
#
#     lst = vector.getFieldNames(shp)
#
#     print(len(lst), lst[-4:])


###################################################################
## classicy crop types into crop classes

# for task in task_lst:
def workFunc(task):
    df_m = pd.read_excel(r'\\141.20.140.91\SAN_Projects\FORLand\Daten\vector\InVekos\Tables\BY_UniqueCropCodes.xlsx',
                         sheet_name='Classifier_ZALF_pre_2008')

    year = task[0]
    index = task[1]

    print(year, index)

    ## naming convetion: #InVekos_BY_2019_1
    in_shp_pth = r"data\vector\IACS\BV\slices\{0}\InVekos_BY_{0}_{1}_temp\IACS_BV_{0}_{1}.shp".format(year, index)
    in_shp = ogr.Open(in_shp_pth, 1)
    in_lyr = in_shp.GetLayer()

    ## get list of field names
    fname_lst = vector.getFieldNames(in_shp)

    ## column name of Kulturtypen
    fname_ktyp = "crop_class"
    # fname_ws = "ID_WiSo"
    # fname_cl = "ID_HaBl"
    fname_maxclass = "MAXCL_AR1"

    ## check if this column name already exists
    ## if yes, then no new column will be created
    ## if not, then the column will be created and the field name list will be updated

    if fname_ktyp in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_ktyp))
    else:
        in_lyr.CreateField(ogr.FieldDefn(fname_ktyp, ogr.OFTInteger))
        fname_lst = vector.getFieldNames(in_shp)

    # if fname_ws in fname_lst:
    #     print("The field {0} exists already in the layer.".format(fname_ws))
    # else:
    #     in_lyr.CreateField(ogr.FieldDefn(fname_ws, ogr.OFTInteger))
    #     fname_lst = vector.getFieldNames(in_shp)
    #
    # if fname_cl in fname_lst:
    #     print("The field {0} exists already in the layer.".format(fname_cl))
    # else:
    #     in_lyr.CreateField(ogr.FieldDefn(fname_cl, ogr.OFTInteger))
    #     fname_lst = vector.getFieldNames(in_shp)

    if fname_maxclass in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_maxclass))
    else:
        in_lyr.CreateField(ogr.FieldDefn(fname_maxclass, ogr.OFTReal))
        fname_lst = vector.getFieldNames(in_shp)

    for feat in in_lyr:
        use_n = feat.GetField("anz_nutz")
        if use_n == 1:
            fname_code = 'nutz_c1'
            nu_code = int(feat.GetField(fname_code))

            ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
            ktyp = ktyp.iloc[0]  # extracts value from pd Series

            # ws = df_m['ID_WinterSommer'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
            # ws = ws.iloc[0]  # extracts value from pd Series
            #
            # cl = df_m['ID_HalmfruchtBlattfrucht'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
            # cl = cl.iloc[0]

            maxclass = 1.0

        elif use_n > 1:

            ktyp_lst = []
            ws_lst = []
            cl_lst = []

            for i in range(1, int(use_n) + 1):
                fname_code = 'nutz_c' + str(i)
                fname_area = 'nutz_f' + str(i)

                nu_code = int(feat.GetField(fname_code))
                area = feat.GetField(fname_area)
                if area != None:
                    area = float(area)
                else:
                    area = 0

                ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
                ktyp = ktyp.iloc[0]  # extracts value from pd Series
                ktyp_lst.append([ktyp, area])

                # ws = df_m['ID_WinterSommer'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
                # ws = ws.iloc[0]  # extracts value from pd Series
                # ws_lst.append([ws,area])
                #
                # cl = df_m['ID_HalmfruchtBlattfrucht'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
                # cl = cl.iloc[0]
                # cl_lst.append([cl,area])

            df = pd.DataFrame(ktyp_lst, columns=['KTYP', 'AREA'])
            df = df.groupby('KTYP').sum() / df['AREA'].sum()
            maxclass = df['AREA'].max()
            df.reset_index(inplace=True)
            ktyp = df['KTYP'].loc[df['AREA'] > .75]
            if ktyp.shape[0] == 1:
                ktyp = ktyp.iloc[0]
            else:
                ktyp = 70  ## MULTICROPPING

            # df = pd.DataFrame(ws_lst, columns=['WS', 'AREA'])
            # df = df.groupby('WS').sum() / df['AREA'].sum()
            # df.reset_index(inplace=True)
            # ws = df['WS'].loc[df['AREA'] > .5]
            # if ws.shape[0] == 1:
            #     ws = ws.iloc[0]
            # else:
            #     ws = 99 ## MULTICROPPING
            #
            # df = pd.DataFrame(cl_lst, columns=['CL', 'AREA'])
            # df = df.groupby('CL').sum() / df['AREA'].sum()
            # df.reset_index(inplace=True)
            # cl = df['CL'].loc[df['AREA'] > .5]
            # if cl.shape[0] == 1:
            #     cl = cl.iloc[0]
            # else:
            #     cl = 99  ## MULTICROPPING

        else:
            ktyp = 80
            # ws = 99
            # cl = 99
            maxclass = 0.0

        ind = fname_lst.index(fname_ktyp)
        feat.SetField(ind, int(ktyp))
        #
        # ind = fname_lst.index(fname_ws)
        # feat.SetField(ind, int(ws))
        #
        # ind = fname_lst.index(fname_cl)
        # feat.SetField(ind, int(cl))

        ind = fname_lst.index(fname_maxclass)
        feat.SetField(ind, round(maxclass,2))

        in_lyr.SetFeature(feat)

    in_lyr.ResetReading()

    del in_shp, in_lyr

if __name__ == '__main__':
    joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(task) for task in task_lst)

## derive all nu-code and nu-bez combinations 2017-2020

# for task in task_lst:
# def workFunc(task):
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
#     in_shp = ogr.Open(in_shp_pth, 1)
#     in_lyr = in_shp.GetLayer()
#
#     ## get list of field names
#     fname_lst = vector.getFieldNames(in_shp)
#
#     ## column name of Kulturtypen
#     fname_ktyp = "ID_KTYP"
#     fname_ws = "ID_WiSo"
#     fname_cl = "ID_HaBl"
#     fname_maxclass = "MAXCL_AREA"
#
#     ## check if this column name already exists
#     ## if yes, then no new column will be created
#     ## if not, then the column will be created and the field name list will be updated
#
#     if fname_ktyp in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_ktyp))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_ktyp, ogr.OFTInteger))
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
#     if fname_maxclass in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_maxclass))
#     else:
#         in_lyr.CreateField(ogr.FieldDefn(fname_maxclass, ogr.OFTReal))
#         fname_lst = vector.getFieldNames(in_shp)
#
#     for feat in in_lyr:
#         fname_code = 'nutz_code'
#         nu_code = int(feat.GetField(fname_code))
#
#         ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#         ktyp = ktyp.iloc[0]  # extracts value from pd Series
#
#         ws = df_m['ID_WinterSommer'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#         ws = ws.iloc[0]  # extracts value from pd Series
#
#         cl = df_m['ID_HalmfruchtBlattfrucht'].loc[df_m['K_ART'] == nu_code]  # returns a pd Series
#         cl = cl.iloc[0]
#
#         ind = fname_lst.index(fname_ktyp)
#         feat.SetField(ind, int(ktyp))
#
#         ind = fname_lst.index(fname_ws)
#         feat.SetField(ind, int(ws))
#
#         ind = fname_lst.index(fname_cl)
#         feat.SetField(ind, int(cl))
#
#         ind = fname_lst.index(fname_maxclass)
#         feat.SetField(ind, 1.0)
#
#         in_lyr.SetFeature(feat)
#
#     in_lyr.ResetReading()
#
#     del in_shp, in_lyr
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=25)(joblib.delayed(workFunc)(task) for task in task_lst)

# ---------------------

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


