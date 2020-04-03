import ogr
import joblib

## CJ REPO
import vector

# year_lst = [2015]

for year in range(2013, 2014):
# def workFunc(year):
    ## Destination Shapefile
    pth1 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege{0}_temp\05_nodups_cleaned_02.shp".format(year)
    ## Reference Shapefile
    pth2 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege{0}.shp".format(year)

    ## Open both files
    shp1 = ogr.Open(pth1, 1)
    lyr1 = shp1.GetLayer()

    shp2 = ogr.Open(pth2)
    lyr2 = shp2.GetLayer()

    ## Create list of IDs
    lst = []

    ## Get Field Names of
    fname_lst1 = vector.getFieldNames(shp1)
    fname_lst2 = vector.getFieldNames(shp2)

    for feat in lyr1:
        fid = feat.GetField("ID")
        id_old = feat.GetField("ID_HaBl")

        if id_old == None:
            lst.append(fid)

    lyr1.ResetReading()
    total = len(lst)
    print(total)

    for f, fid in enumerate(lst):

        print(year, '{}/{}'.format(f, total), fid)

        lyr1.SetAttributeFilter("ID = " + str(fid))
        lyr2.SetAttributeFilter("ID = " + str(fid))

        feat1 = lyr1.GetNextFeature()
        feat2 = lyr2.GetNextFeature()

        for fname in fname_lst2:

            if fname in fname_lst1:
                ind = fname_lst1.index(fname)
                attr = feat2.GetField(fname)

                print("Field:", fname)#, "Attribute:", attr)

                feat1.SetField(ind, attr)
                lyr1.SetFeature(feat1)
            else:
                pass

# if __name__ == '__main__':
#     joblib.Parallel(n_jobs=10)(joblib.delayed(workFunc)(year) for year in year_lst)