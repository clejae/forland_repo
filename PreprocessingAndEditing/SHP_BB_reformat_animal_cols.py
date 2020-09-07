# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import joblib
import ogr

import vector
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ USER VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'BB'
fname_old_lst = ['Rinder', 'Schwein', 'Schafe']
fname_new_lst = ['Cattle','Pig','Sheep']

def workFunc(year):
    print(year)

    pth = r'data\vector\IACS\{0}\IACS_{0}_{1}.shp'.format(bl, year)
    shp = ogr.Open(pth, 1)
    lyr = shp.GetLayer()
    fname_lst = vector.getFieldNames(shp)

    for i, fname_new in enumerate(fname_new_lst):

        if fname_new in fname_lst:
            print("The field {0} exists already in the layer.".format(fname_new))
        else:
            lyr.CreateField(ogr.FieldDefn(fname_new, ogr.OFTReal))
            fname_lst = vector.getFieldNames(shp)

        ref_field = fname_old_lst[i]

        for f, feat in enumerate(lyr):
            nr = str(feat.GetField(ref_field))
            try:
                nr = float(nr.replace(',',''))
            except:
                nr = 0
            feat.SetField(fname_new, nr)
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