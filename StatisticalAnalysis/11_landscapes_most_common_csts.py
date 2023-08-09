# 
# github Repo: https://github.com/clejae

# ------------------------------------------ LOAD PACKAGES ---------------------------------------------------#
import os
import time
import pandas as pd
from collections import Counter
# ------------------------------------------ DEFINE FUNCTIONS ------------------------------------------------#

# ------------------------------------------ START TIME ------------------------------------------------------#
stime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
# ------------------------------------------ GLOBAL VARIABLES ------------------------------------------------#
wd = r'\\141.20.140.91\SAN_Projects\FORLand\Clemens\\'
# ------------------------------------------ LOAD DATA & PROCESSING ------------------------------------------#
os.chdir(wd)

bl = "BV"
## BV Dungau
tile_lst = ["0031_0012","0031_0013","0031_0014","0032_0012","0032_0013","0032_0014","0033_0012","0033_0013","0034_0011","0034_0012","0034_0013","0035_0011","0035_0012"]
## BV Unteres Inntal, Nördl. Isar-Inn-Hügelland, Rottal
tile_lst = ["0033_0009","0033_0010","0034_0009","0034_0010","0035_0009","0035_0010","0036_0009","0036_0010","0037_0009","0037_0010"]
## BV Unteres Lech-Wertach-Ebene, Landsberger Platten
tile_lst = ["0024_0007","0024_0008","0025_0007","0025_0008"]
## BV Gäuplatten im Maindreieck
tile_lst = ["0020_0019","0021_0020","0020_0020"]
## BV Vorland der südlichen Frankenalb, Ries
tile_lst = ["0022_0012","0022_0013","0022_0014","0023_0012","0023_0013","0023_0014","0024_0014"]

bl = "LS"
## LS Weener Geest, Butanger Moor
tile_lst = ["0006_0040","0006_0041","0006_0042","0007_0040","0007_0041","0007_0042"]
## LS Ostfriesische Seemarschen, Stader Elbmarschen
tile_lst = ["0006_0046","0006_0047","0007_0045","0007_0046","0007_0047","0007_0048","0008_0048","0009_0048","0010_0048","0011_0048","0014_0049","0015_0049","0016_0048","0016_0049","0017_0048","0017_0049"]
## LS Ostfriesische-Oldenburger Geest
tile_lst = ["0008_0046","0008_0047","0009_0043","0009_0044","0009_0045","0009_0046","0009_0047","0010_0043","0010_0044","0010_0045","0010_0046","0010_0047","0011_0043","0011_0044","0011_0045","0011_0046"]
## LS Wesermünder Geest, Teufelsmoor, Zevener Geest
tile_lst = ["0014_0045","0014_0046","0014_0047","0014_0048","0015_0044","0015_0045","0015_0046","0015_0047","0015_0048","0016_0044","0016_0045","0016_0046","0016_0047","0016_0048","0017_0045","0017_0046","0017_0047"]
## LS Hohe Heide, Luheheide, Ostheide, Uelzener Becken, Lüß
tile_lst = ["0020_0044","0021_0042","0021_0043","0021_0044","0021_0045","0022_0041","0022_0042","0022_0043","0022_0044","0022_0045","0023_0041","0023_0042","0023_0043","0023_0044","0023_0045","0024_0042","0024_0043","0024_0044"]
## LS Obere Allerniederung, Burgdorf-Peiner-Geestplatte
tile_lst = ["0020_0038","0020_0039","0021_0038","0021_0039"]
## LS around Hildesheimer Boerde
tile_lst = ["0017_0038","0018_0036","0018_0037","0018_0038","0019_0036","0019_0037","0019_0038","0020_0036","0020_0037","0020_0038","0021_0036","0021_0037","0021_0038","0021_0039","0022_0036","0022_0037","0023_0036","0023_0037"]
## LS Südwestliches Harzvorland
tile_lst = ["0020_0033","0020_0034","0021_0033","0021_0034","0022_0033"]
## LS Südhümmling, Cloppenburger Geest, Bersenbrücker Land, Plantlünner Sandebene
tile_lst = ["0009_0041","0009_0042","0010_0039","0010_0040","0010_0041","0010_0042","0011_0039","0011_0040","0011_0041","0011_0042","0012_0040","0012_0041"]

bl = "SA"
with open(r'data\raster\tile_list_{}.txt'.format(bl)) as file:
    tiles_lst = file.readlines()
tile_lst = [item.strip() for item in tiles_lst]


df = pd.DataFrame(columns=[0, 1])
for tile in tile_lst:
    pth = r"Q:\FORLand\Clemens\data\tables\FarmSize-CSTs\{0}\{0}_2012-2018_sequences_farm-size_{1}.csv".format(bl, tile)
    csv = pd.read_csv(pth, header=None)
    df = df.append(csv)

df = df.reset_index()
df = df.drop(columns=['index'])
df.columns = ['CST','Sequence','farm size','ID','field size','BNR']
df = df[df["CST"] != 255]
df["CST"] = df["CST"].astype(str)
df["Main Type"] = df.CST.str.slice(0, 1)
df["Main Type"] = df["Main Type"].astype(int)
df["Sub Type"] = df.CST.str.slice(1, 3)
df["Sub Type"] = df["Sub Type"].astype(int)

df_sub = df[df["Sub Type"] > 6]
df_sub = df[df["Sub Type"] == 9]
df_sub = df[df["Sub Type"] == 4]
df_sub = df[df["Sub Type"] == 3]
df_sub = df[df["Sub Type"] == 5]
df_sub = df[df["Sub Type"] == 6]
df_sub = df[df["Sub Type"] < 4]

df_sub = df[df["Sub Type"] > 3]
df_sub = df_sub[df_sub["Sub Type"] < 7]

df_sub = df[df["CST"] =="62"]

count = Counter(list(df_sub["Sequence"]))
print(count)

# ------------------------------------------ END TIME --------------------------------------------------------#
etime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + stime)
print("end: " + etime)
# ------------------------------------------ UNUSED BUT USEFUL CODE SNIPPETS ---------------------------------#


