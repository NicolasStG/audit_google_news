# coding: utf-8
# ©2020 Nicolas St-Germain GNU GPL v3.

import csv, errno, os, os.path, requests, time
from googleQuebec import termes, villes, montreal
from datetime import datetime

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

#faudrait ajouter que si le directory existe qu'il ajoute le fichier directement dedans et non pas qu'il le overwrite.

def create_path_document(villes):
    root = "./"
    saisie = "Saisie" + "_" + get_current_time() + "/"
    path = villes + "/"

    return root + saisie + path


def create_path_document_csv(villes):
    file = villes.replace(" ", "") + "_" + get_current_time() + ".csv"

    return create_path_document(villes) + file


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
def get_localisation_confirmation(infos, villes):
    if os.path.exists(create_path_document(villes) + "localisation.txt") :
        pass

    else : 
        browser = webdriver.Firefox(options=create_robot_profile(infos))
        browser.get("https://findmylocation.org")
        time.sleep(20)
        location = browser.find_element_by_id("locationname")
        data = location.text
        print(data)
        f = open(create_path_document(villes) + "localisation.txt", "w")
        f.write("Latitude : " + infos[1] + " " + "Longitude : " + infos[2] + "\n\n")
        f.write("L'ADRESSE EXACTE EST : " + data)
        f.close()
        browser.close()


def get_article_url(article) -> str:
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

def get_article_title(article) -> str:
    try : 
        titre_article = article.find_element_by_tag_name("h3").text

        return titre_article

    except NoSuchElementException :
        titre_article =  article.find_element_by_tag_name("h4").text

        return titre_article


def get_media_name(article) -> str:

    media = article.find_element_by_class_name("SVJrMe").find_element_by_tag_name("a")

    return media.text

def get_articles(browser) -> list:
    main_page = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    
    return main_page.find_elements_by_tag_name("article")

def calculate_days_diff(article):

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

    # # type de médias --->
    # type_media = "impossible à déterminer pour l'instant"
    csv_rows = [villes, term, n, nom_media, titre_article, date, days_diff, lien_article]
    print(csv_rows)
    creation_fichier.writerow(csv_rows)


def research_term_in_city(villes, creation_fichier, term, infos) -> None:
    browser = webdriver.Firefox(options=create_robot_profile(infos))
   
    browser.get(get_full_url(term, villes))

    for n, article in enumerate(get_articles(browser)):
        if n < 10:
            write_article_to_csv(creation_fichier, villes, term, n+1, article)


    get_localisation_confirmation(infos, villes)
    browser.close()

def process_city(i: int, city: dict) -> None:
    infos = [city["ville"], city["latitude"], city["longitude"]]
    
    if i < 1:
        print("<>" * 32)
        villes = infos[0]  # imprimer juste les villes

        with safe_open_w(create_path_document_csv(villes)) as f2:
            creation_fichier = csv.writer(f2)
            creation_fichier.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "Journée de différence","URL"])
            # with open(csv_read_terms(), "r") as term_csv:
            #     term_reader = csv.DictReader(term_csv)
            #     for terms in term_reader:
                    # term = terms["term"]
            term = "Police OR Sûreté"
            research_term_in_city(villes, creation_fichier, term, infos)

            #process_term(villes, creation_fichier, infos)
                
#def process_term(villes, creation_fichier, infos) :

def main() -> None:
    # ouvrir le fichier csv contenant les données.
    with open(csv_read_city(), "r") as ville_csv:
        ville_reader = csv.DictReader(ville_csv)
        
        for i, city in enumerate(ville_reader):
            process_city(i, city)


if __name__ == "__main__":
    main()
