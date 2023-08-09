# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import numpy as np
from osgeo import gdal
import time
import json
import pandas as pd
import operator
import plotly.graph_objects as go
from functools import reduce
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER INPUT ------------------------------------------------#
WD = r'C:\Users\IAMO\Documents\work_data\cst_paper'

FS_DICT = {'Brandenburg': {'abbreviation': 'BB',
                           'periods': [1, 2, 3]},
           'Bavaria': {'abbreviation': 'BV',
                       'periods': [1, 2, 3]},
           'Lower Saxony': {'abbreviation': 'LS',
                            'periods': [3]},
           'Saxony-Anhalt': {'abbreviation': 'SA',
                             'periods': [2, 3]}}

PERIODS = ['2005-2011', '2008-2014', '2012-2018']


# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
os.chdir(WD)

## 1. Loop over periods
## 2. For each federal state (and tile), check if csts are available (for current period)
## 3. If not use 14 as indication for no availabe csts in this year (create array), if yes use existing array
## 4. Reclassify 255 to 15 as indication "no csts classified"
## 4. Multiply period1 * 10000, period2 *100 and period3*1
## 6. Add all arrays up
## 7. Count occurrences

def count_function(fs_abbr, periods):

    ## Create output dictionary
    out_dict = {}

    with open(r'data\raster\tile_list_{}.txt'.format(fs_abbr)) as file:
        tiles_lst = file.readlines()
    tiles_lst = [item.strip() for item in tiles_lst]

    for t, tile in enumerate(tiles_lst):
        ## Loop over periods and open cst-raster
        cst_lst = []
        for i, period in enumerate(periods):

            factor = {0: 10000, 1: 100, 2: 1}[i]

            ## For each federal state (and tile), check if csts are available (for current period)
            ## If not use 14 as indication for no availabe csts in this year (create array), if yes use existing array
            cst_pth = rf'data\raster\grid_15km\{tile}\{fs_abbr}_{period}_CropSeqType_clean.tif'
            if os.path.exists(cst_pth):
                cst_ras = gdal.Open(cst_pth)
                cst_arr = cst_ras.ReadAsArray()
            else:
                ## 14 is a cst that cannot occur. I use it to indicate that in this state there were not csts
                ## calculated
                cst_arr = np.zeros((3000, 3000)) + 14

            ## 15 cannot occur. I use it to replace 255 so that all values have only two digits
            cst_arr[cst_arr == 255] = 15
            cst_arr = cst_arr.astype(np.int32)

            ## multiply cst array with factor
            cst_arr = cst_arr * factor

            cst_lst.append(cst_arr)

        conc_arr = np.sum(cst_lst, axis=0)

        ## Count the occurrence of all unique concatenated csts
        unique, counts = np.unique(conc_arr, return_counts=True)
        tile_dict = dict(zip(unique, counts))
        for cst in tile_dict:
            if str(cst) not in out_dict:
                out_dict[str(cst)] = tile_dict[cst]
            else:
                out_dict[str(cst)] += tile_dict[cst]

        print(fs_abbr, tile, "done!")

    for key in out_dict:
        out_dict[key] = str(out_dict[key])

    json_out = rf'data\tables\changes_in_sequences\{fs_abbr}_changes_in_sequence.json'
    with open(json_out, "w") as outfile:
        json.dump(out_dict, outfile, indent=4)


