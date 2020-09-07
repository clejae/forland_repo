import os

os.chdir(r'Z:\germany-drought\00_parameter_files')

for year in range(2005, 2019):

    in_file = open('TSA-NDVI_2019.prm','r')
    out_pth = 'TSA-NDVI_' + str(year) + '.prm'
    out_file = open(out_pth, 'w+', newline='')
    print(str)
    for i, line in enumerate(in_file):
        if i == 44:
            out_file.write('DATE_RANGE = {0}-01-01 {0}-12-31\n'.format(year))
        else:
            out_file.write(line)
    print("Close files.")
    in_file.close()
    out_file.close()

batch_file = open('batch_tsa.sh','w', newline='')
for i in range(2005, 2020):
    print(i)
    batch_file.write('force-higher-level ./00_parameter_files/TSA-NDVI_{0}.prm\n'.format(i))
batch_file.close()