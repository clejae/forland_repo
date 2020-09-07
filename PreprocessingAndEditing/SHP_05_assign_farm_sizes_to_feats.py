# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import pandas as pd
import vector
import matplotlib.pyplot as plt
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

year = 2018

## column names of farm sizes excel
col_names = ['Betrieb','Area','BL']
out_lst = [col_names]

## column name of farm sizes column that will be created in shapefile
fname_bgr = 'BTR_GROESS'
fname_bgr_cl = 'BTR_CLASS'

## field names of farm number (Betriebsnummern) and field sizes for the respective federal states
fname_dict = {'BB':['BNR_ZD','GROESSE'],
              'SA':['btnr','PARZ_FLAE'],
              'LS':['REGISTRIER','AREA_ha'],
              'BV':['bnrhash','flaeche']}

# ### LS, SA, BB
# ## extract field sizes and aggregate them per farm
# ## write farm sizes to excel file if file not already exists
# for bl in ['LS']:
#     print(bl)
#     fname_btr = fname_dict[bl][0]
#     fname_area = fname_dict[bl][1]
#     df_pth = r'tables\FarmSizes\farm_sizes_{0}_{1}.xlsx'.format(bl, year)
#     if not os.path.exists(df_pth):
#         lst = []
#         pth = r'vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
#         shp = ogr.Open(pth)
#         lyr = shp.GetLayer()
#         for feat in lyr:
#             betr = str(feat.GetField(fname_btr))
#             area = float(feat.GetField(fname_area))
#             lst.append([betr, area, bl])
#         lyr.ResetReading()
#
#         df = pd.DataFrame(lst)
#         df.columns = col_names
#         df = df.groupby(['Betrieb', 'BL'])[['Area']].sum()
#         df = df.reset_index()
#         with pd.ExcelWriter(df_pth) as writer:
#             df.to_excel(writer, sheet_name ='{0}_{1}_FarmSizes'.format(bl, year), index=False)
#         del shp, lyr
#     else:
#         df = pd.read_excel(df_pth)
#
#     ## assign farm sizes to fields in shapefile
#     pth = 'vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
#     shp = ogr.Open(pth, 1)
#     lyr = shp.GetLayer()
#     fname_lst = vector.getFieldNames(shp)
#
#     ## create column in layer
#     if fname_bgr in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_bgr))
#     else:
#         lyr.CreateField(ogr.FieldDefn(fname_bgr, ogr.OFTReal))
#         fname_lst = vector.getFieldNames(shp)
#
#     ## assign field sizes to each feature
#     for f, feat in enumerate(lyr):
#         betr = str(feat.GetField(fname_btr))
#         betr_gr =  df['Area'].loc[df['Betrieb'] == betr] # returns a pd Series
#         betr_gr = betr_gr.iloc[0] # extracts value from pd Series
#         ind = fname_lst.index(fname_bgr)
#         feat.SetField(fname_bgr, betr_gr)
#         lyr.SetFeature(feat)
#     lyr.ResetReading()

