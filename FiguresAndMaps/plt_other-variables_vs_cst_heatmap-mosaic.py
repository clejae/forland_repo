# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib as mpl
import numpy as np
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """
    import matplotlib

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center",
              fontdict={'size':20})
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

def pltAxs(arr, ix, x_label, y_label, title, cmap, norm):

    im = axs[ix].imshow(arr, cmap=cmap, norm = norm, vmin=1, vmax=972) #plot
    ## add labels
    axs[ix].set_yticks(range(0, 10))
    axs[ix].set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','Total'],fontdict={'size':22})
    axs[ix].set_xticks(range(0, 10))
    axs[ix].set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9','Total'],fontdict={'size':22})
    axs[ix].set_ylabel(y_label,fontdict={'size':22})
    axs[ix].set_xlabel(x_label,fontdict={'size':22})
    axs[ix].axvline(8.5, color='black')
    axs[ix].axhline(8.5, color='black')

    ## Turn spines off and create white grid.
    for edge, spine in axs[0,1].spines.items():
        spine.set_visible(False)
    axs[ix].set_xticks(np.arange(arr.shape[1] + 1) - .5, minor=True)
    axs[ix].set_yticks(np.arange(arr.shape[0] + 1) - .5, minor=True)
    axs[ix].grid(which="minor", color="w", linestyle='-', linewidth=1)
    axs[ix].tick_params(which="minor", bottom=False, left=False)


    ## add text to the fields
    axs[ix].set_title(title, loc='left', fontdict={'size': 24, 'weight':'bold'})
    texts = annotate_heatmap(im, valfmt="{x:.0f}", threshold=496)

def mainFunc2(df1, col, ix, x_label, y_label, title, cmap, norm):
    ## Open data (remove fields with no cst, calc mean field/farm size for each cst)
    df1 = df1[df1['CST'] != 255]
    df1 = df1[['CST', col]]
    df = df1.groupby(['CST']).median()#.mean()#
    df['Count'] = df1.groupby(['CST']).count()
    df['CST'] = df.index
    df[col][df['Count'] < 25] = 0

    ## check for missing csts
    cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
    for cst in cst_lst:
        if cst not in df['CST']:
            df.loc[cst] = [0, 0, cst]
    df = df.sort_index()

    ## prepare plotting array
    arr = np.zeros((9, 9))
    x = 0
    for i in range(0, 81, 9):
        # fill array with subset of farm sizes, which is always a slice of 9 values
        arr[x, 0:9] = df[col].iloc[i:i + 9]
        x += 1

    ## add mean per main type and sub type
    df1['CST'] = df1['CST'].astype(str)
    df1['Main Type'] = df1.CST.str.slice(0, 1)
    df1['Sub Type'] = df1.CST.str.slice(1, 2)
    mt_means = df1.groupby(['Main Type']).median()#.mean()#
    st_means = df1.groupby(['Sub Type']).median()#.mean()#

    arr_mt_mean = np.array(mt_means[col])
    arr_mt_mean = np.reshape(arr_mt_mean, (9, 1))
    arr = np.concatenate((arr, arr_mt_mean), 1)

    arr_st_mean = np.array(st_means[col])
    arr_st_mean = np.append(arr_st_mean, (0))
    arr_st_mean = np.reshape(arr_st_mean, (1, 10))
    arr = np.concatenate((arr, arr_st_mean), 0)

    pltAxs(arr, ix, x_label, y_label, title, cmap = cmap, norm=norm)

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)
x_labels = ['','','Functional Type', 'Functional Type']
y_labels = ['Structural Type', '', 'Structural Type', '']
titles = ['Saxony-Anhalt', 'Brandenburg', 'Lower-Saxony', 'Bavaria']

## Define colormap
## Version 1:
# viridis = cm.get_cmap('Blues', 256)
# newcolors = viridis(np.linspace(0, 1, 256))
# white = np.array([256 / 256, 256 / 256, 256 / 256, 1])
# newcolors[:1, :] = white
# newcmp = ListedColormap(newcolors)

## Version 2 (color boundaries are the quantiles of the values in all four heatmaps)
col = 'farm size'
lst = []
for b, bl in enumerate(['SA','BB','LS','BV']):
    pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
    df1 = pd.read_csv(pth, index_col=0)

    ## Open data (remove fields with no cst, calc mean field/farm size for each cst)
    df1 = df1[df1['CST'] != 255]
    df1 = df1[['CST', col]]
    df = df1.groupby(['CST']).median()  # .mean()#
    df['Count'] = df1.groupby(['CST']).count()
    df['CST'] = df.index
    df[col][df['Count'] < 25] = 0

    ## check for missing csts
    cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
    for cst in cst_lst:
        if cst not in df['CST']:
            df.loc[cst] = [0, 0, cst]
    df = df.sort_index()
    lst = lst + list(df[col])

    df1['CST'] = df1['CST'].astype(str)
    df1['Main Type'] = df1.CST.str.slice(0, 1)
    df1['Sub Type'] = df1.CST.str.slice(1, 2)
    mt_means = df1.groupby(['Main Type']).median()#.mean()#
    st_means = df1.groupby(['Sub Type']).median()#.mean()#

    lst = lst + list(mt_means[col])
    lst = lst + list(st_means[col])

val_arr = np.array(lst)
val_arr = val_arr[val_arr != 0]
quant_lst = [0,0.1]
for q in np.arange(0, 1, .05).tolist():
    print(q)
    quant = np.quantile(val_arr, q)
    quant_lst.append(quant)

cmap = plt.cm.Blues  # define the colormap
cmaplist = [cmap(i) for i in range(cmap.N)]
cmaplist[0] = (1, 1, 1, 1.0)
cmap = mpl.colors.LinearSegmentedColormap.from_list(
    'Custom cmap', cmaplist, cmap.N)
norm = mpl.colors.BoundaryNorm(quant_lst, cmap.N)

## plot colormap
fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)
cb2 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb2.set_label("Discrete intervals with extend='both' keyword")
fig.show()

## Plot field sizes in a 2x2 mosaic of heatmaps
#
# fig, axs = plt.subplots(2,2, figsize=(16,16), sharex=True, sharey=True)
# for b, bl in enumerate(['SA','BB','LS','BV']):
#     pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
#     df1 = pd.read_csv(pth, index_col=0)
#     ix = np.unravel_index(b, axs.shape)
#     mainFunc2(df1, 'field size', ix, x_labels[b], y_labels[b], titles[b], cmap= newcmp)
# plt.tight_layout()
# out_pth = r"figures\plots\field sizes\heatmaps\ALL_2012-2018_median-field-size-per-cst-heatmap4.png"
# plt.savefig(out_pth,bbox_inches='tight')

# ## Plot farm sizes in 2x2 mosaic of heatmaps

fig, axs = plt.subplots(2,2, figsize=(16,16), sharex=True, sharey=True)
for b, bl in enumerate(['SA','BB','LS','BV']):
    pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
    df1 = pd.read_csv(pth, index_col=0)
    ix = np.unravel_index(b, axs.shape)
    mainFunc2(df1, 'farm size', ix, x_labels[b], y_labels[b], titles[b], cmap= cmap, norm = norm)
plt.tight_layout()
out_pth = r"figures\plots\farm sizes\heatmaps\ALL_2012-2018_median-farm-size-per-cst-heatmap5.png"
plt.savefig(out_pth,bbox_inches='tight')
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
