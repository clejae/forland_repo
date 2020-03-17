# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Patch
import gdal
import numpy as np
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
os.chdir(wd)
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
with open(r'data\raster\tile_list_BB.txt') as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

plt.ioff()

# A3, B2, B3, C5, E2, E4, E5, F2, F4, F5, G5, H2, H4, H5, I5
cst_lst = [22, 35, 52, 62]#, 35, 52, 54, 55, 62, 64, 65, 75, 82, 84, 85, 95]
# Maize, Winter Wheat, Oilseed Rape, Winter Barley, Rye
main_ct = [1, 2, 4, 9, 10]
per = '2005-2011'
ct = 10
for cst in cst_lst:
    main_cst = [cst]
    for tile in tiles_lst:
        ras_cst = gdal.Open(r'data\raster\grid_15km\{0}\{1}_CropSeqType.tif'.format(tile, per))
        arr_cst = ras_cst.ReadAsArray()

        ras_ct = gdal.Open(r'data\raster\grid_15km\{0}\{1}_Inv_CropTypes_BB_5m.tif'.format(tile, per))
        arr_ct = ras_ct.ReadAsArray()

        arr_ct_sum = arr_ct.copy()
        for band in range(7):
            arr_ct_sum[band, :, :][arr_ct_sum[band, :, :] != ct] = 0
            arr_ct_sum[band, :, :][arr_ct_sum[band, :, :] == ct] = 1
        arr_ct_sum = np.sum(arr_ct_sum,0)
        arr_ct_sum[arr_ct_sum > 0] = 1

        class_bins = [0, 1, 2]
        cmap = ListedColormap(['white','darkgreen', 'orange'])

        fig, axs = plt.subplots(nrows = 1, ncols =  len(main_cst) +1, sharey=True)
        axs[0].imshow(arr_ct_sum, cmap=cmap)
        axs[0].set_title('Crop type {0}'.format(ct))

        legend_patches = [Patch(color=icolor, label=label) for icolor, label in zip(['orange'], [ 'CT {0}'.format(ct)])]
        axs[0].legend(handles=legend_patches, loc='upper center', facecolor='lightgrey', edgecolor='black', bbox_to_anchor=(0.5, -0.05), ncol=2)
        box = axs[0].get_position()
        axs[0].set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        axs[0].set_yticklabels([])
        axs[0].set_xticklabels([])
        for i, cst in enumerate(main_cst):
            ## where is the current cst
            arr_cst2 = np.where(arr_cst == cst, 1, 0)
            ## where are current cst and current ct simultaneously
            arr_ct_cst = arr_ct_sum * arr_cst2
            ## sum up: 2=here are cst and ct, 2 = here is only cst
            arr_plt = arr_ct_cst + arr_cst2
            total_area = np.sum(arr_cst2)
            covered_area = np.sum(arr_ct_cst)
            covered_share = round(covered_area / total_area, 2)
            axs[i+1].imshow(arr_plt, cmap=cmap)
            axs[i+1].set_title('CST: {0}'.format(cst))
            axs[i+1].annotate('Covered area:' + str(covered_share),(0.9,.1))

            colors = ['darkgreen', 'orange']
            labels = ['only CST {0}'.format(cst), 'CT {0} in CST {1}'.format(ct, cst)]
            legend_patches = [Patch(color=icolor, label=label) for icolor, label in zip(colors, labels)]
            axs[i+1].legend(handles=legend_patches,loc='upper center', facecolor='lightgrey', edgecolor='black', bbox_to_anchor=(0.5, -0.05), ncol=2)
            box = axs[i+1].get_position()
            axs[i+1].set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
            axs[i+1].set_yticklabels([])
            axs[i+1].set_xticklabels([])
        fig.savefig(r'figures\maps\CT in CSTs\{0}_{1}_CTinCST{2}.png'.format(per,tile,cst), dpi=fig.dpi)
        plt.close()
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
# viridis = cm.get_cmap('viridis', 256)
# newcolors = viridis(np.linspace(0, 1, 256))
# newcolors[0:44,:] = np.array([1,1,1,1]) # black
# newcolors[44:87,:] = np.array([1,0,0,1]) # red
# newcolors[87:131,:] = np.array([127/256,0,1,1]) # purple
# newcolors[131:174,:] = np.array([128/256,1,0,1]) # green
# newcolors[174:218,:] = np.array([1,128/256,0,1]) # orange
# newcolors[218:255,:] = np.array([0,0,0,1]) # white
#
# newcmp = ListedColormap(newcolors)

# def my_func(ts,ct):
#     try:
#         a = np.min(np.where(ts == ct)) + 2005
#     except:
#         a = 0
#     return a
#
# arr_first_ct = np.apply_along_axis(my_func, 0, arr_ct, ct)
