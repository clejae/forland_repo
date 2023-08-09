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

def prepareDataFrame(bl_lst, per, sheet, df_descr):
    df_lst = []
    for b, bl, in enumerate(bl_lst):
        df_pth = r"data\tables\crop_sequence_types\{0}\{0}_{1}_{2}.xlsx".format(bl, per, df_descr)
        df = pd.read_excel(df_pth, sheet)
        t_area = df['SUM'].sum()
        for i in range(1, 10):
            df[str(i)] = round(df[str(i)] / t_area * 100, 2)
        df_lst.append(df)

    mt_lst = []
    for mt in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
        for df in df_lst:
            df_mt = df[df['MainType'] == mt]
            mt_lst.append(df_mt)
        cols = ['MainType', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SUM']
        if mt != 'I':
            df_dummy = pd.DataFrame(np.zeros((1, 11)), columns=cols)
            mt_lst.append(df_dummy)
    df_plt = pd.concat(mt_lst)

    return df_plt

def plot_grouped_stacked_bars(df_plt, axs, ix, axs_title):

    ## plot stacked bars
    colors = ['#ffd37f','#e69600','#a87000','#d1ff73','#7aab00','#4c7300','#bee8ff','#73b2ff','#004da8']
    df_plt[[str(i)for i in range(1,10)]].plot(kind="bar", stacked=True, color=colors, ax = axs[ix], legend=False)

    ## set x  and label them
    axs[ix].set_yticks(np.arange(0, 36, step=5))
    axs[ix].set_yticklabels(range(0, 36, 5), fontdict={'size': 10})
    x_ticks = list(np.arange(0,26,1))
    del x_ticks[2::3]
    axs[ix].set_xticks(x_ticks)
    # axs[ix].set_xticklabels(9 * ["BB","LS"],fontdict={'size': 10})
    axs[ix].set_xticklabels(18 * [""],fontdict={'size': 10})

    ## add y-grid, adjust tick colors, remove frame
    axs[ix].grid(b=True, which='major', axis='y', color='grey', linewidth=0.5)
    axs[ix].tick_params(axis='x', colors='white', labelcolor ='black')
    axs[ix].tick_params(axis='y', colors='grey', labelcolor ='black')
    axs[ix].spines['bottom'].set_color('white')
    axs[ix].spines['right'].set_visible(False)
    axs[ix].spines['left'].set_visible(False)
    axs[ix].spines['top'].set_visible(False)
    axs[ix].set_axisbelow(True)

    ## set title of subplot (name of federl state)
    axs[ix].set_title(axs_title, loc='center',fontdict={'size':12})# , 'weight':'semibold'})


# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
out_pth = r"figures\poster\Landscape21 - farm characteristics.png"
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## define lists to access data and datasheets
## and to provide federal state names for annotation
bl_lst = ['BB','LS']
strata_cattle = [[0, 1], [1, 50000]]
strata_oeko = [[0, 1], [7, 8]]
per = '2012-2018'

name_lst = [ "Conventional", "Organic"]  #"Without cattle","With cattle",

## set plotting parameters
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1.125
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

## Create plot
ncol = 2
nrow = 1
fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, figsize=cm2inch(15, 9))
s = 0 # index for subplot (axs) title

# ## Plot cattle vs. no cattle husbandry
# for strat in strata_cattle:
#     sheet = 'Collapsed>={}<{}'.format(strat[0], strat[1])
#     ix = np.unravel_index(s, axs.shape)
#
#     ## Prepare data frame
#     df_descr = 'CSTArea-CattleNumbers_binary'
#     df_plt = prepareDataFrame(bl_lst, per, sheet, df_descr)
#
#     ## Plot stacked bars
#     axs_title = name_lst[s]
#     plot_grouped_stacked_bars(df_plt, axs, ix, axs_title)
#
#     s += 1

## Plot conventional vs. organic
for strat in strata_oeko:
    sheet = 'Collapsed>={}<{}'.format(strat[0], strat[1])
    ix = np.unravel_index(s, axs.shape)

    ## Prepare data frame
    df_descr = 'CSTArea-Oeko_AFSD'
    df_plt = prepareDataFrame(bl_lst, per, sheet, df_descr)

    ## Plot stacked bars
    axs_title = name_lst[s]
    plot_grouped_stacked_bars(df_plt, axs, ix, axs_title)

    s += 1

# for ix in [(0,0),(0,1)]:
for s in range(2):
    ix = np.unravel_index(s, axs.shape)
    ## set y ticks and label them
    axs[ix].set_yticks(np.arange(-5, 36, step=5))
    y_labels = [str(i) for i in range(0, 36, 5)]
    y_labels.insert(0,'')
    axs[ix].set_yticklabels(y_labels, fontdict={'size': 10})

    ## annotate main types in top subplot
    bbox = dict(facecolor='white', edgecolor='black', boxstyle='round')
    x = .5
    # for mt in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
    #     axs[ix].annotate(mt, xy=(x, -2.2), fontsize=8) # 35.5 -
    #     x += 3
    for mt in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
        axs[ix].annotate(mt, xy=(x, 35.5), fontsize=10)
        x += 4

    ## create
    bbox = dict(facecolor='white', edgecolor='black', boxstyle='round')
    xs = list(np.arange(0, 26, 1))
    del xs[2::3]
    for i in range(0,len(xs),2):
        x = xs[i]
        label = 'BB'
        axs[ix].annotate(label, xy=(x - .4, -2), fontsize=8, rotation=90) # 35.5 -

    for j in range(1,len(xs),2):
        x = xs[j]
        label = 'LS'
        axs[ix].annotate(label, xy=(x - .4, -2), fontsize=8, rotation=90)

## Label x-axis in lower axis
axs[0].set_xlabel('Structural diversity', fontdict={'size': 10})
axs[1].set_xlabel('Structural diversity', fontdict={'size': 10})

## label y axis in lower axes
axs[0].set_ylabel('Share of cropland [%]', fontdict={'size': 10})
# axs[(1,0)].set_ylabel('Share of cropland [%]', fontdict={'size': 10})

# pad = 5
# for ax, row in zip(axs[:,0], ['a\n','b\n']):
#     ax.annotate(row, xy=(2.0, 1.55), xytext=(-ax.yaxis.labelpad - pad, 0),
#                 xycoords=ax.yaxis.label, textcoords='offset points',
#                 size='large', ha='center', va='center', fontsize=12, fontweight = 'semibold')

# create custom legend
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

fig.legend(handles=legend_elements, loc='lower center', ncol=9, title='Functional diversity', fontsize=8, frameon=False)# bbox_to_anchor= (0.00, 0.00, 0.1, 0.1))
fig.tight_layout()
fig.subplots_adjust(bottom=0.17)
plt.savefig(out_pth, dpi=300)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


