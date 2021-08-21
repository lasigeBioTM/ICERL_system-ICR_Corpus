from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import sys
import time
from langdetect import detect

sys.path.append("./")


start_time = time.time()
print("Retrieving Files for training Portuguese NER model.......................")

start = 1

ids_str = str()
pt_ids_count, es_ids_count, en_ids_count = int(), int(), int()
abstracts_removal = list()
language_list = ["pt"]


while start <= 4261:

    url = 'https://search.scielo.org/?fb=&q=%28%28*%29+AND+%28oncology%29%29+OR+%28cancer%29&lang=pt&count=15&from=' + str(start) + '&output=site&sort=&format=summary&page=285&where=&filter%5Bla%5D%5B%5D=pt'
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

        for value in abstracts_dict[abstract_id]:
             #print(value[1][:-7])

            if value[0] == "pt":

                with open('./data/train_files_pt/' + value[1][:-7] + '.txt', 'w') as pt_file:
                    pt_ids_count += 1
                    pt_file.write(value[2])
                    pt_file.close
                    ids_str += value[1] + "\n"


#delete files if they are in icr_corpus

icr = os.listdir("./data/ICR_corpus/pt/")
icrDir = "./data/ICR_corpus/pt/"
train = os.listdir("./data/train_files_pt/")
trainDir = "./data/train_files_pt/"
ls = []
for i in train:
    with open(trainDir + i,'r',encoding = 'utf-8') as trainFile:
        trainContent = trainFile.readlines()
    for j in icr:
        with open(icrDir + j,'r',encoding = 'utf-8') as icrFile:
            icrContent = icrFile.readlines()
            if trainContent == icrContent:
                #print(j)
                ls.append(i)
                #os.remove(trainDir + i)
                
for i in ls:
    try:
        os.remove(trainDir + i)
    except FileNotFoundError:
        pass


#process the pubmedfiles

from langdetect import detect

ls = [] 

with open("CancerPortuguesePubMedCaseAbstracts3.txt","r",encoding = "utf-8") as pubmedfile:
    data = pubmedfile.readlines()
    #print(data)
    for i in data:
        if i[0].isdigit() == False:
            #some files in english are not detect by the langdetect, check manually the outputfiles
            if detect(i) != 'en':
                ls.append(i)


outDir = "./data/train_files_pt/"
for i in range(0,len(ls)-1):
    #print(ls[i][0])
    if ls[i][0] == 'S' and ls[i][1].isdigit() and ls[i+1][0] != 'S' and ls[i+1][1].isdigit() == False :
        docName = ls[i][:-1]
        with open(outDir + str(docName) + ".txt","w",encoding = "utf-8") as outFile:
            outFile.write(ls[i+1])
            outFile.close()
          
###data augmentation
import os
import nlpaug.augmenter.word as naw
import nltk
from nlpaug.util import Action

filenames = ["./data/train_files_pt/" + input_file for input_file in os.listdir("./data/train_files_pt/")]
for filename in filenames:
    ls = []
    with open(filename,'r',encoding='utf-8') as doc:
        data = doc.read()
        sentences = nltk.sent_tokenize(data)
        doc.close()
        docname = filename.split("/")[3]
        outfilepath = './data/train_files_pt/' + docname[:-4] + '-1.txt'
        outfilepath2 = './data/train_files_pt/' + docname[:-4] + '-2.txt'
        for text in sentences:    
            aug = naw.SynonymAug(aug_src='wordnet', lang = 'por', aug_p =0.7)
            augmented_text = aug.augment(text)
            ls.append(augmented_text)

    ls2 = []
    with open(outfilepath,'w',encoding='utf-8') as outfile1:
        output = ''.join(ls)
        outfile1.write(output)
        outfile1.close()
        outfilepath2 = './data/train_files_pt/' + docname[:-4] + '-2.txt'
        for text2 in ls:
            aug = naw.SynonymAug(aug_src='wordnet', lang = 'por', aug_p =0.8)
            augmented_text = aug.augment(text2)
            ls2.append(augmented_text)
        
    with open(outfilepath2,'w',encoding='utf-8') as outfile2:
        output = ''.join(ls2)
        outfile2.write(output)
        outfile2.close()
        
        
