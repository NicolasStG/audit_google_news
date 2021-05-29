# coding: utf-8
# ©2020 Nicolas St-Germain GNU GPL v3.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import csv
import datetime
import requests
import os
import os.path
import errno

# Éléments de base ------------>


terms = ["Accident", "Cégep"] # "Police OR Sûreté", "décès OR mort", "Incendie", "Préfêt" "Centre de services scolaire OR commission scolaire", "CISSS OR CIUSSS", "Maire OR Mairesse", "Candidat", "Travaux ET Routiers", "Autobus OR Tramway", "Météo", "Constrution", "Élection OR campagne", "député", "Armes à feu", "Santé publique", "COVID", "Immigration", "Climat", "Racisme", "Premier ministre", "Chine", "Biden OR Trump", "déficit"

#########################
####### FONCTIONS #######
#########################

# Lien qu'utilise le bot pour récupérer les données ------>
def get_full_url(): 
    base_url = "https://news.google.com/search?q="
    url = base_url + term + "%20près%20de%20" + villes
    return url

# Pour enregistrer les documents à la bonne place ------>
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def create_path_document():
    root = "/Users/nicolasst-germain/Documents/CODE_STUFF/test_selenium/google_test/"
    saisie = "Saisie" + "_" + get_current_time() + "/"
    path =  villes_2 + "/"
    return root + saisie + path

def create_path_document_csv():
    file = villes_2 + "_" + get_current_time() + ".csv"
    path_file = create_path_document() + file
    return path_file

def safe_open_w(path): # Open "path" for writing, creating any parent directories as needed.
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')

# pour ouvrir le bon fichier ------->
def csv_read_place(): #faut juste changer le path pour chaque code à utiliser. 
    csv_read = "/Users/nicolasst-germain/Documents/CODE_STUFF/test_selenium/google_test/MRC_points.csv" 
    return csv_read

# Date et heure du jour de la saisie utilisé dans la création du dossier et du fichier --->
def get_current_time():
    now = datetime. datetime. now()
    date_jour = now.strftime('%d-%m-%Y')
    return date_jour

# Le profil pour le navigateur lors de la saisie ---->
def create_robot_profile(): 

    #Profil de la page qui sera ouverte : 
    profile = webdriver.FirefoxProfile() 
    hoptions = Options()
    hoptions.headless = True
    #profile.set_preference("browser.privatebrowsing.autostart", True)
    profile.set_preference("geo.enabled", True)
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    profile.set_preference("dom.disable_open_during_load", False)


    #déterminer la localisation : 
    profile.set_preference('geo.prompt.testing', True)
    profile.set_preference('geo.prompt.testing.allow', True)
    profile.set_preference('geo.provider.network.url',
        'data:application/json,{"status":"OK","location": {"lat":'+str(infos[1])+',"lng":'+str(infos[2])+'}, "accuracy": 100}')
    
    return profile

# Confirmer que la localisation est bonne --> NE MARCHE PAS
def get_localisation_confirmation(): #À CORRIGER ET À METTRE À LA BONNE PLACE
    browser = webdriver.Firefox(options=create_robot_profile())
    browser.get("https://findmylocation.org")
 
    main = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "locationname"))
        )
    data = main.text
    print(data)
    # f = open(create_path_document() + "localisation.txt", "w")
    # f.write(infos)         
    # f.write("L'ADRESSE EXACTE EST :" + data)
    # f.close()
    # browser.close()


#CODE DU PROGRAMME -------> 
with open(csv_read_place(), "r") as ville_csv: #ouvrir le fichier csv contenant les données. 
    ville_reader = csv.DictReader(ville_csv)
    i = 0
    for line in ville_reader:
        infos = [line["ville"], line["latitude"], line["longitude"]] #imprimer juste les villes
        i+=1
        if i < 2:
            print("<>" * 32)
            # print(i)
            # print(infos)

            villes = infos[0]
            villes_2 = villes.replace(" ", "")
            #print(villes_fichier())


            #print(fichier)

            with safe_open_w(create_path_document_csv()) as f2:
                creation_fichier = csv.writer(f2)
                creation_fichier.writerow(["Villes", "Mots-clés","position du média","Nom du média", "Titre de l'article", "Date de publication", "URL"])
                #print(ville)
                for term in terms :
                    #print(term)
                    try : 
                        browser = webdriver.Firefox(options=create_robot_profile())
                        browser.get(get_full_url())

                        main = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "main"))
                        )
                        #print(main.text)

                        articles = main.find_elements_by_tag_name("article")

                        n = 0

                        for article in articles:
                            n +=1

                            if n < 4:
                                #print("-"*10)
                            
                                #Mots-clés --->
                                #print(term)


                                #position du média -->
                                #print(n)

                                #Nom du média --->
                                media = article.find_element_by_class_name("SVJrMe").find_element_by_tag_name("a")
                                nom_media = media.text
                                #print(nom_media)

                                #URL ---> DÉTERMINER COMMENT DIFFÉRENCIER LOCAL, NATIONAL, RÉGIONAL ET HORS-CANADA
                                try :
                                    lien_article = article.find_element_by_class_name("VDXfz").get_attribute('href')
                                    # print(lien_article)
                                    r = requests.get(lien_article, allow_redirects=False)
                                    lien_article = r.headers['Location']

                                except :
                                    lien_article = "url marche pas"


                                #Titre de l'article --->
                                titre_article = article.find_element_by_tag_name("h3")
                                titre_article2 = titre_article.text
                                #print(titre_article2)


                                #Date de publication --->

                                try :
                                    date = article.find_element_by_tag_name("time").get_attribute("outerHTML")
                                    dat = date.split('datetime="')[1].split("T")[0]

                                except : 
                                    dat = ""
                                
                                # #type de médias --->
                                # #type_media = "impossible à déterminer pour l'instant"
                                # #print(type_media)
                                infos = [villes, term,n, nom_media, titre_article2, dat, lien_article]
                                print(infos)
                                creation_fichier.writerow(infos)
                        
                        # get_localisation_confirmation()
                        get_localisation_confirmation()
                        browser.quit()
                        print("fermeture pour mieux ouvrir")

                        # try :
                        #     get_localisation_confirmation()

                        # except : 
                        #     print("erreur au niveau de la fonction")
                    except:
                        browser.quit()
                        print ("erreur à la hauteur des termes")