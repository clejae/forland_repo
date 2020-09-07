# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import ogr
import os

## CJ REPO
import vector
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'SA'

## loop over shapefiles, add new column and fill it with code for the kulturtyp
for year in range(2009, 2019): #[2008]: #
    print(year)

    shp_name = r"Clemens\data\vector\IACS\{0}\IACS_{0}_{1}.shp".format(bl, year)

    if bl == 'BB':
        kart_fname = 'K_ART'
        kartk_fname = 'K_ART_K'
    if bl == 'SA':
        kart_fname = 'NU_CODE'
        kartk_fname = 'NU_BEZ'

    bem_fname= 'BEMERKUNG'

    shp = ogr.Open(shp_name, 1)
    lyr = shp.GetLayer()

    ## get list of field names
    fname_lst = vector.getFieldNames(shp)

    field_index = fname_lst.index(kartk_fname)

    ## loop over features and set kulturtyp and WinterSummer-code depending on the k_art code,
    ## set CerealLeaf-Code depending on kulturtyp

    for f, feat in enumerate(lyr):
        fid = feat.GetField("ID")
        print(year, "ID:", fid)
        ## get kulturart name
        ## Although all umlaute were replaced, there are some encoding issues.
        ## After every replaced Umlaut, there is still a character, that can't be decoded by utf-8
        ## By encoding it again and replacing it with '?', I can remove this character
        kart_k = feat.GetField(kartk_fname)

        if kart_k != None:
            kart_k = kart_k.encode('utf8','replace')  # turns string to bytes representation
            print(year, "Uncorrected:", kart_k)
            kart_k = kart_k.replace(b'\xc2\x9d', b'')   # this byte representations got somehow into some strings
            kart_k = kart_k.replace(b'\xc2\x81', b'')   # this byte representations got somehow into some strings
            kart_k = kart_k.decode('utf8', 'replace') # turns bytes representation to string
            kart_k = kart_k.replace('?', '')
        else:
            kart_k = ''
        print(year, "Corrected:", kart_k)
        feat.SetField(field_index, kart_k)

        bem = feat.GetField(bem_fname)
        if bem != None:
            bem = bem.encode('utf8','replace')  # turns string to bytes representation
            print(year, "Uncorrected:", bem)
            bem = bem.replace(b'\xc2\x9d', b'')   # this byte representations got somehow into some strings
            bem = bem.replace(b'\xc2\x81', b'')   # this byte representations got somehow into some strings
            bem = bem.replace(b'\udcdc', b'')  # this byte representations got somehow into some strings
            bem = bem.decode('utf8', 'replace') # turns bytes representation to string
            bem = bem.replace('?', '')
        else:
            bem = ''
        print(year, "Corrected:", bem)
        ind = fname_lst.index(bem_fname)
        feat.SetField(ind, bem)

        lyr.SetFeature(feat)
    lyr.ResetReading()
