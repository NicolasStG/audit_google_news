# coding: utf-8
# ©2020 Nicolas St-Germain GNU GPL v3.

import csv
import datetime
import errno
import os
import os.path
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Éléments de base ------------>


terms = ["Accident", "Cégep"]  # "Police OR Sûreté", "décès OR mort", "Incendie", "Préfêt" "Centre de services scolaire OR commission scolaire", "CISSS OR CIUSSS", "Maire OR Mairesse", "Candidat", "Travaux ET Routiers", "Autobus OR Tramway", "Météo", "Constrution", "Élection OR campagne", "député", "Armes à feu", "Santé publique", "COVID", "Immigration", "Climat", "Racisme", "Premier ministre", "Chine", "Biden OR Trump", "déficit"

#########################
####### FONCTIONS #######
#########################

# Lien qu'utilise le bot pour récupérer les données ------>
def get_full_url(term, villes):
    base_url = "https://news.google.com/search?q="

    return base_url + term + "%20près%20de%20" + villes


# Pour enregistrer les documents à la bonne place ------>
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_path_document(villes):
    root = "./"
    saisie = "Saisie" + "_" + get_current_time() + "/"
    path = villes + "/"

    return root + saisie + path


def create_path_document_csv(villes):
    file = villes + "_" + get_current_time() + ".csv"

    return create_path_document(villes) + file


# Open "path" for writing, creating any parent directories as needed.
def safe_open_w(path):
    mkdir_p(os.path.dirname(path))

    return open(path, 'w')


# pour ouvrir le bon fichier ------->
def csv_read_place():
    return "./MRC_points.csv"


# Date et heure du jour de la saisie utilisé dans la création du dossier et du fichier --->
def get_current_time():
    now = datetime.datetime.now()

    return now.strftime('%d-%m-%Y')


# Le profil pour le navigateur lors de la saisie ---->
def create_robot_profile(infos) -> FirefoxProfile:

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
def get_localisation_confirmation(infos):  # À CORRIGER ET À METTRE À LA BONNE PLACE
    browser = webdriver.Firefox(options=create_robot_profile(infos))
    browser.get("https://findmylocation.org")

    main = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "locationname")))
    data = main.text
    print(data)
    # f = open(create_path_document() + "localisation.txt", "w")
    # f.write(infos)
    # f.write("L'ADRESSE EXACTE EST :" + data)
    # f.close()
    # browser.close()


def get_article_url(article) -> str:
    #URL ---> DÉTERMINER COMMENT DIFFÉRENCIER LOCAL, NATIONAL, RÉGIONAL ET HORS-CANADA
    try:
        lien_article = article.find_element_by_class_name("VDXfz").get_attribute('href')
        r = requests.get(lien_article, allow_redirects=False)
        return r.headers['Location']

    except:
        return "url marche pas"


def get_article_date(article) -> str:
    #Date de publication --->
    try:
        date = article.find_element_by_tag_name("time").get_attribute("outerHTML")
        return date.split('datetime="')[1].split("T")[0]

    except:
        return ""


def get_article_title(article) -> str:
    titre_article = article.find_element_by_tag_name("h3").text
    
    return titre_article.text


def get_media_name(article) -> str:
    media = article.find_element_by_class_name("SVJrMe").find_element_by_tag_name("a")
    
    return media.text


def get_articles(browser) -> list:
    main_page = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    
    return main_page.find_elements_by_tag_name("article")


def write_article_to_csv(creation_fichier, villes, term, n, article) -> None:
    nom_media = get_media_name(article)
    lien_article = get_article_url(article)
    titre_article = get_article_title(article)
    date = get_article_date(article)

    # # type de médias --->
    # type_media = "impossible à déterminer pour l'instant"
    csv_rows = [villes, term, n, nom_media, titre_article, date, lien_article]
    print(csv_rows)
    creation_fichier.writerow(csv_rows)


def research_term_in_city(villes, creation_fichier, term, infos) -> None:
    try:
        browser = webdriver.Firefox(options=create_robot_profile())
        browser.get(get_full_url(terms, villes))

        for n, article in enumerate(get_articles(browser)):
            if n < 4:
                write_article_to_csv(creation_fichier, villes, term, n, article)

        get_localisation_confirmation(infos)
        browser.quit()
        print("fermeture pour mieux ouvrir")

    except:
        browser.quit()
        print("erreur à la hauteur des termes")

def process_city(i: int, city: dict) -> None:
    infos = [city["ville"], city["latitude"], city["longitude"]]
    
    if i < 2:
        print("<>" * 32)
        villes = infos[0]  # imprimer juste les villes

        with safe_open_w(create_path_document_csv(villes.replace(" ", ""))) as f2:
            creation_fichier = csv.writer(f2)
            creation_fichier.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "URL"])
            for term in terms:
                research_term_in_city(villes, creation_fichier, term, infos)
                

def main() -> None:
    # ouvrir le fichier csv contenant les données.
    with open(csv_read_place(), "r") as ville_csv:
        ville_reader = csv.DictReader(ville_csv)
        
        for i, city in enumerate(ville_reader):
            process_city(i, city)


if __name__ == "__main__":
    main()
