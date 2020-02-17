# Clemens Jänicke
# github Repo: https://github.com/clejae

# --------------------------------------------------------------- LOAD PACKAGES ---------------------------------------------------------------#
import pandas as pd
import os
import ogr
# --------------------------------------------------------------- DEFINE FUNCTIONS ---------------------------------------------------------------#

# --------------------------------------------------------------- GLOBAL VARIABLES ---------------------------------------------------------------#
wd = r'L:\Clemens\data\\'

# --------------------------------------------------------------- LOAD DATA & PROCESSING ---------------------------------------------------------------#
os.chdir(wd)
#### join dataframes

## load data
# # data frame with crop code (cleaned by us)
# df = pd.read_excel(r"L:\Daten\vector\InVekos\Crops\Unique_crops_all_years.xlsx", sheet_name='Sheet1')
# df = df.drop(columns=['Unnamed: 3', 'Unnamed: 4'])
#
# # data frame with crop codes (SteinSteinmann2018)
# df_st = pd.read_excel(r"L:\Daten\vector\InVekos\Crops\K_ART_SteinSteinmann2018.xlsx")
#
# ## merge dataframes
# df_m = pd.merge(df, df_st, left_on='K_ART', right_on='KULTUR_ID (InVeKoS)', how='left')
#
# ## save to excel
# df_m.to_excel(r"L:\Daten\vector\InVekos\Crops\Unique_crops_all_years_SteinSteinmann.xlsx", sheet_name='Sheet1', index=False)

#### calculate area per year per crop code
## open the joined data frame (if script is rerun)
df_m = pd.read_excel(r"L:\Daten\vector\InVekos\Crops\Unique_crops_all_years_SteinSteinmann.xlsx", sheet_name='Sheet1')

## loop over shapefiles and calcuate area per kulturart per year
for year in range(2005,2019):

    ## open shapefile
    shp_name = r"L:\Daten\vector\InVekos\Crops\AKTUELL_Invekos_20191217\Inv_NoDups_{0}.shp".format(year)
    print(shp_name)
    shp = ogr.Open(shp_name)
    lyr = shp.GetLayer()

    ## loop over features of shapefile and extract k_art and size, save in list
    print("Loop over features")
    out_lst = []
    for feat in lyr:
        var = feat.GetField('K_ART')
        size = feat.GetField('Area_H')
        out_lst.append([var, size])
    lyr.ResetReading()

    ## aggregate size per k_art,
    print("Save in dataframe")
    df_out = pd.DataFrame(out_lst, columns=['K_ART', str(year)])    # save list to df
    df_aggr = df_out.groupby('K_ART').sum()                         # aggregation
    df_aggr.reset_index(level=0, inplace=True)                      # convert index to column
    df_aggr['K_ART'] = df_aggr['K_ART'].astype(int)                 # convert type for merging

    ## merge dfs
    df_m = pd.merge(df_m, df_aggr, left_on='K_ART_FL', right_on='K_ART', how='left')
    print("Done")

## save to excel
df_m.to_excel(r"L:\Daten\vector\InVekos\Crops\temp_Unique_crops_all_years_SteinSteinmann.xlsx", sheet_name='Summary')

# --------------------------------------------------------------- UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------------------------------------#

## get field names of a layer
# lyr_def = lyr.GetLayerDefn()
#
# fname_lst = []
# for i in range(lyr_def.GetFieldCount()):
#     fname = lyr_def.GetFieldDefn(i).GetName()
#     fname_lst.append(fname)
#
#     print(fname)

## get unique values of a field in a layer
# var_lst = []
# for feat in lyr:
#     var = feat.GetField('K_ART')
#     var_lst.append(var)
# lyr.ResetReading()
#
# var_set = set(var_lst)
# var_lst = list(var_set)
# #
