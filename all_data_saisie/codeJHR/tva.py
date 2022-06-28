# coding: utf-8
# ©2022 Jean-Hugues Roy. GNU GPL v3.

import csv, requests, pandas
from bs4 import BeautifulSoup

fIn = "tva.csv"
fOut = "tva-complete.csv"

f = open(fIn)
resultats = csv.reader(f)
next(resultats)

for res in resultats:
    # print(res)
    url = res[7]

    req = requests.get(url)
    page = BeautifulSoup(req.text, "html.parser")

    try:
        # region1 = page.find("meta", attrs={"name":"cXenseParse:category"})["content"]
        region2 = page.find("meta", attrs={"name":"cXenseParse:taxonomy"})["content"]
    except:
        # region1 = "?"
        region2 = "?"
        
    # print(region1)
    print(region2)

    if res[6] == "":

        try:
            publie = page.find("meta", attrs={"name":"cXenseParse:recs:publishtime"})["content"]
            publie = pandas.to_datetime(publie, utc=True)
            print(publie)

            moissonne = res[8]
            moissonne = pandas.to_datetime(moissonne, utc=True)
            print(moissonne)

            diff = int(round((moissonne - publie) / pandas.Timedelta('1 day'),0))
            print(diff)

            res[6] = diff
            res[5] = publie
            
        except:
            pass

    # res.append(region1)
    res.append(region2)

    print("...")

    magda = open(fOut, "a")
    fusaro = csv.writer(magda)
    fusaro.writerow(res)
    magda.close()
