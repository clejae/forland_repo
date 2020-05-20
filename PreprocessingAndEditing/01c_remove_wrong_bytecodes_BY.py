# Clemens Jänicke
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import ogr
import os
import joblib

## CJ REPO
import vector
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = 'BY'

ind_lst = [15, 23, 18, 14, 17, 9, 1, 19, 22, 20, 3, 5, 16, 21, 11, 13, 8, 12, 4, 6, 2, 10, 7] # sorted by feature count

task_lst = []
for year in range(2017, 2020):
    for index in ind_lst:
        task_lst.append((year, index))
print(len(task_lst), task_lst)

# for task in task_lst:
def workFunc(task):

    year = task[0]
    index = task[1]

    print(year, index, '/n')

    ## Input shapefile & output folder
    out_folder = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}_temp\\".format(year, index)
    in_shp_pth = r"data\vector\InvClassified\BY\slices\{0}\InVekos_BY_{0}_{1}.shp".format(year, index)

    #### Define paths
    no_dups_pth = out_folder + '01_noDuplicates.shp'
    inters_pth = out_folder + '02_intersections.shp'

    target_fname = 'beschreibu'
    # bem_fname= 'beschreibu'
    # kart_fname = 'K_ART'

    for pth in [inters_pth,no_dups_pth]:
        print(pth)
        shp = ogr.Open(pth, 1)
        lyr = shp.GetLayer()

        ## get list of field names
        fname_lst = vector.getFieldNames(shp)

        field_index = fname_lst.index(target_fname)

        ## loop over features and set kulturtyp and WinterSummer-code depending on the k_art code,
        ## set CerealLeaf-Code depending on kulturtyp

        for f, feat in enumerate(lyr):
            fid = feat.GetField("ID")
            # print(year, index, "ID:", fid)

            ## Although all umlaute were replaced, there are some encoding issues.
            ## After every replaced Umlaut, there is still a character, that can't be decoded by utf-8
            ## By encoding it again and replacing it with '?', I can remove this character
            target_str = feat.GetField(target_fname)

            if target_str != None:
                target_str = target_str.encode('utf8', 'replace')  # turns string to bytes representation
                # print(year, "Uncorrected:", target_str)
                target_str = target_str.replace(b'\xc2\x9d', b'')   # this byte representations got somehow into some strings
                target_str = target_str.replace(b'\xc2\x81', b'')   # this byte representations got somehow into some strings
                target_str = target_str.replace(b'\udcfc', b'')  # this byte representations got somehow into some strings
                target_str = target_str.decode('utf8', 'replace') # turns bytes representation to string
                target_str = target_str.replace('?', '')
                target_str = target_str.replace('Ä','Ae')
                target_str = target_str.replace('Ö', 'Oe')
                target_str = target_str.replace('Ü', 'Ue')
                target_str = target_str.replace('ä', 'ae')
                target_str = target_str.replace('ö', 'oe')
                target_str = target_str.replace('ü', 'ue')
                target_str = target_str.replace('ß', 'ss')
            else:
                target_str = ''
            # print(year, "Corrected:", target_str)
            feat.SetField(field_index, target_str)

            lyr.SetFeature(feat)
        lyr.ResetReading()

    del shp, lyr

if __name__ == '__main__':
    joblib.Parallel(n_jobs=15)(joblib.delayed(workFunc)(task) for task in task_lst)