def analyze_function(pth, fs_abbr, out_folder=None):

    with open(pth) as json_file:
        count_dict = json.load(json_file)

    ## for each count-dictionary:
    ## delete key 151515
    for k in ['151515', '141515']:
        if k in count_dict:
            count_dict.pop(k)

    ana_dict = {}

    ## This is the area of each period for which a cst could be identified
    area_per1 = 0
    area_per2 = 0
    area_per3 = 0

    ## separate each keys at 2. and 4. digit (xx-xx-xx)
    ## in each key: for each two number digit replace 15 with 00 and 14 with xx
    for key in count_dict:
        k1 = key[:2]
        k2 = key[2:4]
        k3 = key[4:]

        if k1 == '15':
            k1 = '00'
        elif k1 == '14':
            k1 = 'xx'
        else:
            area_per1 += int(count_dict[key])

        if k2 == '15':
            k2 = '00'
        elif k2 == '14':
            k2 = 'xx'
        else:
            area_per2 += int(count_dict[key])

        if k3 == '15':
            k3 = '00'
        elif k3 == '14':
            k3 = 'xx'
        else:
            area_per3 += int(count_dict[key])

        newkey = k1 + '-' + k2 + '-' + k3
        ana_dict[newkey] = int(count_dict[key])

    ## create ranking of all change sequences
    ana_dict = dict(sorted(ana_dict.items(), key=operator.itemgetter(1), reverse=True))

    ## calculate shares of change sequences
    total_area = sum(ana_dict.values())
    share_dict = {key: ana_dict[key] / total_area for key in ana_dict}

    ## identify biggest change sequences that make up > 50/75% --> create table
    big_dict = {}
    cum_share = 0
    for i, key in enumerate(share_dict):
        if cum_share > .5:
            break
        cum_share += share_dict[key]
        big_dict[key] = cum_share

    ## calculate area of structural types (first digit of each two number digits)
    ## for each change sequence
    str_dict = {}
    fct_dict = {}

    ana_l_dict1 = {}
    str_l_dict1 = {}
    fct_l_dict1 = {}

    ana_l_dict2 = {}
    str_l_dict2 = {}
    fct_l_dict2 = {}

    ana_l_dict3 = {}
    str_l_dict3 = {}
    fct_l_dict3 = {}

    for key in ana_dict:
        ks = key.split('-')
        k1 = ks[0]
        k2 = ks[1]
        k3 = ks[2]

        strkey = k1[0] + '-' + k2[0] + '-' + k3[0]
        fctkey = k1[1] + '-' + k2[1] + '-' + k3[1]

        if strkey not in str_dict:
            str_dict[strkey] = ana_dict[key]
        else:
            str_dict[strkey] += ana_dict[key]

        if fctkey not in fct_dict:
            fct_dict[fctkey] = ana_dict[key]
        else:
            fct_dict[fctkey] += ana_dict[key]

        ## for plotting
        kl1 = k1 + 'a' + '-' + k2 + 'b'
        kl2 = k2 + 'b' + '-' + k3 + 'c'
        kl3 = k1 + 'a' + '-' + k3 + 'c'
        if kl1 not in ana_l_dict1:
            ana_l_dict1[kl1] = ana_dict[key]
        else:
            ana_l_dict1[kl1] += ana_dict[key]
        if kl2 not in ana_l_dict2:
            ana_l_dict2[kl2] = ana_dict[key]
        else:
            ana_l_dict2[kl2] += ana_dict[key]
        if kl3 not in ana_l_dict3:
            ana_l_dict3[kl3] = ana_dict[key]
        else:
            ana_l_dict3[kl3] += ana_dict[key]

        ## for plotting
        kstr1 = k1[0] + 'a' + '-' + k2[0] + 'b'
        kstr2 = k2[0] + 'b' + '-' + k3[0] + 'c'
        kstr3 = k1[0] + 'a' + '-' + k3[0] + 'c'
        if kstr1 not in str_l_dict1:
            str_l_dict1[kstr1] = ana_dict[key]
        else:
            str_l_dict1[kstr1] += ana_dict[key]
        if kstr2 not in str_l_dict2:
            str_l_dict2[kstr2] = ana_dict[key]
        else:
            str_l_dict2[kstr2] += ana_dict[key]
        if kstr3 not in str_l_dict3:
            str_l_dict3[kstr3] = ana_dict[key]
        else:
            str_l_dict3[kstr3] += ana_dict[key]

        ## for plotting
        kfct1 = k1[1] + 'a' + '-' + k2[1] + 'b'
        kfct2 = k2[1] + 'b' + '-' + k3[1] + 'c'
        kfct3 = k1[1] + 'a' + '-' + k3[1] + 'c'
        if kfct1 not in fct_l_dict1:
            fct_l_dict1[kfct1] = ana_dict[key]
        else:
            fct_l_dict1[kfct1] += ana_dict[key]
        if kfct2 not in fct_l_dict2:
            fct_l_dict2[kfct2] = ana_dict[key]
        else:
            fct_l_dict2[kfct2] += ana_dict[key]
        if kfct3 not in fct_l_dict3:
            fct_l_dict3[kfct3] = ana_dict[key]
        else:
            fct_l_dict3[kfct3] += ana_dict[key]

    def create_df_from_dict(in_dict, out_pth=None):
        df = pd.DataFrame.from_dict(data=in_dict, orient='index')
        if df.empty:
            return df
        df.reset_index(inplace=True)
        df.columns = ['change sequence', 'px_count']
        df.sort_values(by='px_count', inplace=True, ascending=False)
        df['share'] = round(df['px_count'] / df['px_count'].sum() * 100, 1)
        df['cum_share'] = df['share'].cumsum()
        if out_pth:
            df.to_csv(out_pth, sep=';')
        return df

    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences.csv'
    df_orig = create_df_from_dict(ana_dict, out_pth)
    out_pth = out_folder + f'/{fs_abbr}-structural_change_sequences.csv'
    df_str = create_df_from_dict(str_dict, out_pth)
    out_pth = out_folder + f'/{fs_abbr}-functional_change_sequences.csv'
    df_fct = create_df_from_dict(fct_dict, out_pth)

    ## get total area, including areas that are newly cultivated or abandoned
    ana_l_dict1_area = ana_l_dict1.copy()
    ana_l_dict2_area = ana_l_dict2.copy()
    ana_l_dict3_area = ana_l_dict3.copy()

    for key in ["00a-00b", "xxa-xxb", "xxa-00b"]:
        if key in ana_l_dict1_area:
            ana_l_dict1_area.pop(key)
    for key in ["00b-00c", "xxb-xxc", "xxb-00c"]:
        if key in ana_l_dict2_area:
            ana_l_dict2_area.pop(key)
    for key in ["00a-00c", "xxa-xxc", "xxa-00c"]:
        if key in ana_l_dict3_area:
            ana_l_dict3_area.pop(key)

    total_area1 = sum(ana_l_dict1_area.values())
    total_area2 = sum(ana_l_dict2_area.values())
    total_area3 = sum(ana_l_dict3_area.values())

    def create_plot_lists_from_dict(in_dict):
        labels = []
        source = []
        target = []
        value = []

        label_to_index = {}

        i = 0
        for key in in_dict:
            ks = key.split('-')
            k1 = ks[0]
            k2 = ks[1]

            if k1 not in labels:
                labels.append(k1)
                label_to_index[k1] = i
                i += 1

            if k2 not in labels:
                labels.append(k2)
                label_to_index[k2] = i
                i += 1

            source.append(label_to_index[k1])
            target.append(label_to_index[k2])
            value.append(in_dict[key])

        link = {'source': source,
                'target': target,
                'value': value}

        return link, labels

    def plot_sankey(link, labels, title):
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=link)])

        fig.update_layout(title_text=title, font_size=10)
        fig.show()

    ## Exclude all change sequence where in one period there was no cst
    # ana_l_dict2 = {key: ana_l_dict2[key] for key in ana_l_dict2 if '0' not in key}
    # str_l_dict2 = {key: str_l_dict2[key] for key in str_l_dict2 if '0' not in key}
    # fct_l_dict2 = {key: fct_l_dict2[key] for key in fct_l_dict2 if '0' not in key}

    ## exclude stable change sequences
    def exclude_stable_change_sequences(in_dict):
        out_dict = {}
        stable_dict = {"stable_total_area": 0}
        for key in in_dict:
            ks = key.split('-')
            ks = [k[:-1] for k in ks]
            ks = list(set(ks))
            if len(ks) > 1:
                out_dict[key] = in_dict[key]
            else:
                if ks != ['00']:
                    stable_dict["stable_total_area"] += in_dict[key]
                if ks[0] not in stable_dict:
                    stable_dict["stable_" + ks[0]] = in_dict[key]
                else:
                    stable_dict["stable_" + ks[0]] += in_dict[key]

        return out_dict, stable_dict

    ana_l_dict1_stable_excl, ana_stable_dict1 = exclude_stable_change_sequences(ana_l_dict1)
    str_l_dict1_stable_excl, str_stable_dict1 = exclude_stable_change_sequences(str_l_dict1)
    fct_l_dict1_stable_excl, fct_stable_dict1 = exclude_stable_change_sequences(fct_l_dict1)

    ana_l_dict2_stable_excl, ana_stable_dict2 = exclude_stable_change_sequences(ana_l_dict2)
    str_l_dict2_stable_excl, str_stable_dict2 = exclude_stable_change_sequences(str_l_dict2)
    fct_l_dict2_stable_excl, fct_stable_dict2 = exclude_stable_change_sequences(fct_l_dict2)

    ana_l_dict3_stable_excl, ana_stable_dict3 = exclude_stable_change_sequences(ana_l_dict3)
    str_l_dict3_stable_excl, str_stable_dict3 = exclude_stable_change_sequences(str_l_dict3)
    fct_l_dict3_stable_excl, fct_stable_dict3 = exclude_stable_change_sequences(fct_l_dict3)

    ## for complete sequences identify 10 or 20 largest changes
    # link_ana, labels_ana = create_plot_lists_from_dict(ana_l_dict2)
    # plot_sankey(link_ana, labels_ana, "Complete CSTs")

    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict1)
    # plot_sankey(link_str, labels_str, f"{fs_abbr}-Structural diversity - all changes - 1.-2.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict1)
    # plot_sankey(link_fct, labels_fct, f"{fs_abbr}-Functional diversity - all changes - 1.-2.")
    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict2)
    # plot_sankey(link_str, labels_str, f"{fs_abbr}-Structural diversity - all changes - 2.-3.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict2)
    # plot_sankey(link_fct, labels_fct, f"{fs_abbr}-Functional diversity - all changes - 2.-3.")
    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict3)
    # plot_sankey(link_str, labels_str, f"{fs_abbr}-Structural diversity - all changes - 1.-3.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict3)
    # plot_sankey(link_fct, labels_fct, f"{fs_abbr}-Functional diversity - all changes - 1.-3.")


    ## identifiy largest losses and largest gains
    def identify_largest_changes(in_dict):
        out_dict = {}
        loss_key_lst = []
        gain_key_lst = []
        for key in in_dict:
            ks = key.split('-')
            k_loss = ks[0]
            k_gain = ks[1]
            if k_loss not in loss_key_lst:
                loss_key_lst.append(k_loss)
            if k_gain not in gain_key_lst:
                gain_key_lst.append(k_gain)

        for k in loss_key_lst:
            loss_dict = {}
            for key in in_dict:
                ks = key.split('-')
                k_loss = ks[0]
                if k_loss == k:
                    loss_dict[key] = in_dict[key]
            max_loss_key = max(loss_dict, key=loss_dict.get)
            out_dict[max_loss_key] = loss_dict[max_loss_key]

        for k in gain_key_lst:
            gain_dict = {}
            for key in in_dict:
                ks = key.split('-')
                k_gain = ks[-1]
                if k_gain == k:
                    gain_dict[key] = in_dict[key]
            max_gain_key = max(gain_dict, key=gain_dict.get)
            out_dict[max_gain_key] = gain_dict[max_gain_key]

        return out_dict

    str_l_dict1b = identify_largest_changes(str_l_dict1)
    fct_l_dict1b = identify_largest_changes(fct_l_dict1)
    str_l_dict2b = identify_largest_changes(str_l_dict2)
    fct_l_dict2b = identify_largest_changes(fct_l_dict2)
    str_l_dict3b = identify_largest_changes(str_l_dict3)
    fct_l_dict3b = identify_largest_changes(fct_l_dict3)

    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict1b)
    # plot_sankey(link_str, labels_str, f'{fs_abbr}-Structural diversity - largest changes - 1.-2.')
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict1b)
    # plot_sankey(link_fct, labels_fct, f'{fs_abbr}-Functional diversity - largest changes - 1.-2.')
    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict2b)
    # plot_sankey(link_str, labels_str, f'{fs_abbr}-Structural diversity - largest changes - 2.-3.')
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict2b)
    # plot_sankey(link_fct, labels_fct, f'{fs_abbr}-Functional diversity - largest changes - 2.-3.')
    # link_str, labels_str = create_plot_lists_from_dict(str_l_dict3b)
    # plot_sankey(link_str, labels_str, f'{fs_abbr}-Structural diversity - largest changes - 1.-3.')
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_l_dict3b)
    # plot_sankey(link_fct, labels_fct, f'{fs_abbr}-Functional diversity - largest changes - 1.-3.')

    ## Calculate net fluxes between csts

    def calculate_net_fluxes(in_dict):
        out_dict = {}
        done_lst = []
        for key in in_dict:
            if key not in done_lst:
                ks = key.split('-')
                keys = [k[:-1] for k in ks]
                exts = [k[-1] for k in ks]
                newkey = keys[1]+exts[0] + '-' + keys[0]+exts[1]

                if newkey in in_dict:
                    change = in_dict[key] - in_dict[newkey]
                    if change > 0:
                        out_dict[key] = change
                    else:
                        out_dict[newkey] = -change
                else:
                    out_dict[key] = in_dict[key]

                done_lst.append(key)
                done_lst.append(newkey)

        return out_dict

    ana_flux_dict1 = calculate_net_fluxes(ana_l_dict1)
    str_flux_dict1 = calculate_net_fluxes(str_l_dict1)
    fct_flux_dict1 = calculate_net_fluxes(fct_l_dict1)
    ana_flux_dict2 = calculate_net_fluxes(ana_l_dict2)
    str_flux_dict2 = calculate_net_fluxes(str_l_dict2)
    fct_flux_dict2 = calculate_net_fluxes(fct_l_dict2)
    ana_flux_dict3 = calculate_net_fluxes(ana_l_dict3)
    str_flux_dict3 = calculate_net_fluxes(str_l_dict3)
    fct_flux_dict3 = calculate_net_fluxes(fct_l_dict3)

    # link_str, labels_str = create_plot_lists_from_dict(str_flux_dict1)
    # plot_sankey(link_str, labels_str, "Structural diversity - net changes - 1.-2.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_flux_dict1)
    # plot_sankey(link_fct, labels_fct, "Functional diversity - net changes - 1.-2.")
    # link_str, labels_str = create_plot_lists_from_dict(str_flux_dict2)
    # plot_sankey(link_str, labels_str, "Structural diversity - net changes - 2.-3.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_flux_dict2)
    # plot_sankey(link_fct, labels_fct, "Functional diversity - net changes - 2.-3.")
    # link_str, labels_str = create_plot_lists_from_dict(str_flux_dict3)
    # plot_sankey(link_str, labels_str, "Structural diversity - net changes - 1.-3.")
    # link_fct, labels_fct = create_plot_lists_from_dict(fct_flux_dict3)
    # plot_sankey(link_fct, labels_fct, "Functional diversity - net changes - 1.-3.")

    df_orig1 = create_df_from_dict(ana_flux_dict1)
    df_str1 = create_df_from_dict(str_flux_dict1)
    df_fct1 = create_df_from_dict(fct_flux_dict1)
    df_orig2 = create_df_from_dict(ana_flux_dict2)
    df_str2 = create_df_from_dict(str_flux_dict2)
    df_fct2 = create_df_from_dict(fct_flux_dict2)
    df_orig3 = create_df_from_dict(ana_flux_dict3)
    df_str3 = create_df_from_dict(str_flux_dict3)
    df_fct3 = create_df_from_dict(fct_flux_dict3)

    def classify_structural_and_functional_change(df, out_pth):

        if df.empty:
            return df

        df["source_str"] = df["change sequence"].apply(lambda row: row.split('-')[0][0])
        df["source_str"] = df["source_str"].str.replace("x", "0")
        df["target_str"] = df["change sequence"].apply(lambda row: row.split('-')[1][0])
        df["target_str"] = df["target_str"].str.replace("x", "0")
        df["source_fct"] = df["change sequence"].apply(lambda row: row.split('-')[0][1])
        df["source_fct"] = df["source_fct"].str.replace("x", "0")
        df["target_fct"] = df["change sequence"].apply(lambda row: row.split('-')[1][1])
        df["target_fct"] = df["target_fct"].str.replace("x", "0")

        df["change_str"] = df["target_str"].astype(int) - df["source_str"].astype(int)

        bins = [-99, -1, 0, 99]
        labels = ["declining", "stable", "increasing"]

        df["structural_change"] = pd.cut(df["change_str"], bins, labels=labels)
        df["structural_change"] = df["structural_change"].astype(str)
        df.loc[df["source_str"] == "0", "structural_change"] = "newly classified"
        df.loc[df["target_str"] == "0", "structural_change"] = "no 2nd classification"

        df["change_fct"] = df["target_fct"].astype(int) - df["source_fct"].astype(int)
        df["change_fct_str"] = df["source_fct"] + df["target_fct"]

        sprwin_change_classification = {
            '15': 'Increasing spring shares to sw balance',
            '25': 'Stable sw balance',
            '35': 'Decreasing spring shares to sw balance',
            '45': 'Increasing spring shares to sw balance',
            '65': 'Decreasing spring shares to sw balance',
            '75': 'Increasing spring shares to sw balance',
            '85': 'Stable sw balance',

            '95': 'Decreasing spring shares to sw balance',
            '13': 'Increasing spring shares to s dominance',
            '23': 'Increasing spring shares to s dominance',
            '43': 'Increasing spring shares to s dominance',
            '53': 'Increasing spring shares to s dominance',
            '73': 'Increasing spring shares to s dominance',
            '83': 'Increasing spring shares to s dominance',
            '16': 'Increasing spring shares to s dominance',
            '26': 'Increasing spring shares to s dominance',
            '46': 'Increasing spring shares to s dominance',
            '56': 'Increasing spring shares to s dominance',
            '76': 'Increasing spring shares to s dominance',
            '86': 'Increasing spring shares to s dominance',
            '19': 'Increasing spring shares to s dominance',
            '29': 'Increasing spring shares to s dominance',
            '49': 'Increasing spring shares to s dominance',
            '59': 'Increasing spring shares to s dominance',
            '79': 'Increasing spring shares to s dominance',
            '89': 'Increasing spring shares to s dominance',
            '21': 'Decreasing spring shares to w only',
            '31': 'Decreasing spring shares to w only',
            '51': 'Decreasing spring shares to w only',
            '61': 'Decreasing spring shares to w only',
            '81': 'Decreasing spring shares to w only',
            '91': 'Decreasing spring shares to w only',
            '24': 'Decreasing spring shares to w only',
            '34': 'Decreasing spring shares to w only',
            '54': 'Decreasing spring shares to w only',
            '64': 'Decreasing spring shares to w only',
            '84': 'Decreasing spring shares to w only',
            '94': 'Decreasing spring shares to w only',
            '27': 'Decreasing spring shares to w only',
            '37': 'Decreasing spring shares to w only',
            '57': 'Decreasing spring shares to w only',
            '67': 'Decreasing spring shares to w only',
            '87': 'Decreasing spring shares to w only',
            '97': 'Decreasing spring shares to w only',
            '12': 'Increasing spring shares to sw balance',
            '32': 'Increasing spring shares to sw balance',
            '42': 'Increasing spring shares to sw balance',
            '62': 'Increasing spring shares to sw balance',
            '72': 'Increasing spring shares to sw balance',
            '92': 'Increasing spring shares to sw balance',
            '52': 'Stable sw balance',
            '58': 'Stable sw balance',
            '14': 'Stable w only',
            '41': 'Stable w only',
            '74': 'Stable w only',
            '47': 'Stable w only',
            '36': 'Stable s dominance',
            '96': 'Stable s dominance',
            '69': 'Stable s dominance',
            '63': 'Stable s dominance',
            '18': 'Decreasing spring shares to sw balance',
            '38': 'Decreasing spring shares to sw balance',
            '48': 'Decreasing spring shares to sw balance',
            '68': 'Decreasing spring shares to sw balance',
            '78': 'Decreasing spring shares to sw balance',
            '98': 'Decreasing spring shares to sw balance',
            '11': 'Stable w only',
            '22': 'Stable sw balance',
            '33': 'Stable s dominance',
            '44': 'Stable w only',
            '55': 'Stable sw balance',
            '66': 'Stable s dominance',
            '77': 'Stable w only',
            '88': 'Stable sw balance',
            '99': 'Stable s dominance',
            '28': 'Stable sw balance',
            '82': 'Stable sw balance',
            '17': 'Stable w only',
            '71': 'Stable w only',
            '39': 'Stable s dominance',
            '93': 'Stable s dominance',
            '01': 'Newly cultivated to w only',
            '02': 'Newly cultivated to sw balance',
            '03': 'Newly cultivated to s dominance',
            '04': 'Newly cultivated to w only',
            '05': 'Newly cultivated to sw balance',
            '06': 'Newly cultivated to s dominance',
            '07': 'Newly cultivated to w only',
            '08': 'Newly cultivated to sw balance',
            '09': 'Newly cultivated to s dominance',
        }

        leacer_change_classification = {
            '41': 'Decreasing leaf shares to c only',
            '51': 'Decreasing leaf shares to c only',
            '61': 'Decreasing leaf shares to c only',
            '71': 'Decreasing leaf shares to c only',
            '81': 'Decreasing leaf shares to c only',
            '91': 'Decreasing leaf shares to c only',
            '42': 'Decreasing leaf shares to c only',
            '52': 'Decreasing leaf shares to c only',
            '62': 'Decreasing leaf shares to c only',
            '72': 'Decreasing leaf shares to c only',
            '82': 'Decreasing leaf shares to c only',
            '92': 'Decreasing leaf shares to c only',
            '43': 'Decreasing leaf shares to c only',
            '53': 'Decreasing leaf shares to c only',
            '63': 'Decreasing leaf shares to c only',
            '73': 'Decreasing leaf shares to c only',
            '83': 'Decreasing leaf shares to c only',
            '93': 'Decreasing leaf shares to c only',
            '17': 'Increasing leaf shares to l dominance',
            '27': 'Increasing leaf shares to l dominance',
            '37': 'Increasing leaf shares to l dominance',
            '47': 'Increasing leaf shares to l dominance',
            '57': 'Increasing leaf shares to l dominance',
            '67': 'Increasing leaf shares to l dominance',
            '18': 'Increasing leaf shares to l dominance',
            '28': 'Increasing leaf shares to l dominance',
            '38': 'Increasing leaf shares to l dominance',
            '48': 'Increasing leaf shares to l dominance',
            '58': 'Increasing leaf shares to l dominance',
            '68': 'Increasing leaf shares to l dominance',
            '19': 'Increasing leaf shares to l dominance',
            '29': 'Increasing leaf shares to l dominance',
            '39': 'Increasing leaf shares to l dominance',
            '49': 'Increasing leaf shares to l dominance',
            '59': 'Increasing leaf shares to l dominance',
            '69': 'Increasing leaf shares to l dominance',
            '14': 'Increasing leaf shares to lc balance',
            '24': 'Increasing leaf shares to lc balance',
            '34': 'Increasing leaf shares to lc balance',
            '74': 'Decreasing leaf shares to lc balance',
            '84': 'Decreasing leaf shares to lc balance',
            '94': 'Decreasing leaf shares to lc balance',
            '16': 'Increasing leaf shares to lc balance',
            '26': 'Increasing leaf shares to lc balance',
            '36': 'Increasing leaf shares to lc balance',
            '76': 'Decreasing leaf shares to lc balance',
            '86': 'Decreasing leaf shares to lc balance',
            '96': 'Decreasing leaf shares to lc balance',
            '15': 'Increasing leaf shares to lc balance',
            '25': 'Increasing leaf shares to lc balance',
            '35': 'Increasing leaf shares to lc balance',
            '45': 'Stable lc balance',
            '65': 'Stable lc balance',
            '75': 'Decreasing leaf shares to lc balance',
            '85': 'Decreasing leaf shares to lc balance',
            '95': 'Decreasing leaf shares to lc balance',
            '11': 'Stable c only',
            '22': 'Stable c only',
            '33': 'Stable c only',
            '44': 'Stable lc balance',
            '55': 'Stable lc balance',
            '66': 'Stable lc balance',
            '77': 'Stable l dominance',
            '88': 'Stable l dominance',
            '99': 'Stable l dominance',
            '23': 'Stable c only',
            '56': 'Stable lc balance',
            '12': 'Stable c only',
            '21': 'Stable c only',
            '89': 'Stable l dominance',
            '87': 'Stable l dominance',
            '78': 'Stable l dominance',
            '98': 'Stable l dominance',
            '32': 'Stable c only',
            '54': 'Stable lc balance',
            '46': 'Stable lc balance',
            '64': 'Stable lc balance',
            '13': 'Stable c only',
            '31': 'Stable c only',
            '79': 'Stable l dominance',
            '97': 'Stable l dominance',
            '01': 'Newly cultivated to c only',
            '02': 'Newly cultivated to c only',
            '03': 'Newly cultivated to c only',
            '04': 'Newly cultivated to lc balance',
            '05': 'Newly cultivated to lc balance',
            '06': 'Newly cultivated to lc balance',
            '07': 'Newly cultivated to l dominance',
            '08': 'Newly cultivated to l dominance',
            '09': 'Newly cultivated to l dominance',
        }

        df["sprwin_change"] = df["change_fct_str"].map(sprwin_change_classification)
        df["leacer_change"] = df["change_fct_str"].map(leacer_change_classification)
        # t = df.loc[df["sprwin_change"].isna()].copy()
        # missed = t["change_fct_str"].unique()
        df.loc[df["sprwin_change"].isna(), "sprwin_change"] = "No change"
        # t = df.loc[df["leacer_change"].isna()].copy()
        # missed = t["change_fct_str"].unique()
        df.loc[df["leacer_change"].isna(), "leacer_change"] = "No change"
        # df.loc[df["source_str"] == "0", "sprwin_change"] = "newly classified"
        # df.loc[df["source_str"] == "0", "leacer_change"] = "newly classified"
        df.loc[df["target_str"] == "0", "sprwin_change"] = "no 2nd classification"
        df.loc[df["target_str"] == "0", "leacer_change"] = "no 2nd classification"
        df["functional_change"] = df["sprwin_change"] + ' - ' + df["leacer_change"]
        df.drop(columns=["source_str", "target_str", "source_fct", "target_fct", "change_str", "change_fct", "change_fct_str"], inplace=True)
        df["overall_change"] = df["structural_change"] + '-' + df["functional_change"]

        return df

    def calc_stats_from_change_sequences(df, stable_dict, total_area):
        if df.empty:
            writer = pd.ExcelWriter(out_pth)
            for c, df in enumerate([df, df, df, df, df, df]):
                name = ['Changes_classified', 'combined_change_stats', 'struct_change_stats', 'funct_change_stats',
                        'stable_area', 'summary'][c]
                df.to_excel(writer, sheet_name=name, index=False)
            writer.save()
            return df, df, df, df, df

        stable_area = stable_dict["stable_total_area"]
        change_area = total_area - stable_area
        net_change_area1 = df["px_count"].sum()
        newly_cultivated = df.loc[df["structural_change"] == "newly classified", "px_count"].sum()
        abandoned = df.loc[df["structural_change"] == "no 2nd classification", "px_count"].sum()
        net_change_area2 = net_change_area1 - newly_cultivated - abandoned

        df_stable = pd.DataFrame.from_dict(data=stable_dict, orient='index').reset_index()
        df_stable.rename(columns={"index": "class", 0: "px_count"}, inplace=True)
        df_stable.sort_values(by="px_count", ascending=False, inplace=True)
        df_stable.loc[df_stable["class"] == 'stable_00',  "class"] = "no_cst_in_both_periods"
        df_stable["share_of_total_area"] = round(df_stable["px_count"] / total_area * 100, 2)
        df_stable["share_of_stable_area"] = round(df_stable["px_count"] / stable_area * 100, 2)
        df_stable.loc[df_stable["class"] == 'no_cst_in_both_periods', "share_of_stable_area"] = 0

        df_stat = df[["overall_change", "px_count"]].groupby("overall_change").sum().reset_index()
        df_stat.sort_values(by="px_count", ascending=False, inplace=True)
        df_stat["share_of_total_area"] = round(df_stat["px_count"] / total_area * 100, 2)
        df_stat["share_of_change_area"] = round(df_stat["px_count"] / change_area * 100, 2)
        df_stat["share_of_net_change_area_incl_new"] = round(df_stat["px_count"] / net_change_area1 * 100, 2)
        df_stat["share_of_net_change_area_excl_new"] = round(df_stat["px_count"] / net_change_area2 * 100, 2)



        df_str_stat = df[["structural_change", "px_count"]].groupby("structural_change").sum().reset_index()
        df_str_stat.sort_values(by="px_count", ascending=False, inplace=True)
        df_str_stat["share_of_total_area"] = round(df_str_stat["px_count"] / total_area * 100, 2)
        df_str_stat["share_of_change_area"] = round(df_str_stat["px_count"] / change_area * 100, 2)
        df_str_stat["share_of_net_change_area_incl_new"] = round(df_str_stat["px_count"] / net_change_area1 * 100, 2)
        df_str_stat["share_of_net_change_area_excl_new"] = round(df_str_stat["px_count"] / net_change_area2 * 100, 2)

        df_fct_stat = df[["functional_change", "px_count"]].groupby("functional_change").sum().reset_index()
        df_fct_stat.sort_values(by="px_count", ascending=False, inplace=True)
        df_fct_stat["share_of_total_area"] = round(df_fct_stat["px_count"] / total_area * 100, 2)
        df_fct_stat["share_of_change_area"] = round(df_fct_stat["px_count"] / change_area * 100, 2)
        df_fct_stat["share_of_net_change_area_incl_new"] = round(df_fct_stat["px_count"] / net_change_area1 * 100, 2)
        df_fct_stat["share_of_net_change_area_excl_new"] = round(df_fct_stat["px_count"] / net_change_area2 * 100, 2)

        df_lcc_stat = df[["leacer_change", "px_count"]].groupby("leacer_change").sum().reset_index()
        df_lcc_stat.sort_values(by="px_count", ascending=False, inplace=True)
        df_lcc_stat["share_of_total_area"] = round(df_lcc_stat["px_count"] / total_area * 100, 2)
        df_lcc_stat["share_of_change_area"] = round(df_lcc_stat["px_count"] / change_area * 100, 2)
        df_lcc_stat["share_of_net_change_area_incl_new"] = round(df_lcc_stat["px_count"] / net_change_area1 * 100, 2)
        df_lcc_stat["share_of_net_change_area_excl_new"] = round(df_lcc_stat["px_count"] / net_change_area2 * 100, 2)

        df_swc_stat = df[["sprwin_change", "px_count"]].groupby("sprwin_change").sum().reset_index()
        df_swc_stat.sort_values(by="px_count", ascending=False, inplace=True)
        df_swc_stat["share_of_total_area"] = round(df_swc_stat["px_count"] / total_area * 100, 2)
        df_swc_stat["share_of_change_area"] = round(df_swc_stat["px_count"] / change_area * 100, 2)
        df_swc_stat["share_of_net_change_area_incl_new"] = round(df_swc_stat["px_count"] / net_change_area1 * 100, 2)
        df_swc_stat["share_of_net_change_area_excl_new"] = round(df_swc_stat["px_count"] / net_change_area2 * 100, 2)

        df_summary = pd.DataFrame(data={
            "class": ["total_area", "stable_area", "change_area", "net_change_area", "newly_cultivated", "abandoned"],
            "area": [total_area, stable_area, change_area, net_change_area2, newly_cultivated, abandoned]})

        writer = pd.ExcelWriter(out_pth)
        for c, df in enumerate([df, df_stat, df_str_stat, df_fct_stat, df_stable, df_summary, df_lcc_stat, df_swc_stat]):
            name = ['Changes_classified',
                    'combined_change_stats',
                    'struct_change_stats',
                    'funct_change_stats',
                    'stable_area',
                    'summary',
                    'leacer_change_stats',
                    'sprwin_change_stats'
                    ][c]
            df.to_excel(writer, sheet_name=name, index=False)
        writer.save()

    ## use area of second period as it is the reference for
    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-net_changes-1_2.xlsx'
    df_orig1 = classify_structural_and_functional_change(df_orig1, out_pth)
    calc_stats_from_change_sequences(df_orig1, ana_stable_dict1, total_area1)

    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-net_changes-2_3.xlsx'
    df_orig2 = classify_structural_and_functional_change(df_orig2, out_pth)
    calc_stats_from_change_sequences(df_orig2, ana_stable_dict2,  total_area2)

    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-net_changes-1_3.xlsx'
    df_orig3 = classify_structural_and_functional_change(df_orig3, out_pth)
    calc_stats_from_change_sequences(df_orig3, ana_stable_dict3, total_area3)


    df_orig1 = create_df_from_dict(ana_l_dict1)
    df_orig2 = create_df_from_dict(ana_l_dict2)
    df_orig3 = create_df_from_dict(ana_l_dict3)
    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-total_changes-1_2.xlsx'
    df_orig1 = classify_structural_and_functional_change(df_orig1, out_pth)
    calc_stats_from_change_sequences(df_orig1, ana_stable_dict1,total_area1)

    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-total_changes-2_3.xlsx'
    df_orig2 = classify_structural_and_functional_change(df_orig2, out_pth)
    calc_stats_from_change_sequences(df_orig2, ana_stable_dict2, total_area2)

    out_pth = out_folder + f'/{fs_abbr}-complete_change_sequences-total_changes-1_3.xlsx'
    df_orig3 = classify_structural_and_functional_change(df_orig3, out_pth)
    calc_stats_from_change_sequences(df_orig3, ana_stable_dict3, total_area3)

    print(fs_abbr, "done!")


