# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
from osgeo import gdal
from osgeo import ogr
import time
import numpy as np

## ToDo: Dieses package musst du wahrscheinlich noch installieren
import joblib

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
WD = r'C:\Users\IAMO\Documents\work_data\cst_paper'
os.chdir(WD)

##
MIN_YEAR = 2013
MAX_YEAR = 2019
BL = 'TH'

## ToDo: Hier musst du den Pfad angeben, wo du das Text file abelegt hast
TILES_LST_TXT_PTH = rf'data\raster\tile_list_{BL}.txt'
## ToDo: Hier musst du den Pfad angeben, wo du die von dir erstellten Raster abelegt hast
MOSAICS_PTH = r"data\raster\mosaics\crop types"
## ToDo: Hier musst du den Pfad angeben, wo du das grid shapefile abelegt hast
GRID_PTH = rf"data\vector\grid\Invekos_grid_{BL}_15km.shp"
## ToDo: Hier musst du den Pfad angeben, wo den Ordner "grid_15km" angelegt hast.
TILES_OUT_PTH = r"data\raster\grid_15km"

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
def create_folder(directory):
    """
    Tries to create a folder at the specified location. Path should already exist (excluding the new folder).
    If folder already exists, nothing will happen.
    :param directory: Path including new folder.
    :return: Creates a new folder at the specified location.
    """

    import os
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def open_raster_from_list(raster_pth_lst):
    """
    Opens all rasters from the provided list and puts them in an output list.
    :param raster_pth_lst: List of raster paths which should be opened.
    :return: List of opened rasters.
    """

    rasterList = []
    for rastername in raster_pth_lst:
        raster = gdal.Open(rastername)
        rasterList.append(raster)

    return rasterList


def stack_raster_from_list(rasterList, outputPath, data_type=None):
    """
    Stacks the first band of n rasters that are stored in a list. The properties
    of the first raster are used to set the definition of the output raster.
    rasterList - list containing the rasters that have the same dimensions and Spatial References
    outputPath - Path including the name to which the stack is written
    """
    from osgeo import gdal

    gt = rasterList[0].GetGeoTransform()
    pr = rasterList[0].GetProjection()
    if data_type == None:
        data_type = rasterList[0].GetRasterBand(1).DataType
    x_res = rasterList[0].RasterXSize
    y_res = rasterList[0].RasterYSize

    target_ds = gdal.GetDriverByName('GTiff').Create(outputPath, x_res, y_res, len(rasterList), data_type, options=['COMPRESS=DEFLATE'])
    target_ds.SetGeoTransform(gt)
    target_ds.SetProjection(pr)

    for i in range(0, len(rasterList)):
        # print(i+1, len(rasterList))
        band = target_ds.GetRasterBand(i + 1)
        no_data_value = rasterList[i].GetRasterBand(1).GetNoDataValue()
        no_data_value = int(no_data_value)
        arr = rasterList[i].GetRasterBand(1).ReadAsArray()
        band.WriteArray(arr)
        band.SetNoDataValue(no_data_value)
        band.FlushCache()

    del(target_ds)



def write_array_to_raster(in_array, out_path, gt, pr, no_data_value, type_code=None, options=['COMPRESS=DEFLATE', 'PREDICTOR=1']):
    """
    Writes an array to a tiff-raster. If no type code of output is given, it will be extracted from the input array.
    As default a deflate compression is used, but can be specified by the user.
    :param in_array: Input array
    :param out_path: Path of output raster
    :param gt: GeoTransfrom of output raster
    :param pr: Projection of output raster
    :param no_data_value: Value that should be recognized as the no data value
    :return: Writes an array to a raster file on the disc.
    """

    # Conversion dictionary:
    # NP2GDAL_CONVERSION = {
    #     "uint8": 1,
    #     "int8": 1,
    #     "uint16": 2,
    #     "int16": 3,
    #     "uint32": 4,
    #     "int32": 5,
    #     "float32": 6,
    #     "float64": 7,
    #     "complex64": 10,
    #     "complex128": 11,
    # }

    from osgeo import gdal
    from osgeo import gdal_array

    if type_code == None:
        type_code = gdal_array.NumericTypeCodeToGDALTypeCode(in_array.dtype)

    if len(in_array.shape) == 3:
        nbands_out = in_array.shape[0]
        x_res = in_array.shape[2]
        y_res = in_array.shape[1]

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, type_code, options=options)
        out_ras.SetGeoTransform(gt)
        out_ras.SetProjection(pr)

        for b in range(0, nbands_out):
            band = out_ras.GetRasterBand(b + 1)
            arr_out = in_array[b, :, :]
            band.WriteArray(arr_out)
            band.SetNoDataValue(no_data_value)
            band.FlushCache()

        del (out_ras)

    if len(in_array.shape) == 2:
        nbands_out = 1
        x_res = in_array.shape[1]
        y_res = in_array.shape[0]

        out_ras = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, nbands_out, type_code, options=options)
        out_ras.SetGeoTransform(gt)
        out_ras.SetProjection(pr)

        band = out_ras.GetRasterBand(1)
        band.WriteArray(in_array)
        band.SetNoDataValue(no_data_value)
        band.FlushCache()

        del (out_ras)


