# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd

## CJs Repo
import general
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def convertSequnceStrToList(str):
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

def croppingFrequency(seq, ct):
    ct_lst = seq.split('-')

    if ct in ct_lst:
        count = ct_lst.count(ct)
    else:
        count = 0

    freq = count/len(ct_lst)
    return freq
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
bl_lst = ['BB']
ct_lst = ['MA','WW','SB','OR','PO','SC','TR','WB','RY','LE','GR','LE','VE','FA','UN','MC','OT']

bl_dict = {'BB':['2005-2011','2008-2014','2012-2018'], #
           'SA':['2008-2014','2012-2018'], #,'2012-2018'
           'BV':['2005-2011','2008-2014','2012-2018'], #,'2012-2018'
           'LS':['2012-2018']}

## columns of output list
col_lst = ['federal state','period']
for ct in ct_lst:
    col_lst.append('TotFreq_{}'.format(ct))
    col_lst.append('PlaFreq_{}'.format(ct))

## output list for main statistics
out_lst = [col_lst]

## loop over federal states
for bl in bl_lst:
    print(bl)
    ## get available periods of federal states
    per_lst = bl_dict[bl]

    ## loop over periods
    for per in per_lst:
        print(bl, per)

        ## list for main stats of bl-per combinations
        ## append federal state and period
        sub_lst = []
        sub_lst.append(bl)
        sub_lst.append(per)

        ## read df
        pth = r'data\tables\FarmSize-CSTs\{0}_{1}_sequences_farm-size.csv'.format(bl, per)
        df = pd.read_csv(pth)
        df['Sequence'] = df['Sequence'].map(convertSequnceStrToList)

        ## for all crop types calculate the cropping frequency
        ## do this row wise and then calc mean over all rows
        for ct in ct_lst:
            df['Freq_{}'.format(ct)] = df['Sequence'].apply(croppingFrequency, args=(ct,))

            ## mean frequency over all fields
            total_freq = df['Freq_{}'.format(ct)].mean()
            sub_lst.append(total_freq)

            ## mean frequency over field where the current crop type actually occurs
            plant_freq = df['Freq_{}'.format(ct)][df['Freq_{}'.format(ct)] != 0.0].mean()
            sub_lst.append(plant_freq)

        ## save df with frequencys
        pth = r'data\tables\FarmSize-CSTs\{0}_{1}_sequences_freq.csv'.format(bl, per)
        df.to_csv(pth, index=False)

        ## save main stats of current bl-per combination in out list
        out_lst.append(sub_lst)
    print(bl, 'done!')

## save out list to csv
general.writeListToCSV(out_lst, out_pth=r"data\tables\FarmSize-CSTs\frequencies_main_stats2.txt")
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#







