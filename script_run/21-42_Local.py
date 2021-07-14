#!/Users/goognewsqc/audit_google_news/env/bin/python

# coding: utf-8
# ©2020 Nicolas St-Germain GNU GPL v3.

import csv, errno, os, os.path, re, requests, time

from datetime import datetime

from urllib3 import filepost
from googleQuebec import termes, cities, montreal
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#########################
####### FONCTIONS #######
#########################

# Lien qu'utilise le bot pour récupérer les données ------>
def get_full_url(term : str, villes : str):
    base_url = "https://news.google.com/search?q="
    return base_url + term + "%20près%20de%20" + villes


# Pour enregistrer les documents à la bonne place ------>
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

#faudrait ajouter que si le directory existe qu'il ajoute le fichier directement dedans et non pas qu'il le overwrite.

def create_path_document():
    root = "./audit_google_news/"
    saisie = "Saisie" + "_" + get_current_time() + "/"
    #path = villes + "/"

    return root + saisie


def create_path_document_csv(villes): #csvfilename
    file = villes.replace(" ", "") + "_"
    term_type = "Local" + "_" + get_current_time() + ".csv"

    return create_path_document() + file + term_type

def confirm_path_document_txt(villes): #txtfilename
    file_name = create_path_document() + "localisation_" + villes.replace(" ", "") + "_" 
    file_type = file_name + "Local" + ".txt"

    return file_type


# Open "path" for writing, creating any parent directories as needed.
def safe_open_w(path):
    mkdir_p(os.path.dirname(path))

    return open(path, 'w')


# pour ouvrir le bon fichier ------->
def csv_read_city():
    return "./MRC_points.csv"

def csv_read_terms():
    return "./terms.csv"


# Date et heure du jour de la saisie utilisé dans la création du dossier et du fichier --->
def get_current_time():
    now = datetime.now()

    return now.strftime('%Y-%m-%d')

def get_full_current_time():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



# Le profil pour le navigateur lors de la saisie ---->
def create_robot_profile(infos) -> FirefoxOptions:

    #Profil de la page qui sera ouverte :
    options = webdriver.FirefoxOptions()
    hoptions = Options()
    hoptions.headless = True
    #profile.set_preference("browser.privatebrowsing.autostart", True)
    options.set_preference("geo.enabled", True)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", False)
    options.set_preference("browser.cache.offline.enable", False)
    options.set_preference("network.http.use-cache", False)
    options.set_preference("dom.disable_open_during_load", False)

    #déterminer la localisation :
    options.set_preference('geo.prompt.testing', True)
    options.set_preference('geo.prompt.testing.allow', True)
    options.set_preference('geo.provider.network.url',
                           'data:application/json,{"status":"OK","location": {"lat":'+str(infos[1])+',"lng":'+str(infos[2])+'}, "accuracy": 100}')

    return options


# Confirmer que la localisation est bonne -->
def get_localisation_confirmation(infos : str, villes : str) -> filepost:
    if os.path.exists(confirm_path_document_txt(villes)) :
        pass

    else : 
        browser = webdriver.Firefox(options=create_robot_profile(infos))
        browser.get("https://findmylocation.org")
        time.sleep(20)
        location = browser.find_element_by_id("locationname").text
        latitude = browser.find_element_by_id("latitude").text
        longitude = browser.find_element_by_id("longitude").text


        f = open(confirm_path_document_txt(villes), "w")
        f.write("Latitude : " + latitude + " " + "Longitude : " + longitude + "\n\n")
        f.write("L'ADRESSE EXACTE EST : " + location)
        f.close()
        browser.close()


def get_article_url(article : WebElement) -> str:
    #URL ---> DÉTERMINER COMMENT DIFFÉRENCIER LOCAL, NATIONAL, RÉGIONAL ET HORS-CANADA
    lien_article = article.find_element_by_class_name("VDXfz").get_attribute('href')
    r = requests.get(lien_article, allow_redirects=False)
    return r.headers['Location']



def get_article_date(article : WebElement) -> str:
    #Date de publication --->
    try :
        date = article.find_element_by_tag_name("time").get_attribute("outerHTML")
        return date.split('datetime="')[1].split("T")[0]

    except NoSuchElementException: 

        return ""

def get_article_title(article : WebElement) -> str:
    try : 
        titre_article = article.find_element_by_tag_name("h3").get_attribute("outerHTML")
        m = re.search('DY5T1d RZIKme">(.+?)</a></h3>', titre_article).group(1)

        return m

    except NoSuchElementException :
        titre_article =  article.find_element_by_tag_name("h4").get_attribute("outerHTML")
        m = re.search('DY5T1d RZIKme">(.+?)</a></h4>', titre_article).group(1)

        return m

def get_media_name(article : WebElement) -> str:

    media = article.find_element_by_class_name("SVJrMe").find_element_by_tag_name("a").get_attribute("outerHTML")

    name_media = re.search('data-n-tid="9">(.+?)</a>', media).group(1)

    return name_media

def get_articles(browser) -> list:
    main_page = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    
    return main_page.find_elements_by_tag_name("article")

def calculate_days_diff(article : WebElement):

    try :
        date_saisie = get_current_time()
        date_jour = datetime.strptime(date_saisie, '%Y-%m-%d')

        date_publication = get_article_date(article)
        date_pub_obj = datetime.strptime(date_publication, '%Y-%m-%d')
        return (date_jour - date_pub_obj).days

    except ValueError :
        return ""

def write_article_to_csv(creation_fichier, villes, term, n, article) -> None:
    nom_media = get_media_name(article)
    lien_article = get_article_url(article)
    titre_article = get_article_title(article)
    date = get_article_date(article)
    days_diff = calculate_days_diff(article)
    time_stamp = get_full_current_time()
    keyword_type = "local"

    csv_rows = [villes, term, n, nom_media, titre_article, date, days_diff, lien_article, time_stamp, keyword_type]
    print(csv_rows)
    creation_fichier.writerow(csv_rows)


def research_term_in_city(villes, creation_fichier, term, infos) -> None:
    browser = webdriver.Firefox(options=create_robot_profile(infos))
   
    browser.get(get_full_url(term, villes))

    for n, article in enumerate(get_articles(browser)):
        if n < 25: #numbergrab
            write_article_to_csv(creation_fichier, villes, term, n+1, article)


    get_localisation_confirmation(infos, villes)
    browser.close()

def process_city(i : int, city: dict) -> None:
    infos = [city["ville"], city["latitude"], city["longitude"]]
    print("<>" * 32)
    villes = infos[0]  # imprimer juste les villes
    print(create_path_document_csv(villes))

    with safe_open_w(create_path_document_csv(villes)) as f2:
        creation_fichier = csv.writer(f2)
        creation_fichier.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "Journée de différence","URL", "date et heure saisie", "type mot-clés"])
        local = termes[0]
        national = termes[2]
        mixte = termes[1]
        for term in local: #termin_variable_
            print("---" * 25)
            print(term)
            print("---" * 25)
            research_term_in_city(villes, creation_fichier, term, infos)                

def main() -> None:

    for i, city in enumerate(cities[21:42]): #indexrange
        process_city(i, city)


if __name__ == "__main__":
    main()
