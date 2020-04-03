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

bl = 'SA'

## open reference table
df_m = pd.read_excel(r"Daten\vector\InVekos\Crops\Tables\UniqueCropCodes_AllYrsAndBundeslaender.xlsx", sheet_name='UniqueCodes')

## loop over shapefiles, add new column and fill it with code for the kulturtyp
for year in range(2009, 2019): #[2018]:
    print(year)

    if bl == 'BB':
    ## open
        shp_name = r"Clemens\data\vector\InvClassified\Inv_NoDups_{0}.shp".format(year)
    if bl == 'SA':
        shp_name = r"Clemens\data\vector\InvClassified\Antraege{0}.shp".format(year)
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

        if bl == 'BB':
            kart_fname = 'K_ART'
            kartk_fname = 'K_ART_K'
        if bl == 'SA':
            kart_fname = 'NU_CODE'
            kartk_fname = 'NU_BEZ'

        ## get kulturart code
        kart = feat.GetField(kart_fname) ##
        kart = int(kart) # convert string to int

        ## get kulturart name
        ## Although all umlaute were replaced, there are some encoding issues.
        ## After every replaced Umlaut, there is still a character, that can't be decoded by utf-8
        ## By encoding it again and replacing it with '?', I can remove this character
        kart_k = feat.GetField(kartk_fname)
        if kart_k != None:
            kart_k = kart_k.encode('utf8','replace')  # turns string to bytes representation
            print(kart_k)
            kart_k = kart_k.replace(b'\xc2\x9d', b'')   # this byte representations got somehow into some strings
            kart_k = kart_k.replace(b'\xc2\x81', b'')   # this byte representations got somehow into some strings
            kart_k = kart_k.decode('utf8', 'replace') # turns bytes representation to string
            kart_k = kart_k.replace('?', '')
        else:
            pass

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
