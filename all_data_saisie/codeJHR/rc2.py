# coding: utf-8
# ©2022 Jean-Hugues Roy. GNU GPL v3.

import csv, requests, pandas
from bs4 import BeautifulSoup

fIn = "radiocan.csv"
fOut = "radiocan-complete.csv"

f = open(fIn)
resultats = csv.reader(f)
next(resultats)

x = n = 0

for res in resultats:
    # print(res)
    url = res[7]
    res[3] = "Radio-Canada"

    n += 1

    f2 = open("radiocan-urls-complete.csv")
    urls = csv.reader(f2)

    for u in urls:
        if u[0] == url:
            x += 1
            res.append(u[-1])

            # print(u)
            if res[5] == "" and u[2] != "null":
                
                publie = pandas.to_datetime(u[2])
                moissonne = pandas.to_datetime(res[8])
                diff = int(round((moissonne - publie) / pandas.Timedelta('1 day'),0))
                # print(res)
                res[5] = u[2]
                res[6] = diff
                # print(u)
                # print(diff)
            

    print(n,x,res)

    print("...")

    magda = open(fOut, "a")
    fusaro = csv.writer(magda)
    fusaro.writerow(res)
    magda.close()
