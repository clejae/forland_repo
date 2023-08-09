# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec
import gdal
import numpy as np
import pandas as pd
import math
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
os.chdir(wd)
bl_lst = ['BB','BV']#'SA','LS'
bl_dict = {'BB':['2005-2011','2008-2014','2012-2018'],
           'SA':['2008-2014','2012-2018'],
           'BV':['2005-2011','2008-2014','2012-2018'],
           'LS':['2012-2018']}
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#

## set plotting parameters
# plt.ioff()
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1.125
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

## set figure parameters, initiate figure
heights = [1,4]
nrow = 6
ncol = 20
fig, axs = plt.subplots(nrows=nrow, ncols=ncol, figsize=cm2inch(16,8),  sharey='row')
## loop over federal states and their respective study periods
s = 0
for bl in bl_lst:
    per_lst = bl_dict[bl]
    for per in per_lst:
        ix = np.unravel_index(s, axs.shape)

        ## open current sheet
        sheet_name = 'CTShareOfCSTSeq_{}'.format(per)
        df = pd.read_excel(r'data\tables\CropRotations\{0}\{0}_ShareCTinCSTs.xlsx'.format(bl), sheet_name=sheet_name)
        # sheet_name2 = 'CTShareOfCSTArea_{}'.format(per)
        # df2 = pd.read_excel(r'data\tables\CropRotations\{0}\{0}_ShareCTinCSTs.xlsx'.format(bl), sheet_name=sheet_name2)

        ## get crop types (cts) and crop sequence types (cols/csts)
        cols = list(df.columns)[1:]
        cts = list(df['CT'])
        cts = ['Maize', 'Winter Wheat', 'Oilseed Rape', 'Winter Barley', 'Rye', 'Fallow', 'NoData']
        cts = [str(ct) for ct in cts]

        ## define colors, plot pie chart per ct-cst combination
        #
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:8]
        for c, col in enumerate(cols):
            data = np.array(df[col])
            wedges = axs[s,c].pie(data, colors=colors, radius = 1.4)
            # axs[0,c].set_title('CST {0}'.format(col), fontsize="small")

        # for c, col in enumerate(cols):
        #     data = np.array(df2[col])
        #     bars = axs[1,c].bar(cts, data, color=colors)
        #     axs[1,c].set_xticklabels([])

        # axs[0,0].text(0,2.4, 'Share of occurences of crop type in crop sequence type')
        # axs[1, 0].text(0, 1.1, 'Share of area of crop type in crop sequence type area')
        ## add legend
        # legend_patches = [Patch(color=icolor, label=ct) for icolor, ct in zip(colors, cts)]
        # fig.legend(handles=legend_patches, loc='lower center', ncol=len(cts), title='Crop Classes', fontsize=9,
        #            frameon=False, mode ="expand")

        # axs[1,math.floor(len(cols)/2)].set_title('Share of area of crop type in crop sequence type area')
        # axs[1,math.floor(len(cols)/2)].legend(handles=legend_patches,
        #                                       loc='upper center',
        #                                       facecolor='white',
        #                                       edgecolor='black',
        #                                       bbox_to_anchor=(0.5, -0.05),
        #                                       ncol=len(cts))

        s += 1
# fig.tight_layout()


fig.savefig(r'figures\plots\ShareCTinCSTs\{0}_{1}_ShareCTinCST.png'.format(bl, per), dpi=fig.dpi)
plt.close()
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