def cut_ras_to_tiles(path):
    print(path)
    ## Open raster and shapefile with tile polygons
    ras = gdal.Open(path)
    shp = ogr.Open(GRID_PTH)
    lyr = shp.GetLayer()
    sr = lyr.GetSpatialRef()

    ## Loop over tile polygons
    for feat in lyr:

        ## get polygon id == name
        name = feat.GetField('POLYID')
        print(name)

        ## Get extent
        geom = feat.geometry().Clone()
        ext = geom.GetEnvelope()

        x_min = ext[0]
        x_max = ext[1]
        y_min = ext[2]
        y_max = ext[3]

        ## Create subfolder with tile name as name
        out_path = rf"{TILES_OUT_PTH}\{name}"
        create_folder(out_path)
        rastype = os.path.basename(path).split('_')[0]
        year = os.path.basename(path).split('_')[-1]
        year = year.split(".")[0]
        out_name = rf"{out_path}\{BL}_{rastype}_{year}.tif"

        ## Cut raster to tiles
        # projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
        ras_cut = gdal.Translate(out_name, ras, projWin=[x_min, y_max, x_max, y_min], projWinSRS=sr, creationOptions=['COMPRESS=DEFLATE'])
        ras_cut = None

        print(name, "done")
    lyr.ResetReading()

    print(path, "done")


def identify_structural_diversity(ts, no_data_value, arable_grass_value, skip_lst):
    """
    Classifies crop time series over 7 years into crop sequence types based on the sum of transitions
    from one crop to another and on the number of different crops that are in the time series.
    If there are more than two years no data, arable grass or any class from the skip list, then the crop type is set to 255.
    Crop typification is based on Stein & Steinmann 2018 - "Identying crop rotation practice ..."

    :param ts: A time series of crops.
    :param no_data_value: Value indicating that there is not any crop class.
    :param arable_grass_value: Value indicating arable grass.
    :param skip_lst: List of IDs of classes that are "fallow", "unknown" or "others".
    :return: Returns crop sequence main types in integer values. With 1=A to 9=I and 255 for not classified.
    """

    ## first set all values in the sequence that also occur in the skip list to the no data value
    ts_calc = ts.copy()
    for value in skip_lst:
        ts_calc[ts_calc == value] = no_data_value

    ## now count the transitions between values in the time series
    sum_trans = 0
    for i in range(len(ts_calc) - 1):
        if ts_calc[i] != ts_calc[i + 1]:
            sum_trans += 1
        else:
            sum_trans += 0

    ## count the number of crops
    unique, counts = np.unique(ts_calc, return_counts=True)
    sum_crops = len(unique)

    ## lastly, count the occurences of temporary grass, fallow, others, unkown or no data
    ## for that, set the occurecences of arable grass also to no data
    ts_calc[ts_calc == arable_grass_value] = no_data_value
    num_no_data = np.sum(np.where(ts_calc == no_data_value, 1, 0))

    ## determine the main type of the crop sequence on the following rule set
    if num_no_data > 2:
        main_type = 255
    elif sum_crops == 1:
        main_type = 1  # A
    elif sum_crops == 2 and (sum_trans == 1 or sum_trans == 2):
        main_type = 2  # B
    elif sum_crops == 3 and sum_trans == 2:
        main_type = 2  # B
    elif sum_crops == 2 and (sum_trans == 3 or sum_trans == 4):
        main_type = 3  # C
    elif sum_crops == 2 and (sum_trans == 5 or sum_trans == 6):
        main_type = 4  # D
    elif sum_crops == 3 and (sum_trans == 3 or sum_trans == 4):
        main_type = 5  # E
    elif sum_crops == 3 and (sum_trans == 5 or sum_trans == 6):
        main_type = 6  # F
    elif sum_crops == 4 and (sum_trans == 3 or sum_trans == 4):
        main_type = 7  # G
    elif sum_crops == 4 and (sum_trans == 5 or sum_trans == 6):
        main_type = 8  # H
    elif sum_crops >= 5:
        main_type = 9  # I
    else:
        main_type = 255

    return main_type


