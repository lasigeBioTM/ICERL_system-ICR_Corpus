from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import sys
import time

sys.path.append("./")


# Retrieve clinical case reports from SciELO repository (https://scielo.org/) that have the abstract text simultaneously in English, Portuguese and Spanish

start_time = time.time()
print("Retrieving PT files for training.......................")

start = 1

ids_str = str()
pt_ids_count, es_ids_count, en_ids_count = int(), int(), int()
abstracts_removal = list()
language_list = ["pt"]

while start <= 296686:

    url = 'https://search.scielo.org/?fb=&q=*&lang=pt&count=15&from=' + str(start) + '&output=site&sort=&format=summary&page=19780&where=&filter%5Bla%5D%5B%5D=pt'
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
            

    for abstract_id in abstracts_dict.keys():
    
        for value in abstracts_dict[abstract_id]:
             #print(value[1][:-7])

            if value[0] == "pt":

                with open('./data/pre_pt_scielo_abstracts_embeddings/' + value[1][:-7] + '.txt', 'w') as pt_file:
                    pt_ids_count += 1
                    pt_file.write(value[2])
                    pt_file.close
                    ids_str += value[1] + "\n"

