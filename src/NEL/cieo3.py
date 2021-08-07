import atexit
import logging
import networkx as nx
import os
import pickle
import sys
from fuzzywuzzy import fuzz, process

sys.path.append("./")

# Import cieo3 cache storing the candidates list for each entity mention or create it if it does not exist
cieo3_cache_file = "./tmp/ecie03_cache.pickle"

if os.path.isfile(cieo3_cache_file):
    logging.info("loading CIE-O-3 dictionary...")
    cieo3_cache = pickle.load(open(cieo3_cache_file, "rb"))
    loadedcieo3 = True
    logging.info("loaded CIE-O-3 dictionary with %s entries", str(len(cieo3_cache)))

else:
    cieo3_cache = {}
    loadedcieo3 = False
    logging.info("new CIE-O-3 dictionary")


def exit_handler():
    print('Saving CIE-O-3 dictionary...!')
    pickle.dump(cieo3_cache, open(cieo3_cache_file, "wb"))

atexit.register(exit_handler)

language = sys.argv[-1]

def load_cieo3():
    """Load CIE-O/CID-O codes (Morfología neoplasia) into dict and graph object
    
        Ensures: 
            ontology_graph: is a MultiDiGraph object from Networkx representing the CIE-O/CID-O vocabulary
            name_to_id: is dict with mappings between each ontology concept name and the respective CIE-O/CID-O code
            synonym_to_id: is dict with mappings between each ontology concept name and the respective CIE-O/CID-O code
    """
    
    name_to_id = dict()
    synonym_to_id = dict()
    edge_list = list()
    not_assigned = list()

    if language == 'pt':
        doc_voc = 'cid'
        charac_encoding = 'utf-16'
    if language == 'es':
        doc_voc = 'cie'
        charac_encoding = 'latin-1'
    
    with open('./data/vocabularies/' + doc_voc + '.txt', 'r', encoding = charac_encoding ) as codes_file: 
        valid_codes = codes_file.readlines()

        for code in valid_codes:
            data = str(code).strip("\n").split("\t")
            synonyms = list(data[2:])
            code_id = data[0]
            code_elements = code_id.split("/")
            tumor_type = code_elements[0]
            edge_list.append((tumor_type, "0000")) # Add a root concept to link all tumour types
            tumor_behaviour, diferentiation_degree = str(), str()
           
            if len(code_elements) == 2:
    
                if len(code_elements[1]) == 1: # 8001/3 is the child of 8001
                    tumor_behaviour = code_elements[1] 
                    relationship = (code_id, tumor_type)
                    edge_list.append(relationship)

                elif len(code_elements) == 2: # 8001/31 is the child of 8001/3
                    tumor_behaviour = code_elements[1][0]
                    parent_code = tumor_type + "/" + tumor_behaviour
                    relationship = (code_id, parent_code)
                    edge_list.append(relationship)


            if len(code_elements) ==3:
                    
                if len(code_elements[1]) == 1: # 8001/3 is the child of 8001
                    tumor_behaviour = code_elements[1] 
                    relationship = (code_id, tumor_type)
                    edge_list.append(relationship)

                elif len(code_elements) == 2: # 8001/31 is the child of 8001/3
                    tumor_behaviour = code_elements[1][0]
                    parent_code = tumor_type + "/" + tumor_behaviour
                    relationship = (code_id, parent_code)
                    edge_list.append(relationship)

                elif len(code_elements) == 3: # 8001/31 is the child of 8001/3
                    tumor_behaviour = code_elements[1][0]
                    parent_code = tumor_type + "/" + tumor_behaviour
                    relationship = (code_id, parent_code)
                    edge_list.append(relationship)


            if len(data) > 1:
                code_name = data[1]
                code_name = code_name.encode('latin-1',errors='ignore').decode('utf8', errors='ignore')
                name_to_id[code_name] = code_id
                for i in range(0,len(synonyms)):
                    code_synonym = synonyms[i]
                    code_synonym = code_synonym.encode('latin-1',errors='ignore').decode('utf8', errors='ignore')
                    synonym_to_id[code_synonym] = code_id   
            
            else: #see p.22: C1. Asignación de códigos que no existen en la terminología
                not_assigned.append(code_id)
    
    # Create a MultiDiGraph object with only "is-a" relations - this will allow the further calculation of shorthest path lenght
    ontology_graph = nx.MultiDiGraph([edge for edge in edge_list])
    print("Is ontology_graph acyclic:", nx.is_directed_acyclic_graph(ontology_graph))
    print("CIE-O/CID-O loading complete")

    return ontology_graph, name_to_id, synonym_to_id


