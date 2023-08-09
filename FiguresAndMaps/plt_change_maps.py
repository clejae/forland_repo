# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

import matplotlib.colors as mcolors
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def makeColormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    import matplotlib.colors as mcolors

    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)
# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'BB'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## Load dataframe with changes
## derive csts with largest changes
## and get subset for them
pth = r"data\tables\crop_sequence_types\{0}\{0}_Change_In_Area_Of_CSTs.xlsx".format(bl)
df_change = pd.read_excel(pth, sheet_name='ChangePerTile')
top_csts = pd.read_excel(pth, sheet_name='Top5Changes')
top_csts = list(top_csts['CST'].astype(str))
df_change = df_change[['Tile'] + top_csts]
df_change = df_change.fillna(0)

bin_list = [-225000000, -2500000, -2000000, -1500000, -1000000, -500000, -1, 0, 1, 500000, 1000000, 1500000, 2000000, 2500000, 225000000]
for cst in top_csts:
    df_change["{0}_cuts".format(cst)] = pd.cut(df_change[cst], bins=bin_list, labels=bin_list[1:])

## load grid shapefile
tiles_pth = r'data\vector\grid\Invekos_grid_{0}_15km.shp'.format(bl)
tiles_df = gpd.read_file(tiles_pth)

## merge both
merged_df = tiles_df.set_index('POLYID').join(df_change.set_index('Tile'))

## plot
cst = '85'
fig, axs = plt.subplots(1, 1, figsize=(26, 4))
merged_df.plot(column='{0}_cuts'.format(cst), cmap='RdYlBu',  linewidth=0.8, edgecolor='k', legend=True, categorical=True)
# c = mcolors.ColorConverter().to_rgb
# vmin, vmax = merged_df[cst].min(), merged_df[cst].max()
# vmid = abs(vmin)/vrange
# vdiv1 = vmid - 0.99 * (vmid)
# vdiv2 = vmid + 0.99 * (1-vmid)
# cmap = makeColormap([c('#d7191c'), vdiv1, c('#d7191c'), c('#ffffbf'), vmid, c('#ffffbf'), c('#2c7bb6'), vdiv2, c('#2c7bb6')])



axs[x].title.set_text(col[1:])
axs[x].axis('off')
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


