# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl_lst = ['BB', 'LS'] #'SA', 'BV',
name_lst = ['Brandenburg', 'Lower Saxony']
animal = 'Pig'

## create plot
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1.125
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

ncol = 3
nrow = 2
fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, sharex=True, figsize=cm2inch(17.6, 12))

s = 0
## loop over sheets in dfs
for bl in bl_lst:
    ## open data
    df_pth = r"data\tables\crop_sequence_types\{0}\{0}_2012-2018_CSTArea-{1}Numbers_20201014.xlsx".format(bl, animal)
    strata = [[0, 1], [1, 100], [100, 25000]]
    sheet_lst = ['Collapsed>={}<{}'.format(strat[0], strat[1]) for strat in strata]
    for sheet in sheet_lst:
        ix = np.unravel_index(s, axs.shape)

        ## open current sheet
        df = pd.read_excel(df_pth, sheet)
        df = df[0:9]

        ## calculate shares
        t_area = df['SUM'].sum()
        for i in range(1,10):
            df[str(i)] = round(df[str(i)]/t_area * 100,2)

        ## plot
        colors = ['#ffd37f','#e69600','#a87000','#d1ff73','#7aab00','#4c7300','#bee8ff','#73b2ff','#004da8']
        df[[str(i)for i in range(1,10)]].plot(kind="bar", stacked=True, color=colors, ax = axs[ix],legend=False)

        ## label x and y ticks
        axs[ix].set_xticklabels(['A','B','C','D','E','F','G','H','I'],rotation=0,fontdict={'size':10})
        axs[ix].set_yticks(list(range(0, 30, 5)))
        # axs[ix].set_yticklabels(range(0,60,5),fontdict={'size': 9})

        ## label x and y axis
        axs[ix].set_xlabel('Structural type',fontdict={'size':10})
        axs[ix].set_ylabel('Share of cropland [%]',fontdict={'size':10})

        ## add y-grid, adjust tick colors, remove frame
        axs[ix].grid(b=True, which='major', axis='y', color='grey', linewidth=0.5)
        axs[ix].tick_params(axis='x', colors='white', labelcolor='black')
        axs[ix].tick_params(axis='y', colors='grey', labelcolor='black')
        axs[ix].spines['bottom'].set_color('grey')
        axs[ix].spines['right'].set_visible(False)
        axs[ix].spines['left'].set_visible(False)
        axs[ix].spines['top'].set_visible(False)
        axs[ix].set_axisbelow(True)

        ## annotate total area
        # axs[ix].annotate('Area: ' + f'{int(t_area):,}' + ' ha', xy=(0,26), fontsize=9)

        ## this is a small trick, so that the annotation of the federal states is shifted above the titles of the cols
        axs[ix].annotate('Dummy', xy=(0, 33), fontsize=11)
        plt.tight_layout()

        s += 1

## annotate pig numbers in top subplot
# axs[0,0].annotate("No pigs", xy=(1.5, 31), fontsize=9, fontweight = 'semibold')
# axs[0,1].annotate("< 1000 pigs", xy=(1.5, 31), fontsize=9, fontweight = 'semibold')
# axs[0,2].annotate(">= 1000 pigs", xy=(1.5, 31), fontsize=9, fontweight = 'semibold')

# for y in range(3):
#     axs[0,y].set_yticks(np.arange(0, 36, step=5))
#     axs[1,y].set_yticks(np.arange(0, 36, step=5))

## set title of subplot (name of federl state)
# for b, bl_name in enumerate(name_lst):
#     axs[b, 0].set_title(bl_name, loc='left',fontdict={'size':10, 'weight':'bold'})

## create custom legend
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

fig.legend(handles=legend_elements, loc='lower center', ncol=9, title ='Functional types', fontsize=9, frameon=False)
for ax, col in zip(axs[0], ["No hogs","< 100 hogs", ">= 100 hogs"]):
    ax.set_title(col,fontdict={'size':10})
pad = 5
for ax, row in zip(axs[:,0], ['a\n','b\n']):
    ax.annotate(row, xy=(0.5, 1.20), xytext=(-ax.yaxis.labelpad - pad, 0),
                xycoords=ax.yaxis.label, textcoords='offset points',
                size='large', ha='left', va='center', fontsize=12, fontweight = 'semibold')
fig.tight_layout()
fig.subplots_adjust(bottom=0.195)
out_pth = r"figures\in_paper\FigS2_SuSc.tiff"
plt.savefig(out_pth,dpi=300)
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