def combine_analysis_of_federal_states(fs_dict, changes='net_changes'):
    ana_dict = {"periods_1_2": {
        "summary": [],
        "struct_change_stats": [],
        "funct_change_stats": [],
        "combined_change_stats": [],
        'leacer_change_stats': [],
        'sprwin_change_stats': []
    },
                "periods_2_3": {
        "summary": [],
         "struct_change_stats": [],
        "funct_change_stats": [],
        "combined_change_stats": [],
        'leacer_change_stats': [],
        'sprwin_change_stats': []
    },
                "periods_1_3": {
        "summary": [],
        "struct_change_stats": [],
        "funct_change_stats": [],
        "combined_change_stats": [],
        'leacer_change_stats': [],
        'sprwin_change_stats': []
    }}

    for fs in fs_dict:
        fs_abbr = FS_DICT[fs]['abbreviation']
        if fs_abbr == "LS":
            continue

        if fs_abbr == "SA":
            periods = ['2_3']
        else:
            periods = ['1_2', '2_3', '1_3']

        for period in periods:
            pth = rf'data\tables\changes_in_sequences\{fs_abbr}\{fs_abbr}-complete_change_sequences-{changes}-{period}.xlsx'
            for key in ana_dict[f"periods_{period}"]:
                df = pd.read_excel(pth, sheet_name=key)
                df.rename(columns={"area": f"{fs_abbr}",
                                   "px_count": f"{fs_abbr}",
                                   "structural_change": "class",
                                   "functional_change": "class",
                                   "overall_change": "class",
                                   "leacer_change": "class",
                                   "sprwin_change": "class"},
                          inplace=True)

                if df.empty:
                    df = pd.DataFrame({"class": [], f"{fs_abbr}": []})
                else:
                    df = df[["class", fs_abbr]]
                    df[fs_abbr] = round((df[fs_abbr] * 25) / 10000, 0)

                ana_dict[f"periods_{period}"][key].append(df)

    coll_dict = {
        "summary": [],
        "struct_change_stats": [],
        "funct_change_stats": [],
        "combined_change_stats": [],
        "leacer_change_stats": [],
        "sprwin_change_stats": []
    }

    periods = ['1_2', '2_3', '1_3']
    for period in periods:
        for key in coll_dict:
            df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), ana_dict[f"periods_{period}"][key])
            df[f"total_area"] = df.sum(axis=1)
            df.sort_values(by=f"total_area", ascending=False, inplace=True)
            # df.columns = pd.MultiIndex.from_product([[period], list(df.columns)])
            coll_dict[key].append(df)

    summ_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'),  coll_dict["summary"])
    str_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), coll_dict["struct_change_stats"])
    fct_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), coll_dict["funct_change_stats"])
    comb_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), coll_dict["combined_change_stats"])
    lcc_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), coll_dict["leacer_change_stats"])
    swc_df = reduce(lambda df1, df2: pd.merge(df1, df2, on='class', how='outer'), coll_dict["sprwin_change_stats"])
    # str_df = pd.concat(str_lst, axis=1)
    # fct_df = pd.concat(fct_lst, axis=1)
    # comb_df = pd.concat(comb_lst, axis=1)

    out_pth = rf'data\tables\changes_in_sequences\summary_{changes}.xlsx'
    writer = pd.ExcelWriter(out_pth)
    for c, df in enumerate([summ_df, str_df, fct_df, lcc_df, swc_df, comb_df]):
        name = ['summary', 'structural_change', 'functional_change', 'leaf_cereal_change',  'spring_winter_change', 'combined_change'][c]
        df.to_excel(writer, sheet_name=name, index=True)
    writer.save()


