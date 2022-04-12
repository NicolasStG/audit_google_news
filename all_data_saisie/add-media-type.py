import csv

def open_full_data_without_mediatype_file():
    return "./full-data-nomediatype-dont-import.csv"

def open_liste_media():
    return "./listemedia_test.csv"

def main() -> None:
    #fulldata_nomediatype = csv.reader(open(open_full_data_without_mediatype_file(), 'r'))
    #writer = csv.writer(open('output_full_data-testmediatype.csv', 'w'))
    #liste_media = csv.reader(open(open_liste_media(), 'r'))
    # next(open_full_data_without_mediatype_file())
    # writer.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "Journée de différence","URL", "date et heure saisie", "type mot-clés", "media_url", "media_type"])
    with open(open_full_data_without_mediatype_file(), "r") as f1:
        with open(open_liste_media(), "r") as f2:
            same = set(f1).intersection(f2)
            
    with open('output_full_data-testmediatype.csv', 'w') as file_out:
        #file_out.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "Journée de différence","URL", "date et heure saisie", "type mot-clés", "media_url", "media_type"])
        for line in same:
            print(line)
        
if __name__ == "__main__":
    main()