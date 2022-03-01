import csv

def get_file_name():
    return "./V2_full_data.csv"

def main() -> None:
    reader = csv.reader(open(get_file_name(), 'r'))
    writer = csv.writer(open('output_full_data.csv', 'w'))
    next(reader)
    writer.writerow(["Villes", "Mots-clés", "position du média", "Nom du média", "Titre de l'article", "Date de publication", "Journée de différence","URL", "date et heure saisie", "type mot-clés", "media_url"])
    for row in reader:
        row.append(row[7].split("://")[-1].split("/")[0])
        writer.writerow(row)
    
if __name__ == "__main__":
    main()