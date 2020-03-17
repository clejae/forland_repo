# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import ogr
import os
import pandas as pd

import vector
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## open reference table
df_m = pd.read_excel(r"Q:\FORLand\Daten\vector\InVekos\Crops\Tables\CropCodesOfficial_BB_2017and18.xlsx", sheet_name='K_ART 2018')

year = 2018
print(year)

## open
shp_name = r"Clemens\data\vector\InvClassified\Inv_NoDups_{0}.shp".format(year)
shp = ogr.Open(shp_name, 1)
lyr = shp.GetLayer()

## get list of field names
fname_lst = vector.getFieldNames(shp)

## column name of Kulturtypen
fname_kartk = "K_ART_K"

## check if this column name already exists
## if yes, then no new column will be created
## if not, then the column will be created and the field name list will be updated
if fname_kartk in fname_lst:
    print("The field {0} exists already in the layer.".format(fname_kartk))
else:
    field = ogr.FieldDefn(fname_kartk, ogr.OFTString)
    field.SetWidth(254)
    lyr.CreateField(field)
    fname_lst = vector.getFieldNames(shp)

## loop over features and set k_art_k depending on the k_art code
for f, feat in enumerate(lyr):
    fid = feat.GetField("ID")

    kart = feat.GetField('K_ART')
    kart = int(kart) # convert string to int

    print(fid, kart)
    kartk = df_m['K_ART_KULT_final_NoUm'].loc[df_m['K_ART_in_2018_BB'] == kart] # returns a pd Series
    kartk = kartk.iloc[0] # extracts value from pd Series

    length = len(fname_lst)

    feat.SetField(length-1, kartk)
    lyr.SetFeature(feat)
lyr.ResetReading()

