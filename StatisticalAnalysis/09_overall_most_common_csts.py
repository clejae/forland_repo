# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def cstNumToStr(cst_value):
    import string
    if cst_value < 100:
        cst_value = str(int(cst_value))
        alphabet = string.ascii_uppercase
        cst_str = alphabet[int(cst_value[0])-1] + str(cst_value[1])
    else:
        cst_str = 'NA'

    return cst_str

def convertSequnceNumsToStrs(str):
    ct_dict = {1 : 'MA',
               2 : 'WW',
               3 : 'SB',
               4 : 'OR',
               5 : 'PO',
               6 : 'SC',
               7 : 'TR',
               9 : 'WB',
               10: 'RY',
               12: 'LE',
               13: 'GR',
               14: 'LE',
               60: 'VE',
               30: 'FA',
               80: 'UN',
               70: 'MC',
               99: 'OT',
               255: 'FA'
               }

    ct_lst = str.split('_')
    ct_lst = [ct_dict[int(i)] for i in ct_lst]
    ct_str = '-'.join(ct_lst)
    return ct_str
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
wd = r"C:\Users\IAMO\Documents\work_data\cst_paper\\"
bl_lst = ['BB','SA','LS','BV']
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

cst_lst = [i+j for i in range(10,100,10) for j in range(1,10)]
cst_lst.append(255)

df_lst = []
## loop over federal states
for bl in bl_lst:
    print(bl)
    pth = r"data\tables\FarmSize-CSTs\{0}_2012-2018_sequences_freq.csv".format(bl)
    df = pd.read_csv(pth)
    df_lst.append(df)

df = pd.concat(df_lst)

## count unique CST-Sequence combinations
df_uni = df.groupby(['CST', 'Sequence'])        # groups CST and Sequences where they are the same
df_uni = df_uni.size()                          # returns size of unique groups
df_uni = df_uni.reset_index()                   # resets the columns
df_uni = df_uni.rename(columns={0: 'count'})    # provides a meaningfull name to last col
df_uni = df_uni.sort_values('count', ascending=False)

df_uni = df_uni[df_uni['CST'] != 255]

## count occurences of CSTs
df_cst_count = df_uni.groupby(['CST'])['count'].agg('sum')
df_cst_count = df_cst_count.reset_index()
df_cst_count.columns = ['cst_count_order','cst_count']
df_cst_count = df_cst_count.sort_values('cst_count', ascending=False)
df_cst_count = df_cst_count[:20].copy()

## areas of csts per tiles
df_lst = []
for bl in bl_lst:
    pth = r"data\tables\crop_sequence_types\{0}\{0}_2012-2018_AreaOfCropSequenceTypes_clean.xlsx".format(bl)
    df = pd.read_excel(pth, sheet_name='AreaPerTile')
    df_lst.append(df)
df_tiles = pd.concat(df_lst)

## most common csts by area
total_areas = [df_tiles[str(cst)].sum() * 0.0025 for cst in cst_lst]
df_cst_area = pd.DataFrame(columns=["CST", "area"])
df_cst_area["CST"] = cst_lst
df_cst_area["area"] = total_areas
df_cst_area = df_cst_area[df_cst_area['CST'] != 255]
df_cst_area = df_cst_area.sort_values('area', ascending=False)
df_cst_area = df_cst_area[:20]
df_cst_area.columns = ['cst_area_order', 'cst_area']

share_lst = []
## shares of csts
for bl in bl_lst:
    pth = r"data\tables\crop_sequence_types\{0}\{0}_CSTArea.xlsx".format(bl)
    df = pd.read_excel(pth, sheet_name='AreaAggregated')
    df = df[df['Period'] == '2012-2018']
    total_area = df['Area'].sum()
    sub_lst = list(df['Area'] / total_area * 100)
    share_lst.append(sub_lst)

df_shares = pd.DataFrame(data=share_lst, index=bl_lst)
df_shares.columns = cst_lst[:81]

## most common csts by count
## and most common specific sequences and their counts
df_cst_count['area_cst'] = ""
df_cst_count['main_seq'] = ""
df_cst_count['seq_count'] = ""
df_cst_count['example_tile'] = ""
df_cst_count['example_BB'] = ""
df_cst_count['example_SA'] = ""
df_cst_count['example_LS'] = ""
df_cst_count['example_BV'] = ""
df_cst_count['focus_state'] = ""

for c, cst in enumerate(df_cst_count['cst_count_order']):
    print(cst)

    ## calculate the total area of the current cst
    area_sm = df_tiles[str(cst)].sum()
    area = area_sm / 10000
    df_cst_count['area_cst'].iloc[c] = area

    ## subset df with unique cst-sequence combinations for current cst
    df = df_uni[df_uni['CST'] == cst].copy()

    ## get most common sequence for current cst and its count
    df_cst_count['main_seq'].iloc[c] = df['Sequence'].iloc[0]
    df_cst_count['seq_count'].iloc[c] = df['count'].iloc[0]

    ## get federal state with highest share
    df_cst_count['focus_state'].iloc[c] = df_shares.index[df_shares[cst] == df_shares[cst].max()][0]

    ## get an example tile, where the current cst occurs very often
    ## do this also for all federal states separately
    df_cst_count['example_tile'].iloc[c] = df_tiles['Tile'][df_tiles[str(cst)] == df_tiles[str(cst)].max()].iloc[0]
    for d, df_bl in enumerate(df_lst):
        bl = bl_lst[d]
        df_cst_count['example_{0}'.format(bl)].iloc[c] = df_bl['Tile'][df_bl[str(cst)] == df_bl[str(cst)].max()].iloc[0]

df_out = df_cst_count.copy()
df_out['cst_area_order'] = list(df_cst_area['cst_area_order'])
df_out['area2'] = list(df_cst_area['cst_area'])

df_out['cst_count_order'] = df_out['cst_count_order'].map(cstNumToStr)
df_out['cst_area_order'] = df_out['cst_area_order'].map(cstNumToStr)

pth = r"data\tables\most_common_sequences\most_common_sequences2.csv"
df_out.to_csv(pth, index = False)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#