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
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

##########################################################
out_pth = r"figures\in_paper\FigS3_SuSc.tiff"
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
## define lists to access data and datasheets
## and to provide federal state names for annotation
bl = 'LS'
per_lst = ['12-18 Sub','12-18 Total']

## create plot with subplots
plt.rcParams['legend.handlelength'] = 1
plt.rcParams['legend.handleheight'] = 1.125
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

ncol = 1
nrow = 1
fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharey=True, sharex=True, figsize=cm2inch(17.6, 8))

## prepare data frame
df_pth = r"data\tables\crop_sequence_types\{0}\{0}_2012-2018_CSTArea-StudyAreaSusanne.xlsx".format(bl)
df_plt = prepareDataFrame(df_pth, per_lst)

## plot stacked bars
colors = ['#ffd37f','#e69600','#a87000','#d1ff73','#7aab00','#4c7300','#bee8ff','#73b2ff','#004da8']
df_plt[[str(i)for i in range(1,10)]].plot(kind="bar", stacked=True, color=colors, ax = axs, legend=False)

## set x and y ticks and label them
axs.set_yticks(np.arange(0, 31, step=5))
axs.set_yticklabels(range(0, 31, 5), fontdict={'size': 10})
x_ticks = list(np.arange(0,27,1))
del x_ticks[2::3]
axs.set_xticks(x_ticks)
axs.set_xticklabels(10 * ['Subset','Total'],fontdict={'size': 10})

## label y axis
axs.set_xlabel('Structural diversity', fontdict={'size': 10})
axs.set_ylabel('Share of cropland [%]',fontdict={'size': 10})

## add y-grid, adjust tick colors, remove frame
axs.grid(b=True, which='major', axis='y', color='grey', linewidth=0.5)
axs.tick_params(axis='x', colors='white', labelcolor ='black')
axs.tick_params(axis='y', colors='grey', labelcolor ='black')
axs.spines['bottom'].set_color('grey')
axs.spines['right'].set_visible(False)
axs.spines['left'].set_visible(False)
axs.spines['top'].set_visible(False)
axs.set_axisbelow(True)

# ## Draw line between sub and total columns
# x1 = 0
# x2 = 0
# for count in range(9):
#     x1 = count * 3 + 1.5
#     x2 = count * 3 + 2.5
#     plt.axvline(x1, 0, 30, ls ='--', c = 'black', lw = '0.5')
#     plt.axvline(x2, 0, 30, ls ='--', c = 'black', lw = '0.5')


## annotate main types in top subplot
bbox = dict(facecolor='white', edgecolor='black', boxstyle='round')
x=0
for mt in ['A','B','C','D','E','F','G','H','I']:
    axs.annotate(mt, xy=(x, 26.5), fontsize=10)
    x += 3

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
fig.subplots_adjust(top=0.95,bottom=0.35)
plt.savefig(out_pth, dpi=300)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#





# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


