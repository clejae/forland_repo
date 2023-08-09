# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib as mpl
import numpy as np
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def annotate_heatmap(im, data=None, replace_zero = True, valfmt="{x:.2f}",
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
              fontdict={'size':9})
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
            if replace_zero == True and float(text.get_text()) == 0.0:
                text.set_text('-')
            texts.append(text)

    return texts

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
x_labels = ['','','Functional diversity', 'Functional diversity']
y_labels = ['Structural diversity', '', 'Structural diversity', '']
# titles = ['Saxony-Anhalt', 'Brandenburg', 'Lower-Saxony', 'Bavaria']
titles = ["a","b","c","d"]

col = 'farm size'

## 1. Create Colormap from quantiles of all values in the heatmaps
lst = []
for b, bl in enumerate(['SA','BB','LS','BV']):
    pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
    df1 = pd.read_csv(pth, index_col=0)

    ## Open data (remove fields with no cst, calc mean field/farm size for each cst)
    df1 = df1.query('CST != 255')
    df1 = df1[['CST', col]]
    df = df1.groupby(['CST']).median()
    df['Count'] = df1.groupby(['CST']).count()
    df['CST'] = df.index
    df.loc[df['Count'] < 25, col] = 0

    ## Check for missing csts
    cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
    for cst in cst_lst:
        if cst not in df['CST']:
            df.loc[cst] = [0, 0, cst]
    df = df.sort_index()
    lst = lst + list(df[col])

    df1['CST'] = df1['CST'].astype(str)
    df1['Main Type'] = df1.CST.str.slice(0, 1)
    df1['Sub Type'] = df1.CST.str.slice(1, 2)
    mt_means = df1.groupby(['Main Type']).median()
    st_means = df1.groupby(['Sub Type']).median()

    lst = lst + list(mt_means[col])
    lst = lst + list(st_means[col])

val_arr = np.array(lst)
val_arr = val_arr[val_arr != 0]
quant_lst = [0,0.1]
for q in np.arange(0, 1, .05).tolist():
    quant = np.quantile(val_arr, q)
    quant_lst.append(quant)

## Define colormap
cmap = plt.cm.Blues  # define the colormap
cmaplist = [cmap(i) for i in range(cmap.N)]
cmaplist[0] = (1, 1, 1, 1.0)
cmap = mpl.colors.LinearSegmentedColormap.from_list(
    'Custom cmap', cmaplist, cmap.N)
norm = mpl.colors.BoundaryNorm(quant_lst, cmap.N)

## 2. Plot farm sizes in a 2x2 mosaic of heatmaps
plt.rcParams["font.family"] = "Calibri"

fig, axs = plt.subplots(2,2, figsize=cm2inch((17.6,16)), sharex=True, sharey=True)
for b, bl in enumerate(['SA','BB','LS','BV']):

    ## 2.1 Prepare data
    pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
    df1 = pd.read_csv(pth, index_col=0)

    ## Open data (remove fields with no cst, calc mean field/farm size for each cst)
    df1 = df1.query('CST != 255')
    df1 = df1[['CST', col]]
    df = df1.groupby(['CST']).median()  # .mean()#
    df['Count'] = df1.groupby(['CST']).count()
    df['CST'] = df.index
    df.loc[df['Count'] < 25, col] = 0

    ## Check for missing csts
    cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
    for cst in cst_lst:
        if cst not in df['CST']:
            df.loc[cst] = [0, 0, cst]
    df = df.sort_index()

    ## Prepare plotting array
    arr = np.zeros((9, 9))
    x = 0
    for i in range(0, 81, 9):
        # fill array with subset of farm sizes, which is always a slice of 9 values
        arr[x, 0:9] = df[col].iloc[i:i + 9]
        x += 1

    ## Add mean per main type and sub type
    df1['CST'] = df1['CST'].astype(str)
    df1['Main Type'] = df1.CST.str.slice(0, 1)
    df1['Sub Type'] = df1.CST.str.slice(1, 2)
    mt_means = df1.groupby(['Main Type']).median()  # .mean()#
    st_means = df1.groupby(['Sub Type']).median()  # .mean()#

    arr_mt_mean = np.array(mt_means[col])
    arr_mt_mean = np.reshape(arr_mt_mean, (9, 1))
    arr = np.concatenate((arr, arr_mt_mean), 1)

    arr_st_mean = np.array(st_means[col])
    arr_st_mean = np.append(arr_st_mean, (0))
    arr_st_mean = np.reshape(arr_st_mean, (1, 10))
    arr = np.concatenate((arr, arr_st_mean), 0)

    ## 2.2 Plot heatmap
    x_label = x_labels[b]
    y_label = y_labels[b]
    title = titles[b]

    ix = np.unravel_index(b, axs.shape)
    im = axs[ix].imshow(arr, cmap=cmap, norm=norm, vmin=1, vmax=972)

    ## Add labels
    axs[ix].set_yticks(range(0, 10))
    axs[ix].set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'Median'], fontdict={'size': 10})
    axs[ix].set_xticks(range(0, 10))
    axs[ix].set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Median'], fontdict={'size': 10})
    axs[ix].set_ylabel(y_label, fontdict={'size': 10})
    axs[ix].set_xlabel(x_label, fontdict={'size': 10})
    axs[ix].axvline(8.5, color='black')
    axs[ix].axhline(8.5, color='black')

    ## Create white grid.
    axs[ix].set_xticks(np.arange(arr.shape[1] + 1) - .5, minor=True)
    axs[ix].set_yticks(np.arange(arr.shape[0] + 1) - .5, minor=True)
    axs[ix].grid(which="minor", color="w", linestyle='-', linewidth=1)
    axs[ix].tick_params(which="minor", bottom=False, left=False)

    ## Add text to the fields
    axs[ix].set_title(title, loc='left', fontdict={'size': 12, 'weight': 'bold'})

    ## Edit data for annotation
    arr_ann = arr.astype(str)
    arr_ann[arr_ann == '0.0'] = '-'
    texts = annotate_heatmap(im, valfmt="{x:.0f}",threshold=496)

plt.tight_layout()
out_pth = r"figures\in_paper\EJA\Fig4_EJA.jpg"
plt.savefig(out_pth, bbox_inches='tight', dpi=300)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)

# ------------------------------------------ UNUSED CODE --------------------------------------------------------#

# ## plot colormap
# fig, ax = plt.subplots(figsize=(6, 1))
# fig.subplots_adjust(bottom=0.5)
# cb2 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
#                                 norm=norm,
#                                 orientation='horizontal')
# cb2.set_label("Discrete intervals with extend='both' keyword")
# fig.show()
