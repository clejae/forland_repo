# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import ogr
import os
import pandas as pd
import gdal

import vector
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

pth = r"Daten\vector\InVekos\Niedersachsen\NiSa_OriginalData\UNI_Goettingen\shp\schlaege_2011_130214.shp"
fname_ktyp = "CST_USE"
## open reference table
# df_m = pd.read_excel(r"Daten\vector\InVekos\Niedersachsen\NiSa_OriginalData\UNI_Goettingen\CENTR_ID_2011.xlsx", sheet_name='Tabelle1')
# use_lst = list(df_m['CENTR_ID'])

# shp = ogr.Open(pth, 1)
# lyr = shp.GetLayer()

## get list of field names
# fname_lst = vector.getFieldNames(shp)

## column name of Kulturtypen
#
# ## check if this column name already exists
# ## if yes, then no new column will be created
# ## if not, then the column will be created and the field name list will be updated
# if fname_ktyp in fname_lst:
#     print("The field {0} exists already in the layer.".format(fname_ktyp))
# else:
#     lyr.CreateField(ogr.FieldDefn(fname_ktyp, ogr.OFTInteger))
#     fname_lst = vector.getFieldNames(shp)

## loop over features and set binary column
# for f, feat in enumerate(lyr):
#     fid = feat.GetField("FLIK")
#
#     kart_fname = 'CENTR_ID'
#
#     ## get kulturart code
#     kart = feat.GetField(kart_fname) ##
#     kart = int(kart) # convert string to int
#
#     if kart in use_lst:
#         length = len(fname_lst)
#         feat.SetField(fname_ktyp, 1)
#     else:
#         feat.SetField(fname_ktyp, 0)
#
#     lyr.SetFeature(feat)
# lyr.ResetReading()
#
# del shp, lyr

shp_name = wd + r'Clemens\data\vector\grid\Invekos_grid_LS-Box_15km.shp'
shp = ogr.Open(shp_name, 0)
lyr = shp.GetLayer()
x_min_ext, x_max_ext, y_min_ext, y_max_ext = lyr.GetExtent()

#### Rasterize the IACS data
res = 5
no_data_val = 255

target_ds_pth = r'Clemens\data\raster\mosaics\LS_Fields_2005-2011_Analysis.tif'
vector.rasterizeShape(pth, target_ds_pth, fname_ktyp, [x_min_ext, x_max_ext, y_min_ext, y_max_ext], res, no_data_val, gdal_dtype=gdal.GDT_Byte)
