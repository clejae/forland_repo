# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import gdal
import numpy as np
import pandas as pd

# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl_lst = ['BB']

bl_dict = {'BB':['2005-2008','2006-2009','2007-2010','2008-2011','2009-2012','2010-2013',
                 '2011-2014','2012-2015','2013-2016','2014-2017','2015-2018'],
           'SA':['2008-2014','2012-2018'],
           'BV':['2012-2018'],#'2005-2011','2008-2014',
           'LS':['2012-2018']}

# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

for bl in bl_lst:

    ## list of tile names of current federal state
    with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
        tiles_lst = file.readlines()
    tiles_lst = [item.strip() for item in tiles_lst]

    ## get periods for which the csts are available for the current federal state
    per_lst = bl_dict[bl]

    ##
    df_lst = []
    per_df_lst = []
    top15_lst = []

    ## loop over periods
    for per in per_lst:
        print('\n########', bl, per, '#######\n')

        ## define list of all possible crop sequence types
        ## these will be the column names
        cst_lst = [i+j for i in range(10,100,10) for j in range(1,10)]
        cst_lst.append(255)
        cols = [str(i) for i in cst_lst]
        cols.insert(0, 'Tile')

        ## create an empty df that will be filled
        df = pd.DataFrame(columns=cols)

        ## loop over tiles
        for t, tile in enumerate(tiles_lst):
            print(tile, t, 'of', len(tiles_lst))

            ## open raster, get no data value
            ras = gdal.Open(r'data\raster\grid_15km\{0}\{1}_{2}_CropSeqType.tif'.format(tile, bl, per))
            arr = ras.ReadAsArray()
            ndval = ras.GetRasterBand(1).GetNoDataValue()

            ## get all csts that occur in current raster
            ## and count them
            uniques, counts= np.unique(arr, return_counts=True)

            ## calculate area for all occuring csts and write to dataframe
            df.at[t, 'Tile'] = tile
            for c, count in enumerate(counts):
                area = count * .0025
                col = str(uniques[c])
                df.at[t, col] = area

        ## aggregate the areas over all tiles,
        df_sum = round(df[cols[1:-1]].sum(0),3)
        df_sum = pd.DataFrame(df_sum)
        df_sum.reset_index(inplace=True)
        df_sum.columns = ['CST', 'Area']

        ## calculate share of all csts
        total_area = df_sum['Area'].sum()
        df_sum['Share'] = round(df_sum['Area']/total_area * 100, 2)

        ## add column of current period
        df_sum['Period'] = per

        df_lst.append(df_sum)

        ## calculate shares of all csts of current period
        columns = ['MainType', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SUM']
        indeces = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'SUM']
        # indeces = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'SUM']
        df_per = pd.DataFrame(columns=columns)

        for r, i in enumerate(range(0, 80, 9)):
            sl = list(df_sum['Area'][i: i + 9])
            sl.append(round(sum(sl),3))
            row = indeces[r]
            sl.insert(0, row)
            print(sl)
            df_per.loc[r] = sl
        per_df_lst.append(df_per)

        ## derive top fifteen csts of current period
        ## calculate their shares
        top_15 = df_sum.sort_values(by=['Area'], ascending=False)
        top_15 = top_15[:15]
        top15_lst.append(top_15)

    ## concatenate the aggregated tables
    ## so that all periods are in one table
    df_area_aggr = pd.concat(df_lst)
    top15_aggr = pd.concat(top15_lst)

    with pd.ExcelWriter(r'data\tables\crop_sequence_types\{0}\{0}_CSTArea_4_year_seq.xlsx'.format(bl)) as writer:
        df_area_aggr.to_excel(writer, sheet_name='AreaAggregated', index=False)
        top15_aggr.to_excel(writer, sheet_name='Top15CSTs', index=False)
        for s, sheet in enumerate(per_df_lst):
            sheet_name = per_lst[s]
            sheet.to_excel(writer, sheet_name = sheet_name, index=False)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#