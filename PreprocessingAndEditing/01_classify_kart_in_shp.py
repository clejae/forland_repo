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
df_m = pd.read_excel(r"Daten\vector\InVekos\Crops\Tables\UniqueCropCodes_AllYrsAndBundeslaender.xlsx", sheet_name='UniqueCodes')

## loop over shapefiles, add new column and fill it with code for the kulturtyp
for year in [2018]:
    print(year)

    ## open
    shp_name = r"Clemens\data\vector\InvClassified\Inv_NoDups_{0}.shp".format(year)
    shp = ogr.Open(shp_name, 1)
    lyr = shp.GetLayer()

    ## get list of field names
    fname_lst = vector.getFieldNames(shp)

    ## column name of Kulturtypen
    fname_ktyp = "ID_KTYP"
    fname_ws = "ID_WiSo"
    fname_cl = "ID_HaBl"

    ## check if this column name already exists
    ## if yes, then no new column will be created
    ## if not, then the column will be created and the field name list will be updated
    if fname_ktyp in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_ktyp))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_ktyp, ogr.OFTInteger))
        fname_lst = vector.getFieldNames(shp)
    if fname_ws in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_ws))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_ws, ogr.OFTInteger))
        fname_lst = vector.getFieldNames(shp)
    if fname_cl in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_cl))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_cl, ogr.OFTInteger))
        fname_lst = vector.getFieldNames(shp)

    ## loop over features and set kulturtyp and WinterSummer-code depending on the k_art code,
    ## set CerealLeaf-Code depending on kulturtyp
    for f, feat in enumerate(lyr):
        fid = feat.GetField("ID")

        kart = feat.GetField('K_ART')
        kart = int(kart) # convert string to int

        kart_k = feat.GetField('K_ART_K')

        identifier = '{}_{}'.format(kart, kart_k)
        print(year, fid, identifier)

        ktyp = df_m['ID_KULTURTYP4_FL'].loc[df_m['K_ART_UNIQUE_noUmlaute']==identifier] # returns a pd Series
        ktyp = ktyp.iloc[0] # extracts value from pd Series

        ws = df_m['ID_WinterSommer'].loc[df_m['K_ART_UNIQUE_noUmlaute']==identifier] # returns a pd Series
        ws = ws.iloc[0] # extracts value from pd Series

        cl = df_m['ID_HalmfruchtBlattfrucht'].loc[df_m['K_ART_UNIQUE_noUmlaute']==identifier] # returns a pd Series
        cl = cl.iloc[0]

        length = len(fname_lst)

        feat.SetField(length-3, int(ktyp))
        feat.SetField(length-2, int(ws))
        feat.SetField(length-1, int(cl))
        lyr.SetFeature(feat)
    lyr.ResetReading()
