# github Repo: https://github.com/clejae

# --------------------------------------------------------------- LOAD PACKAGES ---------------------------------------------------------------#
import pandas as pd
import os

# --------------------------------------------------------------- DEFINE FUNCTIONS ---------------------------------------------------------------#

# --------------------------------------------------------------- GLOBAL VARIABLES ---------------------------------------------------------------#

wd = r'L:\Clemens\data\\'

# --------------------------------------------------------------- LOAD DATA & PROCESSING ---------------------------------------------------------------#

os.chdir(wd)

## load data
df = pd.read_excel(r'tables\InVekos\crop_codes_20190308.xlsx', sheet_name='crop_codes_full')

## get unique values of kulturarten (K_ART_N) that are ackerland (AL)
df_al = df[df['K_ART_N']=='AL']
df_uni_artn = pd.DataFrame(df_al.K_ART_KULT.unique().transpose(), columns=['K_ART_N'])
df_uni_artn.to_excel(r'tables\InVekos\k_art_n_unique.xlsx', sheet_name='K_ART_N')

## calculate the area of each kulturart per year
df_kult = df_al.groupby(['ANTRAGSJAH', 'K_ART_KULT'])[['area_ha']].sum()#.unstack()
df_kult = df_kult.unstack()

df_prop_kult = df_kult.div(df_kult.sum(axis=1), axis=0)
df_prop_kult["sum"] = df_prop_kult.sum(axis = 1)

df_prop_kult.to_excel(r'tables\InVekos\area_per_k_art.xlsx', sheet_name='K_ART_N')

## calculate the proportional area of each kulturart per year
df_name = df_al.groupby(['ANTRAGSJAH', 'K_ART_NAME'])[['area_ha']].sum()#.unstack()
df_name = df_name.unstack()

df_prop_name = df_name.div(df_name.sum(axis=1), axis=0)
df_prop_name["sum"] = df_prop_name.sum(axis = 1)
df_prop_kult.to_excel(r'tables\InVekos\area_prop_per_k_art.xlsx', sheet_name='K_ART_N')

#t = df_al.groupby(['ANTRAGSJAH'])[['area_ha']].sum().unstack()
#
#t = df_al.groupby(
#    ['ANTRAGSJAH','K_ART_KULT']
#).agg(
#    {
#        'area_ha':sum,
#        'area_km2':sum
#
#    }
#)