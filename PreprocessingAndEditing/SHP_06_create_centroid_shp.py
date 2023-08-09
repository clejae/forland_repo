# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import ogr
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
bl_lst = ['BB']#'BV','SA']
year = 2018
fname_dict = {'BB':['BNR_ZD','GROESSE','ID'],
              'SA':['btnr','PARZ_FLAE','ID'],
              'LS':['REGISTRIER','AREA_ha','S_FACHID'],
              'BV':['bnrhash','flaeche','ID']}
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

for bl in bl_lst:
    print('########################\n', bl, '\n########################' )

    ## Input
    in_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}.shp".format(bl, year)
    shp = ogr.Open(in_shp_pth)
    lyr = shp.GetLayer()
    sr = lyr.GetSpatialRef()

    ## Output
    out_shp_pth = r"data\vector\IACS\{0}\IACS_{0}_{1}_centroids2.shp".format(bl, year)

    ## Create centroid shapefile
    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(out_shp_pth):
        drv.DeleteDataSource(out_shp_pth)
    out_shp = drv.CreateDataSource(out_shp_pth)
    lyr_name = os.path.basename(out_shp_pth)
    out_lyr = out_shp.CreateLayer(lyr_name, sr, geom_type=ogr.wkbPoint)
    out_lyr.CreateField(ogr.FieldDefn("ID", ogr.OFTString))
    out_lyr.CreateField(ogr.FieldDefn("Area", ogr.OFTReal))
    out_lyr.CreateField(ogr.FieldDefn("BNR", ogr.OFTInteger64))
    out_defn = out_lyr.GetLayerDefn()

    ## loop over features of IACS 2018
    ## calculate centroid, get attributes
    ## set feature to new shapefile
    for feat in lyr:
        ## get ID
        fname_id = fname_dict[bl][2]
        fid = feat.GetField(fname_id)
        fname_area = fname_dict[bl][1]
        area = feat.GetField(fname_area)
        fname_bnr = fname_dict[bl][0]
        bnr = feat.GetField(fname_bnr)

        geom = feat.GetGeometryRef()

        centroid = geom.Centroid()
        out_feat = ogr.Feature(out_defn)
        out_feat.SetGeometry(centroid)
        out_feat.SetField("ID", fid)
        out_feat.SetField("Area", area)
        out_feat.SetField("BNR", bnr)
        out_lyr.CreateFeature(out_feat)

    lyr.ResetReading()
    out_shp.Destroy()

    print('########################\n', bl, "done", '\n########################')
# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


