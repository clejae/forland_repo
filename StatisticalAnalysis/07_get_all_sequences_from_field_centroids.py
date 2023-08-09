# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd
import gdal
import raster
import general
import glob
from collections import Counter
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl_lst = ['BB']#'BV','SA']
year = 2018

bl_dict = {'BB':['2005-2011','2008-2014','2012-2018'], #
           'SA':['2008-2014','2012-2018'], #,'2012-2018'
           'BV':['2005-2011','2008-2014','2012-2018'], #,'2012-2018'
           'LS':['2012-2018']}

fname_dict = {'BB':['BNR_ZD','GROESSE','ACKERZ'],
              'SA':['btnr','PARZ_FLAE'],
              'LS':['REGISTRIER','AREA_ha'],
              'BV':['bnrhash','flaeche']}
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

## INPUT
for bl in bl_lst:
    per_lst = bl_dict[bl]
    for per in per_lst:

        # print('########################\n', bl, per, '\n########################' )
        #
        in_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}_centroids2.shp".format(bl, year)

        cst_ras_name = "{0}_{1}_CropSeqType_clean.tif".format(bl, per)
        ct_ras_name = "{0}_{1}_CropTypes.tif".format(bl, per)
        bgr_ras_name = "{0}_BTR_GROESS_2018.tif".format(bl)

        # ## OUTPUT
        # out_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}_centroids.shp".format(bl, year)
        out_csv_descr = '{0}_{1}_sequences_farm-size'.format(bl, per)
        #
        #############
        with open(r'data\raster\tile_list_{0}.txt'.format(bl)) as file:
            tiles_lst = file.readlines()
        tiles_lst = [item.strip() for item in tiles_lst]

        shp_tiles = ogr.Open(r"data\vector\grid\Invekos_grid_GER_15km.shp")
        lyr_tiles = shp_tiles.GetLayer()


        ## extract sequences, csts and farm sizes from fields
        print("\n######## EXTRACTION ########\n")
        def workFunc(tile):
            print(tile)
            ras_cst_pth = r"data\raster\grid_15km\{}\{}".format(tile, cst_ras_name)
            ras_ct_pth = r"data\raster\grid_15km\{}\{}".format(tile, ct_ras_name)
            ras_bgr_pth = r"data\raster\grid_15km\{}\{}".format(tile, bgr_ras_name)

            ras_cst = gdal.Open(ras_cst_pth)
            arr_cst = ras_cst.ReadAsArray()

            ras_ct = gdal.Open(ras_ct_pth)
            arr_ct = ras_ct.ReadAsArray()

            ras_bgr = gdal.Open(ras_bgr_pth)
            arr_bgr = ras_bgr.ReadAsArray()

            gt = ras_cst.GetGeoTransform()
            minx, miny, maxx, maxy = raster.getCorners(ras_cst_pth)

            out_lst = []

            shp = ogr.Open(in_shp_pth)
            lyr = shp.GetLayer()
            # double minx, double miny, double maxx, double maxy
            lyr.SetSpatialFilterRect(minx, miny, maxx, maxy)

            for feat in lyr:
                fid = feat.GetField("ID")
                fname_farm = 'BNR'
                fname_area = 'Area'

                bnr = feat.GetField(fname_farm)
                area = feat.GetField(fname_area)
                # ackerz = feat.GetField("ACKERZ")
                geom = feat.GetGeometryRef()
                centroid = geom.Centroid()
                mx, my = centroid.GetX(), centroid.GetY()
                px = int((mx - gt[0]) / gt[1])  # x pixel
                py = int((my - gt[3]) / gt[5])  # y pixel
                cst = arr_cst[ py, px]
                ct = arr_ct[:, py, px]
                bgr = arr_bgr[ py, px]
                # ct[ct == 30] = 255
                # ct[ct == 70] = 255
                # ct[ct == 80] = 255
                # ct[ct == 99] = 255
                ct[ct == 14] = 12

                ct = list(ct)
                ct = [str(id) for id in ct]
                out_str = '_'.join(list(ct))

                out_lst.append([cst, out_str, bgr, fid, area, bnr])

            out_pth = r"data\tables\FarmSize-CSTs\{0}\{1}_{2}.csv".format(bl, out_csv_descr, tile)
            if len(out_lst) > 0:
                general.writeListToCSV(out_lst, out_pth)
            print(tile, "done")

        if __name__ == '__main__':
            joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(tile) for tile in tiles_lst)
        #
        # lst = general.getFilesinFolderWithEnding(r'data\tables\FarmSize-CSTs\{0}'.format(bl), "csv", True)
        lst = glob.glob(r"Q:\FORLand\Clemens\data\tables\FarmSize-CSTs\{0}\{0}_{1}_sequences_farm-size_*.csv".format(bl,per))

        df = pd.DataFrame(columns=[0,1,2,3,4,5])
        for c, csv_pth in enumerate(lst):
            print(c, csv_pth)
            csv = pd.read_csv(csv_pth, header=None)
            df = df.append(csv)

        df = df.reset_index()
        df = df.drop(columns=['index'])
        df.columns = ['CST','Sequence','farm size','ID','field size','BNR']
        df.to_csv(r'data\tables\FarmSize-CSTs\{}.csv'.format(out_csv_descr))
        # ind_lst = df.index[df[0] == 255].tolist()
        # df_clean = df.drop(ind_lst)
        #
        # seq_lst = df_clean[1].tolist()
        # seq_count = Counter(seq_lst)
        #
        # df_out = pd.DataFrame.from_dict(seq_count, orient='index') #, columns=
        # df_out = df_out.reset_index()
        # df_out.columns = ['sequence','count']
        #
        # df_out.to_csv(r'data\tables\CropRotations\{}_counts.csv'.format(out_csv_descr))

        # mcst_lst = [13, 23, 35, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
        # for mcst in mcst_lst:
        #     ind_lst = df_clean.index[df_clean[0] != mcst].tolist()
        #     df_mcst = df_clean.drop(ind_lst)
        #     seq_lst = df_mcst[1].tolist()
        #     seq_count = Counter(seq_lst)
        #
        #     df_out = pd.DataFrame.from_dict(seq_count, orient='index')  # , columns=
        #     df_out = df_out.reset_index()
        #     df_out.columns = ['sequence', 'count']
        #
        #     df_out.to_csv(r'data\tables\CropRotations\{}_counts_{}.csv'.format(out_csv_descr,mcst), index=False)
        #
        # mcst_lst = [13, 23, 35, 52, 54, 55, 62, 64, 65, 75, 84, 85, 95]
        # mcst = 13
        # for mcst in mcst_lst:
        #     csv_pth = r'Q:\FORLand\Clemens\data\tables\CropRotations\sequences\2005-2011_all_sequences_counts_{}.csv'.format(mcst)
        #     df = pd.read_csv(csv_pth)
        #
        #     ct_dict = {
        #         1 : 'MA',
        #         2 : 'WW',
        #         3 : 'SB',
        #         4 : 'OR',
        #         5 : 'PO',
        #         6 : 'SC',
        #         7 : 'TR',
        #         9 : 'WB',
        #         10: 'RY',
        #         12: 'LE',
        #         13: 'GR',
        #         14: 'LE',
        #         60: 'VE',
        #         255: 'FA'
        #     }
        #
        #     def convert(str):
        #         ct_lst = str.split('_')
        #         ct_lst = [ct_dict[int(i)] for i in ct_lst]
        #         ct_str = '-'.join(ct_lst)
        #         return ct_str
        #
        #     df['seq_names'] = df['sequence'].map(convert)
        #     df.to_excel(csv_pth[:-3] + 'xlsx', index = False)
        #
        #     os.remove(csv_pth)

    print('########################\n', bl, "done", '\n########################')
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