def map_to_cieo3(entity_text, name_to_id, synonym_to_id):
    """Get best CIE-O/CID-O matches for entity text according to lexical similarity (edit distance).
    
    Ensures: 
        matches: is list; each match is dict with the respective properties
    """
    
    global cieo3_cache

    entity_text_spaces = entity_text.replace("_"," ")

    if entity_text_spaces.replace(',','') in map(str.lower,name_to_id): #There is an exact match for this entity in name_to_id
        codes = process.extract(entity_text_spaces.replace(" ","_"), name_to_id.keys(), limit=4000, scorer=fuzz.token_sort_ratio)

        for d in codes:
            term_name = d[0]
            score = d[1]
            if entity_text_spaces.replace(',','').lower() == term_name.lower():
                codes = [(term_name,score)]

        cieo3_cache[entity_text] = codes

    elif entity_text_spaces.replace(',','') in map(str.lower,synonym_to_id): #There is an exact match for this entity in synonym_to_id
        codes = process.extract(entity_text_spaces.replace(" ","_"), synonym_to_id.keys(), limit = 4000, scorer=fuzz.token_sort_ratio)
        for d in codes:   
            term_name = d[0]
            score = d[1]
            term_id = synonym_to_id[term_name]
            if entity_text_spaces.replace(',','').lower() == term_name.lower():
                codes = [(term_name,score)]
        cieo3_cache[entity_text] = codes
    
    
    elif entity_text.endswith("s") and entity_text[:-1] in cieo3_cache: # Removal of suffix -s 
        codes = cieo3_cache[entity_text[:-1]]

    
    elif entity_text in cieo3_cache: # There is already a candidate list stored in cache file
        codes = cieo3_cache[entity_text]


    else:
        # Get first ten candidates according to lexical similarity with entity_text
        
        codes = process.extract(entity_text, name_to_id.keys(), scorer=fuzz.token_sort_ratio, limit=10)
        if codes == []:
            pass
        
        elif codes[0][1] == 100: # There is an exact match for this entity
            codes = [codes[0]]
    
        elif codes[0][1] < 100: # Check for synonyms of this entity
            drug_syns = process.extract(entity_text, synonym_to_id.keys(), limit=10, scorer=fuzz.token_sort_ratio)

            for synonym in drug_syns:

                if synonym[1] == 100:
                    codes = [synonym]
                
                else:
                    if synonym[1] > codes[0][1]:
                        codes.append(synonym)
        
        cieo3_cache[entity_text] = codes
    
    # Build the candidates list with each match id, name and matching score with entity_text

    matches = []
    for d in codes:
        term_name = d[0]
        score = d[1]

        if term_name in name_to_id.keys():
            ls2 = []
            for i in name_to_id.keys():
                if i.lower() == term_name.lower():      
                    ls2.append(name_to_id[i])
            term_id = ls2[0] #If there is 2 or more term_ids for the same entity the first id will be linked to the entity

        elif term_name in synonym_to_id.keys():
            ls2=[]
            for i in  synonym_to_id.keys():
                if i.lower() == term_name.lower():      
                    ls2.append(synonym_to_id[i])
            term_id = ls2[0] #If there is 2 or more term_ids for the same entity the first id will be linked to the entity

            
        else:
            term_id = "NIL"

        match = {"ontology_id": term_id,
                 "name": term_name,
                 "match_score": d[1]/100}


        matches.append(match)

    return matches
