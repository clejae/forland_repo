# 
# github Repo: https://github.com/clejae

# --------------------------------------------------------------- LOAD PACKAGES ---------------------------------------------------------------#
from osgeo import ogr
from osgeo import gdal
import os
import time

# --------------------------------------------------------------- USER VARIABLES ---------------------------------------------------------------#
## ToDo: Anpassen!!
WD = r'\\141.20.140.92\SAN_Projects\FORLand\\'
os.chdir(WD)

BL = "TH"
MIN_YEAR = 2013
MAX_YEAR = 2019
# --------------------------------------------------------------- LOAD DATA & PROCESSING ---------------------------------------------------------------#


def rasterize_shape(in_shp_pth, out_ras_pth, attribute, extent, res, no_data_val, gdal_dtype):
    """
    This function rasterizes a shapefile based on a provided attribute of the shapefile.
    :param in_shp_pth: Path to input shapefile. String.
    :param out_ras_pth: Path to output raster, including file name and ".shp". String.
    :param attribute: Attribute (i.e. field) of shapefile that should be rasterized. If attr is an integer,
    then only the geometries of the shape will be rasterized with the provided integer as the burn value.
    :param extent: List of extent of raster. Will be checked if it fits to provided resolution.
    [xmin, xmax, ymin, ymax]
    :param res: Resolution of raster in units of projection of input shapefile.
    :param no_data_val: No data value of raster.
    :gdal_dtype = gdal data type of raster.
    :return: Output raster will be written to specified location.
    """

    import math
    import gdal
    import ogr
    import os

    ## Determine raster extent
    ## Reassuring, that extent and resolution fit together
    ## Assuming that upper left corner is correct (x_min, y_max)
    x_min = extent[0]
    x_max = extent[1]
    y_min = extent[2]
    y_max = extent[3]
    cols = math.ceil((x_max - x_min) / res)
    rows = math.ceil((y_max - y_min) / res)
    x_max = x_min + cols * res
    y_min = y_max - rows * res

    ## If input shape exists, then start the rasterization
    if os.path.exists(in_shp_pth):
        shp = ogr.Open(in_shp_pth, 0)  # 0=read only, 1=writeabel
        lyr = shp.GetLayer()

        #### Transform spatial reference of input shapefiles into projection of raster
        sr = lyr.GetSpatialRef()
        pr = sr.ExportToWkt()

        #### Create output raster
        target_ds = gdal.GetDriverByName('GTiff').Create(out_ras_pth, cols, rows, 1, gdal_dtype,
                                                         options=['COMPRESS=DEFLATE'])  # gdal.GDT_Int16)#
        target_ds.SetGeoTransform((x_min, res, 0, y_max, 0, -res))
        target_ds.SetProjection(pr)
        band = target_ds.GetRasterBand(1)
        band.Fill(no_data_val)
        band.SetNoDataValue(no_data_val)
        band.FlushCache()

        if isinstance(attribute, str):
            option_str = "ATTRIBUTE=" + attribute
            gdal.RasterizeLayer(target_ds, [1], lyr, options=[option_str])
        elif isinstance(attribute, int):
            gdal.RasterizeLayer(target_ds, [1], lyr, burn_values = [attribute])
        else:
            print("Provided attribute is not of type str or int.")

        del target_ds
    else:
        print(in_shp_pth, "doesn't exist.")


def work_func(year, feder_stat_abbr):

    #### Define extent
    ## Get extent of box of federal state
    shp_pth = fr'Clemens\data\vector\grid\Invekos_grid_{feder_stat_abbr}-Box_15km.shp'
    shp = ogr.Open(shp_pth, 0)
    lyr = shp.GetLayer()
    x_min_ext, x_max_ext, y_min_ext, y_max_ext = lyr.GetExtent()

    #### Rasterize the IACS data
    attr_lst = ["ID_KTYP", "ID_WiSo", "ID_HaBl"]
    res = 5
    no_data_val = 255
    for attr in attr_lst:

        ## input shapefile path
        ## TODO: Muss so aussehen: Clemens\data\vector\IACS\TH\IACS_TH_20xx.shp
        shp_pth = rf'Clemens\data\vector\IACS\{feder_stat_abbr}\IACS_{feder_stat_abbr}_{year}.shp'
        ## output raster path
        if attr == 'ID_KTYP':
            target_ds_pth = rf'Clemens\data\raster\mosaics\CropTypes_{feder_stat_abbr}_{year}.tif'
        elif attr == 'ID_WiSo':
            target_ds_pth = rf'Clemens\data\raster\mosaics\CropTypesWiSu_{feder_stat_abbr}_{year}.tif'
        elif attr == 'ID_HaBl':
            target_ds_pth = rf'Clemens\data\raster\mosaics\CropTypesLeCe_{feder_stat_abbr}_{year}.tif'
        else:
            target_ds_pth = rf'raster\mosaics\CropTypes{attr}_{feder_stat_abbr}_{year}.tif'

        rasterize_shape(
            in_shp_pth=shp_pth,
            out_ras_pth=target_ds_pth,
            attribute=attr,
            extent=[x_min_ext, x_max_ext, y_min_ext, y_max_ext],
            res=res,
            no_data_val=no_data_val,
            gdal_dtype=gdal.GDT_Byte)

def main():
    stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("start: " + stime)

    for year in range(MIN_YEAR, MAX_YEAR+1):
        print(year)
        work_func(
            year=year,
            feder_stat_abbr=BL
        )
        print(year, "done!")

    etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("start: " + stime)
    print("end: " + etime)



if __name__ == '__main__':
    main()