# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import ogr
import os
import pandas as pd

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def GetFieldNames(shp):
    """
    :param shp: Shapefile to get the field names from
    :return: List of all field names
    """
    lyr = shp.GetLayer()
    lyr_def = lyr.GetLayerDefn()

    fname_lst = []
    for i in range(lyr_def.GetFieldCount()):
        fname = lyr_def.GetFieldDefn(i).GetName()
        fname_lst.append(fname)

    return fname_lst
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## open reference table
df_m = pd.read_excel(r"L:\Daten\vector\InVekos\Crops\Unique_crops_all_years_SteinSteinmann.xlsx", sheet_name='Sheet1')

## fill NAs with value 80, which is the code for no data
df_m['ID_KULTURTYP4_SandS'] = df_m['ID_KULTURTYP4_SandS'].fillna(80)
df_m['ID_WinterSommer'] = df_m['ID_WinterSommer'].fillna(-9999)

cl_dict = {
    1:0,
    2:0,
    3:1,
    4:1,
    5:1,
    6:0,
    7:0,
    9:0,
    10:0,
    12:0,
    13:0,
    14:0,
    30:-9999,
    60:1,
    80:-9999,
    99:-9999
}


## loop over shapefiles, add new column and fill it with code for the kulturtyp
for year in range(2012,2019):
    print(year)

    ## open
    shp_name = r"L:\Clemens\data\vector\misc\Inv_NoDups_{0}_testsub.shp".format(year)
    shp = ogr.Open(shp_name, 1)
    lyr = shp.GetLayer()

    ## get list of field names
    fname_lst = GetFieldNames(shp)

    ## column name of Kulturtypen
    fname_ktyp = "KULTURTYP"
    fname_ws = "WintSumm"
    fname_cl = "CerealLeaf"

    ## check if this column name already exists
    ## if yes, then no new column will be created
    ## if not, then the column will be created and the field name list will be updated
    if fname_ktyp in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_ktyp))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_ktyp, ogr.OFTReal))
        fname_lst = GetFieldNames(shp)
    if fname_ws in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_ws))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_ws, ogr.OFTReal))
        fname_lst = GetFieldNames(shp)
    if fname_cl in fname_lst:
        print("The field {0} exists already in the layer.".format(fname_cl))
    else:
        lyr.CreateField(ogr.FieldDefn(fname_cl, ogr.OFTReal))
        fname_lst = GetFieldNames(shp)

    ## loop over features and set kulturtyp and WinterSummer-code depending on the k_art code,
    ## set CerealLeaf-Code depending on kulturtyp
    for f, feat in enumerate(lyr):

        kart = feat.GetField('K_ART')
        kart = int(kart) # convert string to int

        ktyp = df_m['ID_KULTURTYP4_SandS'].loc[df_m['K_ART_FL']==kart] # returns a pd Series
        ktyp = ktyp.iloc[0] # extracts value from pd Series

        ws = df_m['ID_WinterSommer'].loc[df_m['K_ART_FL']==kart] # returns a pd Series
        ws = ws.iloc[0] # extracts value from pd Series
        if ws == 13:
            ws = 1
        elif ws == 12:
            ws = 0
        else:
            ws = -9999

        cl = cl_dict[ktyp]

        feat.SetField(31, ktyp)
        feat.SetField(32, ws)
        feat.SetField(33, cl)
        lyr.SetFeature(feat)
    lyr.ResetReading()
