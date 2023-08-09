# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl = 'BV'
per = '2012-2018'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

df = pd.read_csv(r"Q:\FORLand\Clemens\data\tables\FarmSize-CSTs\{0}_{1}_sequences_farm-size.csv".format(bl, per))

df = df[["CST","farm size"]]
df = df[df["CST"] != 255]
df["CST"] = df["CST"].astype(str)
df["Main Type"] = df.CST.str.slice(0, 1)
df["Sub Type"] = df.CST.str.slice(1, 3)

mt_lst = ['A','B','C','D','E','F','G','H','I']
## MAIN TYPES
fig, axs = plt.subplots(1, 9, sharey=True, figsize=(16, 6))
fig.text(0.5, 0.95, '{0}: farm sizes vs main types of CSTs {1}'.format(bl, per), ha='center', va='center', size=16)
fig.text(0.06, 0.5, 'Farm Size [ha]', ha='center', va='center', rotation='vertical', size=12)
for i in range(9):
    axs[i].grid(b=True, which='major', color='#666666', linestyle='-', alpha = .4)
    axs[i].boxplot(df['farm size'][df['Main Type'] == str(i+1)], showfliers=False)
    axs[i].set_title(mt_lst[i])
    axs[i].get_xaxis().set_ticks([])
plt.savefig(r"Q:\FORLand\Clemens\figures\FarmSize-CSTs\{0}_{1}_farm-size_main-types.png".format(bl,per))

## SUB TYPES
fig, axs = plt.subplots(3, 3, sharey=True, figsize=(16, 16))
fig.text(0.06, 0.5, 'Farm Size [ha]', ha='center', va='center', rotation='vertical', size=12)
fig.text(0.5, 0.95, '{0}: farm sizes vs sub types of CSTs {1}'.format(bl, per), ha='center', va='center', size=16)
i=1
for y in range(2,-1,-1):
    for x in range(0,3):
        axs[y, x].boxplot(df['farm size'][df['Sub Type'] == str(i)], showfliers=False)
        axs[y, x].set_title(str(i))
        axs[y, x].grid(b=True, which='major', color='#666666', linestyle='-', alpha=.4)
        axs[y, x].get_xaxis().set_ticks([])
        i += 1
plt.savefig(r"Q:\FORLand\Clemens\figures\FarmSize-CSTs\{0}_{1}_farm-size_sub-types.png".format(bl, per))


# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#