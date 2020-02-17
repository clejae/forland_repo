# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import glob
import gdal
import joblib
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#
def StackRasterFromList(rasterList, outputPath):
    """
    Stacks the first band of n rasters that are stored in a list. The properties
    of the first raster are used to set the definition of the output raster.
    rasterList - list containing the rasters that have the same dimensions and Spatial References
    outputPath - Path including the name to which the stack is written
    """
    import gdal

    gt = rasterList[0].GetGeoTransform()
    pr = rasterList[0].GetProjection()
    data_type = rasterList[0].GetRasterBand(1).DataType
    x_res = rasterList[0].RasterXSize
    y_res = rasterList[0].RasterYSize

    target_ds = gdal.GetDriverByName('GTiff').Create(outputPath, x_res, y_res, len(rasterList), data_type)
    target_ds.SetGeoTransform(gt)
    target_ds.SetProjection(pr)

    for i in range(0, len(rasterList)):
        band = target_ds.GetRasterBand(i + 1)
        no_data_value = rasterList[i].GetRasterBand(1).GetNoDataValue()
        band.WriteArray(rasterList[i].GetRasterBand(1).ReadAsArray())
        band.SetNoDataValue(no_data_value)
        band.FlushCache()

    del(target_ds)

# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'L:\Clemens\data\\'
per_lst = [(2005,2011),(2012,2018)]
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
os.chdir(wd)

with open(r"L:\Clemens\data\raster\folder_list.txt") as file:
    tiles_lst = file.readlines()
tiles_lst = [item.strip() for item in tiles_lst]

for per in per_lst:
    print(per)
    min = per[0]
    max = per[1] + 1

    def workFunc(tile):
    # for tile in tiles_lst:
        for str in ['CropTypes','CerLeaf','WinSumm']:
            print(tile, str)
            ras_pth_lst = []
            for year in range(min,max):
                pth = r"L:\Clemens\data\raster\grid_15km\{0}\Inv_{1}_{2}_5m.tif".format(tile,str, year)
                ras_pth_lst.append(pth)
            # ras_pth_lst = glob.glob(r"L:\Clemens\data\raster\grid_15km\{0}\Inv_{1}_*_5m.tif".format(tile,str))
            ras_lst = [gdal.Open(ras) for ras in ras_pth_lst]

            StackRasterFromList(ras_lst, r"L:\Clemens\data\raster\grid_15km\{0}\2005-2011_Inv_{1}_5m.tif".format(tile,str))

    if __name__ == '__main__':
        joblib.Parallel(n_jobs=8)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)


# [(2005,2011),(2012,2018)];['CropTypes','CerLeaf','WinSumm']; 8 job = ca. 35min
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)

# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