## BV
# bl = 'BV'
# print(bl)
# fname_btr = fname_dict[bl][0]
# fname_area = fname_dict[bl][1]
# df_pth = r'tables\FarmSizes\farm_sizes_{0}_{1}.xlsx'.format(bl, year)
# if not os.path.exists(df_pth):
#     lst = []
#     pth = r'vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
#     shp = ogr.Open(pth)
#     lyr = shp.GetLayer()
#     for feat in lyr:
#         betr = str(feat.GetField(fname_btr))
#         area = float(feat.GetField(fname_area))
#         lst.append([betr, area, bl])
#     lyr.ResetReading()
#
#     df = pd.DataFrame(lst)
#     df.columns = col_names
#     df = df.groupby(['Betrieb', 'BL'])[['Area']].sum()
#     df = df.reset_index()
#     with pd.ExcelWriter(df_pth) as writer:
#         df.to_excel(writer, sheet_name ='{0}_{1}_FarmSizes'.format(bl, year), index=False)
#     del shp, lyr
# else:
#     pass
#
# ## assign farm sizes to fields in shapefile
# task_lst = [(year, ind) for year in range(2018,2019) for ind in range(1,24)]
# def workFunc(task):
#
#     year = task[0]
#     index = task[1]
#     print('################\n{0}, {1}\n################'.format(year, index))
#
#     df_pth = r'tables\FarmSizes\farm_sizes_{0}_{1}.xlsx'.format(bl, year)
#     df = pd.read_excel(df_pth)
#
#     pth =  r"vector\IACS\BV\slices\{0}\InVekos_BY_{0}_{1}_temp\IACS_BV_{0}_{1}.shp".format(year, index)
#     shp = ogr.Open(pth, 1)
#     lyr = shp.GetLayer()
#     fname_lst = vector.getFieldNames(shp)
#
#     ## create column in layer
#     if fname_bgr in fname_lst:
#         print("The field {0} exists already in the layer.".format(fname_bgr))
#     else:
#         lyr.CreateField(ogr.FieldDefn(fname_bgr, ogr.OFTReal))
#         fname_lst = vector.getFieldNames(shp)
#
#     ## assign field sizes to each feature
#     for f, feat in enumerate(lyr):
#         betr = str(feat.GetField(fname_btr))
#         betr_gr =  df['Area'].loc[df['Betrieb'] == betr] # returns a pd Series
#         betr_gr = betr_gr.iloc[0] # extracts value from pd Series
#         ind = fname_lst.index(fname_bgr)
#         feat.SetField(fname_bgr, betr_gr)
#         lyr.SetFeature(feat)
#     lyr.ResetReading()
#
# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=23)(joblib.delayed(workFunc)(task) for task in task_lst)


## Assign farm size classes to features
## LS, SA, BB


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


# df = pd.DataFrame(out_lst)
# df.columns = df.iloc(0)[0]
# df = df.drop([0])
# df.info()
#
# df['Betrieb'] = df['Betrieb'].astype('str')
# df['Area'] = df['Area'].astype('float')
# df['BL'] = df['BL'].astype('str')
#
# pd.set_option("display.max.columns", None)
# df.describe()
#
# df_area = df.groupby(['Betrieb','BL'])[['Area']].sum()
# df_area = df_area.reset_index()
#
# df_area.describe()
# ax = df_area[df_area['BL'] == 'BV'].plot.box()
#
# fig, axs = plt.subplots(1, 4, sharey=True)
# axs[0].boxplot(df_area['Area'][df_area['BL'] == 'SA'], showfliers=False)
# axs[0].set_title('SA')
# axs[1].boxplot(df_area['Area'][df_area['BL'] == 'BB'], showfliers=False)
# axs[1].set_title('BB')
# axs[2].boxplot(df_area['Area'][df_area['BL'] == 'LS'], showfliers=False)
# axs[2].set_title('LS')
# axs[3].boxplot(df_area['Area'][df_area['BL'] == 'BV'], showfliers=False)
# axs[3].set_title('BV')

## BB
# org = feat.GetField('Oeko')
# cattle = feat.GetField('Rinder')
# pigs = feat.GetField('Schwein')
# sheep = feat.GetField('Schafe')
# poultry = feat.GetField('Gfl_fc_')
#

# df['Organic'] = df['Organic'].astype('int')
# df['Cattle'] = df['Cattle'].str.replace(',','')
# df['Cattle'] = df['Cattle'].astype('float')
# df['Pigs'] = df['Pigs'].str.replace(',','')
# df['Pigs'] = df['Pigs'].astype('float')
# df['Sheep'] = df['Sheep'].str.replace(',','')
# df['Sheep'] = df['Sheep'].astype('float')
# df['Poultry'] = df['Poultry'].str.replace(',','')
# df['Poultry'] = df['Poultry'].astype('float')
#
# df_oeko = df.groupby(['Betrieb'])[['Organic']].mean()
# df_oeko = df_oeko.reset_index()