def main():
    for fs in FS_DICT:
        print(fs)
        fs_abbr = FS_DICT[fs]['abbreviation']

        # count_function(fs_abbr=fs_abbr, periods=PERIODS)

        pth = rf'data\tables\changes_in_sequences\{fs_abbr}_changes_in_sequence.json'
        out_folder = rf'data\tables\changes_in_sequences\{fs_abbr}'
        analyze_function(pth=pth, fs_abbr=fs_abbr, out_folder=out_folder)

    # combine_analysis_of_federal_states(FS_DICT, changes='net_changes')
    combine_analysis_of_federal_states(FS_DICT, changes='total_changes')



if __name__ == '__main__':
    main()

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

## Old change classification
# change_classification = {
#             "11": "no_change", "12": "to_spr_bal", "13": "to_spr_dom", "14": "to_leaf_bal",
#             "15": "to_gen_bal",
#             "16": "to_spr_dom_leaf_bal", "17": "to_leaf_dom", "18": "to_spr_bal_leaf_dom", "19": "to_spr_dom_leaf_dom",
#
#             "21": "to_win_dom", "22": "no_change", "23": "to_spr_dom", "24": "to_win_dom_leaf_bal",
#             "25": "to_gen_bal",
#             "26": "to_spr_dom_leaf_bal", "27": "to_win_dom_leaf_dom", "28": "to_leaf_dom", "29": "to_spr_dom_leaf_dom",
#
#             "31": "to_win_dom", "32": "to_spr_bal", "33": "no_change", "34": "to_win_dom_leaf_bal",
#             "35": "to_gen_bal",
#             "36": "to_leaf_bal", "37": "to_win_dom_leaf_dom", "38": "to_spr_bal_leaf_dom", "39": "to_leaf_dom",
#
#             "41": "to_cer_dom", "42": "to_spr_bal_cer_dom", "43": "to_spr_dom_cer_dom", "44": "no_change",
#             "45": "to_gen_bal",
#             "46": "to_spr_dom", "47": "to_win_dom_leaf_dom", "48": "to_spr_bal_leaf_dom", "49": "to_spr_dom_leaf_dom",
#
#             "51": "to_win_dom_cer_dom", "52": "to_cer_dom", "53": "to_spr_dom_cer_dom", "54": "to_win_dom",
#             "55": "no_change",
#             "56": "to_spr_dom", "57": "to_win_dom_leaf_dom", "58": "to_leaf_dom", "59": "to_spr_dom_leaf_dom",
#
#             "61": "to_win_dom_cer_dom", "62": "to_spr_bal_cer_dom", "63": "to_cer_dom", "64": "to_win_dom",
#             "65": "to_gen_bal",
#             "66": "no_change", "67": "to_win_dom_leaf_dom", "68": "to_spr_bal_leaf_dom", "69": "to_leaf_dom",
#
#             "71": "to_cer_dom", "72": "to_spr_bal_cer_dom", "73": "to_spr_dom_cer_dom", "74": "to_leaf_bal",
#             "75": "to_gen_bal",
#             "76": "to_spr_dom_leaf_bal", "77": "no_change", "78": "to_spr_bal", "79": "to_spr_dom",
#
#             "81": "to_win_dom_cer_dom", "82": "to_cer_dom", "83": "to_spr_dom_cer_dom", "84": "to_win_dom_leaf_bal",
#             "85": "to_gen_bal",
#             "86": "to_spr_dom_leaf_bal", "87": "to_win_dom", "88": "no_change", "89": "to_spr_dom",
#
#             "91": "to_win_dom_cer_dom", "92": "to_spr_bal_cer_dom", "93": "to_cer_dom", "94": "to_win_dom_leaf_bal",
#             "95": "to_gen_bal",
#             "96": "to_leaf_bal", "97": "to_win_dom", "98": "to_spr_bal", "99": "no_change",
#         }