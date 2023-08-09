# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
from collections import Counter
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def construct_sequences(ordered_crop_lst, split_str = '-'):

    out_lst = [ordered_crop_lst]
    ordered_crop_lst = ordered_crop_lst.split(split_str)
    lst_len = len(ordered_crop_lst)

    for x in range(1, lst_len):
        new_lst = ordered_crop_lst[x:] + ordered_crop_lst[:x]
        new_lst = split_str.join(new_lst)
        out_lst.append(new_lst)

    return out_lst

# ordered_crop_lst = 'OR-WW-SC-WB'
# split_str = '-'
# c_seqs = construct_sequences(ordered_crop_lst)

def get_occurence(df, sequences):

    ## exclude repeating 4-year sequences
    df_ana = df.loc[(df['Sequence'].str.slice(0, 8) != df['Sequence'].str.slice(12, 20))].copy()

    ## loop through orders and extract all sequences
    df_lst = []
    for c_seq in sequences:
        df_sub = df_ana.loc[(df_ana['Sequence'].str.contains(c_seq))].copy()
        df_lst.append(df_sub)
    df_out = pd.concat(df_lst)

    df_out = df_out.drop_duplicates()

    return df_out

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
WD = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
BL_LST = ['BB','SA','LS','BV']
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(WD)

## Prepare df
df_lst = []
for bl in BL_LST:
    pth = r"data\tables\FarmSize-CSTs\{0}_2012-2018_sequences_freq.csv".format(bl)
    df = pd.read_csv(pth)
    df['state'] = bl
    df_lst.append(df)
df = pd.concat(df_lst)
del df_lst
df = df[['ID', 'BNR' , 'CST', 'Sequence', 'Freq_MA', 'Freq_WW', 'Freq_SC', 'state']]

## Calc stats
ordered_crop_lst = 'OR-WW-SC-WB'
print(ordered_crop_lst)
sequences = construct_sequences(ordered_crop_lst)

df1 = df.loc[(df['Sequence'].str.slice(0,8) == df['Sequence'].str.slice(12,20)) &
             (df['Sequence'].str.contains(ordered_crop_lst))].copy()
print(df1[['CST', 'state']].groupby('state').count().reset_index())

df11 = get_occurence(df, sequences)
print(df11[['CST', 'state']].groupby('state').count().reset_index())


ordered_crop_lst = 'WW-OR-WB-MA'
print(ordered_crop_lst)
sequences = construct_sequences(ordered_crop_lst)

df2 = df.loc[(df['Sequence'].str.slice(0,8) == df['Sequence'].str.slice(12,20)) &
             (df['Sequence'].str.contains(ordered_crop_lst))].copy()
print(df2[['CST', 'state']].groupby('state').count().reset_index())
# df2_bv = list(df2['ID'][df2['state'] == 'BV'])

df21 = get_occurence(df, sequences)
print(df21[['CST', 'state']].groupby('state').count().reset_index())


ordered_crop_lst = 'OR-WW-MA-SC'
print(ordered_crop_lst)
sequences = construct_sequences(ordered_crop_lst)

df3 = df.loc[(df['Sequence'].str.slice(0,8) == df['Sequence'].str.slice(12,20)) &
             (df['Sequence'].str.contains(ordered_crop_lst))].copy()
print(df3[['CST', 'state']].groupby('state').count().reset_index())

df31 = get_occurence(df, sequences)
print(df31[['CST', 'state']].groupby('state').count().reset_index())

ordered_crop_lst = 'OR-WW-WB-MA-RY'
print(ordered_crop_lst)
sequences = construct_sequences(ordered_crop_lst)

df4 = df.loc[(df['Sequence'].str.contains(ordered_crop_lst))].copy()
print(df4[['CST', 'state']].groupby('state').count().reset_index())

df41 = get_occurence(df, sequences)
print(df41[['CST', 'state']].groupby('state').count().reset_index())
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


