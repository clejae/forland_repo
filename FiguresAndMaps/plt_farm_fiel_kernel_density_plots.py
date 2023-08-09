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
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

### Boxplots of farm and field sizes
fig, axs = plt.subplots(nrows = 1, ncols = 2)
df_lst = []
for bl in bl_lst:
    pth = r"data\tables\FarmSizes\{0}_farm_sizes_2018.csv".format(bl)
    df_lst.append(pd.read_csv(pth))
df = pd.concat(df_lst)
sns.boxplot(x = 'BL', y = 'Area', data = df, ax = axs[0,])
axs[0,].set(yscale = 'log')
axs[0,].set_ylabel("Log(Area [ha])")
axs[0,].set_title('Farm sizes')

df_lst = []
for bl in bl_lst:
    pth = r"data\tables\FarmSizes\{0}_field_sizes_2018.csv".format(bl)
    df_lst.append(pd.read_csv(pth))
df = pd.concat(df_lst)
sns.boxplot(x = 'BL', y = 'Area', data = df, ax = axs[1,])
axs[1,].set(yscale = 'log')
axs[1,].set_ylabel("Log(Area [ha])")
axs[1,].set_title('Field sizes')

fig.tight_layout()
out_pth = r"figures\plots\farm and field sizes\SA+BB+LS+BV_farm_field_sizes_boxplot.png"
plt.savefig(out_pth)



## Some data exploration
for bl in bl_lst: #= 'BB'
    pth = r"data\tables\FarmSizes\{0}_farm_sizes_2018.csv".format(bl)
    df = pd.read_csv(pth)

    print(bl, df['Area'].sum())

## Some data exploration
for bl in bl_lst: #= 'BB'
    pth = r"data\tables\FarmSizes\{0}_field_sizes_2018.csv".format(bl)
    df = pd.read_csv(pth)

    print(bl, df['Area'].sum())
###
# df_comb_lst = []
for bl in bl_lst:
    # bl = 'BB'
    pth = r"data\tables\FarmSizes\{0}_farm_sizes_2018.csv".format(bl)
    df1 = pd.read_csv(pth)

    pth = r"data\tables\FarmSizes\{0}_field_sizes_2018.csv".format(bl)
    df2 = pd.read_csv(pth)

    df_comb = pd.merge(df2, df1, how='left', on='Betrieb')
    df_comb = df_comb[['Betrieb', 'Area_x', 'BL_x', 'Area_y']]
    df_comb.columns = ['Betrieb', 'Area_field', 'BL', 'Area_farm']
    ax = sns.jointplot(data=df_comb, x="Area_farm", y="Area_field", joint_kws=dict(edgecolors=None, s=5))
    ax.set_axis_labels(xlabel="Area of farm [ha]", ylabel="Area of field [ha]")

    out_pth = r"figures\plots\farm and field sizes\{0}_farm_field_sizes_scatter.png".format(bl)
    plt.savefig(out_pth)

    # df_comb_lst.append(df_comb)

# df_comb = pd.concat(df_comb_lst)


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#