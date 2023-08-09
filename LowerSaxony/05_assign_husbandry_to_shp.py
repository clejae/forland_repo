# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
import joblib
import pandas as pd

## CJs Repo
import vector
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'LS'
fname_dict = {'BB':['BNR_ZD','GROESSE'],
              'SA':['btnr','PARZ_FLAE'],
              'LS':['REGISTRIER','AREA_ha'],
              'BV':['bnrhash','flaeche']}

fname_btr = fname_dict[bl][0]
fname_new_lst = ['Cattle','Pig','Sheep']

def workFunc(year):
    print(year)

    ## Open reference data frame
    pth = r"Daten\vector\InVekos\Niedersachsen\NiSa_OriginalData\SLA_Niedersachsen\{0}\bug55854_tiere_20181115.csv".format(year)
    df = pd.read_csv(pth, sep=';')

    ## Clean dataframe
    cols_corr = ['REG_NR', 'AUFNAHMEWIRTSCHAFTSDUENGERAJ', 'TIERHALTUNG', 'T10', 'T20', 'T30', 'T40', 'T50', 'T60',
                 'T70',
                 'T80', 'T90', 'T100', 'T110', 'T120', 'T130', 'T140', 'T150', 'T160', 'T170', 'T180', 'T190', 'T1200']
    df.columns = cols_corr
    for col in cols_corr[3:22]:
        df[col] = df[col].str.extract('(\d+)', expand=False)
        df[col] = df[col].astype(float)
    df['REG_NR'] = df['REG_NR'].astype(str)
    df['Cattle'] = df[['T10', 'T20', 'T30', 'T40', 'T50', 'T60']].sum(axis=1)
    df['Sheep'] = df[['T90', 'T100', 'T110']].sum(axis=1)
    df['Pig'] = df[['T150', 'T160', 'T170', 'T180', 'T190']].sum(axis=1)

    pth = r'Clemens\data\vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
    shp = ogr.Open(pth, 1)
    lyr = shp.GetLayer()
    fname_lst = vector.getFieldNames(shp)

    for fname_new in fname_new_lst:
        if fname_new in fname_lst:
            print("The field {0} exists already in the layer.".format(fname_new))
        else:
            lyr.CreateField(ogr.FieldDefn(fname_new, ogr.OFTReal))
            fname_lst = vector.getFieldNames(shp)

    for f, feat in enumerate(lyr):
        for fname_new in fname_new_lst:
            betr = str(feat.GetField(fname_btr))
            if betr in list(df['REG_NR']):
                animal_nr =  df[fname_new].loc[df['REG_NR'] == betr] # returns a pd Series
                animal_nr = animal_nr.iloc[0] # extracts value from pd Series
            else:
                animal_nr = 0
            feat.SetField(fname_new, animal_nr)
            lyr.SetFeature(feat)
    lyr.ResetReading()
    print(year, "done")

if __name__ == '__main__':
    joblib.Parallel(n_jobs=1)(joblib.delayed(workFunc)(year) for year in range(2018, 2019))

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#
