# coding: utf-8
# ©2022 Jean-Hugues Roy. GNU GPL v3.

import csv, requests, pandas, datetime, locale
from bs4 import BeautifulSoup

fIn = "radiocan-urls.csv"
fOut = "radiocan-urls-complete.csv"

locale.setlocale(locale.LC_ALL, 'fr_CA')

# for x in range(1,13):
#     if x < 10:
#         x = "0{}".format(x)
#     else:
#         x = str(x)
#     moisNum = datetime.datetime.strptime(x, "%m")
#     mois = datetime.datetime.strftime(moisNum, "%B")
#     print(mois)    

f = open(fIn)
resultats = csv.reader(f)
next(resultats)

for res in resultats:
    # print(res)
    url = res[0]

    req = requests.get(url)
    page = BeautifulSoup(req.text, "html.parser")

    try:
        region = page.find("span", class_="textual-logo-label").text
    except:
        region = "?"

    print(region)

    try:
        publie = page.find("meta", attrs={"name":"dc.date.created"})["content"]
        publie = publie.replace("|", " ")
    except:
        try:
            publie = page.find("meta", attrs={"name":"rc.dateCreation"})["content"]
        except:
            try:
                publie = page.find("span", class_="segment-published-date").text.replace("Publié le ", "")
                publie = datetime.datetime.strptime(publie, "%d %B %Y")
            except:
                try:
                    publie = page.find("p", class_="lf__date").text.strip()
                    publie = datetime.datetime.strptime(publie, "%d %B %Y")
                except:
                    publie = ""
    # print(publie)
    if publie != "null":
        publie = pandas.to_datetime(publie)
    print(publie)

    res.append(publie)
    res.append(region)

    print(res)

    print("...")

    magda = open(fOut, "a")
    fusaro = csv.writer(magda)
    fusaro.writerow(res)
    magda.close()
