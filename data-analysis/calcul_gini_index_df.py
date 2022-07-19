import numpy as np
import csv

#################################################################################
#####Ce script calcule l'index de Gini dans le fichier villesparmotscles2.csv####
#################################################################################
def get_file_name():
    return "/Users/nicolasst-germain/Documents/GitHub/audit_google_news/data-analysis/data_test_gini.csv"

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient
 
def main() -> None:

    reader = np.genfromtxt(get_file_name(), delimiter=',', usecols=range(1,5))
    #writer = csv.writer(open('gini_test.csv', 'w'))
    #next(reader)
    #writer.writerow(["Villes", "hors Québec","local/regional", "national", "non media", "gini coeff"])
    print(reader)
    for rows in reader:
        print(gini(rows))
    #   writer.writerow(rows)

if __name__ == "__main__":
    main()
    