def stack_rasters(tile):
    print("Starting", tile)

    year_range = range(MIN_YEAR, MAX_YEAR + 1)
    per = '{0}-{1}'.format(MIN_YEAR, MAX_YEAR)
    print(f"period {per}")

    print("Stacking")
    ras_ct_lst = [rf'{TILES_OUT_PTH}\{tile}\{BL}_CropTypes_{year}.tif' for year in year_range]
    ras_ct_lst = open_raster_from_list(ras_ct_lst)
    ras_lc_lst = [rf'{TILES_OUT_PTH}\{tile}\{BL}_CropTypesLeCe_{year}.tif' for year in year_range]
    ras_lc_lst = open_raster_from_list(ras_lc_lst)
    ras_ws_lst = [rf'{TILES_OUT_PTH}\{tile}\{BL}_CropTypesWiSu_{year}.tif' for year in year_range]
    ras_ws_lst = open_raster_from_list(ras_ws_lst)

    out_pth_ct = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypes.tif'
    stack_raster_from_list(ras_ct_lst, out_pth_ct, data_type=gdal.GDT_Byte)
    out_pth_lc = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypesLeCe.tif'
    stack_raster_from_list(ras_lc_lst, out_pth_lc, data_type=gdal.GDT_Byte)
    out_pth_ws = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypesWiSu.tif'
    stack_raster_from_list(ras_ws_lst, out_pth_ws, data_type=gdal.GDT_Byte)

def determine_crop_sequence_types(tile):
    print("Starting", tile)

    year_range = range(MIN_YEAR, MAX_YEAR + 1)
    per = '{0}-{1}'.format(MIN_YEAR, MAX_YEAR)
    print(f"period {per}")
    pth_ct = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypes.tif'
    pth_lc = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypesLeCe.tif'
    pth_ws = rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropTypesWiSu.tif'

    print(tile, "Cleaning")
    ## open rasterized kulturtyp raster
    ras = gdal.Open(pth_ct)
    arr = ras.ReadAsArray()

    ## get some arr attributes
    gt = ras.GetGeoTransform()
    pr = ras.GetProjection()
    no_data_value = ras.GetRasterBand(1).GetNoDataValue()
    bands = arr.shape[0]

    ## combine the two legumes classes to one by setting class 14 to class 12
    for b in range(bands):
        arr[b, :, :][arr[b, :, :] == 14] = 12

    print(tile, "Determine structural diversity")
    #### derive main type from kulturtyp raster. If this was alread done, then load the respective raster instead
    arr_mt = np.apply_along_axis(func1d=identify_structural_diversity, axis=0, arr=arr, no_data_value=255, arable_grass_value = 13, skip_lst = [30, 70, 80, 99])
    # arr_mt = arr_mt * arr_mask
    # arr_mt[arr_mt == 0] = 255
    # raster.write_array_to_raster(arr_mt, r'raster\grid_15km\{0}\{1}_MainType_v2.tif'.format(tile, per), gt, pr, no_data_value, type_code = gdal.GDT_Byte)
    # arr_mt = gdal.Open(r'raster\grid_15km\{0}\{1}_MainType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "Determine functional diversity")
    #### derive sub type from cereal leaf raster and winter-summer raster
    arr_lc = gdal.Open(pth_lc).ReadAsArray()
    arr_ws = gdal.Open(pth_ws).ReadAsArray()

    ## where both arrays of the structural types are 99, set them to 255
    bands = arr_lc.shape[0]
    for b in range(bands):
        arr_lc[b, :, :][arr_lc[b, :, :] == 99] = 255

    bands = arr_ws.shape[0]
    for b in range(bands):
        arr_ws[b, :, :][arr_ws[b, :, :] == 99] = 255

    ## mask all no data values
    arr_lc_m = np.ma.masked_where(arr_lc == 255, arr_lc)
    arr_ws_m = np.ma.masked_where(arr_ws == 255, arr_ws)

    ## calculate the sum of leaf crop occurences and the sum of spring crop occurences
    ## leaf crop occurences
    arr_lc_sum = np.ma.sum(arr_lc_m, axis=0)
    arr_lc_sum = np.ma.filled(arr_lc_sum, 255)

    ## spring crop occurences
    arr_ws_sum = np.ma.sum(arr_ws_m, axis=0)
    arr_ws_sum = np.ma.filled(arr_ws_sum, 255)

    ## identify sub types for a seven year period
    ## create output array
    arr_st = np.full(arr_ws_sum.shape, 255)

    arr_st[(arr_lc_sum == 0) & (arr_ws_sum == 0)] = 1
    arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 2
    arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 3
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum == 0)] = 4
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 5
    arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 3) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 6
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum == 0)] = 7
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum >= 1) & (arr_ws_sum <= 4)] = 8
    arr_st[(arr_lc_sum >= 4) & (arr_lc_sum <= 7) & (arr_ws_sum >= 5) & (arr_ws_sum <= 7)] = 9

    # ## identify sub types for a four year period
    # ## create output array
    # arr_st = np.full(arr_ws_sum.shape, 255)
    #
    # arr_st[(arr_lc_sum == 0) & (arr_ws_sum == 0)] = 1
    # arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 1) & (arr_ws_sum <= 2)] = 2
    # arr_st[(arr_lc_sum == 0) & (arr_ws_sum >= 3) & (arr_ws_sum <= 4)] = 3
    # arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 2) & (arr_ws_sum == 0)] = 4
    # arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 2) & (arr_ws_sum >= 1) & (arr_ws_sum <= 2)] = 5
    # arr_st[(arr_lc_sum >= 1) & (arr_lc_sum <= 2) & (arr_ws_sum >= 3) & (arr_ws_sum <= 4)] = 6
    # arr_st[(arr_lc_sum >= 3) & (arr_lc_sum <= 4) & (arr_ws_sum == 0)] = 7
    # arr_st[(arr_lc_sum >= 3) & (arr_lc_sum <= 4) & (arr_ws_sum >= 1) & (arr_ws_sum <= 2)] = 8
    # arr_st[(arr_lc_sum >= 3) & (arr_lc_sum <= 4) & (arr_ws_sum >= 3) & (arr_ws_sum <= 4)] = 9

    # raster.write_array_to_raster(arr_st, r'raster\grid_15km\{0}\{1}_SubType_v2.tif'.format(tile, per), gt, pr, no_data_value, type_code=gdal.GDT_Byte)
    # arr_st = gdal.Open(r'raster\grid_15km\{0}\{1}_SubType.tif'.format(tile, per)).ReadAsArray()

    print(tile, "Combining structural and functional diversity")
    arr_mt_m = np.ma.masked_where(arr_mt == 255, arr_mt)
    arr_st_m = np.ma.masked_where(arr_mt == 255, arr_st)
    arr_ct_comb = (arr_mt_m * 10) + arr_st_m
    write_array_to_raster(arr_ct_comb, rf'{TILES_OUT_PTH}\{tile}\{BL}_{per}_CropSeqType.tif', gt, pr, no_data_value, type_code=gdal.GDT_Byte)

    print(tile, "done!\n")


