# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import gdal
import matplotlib.pyplot as plt
plt.ioff()
import earthpy.plot as ep
import numpy as np
import time
import os
import string
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

def valueToCst(value):
    '''

    :param value: An Integer between 11 and 95
    :return: A String that indicates the Crop Sequence Type according to Stein and Steinman (2018)
    '''

    val1 = int(str(value)[0])
    str1 = string.ascii_uppercase[val1-1]
    str2 = str(value)[1]
    out_str = str1 + str2
    return out_str

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

ras = gdal.Open(r'L:\Clemens\data\raster\2005-2011_CropSeqType.tif')


value = 95


arr = ras.ReadAsArray()
arr[arr != value] = 0
arr[arr == value] = 1
plt.plot(arr)
# fig = ep.plot_bands(arr, title = valueToCst(value))
fig = fig.get_figure()
fig.savefig(r'L:\Clemens\data\t.png', )


fig, ax = ep.hist(arr.ravel(),
                  ylabel="Number of Pixels",
                  bins=range(0,100),
                  xlabel="CST")
ax.set(xlim=[0,100])
plt.show()



x = 95
class_bins = [0,x,256]
arr.dtype = np.int16
arr2 = np.digitize(arr, class_bins)




# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#







r