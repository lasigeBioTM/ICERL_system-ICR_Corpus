import atexit
import logging
import networkx as nx
import obonet
import os
import pickle
import sys
from fuzzywuzzy import fuzz, process

sys.path.append("./")

# Import ES DeCS cache storing the candidates list for each entity mention or create it if it does not exist
decs_cache_file = "./tmp/decs_cache.pickle"

if os.path.isfile(decs_cache_file):
    logging.info("loading ES DeCS dictionary...")
    decs_cache = pickle.load(open(decs_cache_file, "rb"))
    loadeddecs = True
    logging.info("loaded ES DeCS dictionary with %s entries", str(len(decs_cache)))

else:
    decs_cache = {}
    loadededecs = False
    logging.info("new ES DeCS dictionary")


def exit_handler():
    print('Saving ES DeCS dictionary...!')
    pickle.dump(decs_cache, open(decs_cache_file, "wb"))

atexit.register(exit_handler)


def load_decs():
    """Load DeCS ontology from local file 'DeCS_2019.obo' or from online source.
    
    Ensures: 
        ontology_graph: is a MultiDiGraph object from Networkx representing DeCS ontology;
        name_to_id: is dict with mappings between each ontology concept name and the respective DeCS id;
        synonym_to_id: is dict with mappings between each ontology concept name and the respective DeCS id;
    """

    print("Loading ES DeCS...")
    
    graph = obonet.read_obo("./data/vocabularies/DeCS_2019.obo") # Load the ontology from local file
    graph = graph.to_directed()
    name_to_id, synonym_to_id, edges = dict(), dict(), list()
    #print(len(graph.nodes()))

    for node in  graph.nodes(data=True):
        node_id, node_name = node[0], node[1]["name"]
        name_to_id[node_name] = node_id
        
        if 'is_a' in node[1].keys(): # The root node of the ontology does not have is_a relationships
                
            for related_node in node[1]['is_a']: # Build the edge_list with only "is-a" relationships
                edges.append((node[0], related_node)) 
            
        if "synonym" in node[1].keys(): # Check for synonyms for node (if they exist)
                
            for synonym in node[1]["synonym"]:
                synonym_name = synonym.split("\"")[1]
                synonym_to_id[synonym_name] = node_id
    

    ontology_graph = nx.MultiDiGraph([edge for edge in edges])
    print("Is ontology_graph acyclic:", nx.is_directed_acyclic_graph(ontology_graph))
    print("ES DeCS loading complete")
    
    return ontology_graph, name_to_id, synonym_to_id


def map_to_decs(entity_text, name_to_id,synonym_to_id):
    """Get best spanish or portuguese DeCS matches for entity text according to lexical similarity (edit distance).
    
    Ensures: 
        matches: is list; each match is dict with the respective properties
    """
    
    global decs_cache

    entity_text_spaces = entity_text.replace("_"," ")

    if entity_text_spaces.replace(',','') in map(str.lower,name_to_id): #There is an exact match for this entity in name_to_id
        codes = process.extract(entity_text_spaces.replace(" ","_"), name_to_id.keys(), limit=4000, scorer=fuzz.token_sort_ratio)

        for d in codes:
            term_name = d[0]
            score = d[1]
            if entity_text_spaces.replace(',','').lower() == term_name.lower():
                codes = [(term_name,score)]

        decs_cache[entity_text] = codes

    elif entity_text_spaces.replace(',','') in map(str.lower,synonym_to_id): #There is an exact match for this entity in synonym_to_id
        codes = process.extract(entity_text_spaces.replace(" ","_"), synonym_to_id.keys(), limit = 4000, scorer=fuzz.token_sort_ratio)
        for d in codes:   
            term_name = d[0]
            score = d[1]
            term_id = synonym_to_id[term_name]
            if entity_text_spaces.replace(',','').lower() == term_name.lower():
                codes = [(term_name,score)]
        decs_cache[entity_text] = codes
    
    
    elif entity_text.endswith("s") and entity_text[:-1] in decs_cache: # Removal of suffix -s 
        codes = decs_cache[entity_text[:-1]]

    
    elif entity_text in decs_cache: # There is already a candidate list stored in cache file
        codes = decs_cache[entity_text]


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
        
        decs_cache[entity_text] = codes
    
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
        #print(matches)

    return matches