def main():
    stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("start: " + stime)

    print("################# CUT MOSAICS TO TILES ###############")
    ## create list of mosaics
    rastypes = ['CropTypesLeCe', 'CropTypesWiSu', 'CropTypes']
    pth_template = "{0}\{1}_{2}_{3}.tif"
    pth_lst = [pth_template.format(MOSAICS_PTH, rastype, BL, year) for year in range(MIN_YEAR, MAX_YEAR+1) for rastype in rastypes]

    ## Create out folder, just to be sure that it exists
    create_folder(TILES_OUT_PTH)

    ## Parallel processing of cutting
    # joblib.Parallel(n_jobs=3)(joblib.delayed(cut_ras_to_tiles)(pth) for pth in pth_lst)
    # ## Alternative:
    # for pth in pth_lst:
    #     cut_ras_to_tiles(path=pth)

    print("################# DETERMINE CROP SEQUENCE TYPES ###############")
    ## Determine crop sequence types
    with open(TILES_LST_TXT_PTH) as file:
        tiles_lst = file.readlines()
    print(f"Number of tiles: {len(tiles_lst)}")
    tiles_lst = [item.strip() for item in tiles_lst]
    joblib.Parallel(n_jobs=3)(joblib.delayed(stack_rasters)(tile) for tile in tiles_lst[:2])
    joblib.Parallel(n_jobs=3)(joblib.delayed(determine_crop_sequence_types)(tile) for tile in tiles_lst[:2])
    # ## Alternative:
    # for tile in tiles_lst:
    #     stack_rasters(tile=tile)
    #     determine_crop_sequence_types(tile=tile)

    etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("start: " + stime)
    print("end: " + etime)


if __name__ == '__main__':
    main()