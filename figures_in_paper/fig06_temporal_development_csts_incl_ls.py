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
def prepareDataFrame(df_pth, per_lst):
    df_lst = []
    for per in per_lst:
        df = pd.read_excel(df_pth, per)
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
out_pth = r"figures\in_paper\EJA\Fig6_EJA.jpg"
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## define lists to access data and datasheets
## and to provide federal state names for annotation
bl_lst = ['SA', 'BB','LS', 'BV']
per_lst = ['2005-2011','2008-2014','2012-2018']
# name_lst = ['Saxony-Anhalt', 'Brandenburg','Lower-Saxony', 'Bavaria']
name_lst = ["a","b","c","d"]

## create plot with subplots
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1.125
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

ncol = 1
nrow = 4
fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, sharex=True, figsize=cm2inch(17.6, 19))

## loop over federal states
for b,bl in enumerate(bl_lst):
    ## get axes tuple
    ix = np.unravel_index(b, axs.shape)

    ## prepare data frame
    df_pth = r"data\tables\crop_sequence_types\{0}\{0}_CSTArea.xlsx".format(bl)
    df_plt = prepareDataFrame(df_pth, per_lst)

    ## plot stacked bars
    colors = ['#ffd37f','#e69600','#a87000','#d1ff73','#7aab00','#4c7300','#bee8ff','#73b2ff','#004da8']
    df_plt[[str(i)for i in range(1,10)]].plot(kind="bar", stacked=True, color=colors, ax = axs[ix], legend=False)

    ## set x and y ticks and label them
    axs[ix].set_yticks(np.arange(0, 31, step=5))
    axs[ix].set_yticklabels(range(0, 31, 5), fontdict={'size': 10})
    x_ticks = list(np.arange(0,36,1))
    del x_ticks[3::4]
    axs[ix].set_xticks(x_ticks)
    axs[ix].set_xticklabels(9 * ["2005-'11","2008-'14","2012-'18"],fontdict={'size': 10})

    ## label y axis
    axs[ix].set_xlabel('Structural diversity per period', fontdict={'size': 10})
    axs[ix].set_ylabel('Share of cropland [%]',fontdict={'size': 10})

    ## add y-grid, adjust tick colors, remove frame
    axs[ix].grid(b=True, which='major', axis='y', color='grey', linewidth=0.5)
    axs[ix].tick_params(axis='x', colors='white', labelcolor ='black')
    axs[ix].tick_params(axis='y', colors='grey', labelcolor ='black')
    axs[ix].spines['bottom'].set_color('grey')
    axs[ix].spines['right'].set_visible(False)
    axs[ix].spines['left'].set_visible(False)
    axs[ix].spines['top'].set_visible(False)
    axs[ix].set_axisbelow(True)

    ## set title of subplot (name of federl state)
    axs[ix].set_title(name_lst[b], loc='left',fontdict={'size':12, 'weight':'semibold'})

## annotate main types in top subplot
bbox = dict(facecolor='white', edgecolor='black', boxstyle='round')
x=1
for mt in ['A','B','C','D','E','F','G','H','I']:
    axs[0,].annotate(mt, xy=(x, 31.5), fontsize=10)
    x += 4

## for first 2 subplots, the range y_ticks have to be set again
## because somehow the range shifted back to 0, 30
axs[0,].set_yticks(np.arange(0, 31, step=5))
axs[1,].set_yticks(np.arange(0, 31, step=5))
axs[2,].set_yticks(np.arange(0, 31, step=5))

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

fig.legend(handles=legend_elements, loc='lower center', ncol=9, title ='Functional diversity', fontsize=9, frameon=False)# bbox_to_anchor= (0.00, 0.00, 0.1, 0.1))
fig.tight_layout()
fig.subplots_adjust(top=0.95,bottom=0.16)
plt.savefig(out_pth, dpi=300)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


