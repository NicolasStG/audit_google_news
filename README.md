# audit_google_news

Google News audit code. Made for a masters' thesis. 

The goal of the script is to scrap articles data from Google news' agregator's page. 

The script is python's base and use selenium to fake a user's usage on the platform. 

The plan is to determine if local and regional outlet are shown by the platform when users from certain area search for a specific terms. 

The research is based on 26 query used separated in three categories : local, national or mixt. 

104 MRC (link : https://fr.wikipedia.org/wiki/Municipalit%C3%A9_r%C3%A9gionale_de_comt%C3%A9) are used to fake user's usage. The most populated city of the MRC is selected as a reference point.

The script takes all the info asked for and put it in a csv file. 

Algotrithm accountability. 
