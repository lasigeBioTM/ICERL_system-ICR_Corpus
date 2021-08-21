from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import sys
import time

sys.path.append("./")


# Retrieve clinical case reports from SciELO repository (https://scielo.org/) that have the abstract text simultaneously in English, Portuguese and Spanish

start_time = time.time()
print("Retrieving ICR_corpus.......................")

start = 1

ids_str = str()
pt_ids_count, es_ids_count, en_ids_count = int(), int(), int()
abstracts_removal = list()
language_list = ["en", "es", "pt"]

while start <= 19771:

    # Search parameters: ((*) AND (oncology)) OR (cancer)
    url = 'https://search.scielo.org/?q=%28*%29+AND+%28oncology%29&lang=pt&count=50&from=' +str(start) + '&output=site&sort=&format=summary&fb=&page=1&q=%28%28*%29+AND+%28oncology%29%29+OR+%28cancer%29&lang=pt'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    start += 50

    abstracts_dict = dict()

    for abstract in soup.body.find_all('div', attrs={'class':'abstract'}):
        scielo_id = abstract['id']
        text = abstract.text.replace("\n", "").replace("            ", "").replace("        ", "")
        language = scielo_id[-2:]
        abbr_scielo_id = scielo_id[:-3]
        values_to_add = (language, scielo_id, text)
        
        
        if abbr_scielo_id in abstracts_dict.keys():
            current_values = abstracts_dict[abbr_scielo_id]
            current_values.append(values_to_add)
            abstracts_dict[abbr_scielo_id] = current_values
        
        else:
            abstracts_dict[abbr_scielo_id] = [values_to_add]
            
    #print(len(abstracts_dict.keys()))
    for abstract_id in abstracts_dict.keys():
        #print(abstracts_dict.keys())
        
        if len(abstracts_dict[abstract_id]) >= 3:

            if abstracts_dict[abstract_id][0][0] in language_list and abstracts_dict[abstract_id][1][0] in language_list and abstracts_dict[abstract_id][2][0] in language_list:
            
                for value in abstracts_dict[abstract_id]:
                     #print(value[1][:-7])


                    if value[0] == "es":
                        
                        with open('./data/ICR_corpus/es/' + value[1][:-7] + '.txt', 'w') as es_file:
                            es_ids_count += 1
                            es_file.write(value[2])
                            es_file.close
                            ids_str += value[1] + "\n"
                            
                    elif value[0] == "pt":

                        with open('./data/ICR_corpus/pt/' + value[1][:-7] + '.txt', 'w') as pt_file:
                            pt_ids_count += 1
                            pt_file.write(value[2])
                            pt_file.close
                            ids_str += value[1] + "\n"

# Output file with the SciELO ids of the retrieved abstracts
with open("./data/icr_corpus_ids.txt", "w") as ids_file:
    ids_file.write(ids_str)
    ids_file.close()

# Output statistics file 
total = pt_ids_count + es_ids_count + en_ids_count

stats_str = str(pt_ids_count) + " PT abstracts retrieved\n" + str(es_ids_count) + " ES abstracts retrieved\n" + str(en_ids_count) + " EN abstracts retrieved\n" 
stats_str += str(total) + " Total abstracts retrieved" 
   
with open("./data/icr_corpus_stats.txt", "w") as stats_file:
    stats_file.write(stats_str)
    stats_file.close()

print("Total time (aprox.):", int((time.time() - start_time)/60.0), "minutes")


