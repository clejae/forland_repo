# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
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
bl_lst = ['SA','BB','LS','BV']
bl_labels = ['Saxony-Anhalt', 'Brandenburg', 'Lower Saxony', 'Bavaria']
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

### Kernel density plots
plt.rcParams['legend.title_fontsize'] = '10'
plt.rcParams["font.family"] = "Calibri"

fig, axs = plt.subplots(nrows=1, ncols=2, sharey=True, figsize= cm2inch(17.6, 6))
legend_elements = [Line2D([0], [0], color='black', linestyle = '-',
                              label='Saxony-Anhalt'),
                       Line2D([0], [0], color='black', linestyle =  '--',
                              label='Brandenburg'),
                       Line2D([0], [0], color='black', linestyle =  '-.',
                              label='Lower Saxony'),
                       Line2D([0], [0], color='black', linestyle =  ':',
                              label='Bavaria')]
linestyles = ['-', '--', '-.', ':']

for b, bl in enumerate(bl_lst):
    pth = r"data\tables\FarmSizes\{0}_farm_sizes_2018.csv".format(bl)
    df = pd.read_csv(pth)
    df = df[df['Area'] > 3]
    sns.kdeplot(data=df, x='Area', ax=axs[0,], cut=0, log_scale=True, legend=True, linestyle = linestyles[b], linewidth = 1, color='black')
    axs[0,].set_title('a', x=.05, y=.995, pad=-14, fontdict={'size': 12, 'weight': 'semibold'})
    axs[0,].set_xlabel('Hectares')
    axs[0,].spines['right'].set_visible(False)
    axs[0,].spines['top'].set_visible(False)

    pth = r"data\tables\FarmSizes\{0}_field_sizes_2018.csv".format(bl)
    df = pd.read_csv(pth)
    df = df[df['Area'] > .3]
    sns.kdeplot(data=df, x='Area', ax=axs[1,], cut=0, log_scale=True, linestyle = linestyles[b], linewidth = 1, color='black')
    axs[1,].set_title('b',  x=.05, y=.995, pad=-14, fontdict={'size': 12, 'weight': 'semibold'})
    axs[1,].set_xlabel('Hectares')
    axs[1,].spines['right'].set_visible(False)
    axs[1,].spines['top'].set_visible(False)
    axs[1,].legend(legend_elements, bl_labels, frameon=False, bbox_to_anchor=(0.6, 0.25))

plt.sca(axs[0,])
plt.xticks([3, 10, 100, 1000], ['3', '10', '100', '1000'])
axs[0,].set_xticks([], minor=True)

plt.sca(axs[1,])
plt.xticks([.3, 1, 10, 100], ['0.3', '1', '10', '100'])
axs[1,].set_xticks([], minor=True)

fig.tight_layout()
out_pth = r"figures\in_paper\Fig2_SuSc.tiff"
plt.savefig(out_pth, dpi=300)


# ### Kernel density plots colored
# plt.rcParams['legend.title_fontsize'] = '10'
# plt.rcParams["font.family"] = "Calibri"
#
# fig, axs = plt.subplots(nrows=1, ncols=2, sharey=True, figsize= cm2inch(16, 6))
# legend_elements = [Line2D([0], [0], color=sns.color_palette()[0], linestyle = '-',
#                               label='SA'),
#                        Line2D([0], [0], color=sns.color_palette()[1], linestyle =  '--',
#                               label='BB'),
#                        Line2D([0], [0], color=sns.color_palette()[2], linestyle =  '-.',
#                               label='LS'),
#                        Line2D([0], [0], color=sns.color_palette()[3], linestyle =  ':',
#                               label='BV')]
# linestyles = ['-', '--', '-.', ':']
#
# for b, bl in enumerate(bl_lst):
#     pth = r"data\tables\FarmSizes\{0}_farm_sizes_2018.csv".format(bl)
#     df = pd.read_csv(pth)
#     df = df[df['Area'] > 3]
#     sns.kdeplot(data=df, x='Area', ax=axs[0,], cut=0, log_scale=True, legend=True, linestyle = linestyles[b], linewidth = 1, )
#     axs[0,].set_title('a) Farm sizes',  x=0.9, y=0.9)
#     axs[0,].set_xlabel('Hectares')
#     axs[0,].spines['right'].set_visible(False)
#     axs[0,].spines['top'].set_visible(False)
#     # axs[0,].annotate(s='a) Farm sizes', xy=(400, 1), fontsize=12, fontweight = 'light')
#
#     pth = r"data\tables\FarmSizes\{0}_field_sizes_2018.csv".format(bl)
#     df = pd.read_csv(pth)
#     df = df[df['Area'] > .3]
#     sns.kdeplot(data=df, x='Area', ax=axs[1,], cut=0, log_scale=True, linestyle = linestyles[b], linewidth = 1,)
#     axs[1,].set_title('b) Field sizes',  x=0.9, y=1.0, pad=-14)
#     axs[1,].set_xlabel('Hectares')
#     axs[1,].spines['right'].set_visible(False)
#     axs[1,].spines['top'].set_visible(False)
#     axs[1,].legend(legend_elements, bl_lst, frameon=False, bbox_to_anchor=(0.7, 0.2))
#     # axs[1,].annotate(s = 'b) Field sizes', xy = (40,1), fontsize=12, fontweight = 'light')
#
# plt.sca(axs[0,])
# plt.xticks([3, 10, 100, 1000], ['3', '10', '100', '1000'])
# axs[0,].set_xticks([], minor=True)
#
# plt.sca(axs[1,])
# plt.xticks([.3, 1, 10, 100], ['0.3', '1', '10', '100'])
# axs[1,].set_xticks([], minor=True)
#
# fig.tight_layout()
# out_pth = r"figures\plots\farm and field sizes\SA+BB+LS+BV_farm_field_sizes_kdeplot.png"
# plt.savefig(out_pth)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------