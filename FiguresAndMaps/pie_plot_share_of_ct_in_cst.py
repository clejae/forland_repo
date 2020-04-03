# Clemens Jänicke
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

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)
bl = 'SA'
per_lst = ['2012-2018'] #'2005-2011',
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
plt.ioff()

for per in per_lst: #, '2009-2015','2012-2018'
    df = pd.read_excel(r'data\tables\CropRotations\{0}_{1}_ShareOfCropTypesInCropSequences_v2_clean.xlsx'.format(bl, per), sheet_name='PropOfOccInCST')
    df2 = pd.read_excel(r'data\tables\CropRotations\{0}_{1}_ShareOfCropTypesInCropSequences_v2_clean.xlsx'.format(bl, per), sheet_name='PropOfAreaInCST')

    cols = list(df.columns)[1:]

    cts = list(df['CT'])
    cts = ['Maize', 'Winter Wheat', 'Oilseed Rape', 'Winter Barley', 'Rye', 'Fallow', 'Unkown', 'No AL', 'NoData']
    cts = [str(ct) for ct in cts]

    heights = [1,4]

    fig, axs = plt.subplots(nrows=2, ncols=len(cols), figsize=(15,3),  sharey='row')
    fig.suptitle(per)
    spec = fig.add_gridspec(nrows=2, ncols=len(cols),height_ratios=heights)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color'][:8]
    axs[0,0].text(0,2.4, 'Share of occurences of crop type in crop sequence type')
    for c, col in enumerate(cols):
        data = np.array(df[col])
        wedges = axs[0,c].pie(data)
        axs[0,c].set_title('CST {0}'.format(col), fontsize="small")

    for c, col in enumerate(cols):
        data = np.array(df2[col])
        bars = axs[1,c].bar(cts, data, color=colors)
        axs[1,c].set_xticklabels([])

    legend_patches = [Patch(color=icolor, label=ct) for icolor, ct in zip(colors, cts)]
    axs[1,0].text(0,1.1, 'Share of area of crop type in crop sequence type area')
    # axs[1,math.floor(len(cols)/2)].set_title('Share of area of crop type in crop sequence type area')
    axs[1,math.floor(len(cols)/2)].legend(handles=legend_patches,
                                          loc='upper center',
                                          facecolor='white',
                                          edgecolor='black',
                                          bbox_to_anchor=(0.5, -0.05),
                                          ncol=len(cts))

    fig.savefig(r'figures\plots\ShareCTinCSTs\{0}_{1}_ShareCTinCST_v2_clean.png'.format(bl, per), dpi=fig.dpi)
    plt.close()


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
