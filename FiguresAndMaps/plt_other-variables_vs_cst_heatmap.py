# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

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
              verticalalignment="center")
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

def plotCSTHeatmap(arr, title_str):
    plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
    plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

    ## plot heatmap
    ax = plt.gca() #initiate
    im = ax.imshow(arr, cmap='Blues') #plot
    cbar = ax.figure.colorbar(im, **{}) #add colorbar

    ## add labels
    cbar.ax.set_ylabel("Median field size [ha]", rotation=-90, va="bottom")
    ax.set_yticks(range(0, 10))
    ax.set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','Total'])
    ax.set_xticks(range(0, 10))
    ax.set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9','Total'])
    ax.set_xlabel('Sub Type')
    ax.set_ylabel('Main Type')
    ax.axvline(8.5, color='black')
    ax.axhline(8.5, color='black')

    ## Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)
    ax.set_xticks(np.arange(arr.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(arr.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title(title_str, fontdict={'size': 14})

    ## add text to the fields
    texts = annotate_heatmap(im, valfmt="{x:.1f}")

    plt.tight_layout()
    return ax

def mainFunc1(df1, col, title_str, out_pth):
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

    ax = plotCSTHeatmap(arr, title_str)

    plt.savefig(out_pth)
    plt.close()

def pltAxs(arr, ix):
    im = axs[ix].imshow(arr, cmap='Blues') #plot
    ## add labels
    # cbar.ax.set_ylabel("Median field size [ha]", rotation=-90, va="bottom")
    axs[ix].set_yticks(range(0, 10))
    axs[ix].set_yticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','Total'])
    axs[ix].set_xticks(range(0, 10))
    axs[ix].set_xticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9','Total'])
    axs[ix].set_xlabel('Sub Type') # x-axis label on top
    axs[ix].set_ylabel('Main Type')
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
    texts = annotate_heatmap(im, valfmt="{x:.1f}")

def mainFunc2(df1, col, ix):
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

    pltAxs(arr, ix)

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

# df_lst = []
# for bl in ['SA','BB','LS','BV']:
#     pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
#     title_str = '{} - Median Field Size per CST - 2012-2018'.format(bl)
#     out_pth = r"figures\plots\field sizes\heatmaps\{}_2012-2018_median-field-size-per-cst-heatmap2.png".format(bl)
#     df1 = pd.read_csv(pth, index_col=0)
#     df_lst.append(df1)
#     ax = mainFunc1(df1, col='field size', title_str='', out_pth)
#     print(bl, "done")

# df_comb = pd.concat(df_lst, 0)
# title_str = 'ALL - Median field sizes per CST - 2012-2018'
# out_pth = r"figures\plots\field sizes\heatmaps\ALL_2012-2018_median-field-size-per-cst-heatmap2.png"
# mainFunc1(df_comb, 'field size', title_str, out_pth)

fig, axs = plt.subplots(2,2,figsize=(16,16), sharex=True, sharey=True)
# plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = True
# plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = False
for b, bl in enumerate(['SA','BB','LS','BV']):
    pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
    df1 = pd.read_csv(pth, index_col=0)
    ix = np.unravel_index(b, axs.shape)
    mainFunc2(df1, 'field size', ix)
plt.tight_layout()
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#

# def plotCounts2(df1, breaks):
#     mt_lst = list(range(1,10))
#     arr_plt = np.zeros((len(mt_lst),len(breaks)-1))
#     df1['CST'] = df1['CST'].astype(str)
#     df1['Main Type'] = df1.CST.str.slice(0, 1)
#     for m, mt in enumerate(mt_lst):
#         df_sub = df1[df1['Main Type']==str(mt)]
#         lst = []
#         if not df_sub.empty:
#             for i in range(len(breaks)-1):
#                 df_br = df_sub[(df_sub['farm size'] > breaks[i]) & (df_sub['farm size'] <= breaks[i+1])]
#                 share = round(len(df_br['farm size']) / len(df_sub['farm size']) * 100, 2)
#                 lst.append(share)
#             arr_plt[m,] = lst
#         else:
#             continue
#     arr_plt[np.isnan(arr_plt)] = 0.0
#
#     fig, ax = plt.subplots()
#     im, cbar = heatmap(arr_plt[:,:], ['A','B','C','D','E','F','G','H','I'], breaks[1:], ax=ax,
#                        cmap="Blues", cbarlabel="share")
#     texts = annotate_heatmap(im, valfmt="{x:.0f}%")
#     fig.tight_layout()
#     plt.show()
#
# cst_lst = [i + j for i in range(10, 100, 10) for j in range(1, 10)]
# for bl in ['LS']: #,'SA','BV','LS'
#     pth = r"data\tables\FarmSize-CSTs\{}_2012-2018_sequences_farm-size.csv".format(bl)
#     title_str = '{} - Quantiles of farm sizes per CST - 2012-2018'.format(bl)
#     out_pth = r"figures\FarmSize-CSTs\{}_2012-2018_mean-farm-size-per-cst-quantile_heatmap.png".format(bl)
#     df1 = pd.read_csv(pth, index_col=0)
#
#     ### BREAKS NEED TO BE ADJUSTED PER FEDERAL STATE
#     breaks = [0, 25, 50, 75, 100, 125, 150, 175, 200, 300, 400, 500, 7000]
#     breaks = list(range(0, 3000, 100))
#     breaks.append(7000)
#     breaks = [0,50,100,200,300,400,500,750,1000,1500,2000,7000]
#     plotCounts2(df1, breaks)