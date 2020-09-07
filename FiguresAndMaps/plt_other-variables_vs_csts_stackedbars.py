# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.patches import Rectangle
import numpy as np
import math

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def plotStackedCST(df_pth, sheet_lst, title_str):
    plt.rcParams['legend.handlelength'] = 1
    plt.rcParams['legend.handleheight'] = 1.125
    ncol = 2
    nrow = math.floor((len(sheet_lst) + ncol - 1)/ncol)
    fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, sharex=True, figsize=(16, 8))
    # fig.suptitle(title_str, fontsize=20)

    ## loop over sheets in df
    for s, sheet in enumerate(sheet_lst):
        ## open current sheet
        df = pd.read_excel(df_pth, sheet)
        df = df[0:9]

        ## calculate shares
        t_area = df['SUM'].sum()
        for i in range(1,10):
            df[str(i)] = round(df[str(i)]/t_area * 100,2)



        ## plot
        colors = ['#ffd37f','#e69600','#a87000','#d1ff73','#7aab00','#4c7300','#bee8ff','#73b2ff','#004da8']
        ix = np.unravel_index(s, axs.shape)
        df[[str(i)for i in range(1,10)]].plot(kind="bar", stacked=True, color=colors, ax = axs[ix],legend=False)
        axs[ix].set_xticklabels(['A','B','C','D','E','F','G','H','I'],rotation=0,fontdict={'size':24})
        axs[ix].set_yticklabels(range(0,60,5),fontdict={'size': 24})
        # axs[ix].set_title(sheet,fontdict={'size':14})
        axs[ix].set_xlabel('Structural type')
        axs[ix].set_ylabel('Share [%]',fontdict={'size':24})
        axs[ix].grid(b=True, which='major', axis='both',alpha=0.3)
        axs[ix].annotate('Area: ' + f'{int(t_area):,}' + ' ha', xy=(0,34),fontsize=24)
        # axs[ix].legend(handles=legend_elements, loc='center')
        plt.tight_layout()
    return fig, axs
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
animal = 'Cattle'

## for second part
bl_lst = ['BB', 'LS'] #'SA', 'BV',
name_lst = ['Brandenburg', 'Lower Saxony']

legend_elements = [Patch(facecolor='#ffd37f', edgecolor='#ffd37f',
                         label='1'),
                   Patch(facecolor='#e69600', edgecolor='#e69600',
                         label='2'),
                   Patch(facecolor='#a87000', edgecolor='#a87000',
                         label='3'),
                   Patch(facecolor='#d1ff73', edgecolor='#d1ff73',
                         label='4'),
                   Patch(facecolor='#7aab00', edgecolor='#7aab00',
                         label='5'),
                   Patch(facecolor='#4c7300', edgecolor='#4c7300',
                         label='6'),
                   Patch(facecolor='#bee8ff', edgecolor='#bee8ff',
                         label='7'),
                   Patch(facecolor='#73b2ff', edgecolor='#73b2ff',
                         label='8'),
                   Patch(facecolor='#004da8', edgecolor='#004da8',
                         label='9')]

## plot for each federal state separately
for bl in bl_lst:#,'SA','BV','LS']:
    # df_pth = r"data\tables\CropRotations\{0}_2012-2018_CSTArea-FieldSize_BMEL.xlsx".format(bl)
    # out_pth = r"figures\plots\FarmSize-CSTs\{0}_2012-2018_CSTArea-FieldSize_BMEL_stackedBarPlot.png".format(bl)
    # strata = [[0, 5], [5, 10], [10, 20], [20, 50], [50, 100], [100, 200], [200,7000]]
    # # [[0,25],[25,50],[50,100],[100,250],[250,500],[500,1000],[1000,2000],[2000,4000],[4000,6000]]

    # df_pth = r"data\tables\CropRotations\{0}\{0}_2012-2018_CSTArea-{1}Numbers.xlsx".format(bl, animal)
    # out_pth = r"figures\plots\husbandry\{0}_2012-2018_CSTArea-{1}Numbers_stackedBarPlot2.png".format(bl, animal)
    # strata = [[0, 1], [1, 100], [100, 20000]]
    # strata = [[0,1],[1,25000]]

    df_pth = r"data\tables\CropRotations\{0}\{0}_2012-2018_CSTArea-Oeko.xlsx".format(bl)
    out_pth = r"figures\plots\org_vs_conv\{0}_2012-2018_CSTArea-Oeko_stackedBarPlot3.png".format(bl)
    if bl == 'BB':
        strata = [[0, 1], [7, 8]]
    if bl == 'LS':
        strata = [[0, 1], [4, 8]]

    sheet_lst = ['Collapsed>={}<{}'.format(strat[0], strat[1]) for strat in strata]
    # title_str = bl + ' {0} Occurence 2012-2018'.format(animal)
    title_str = bl + 'Cattle Numbers 2012-2018'
    fig, axs = plotStackedCST(df_pth, sheet_lst, title_str)
    box = axs.get_position()
    axs.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])
    fig.legend(handles=legend_elements, loc='lower center', ncol=9, title ='Functional types',bbox_to_anchor=(0.5, -0.05))
    plt.savefig(out_pth)


# ## plot for all states aggregated
# strata = [[0, 5], [5, 10], [10, 20], [20, 50], [50, 100], [100, 200], [200,7000]]
# # [[0,25],[25,50],[50,100],[100,250],[250,500],[500,1000],[1000,2000],[2000,4000],[4000,6000]]
# sheet_lst = ['Collapsed>={}<{}'.format(strat[0], strat[1]) for strat in strata]
# title_str = 'ALL Field Sizes vs. CSTs 2012-2018'
# out_pth = r"figures\FarmSize-CSTs\ALL_2012-2018_CSTArea-FieldSize_BMEL_stackedBarPlot.png"
#
# ncol = 3
# nrow = math.floor((len(sheet_lst) + ncol - 1) / ncol)
# fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, sharex=True, figsize=(10, 10))
# fig.suptitle(title_str, fontsize=20)
#
# for s, sheet in enumerate(sheet_lst):
#     df = pd.DataFrame()
#     for bl in bl_lst:
#         df_pth = r"tables\CropRotations\{0}_2012-2018_CSTArea-FieldSize_BMEL.xlsx".format(bl)
#         df_sub = pd.read_excel(df_pth, sheet)
#         df_sub = df_sub[[str(i)for i in range(1,10)]][0:9]
#         df = df.add(df_sub, fill_value=0)
#
#     ## calculate shares
#     t_area = sum(df.sum())
#     for i in range(1, 10):
#         df[str(i)] = round(df[str(i)] / t_area * 100, 2)
#
#     ## plot
#     colors = ['#ffd37f', '#e69600', '#a87000', '#d1ff73', '#7aab00', '#4c7300', '#bee8ff', '#73b2ff', '#004da8']
#     ix = np.unravel_index(s, axs.shape)
#     df[[str(i) for i in range(1, 10)]].plot(kind="bar", stacked=True, color=colors, ax=axs[ix], legend=False)
#     axs[ix].set_xticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], rotation=0)
#     axs[ix].set_title(sheet, fontdict={'size': 14})
#     axs[ix].set_xlabel('Main Type')
#     axs[ix].set_ylabel('Share [%]')
#     axs[ix].grid(b=True, which='major', axis='both', alpha=0.3)
#     axs[ix].annotate('Area: ' + f'{int(t_area):,}' + ' ha', xy=(0,26))
#
# plt.savefig(out_pth)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


