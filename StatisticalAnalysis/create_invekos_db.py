import ogr
import vector
import pandas as pd

df = pd.DataFrame(columns=["ID","NU_CODE"])

year = 2009
## Destination Shapefile
pth1 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege{0}_temp\01_noDuplicates.shp".format(year)
## Reference Shapefile
pth2 = r"Q:\FORLand\Clemens\data\vector\InvClassified\Antraege{0}.shp".format(year)

## Open both files
shp1 = ogr.Open(pth1, 1)
lyr1 = shp1.GetLayer()

shp2 = ogr.Open(pth2)
lyr2 = shp2.GetLayer()

## Create list of IDs
lst = [["ID","NU_CODE"]]

## Get Field Names of
fname_lst1 = vector.getFieldNames(shp1)
fname_lst2 = vector.getFieldNames(shp2)

for f, feat2 in enumerate(lyr2):
    fid2 = feat2.GetField("ID")
    nu_code = feat2.GetField("NU_CODE")
    df.loc[f] = [fid2, nu_code]


for feat1 in lyr1:


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

            print("Field:", fname, "Attribute:", attr)

            feat1.SetField(ind, attr)
            lyr1.SetFeature(feat1)
        else:
            pass
