import json
import os
import re
import sys
import time
from flair.data import Sentence
from segtok.segmenter import split_single, split_multi

sys.path.append('./')


def pt_train_to_IOB2():
    """Convert the Portuguese training files into IOB2 FORMAT. Example of sentence with an annotation:
        
            Original text: "Carcinoma microcítico de pulmón."
            
            Converted text:"Carcinoma   B-MORF_NEO
                            microcítico I-MORF_NEO
                            de  O
                            pulmón  O
                            .   O"
        Ensures: 
            A .txt file with the text of all Portuguese documents for training tokenized and tagged according with the IOB2 schema
    """

    #if subset == "train":
    cantemist_data_dir = './data/train_dev_pt_txt_ann/'
    
    total_doc_count = int(len(os.listdir(cantemist_data_dir))/2)
    doc_count = int()
    output = str()

    for doc in os.listdir(cantemist_data_dir):
        doc_count += 1

        if doc[-3:] == "txt":
            
            doc_annotations = dict()
            text = str()   
            
            with open(cantemist_data_dir+doc, 'r') as corpus_file:
                text = corpus_file.read()
                corpus_file.close()      

            annotations_filename = doc[:-3] + "ann"
            doc_annotations_begin, doc_annotations_end = list(), list()

            with open(cantemist_data_dir+annotations_filename, 'r') as annotations_file:
                annotations = annotations_file.readlines()
                annotations_file.close()

                for annotation in annotations:
                    begin_position = int(annotation.split("\t")[1].split(" ")[1])
                    end_position = int(annotation.split("\t")[1].split(" ")[2])
                    annotation_str = annotation.split("\t")[2]#.split(" ")[0]
                    doc_annotations_begin.append(begin_position)
                    doc_annotations_end.append(end_position)
                
            # Tag all annotations in text in the respective correct positions
            for begin in doc_annotations_begin:
                text = text[:begin-1] + "@" + text[begin:]
            
            for end in doc_annotations_end:
                text = text[:end] + "$" + text[end+1:]
        
            # Sentence segmentation followed by tokenization of each sentence
            sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
            next_token_is_annotation = False
            
            for sentence in sentences:

                
                for token in sentence:
                    token_text = str(token).split(" ")[2]

                    ls = re.split('(\W+)',token_text)

                    for i in ls:
                        token_text = i
                    
                        if len(token_text) > 0:
                            
                            if  "@" in token_text: # Next token belongs to an annotation
                                
                                next_token_is_annotation = True
                                previous_token_is_begin = True

                                if token_text != "@": # For example "»@"
                                    temp = str(token_text).strip("@")

                                    if temp != "$": # Sometimes a token can be '$@'
                                        output += temp + "\tO" + "\n"

                            elif "$" in token_text: # End of the annotation
                                temp = str(token_text).strip("$")

                                if temp != "@":
                                    next_token_is_annotation = False
                                
                                    if token_text != "$": 
                                        output +=  temp + "\tO" + "\n"
                            
                            else:
                                if next_token_is_annotation:
                                    
                                    if previous_token_is_begin: # The first token of the annotation
                                        output += str(token_text) + "\tB-MOR_NEO" + "\n"
                                        previous_token_is_begin = False
                                    
                                    else: # The intermediate tokens of the annotation
                                        output += str(token_text) + "\tI-MOR_NEO" + "\n"

                                else: # Tokens outside any annotation
                                    output += str(token_text) + "\tO" + "\n"
                                    next_token_is_annotation = False
                    
                output += "\n" # To add a separator between each sentence
    
    output = output[:-2] # To delete empty lines in the final of the doc


    #Create a file with the text of all documents tokenized and tagged
    if not os.path.exists("./data/datasets/iob2/train_pt/"):
        os.makedirs("./data/datasets/iob2/train_pt/")

    with open("./data/datasets/iob2/train_pt/train.txt", 'w',encoding = 'utf-8') as output_file:
        output_file.write(output)
        output_file.close()


pt_train_to_IOB2()
