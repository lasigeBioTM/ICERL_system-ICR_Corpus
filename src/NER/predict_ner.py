import os 
import sys
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.embeddings import FlairEmbeddings
from flair.data import Sentence
import spacy
from spacy.lang.es import Spanish
from spacy.pipeline import SentenceSegmenter

os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

sys.path.append("./")

ner_model=str(sys.argv[1])
language = str(sys.argv[2])

def build_annotation_file(doc, doc_filepath, model):
    #l = 0

    entity_type = "MORFOLOGIA_NEOPLASIA"
    output = str()

    with open(doc_filepath, 'r', encoding='utf-8') as doc_file:
        text = doc_file.read()
        doc_file.close()
    
    # Sentence segmentation followed by tokenization of each sentence
    doc_spacy = nlp(text)
    sent_begin_position = int(0)
    annot_number = int()
    sentence_number = 0
     
    for spacy_sent in doc_spacy.sents:
        entity_number = 0
        sentence_number = sentence_number + 1
        
        if len(spacy_sent.text) >= 2 and spacy_sent.text[0] == "\n":
            sent_begin_position -= 1

        sentence = Sentence(spacy_sent.text, use_tokenizer=True)
        model.predict(sentence)
           
        for entity in sentence.get_spans('ner'):
            entity_number += 1

            if str(entity.tag).strip("\n") == "MOR_NEO":
                 annot_number += 1
                 begin_entity = str(sent_begin_position+entity.start_pos)
                 end_entity = str(sent_begin_position+entity.end_pos)
                 entity_text = ""
                 pre_begin_entity = int(begin_entity) - 2
                 if text[pre_begin_entity] == '/' :
                    entity_number -= 1 
                 output += "T" + str(annot_number) + "\t" + entity_type + " " + begin_entity + " " + end_entity + " " + str(sentence_number) + str(entity_number) + "\t" + str(entity.text) + "\n"
      
        sent_begin_position += len(spacy_sent.text) + 1

    # Output the annotation file
    if language=="es":
        annotation_filepath = './evaluation/NER/es/' + doc[:-3] + 'ann'
    elif language=="pt":
        annotation_filepath = './evaluation/NER/pt/' + doc[:-3] + 'ann'

    #print(l)
    print(annotation_filepath)
    
        

    with open(annotation_filepath, 'w', encoding='utf-8') as annotation_file:
        annotation_file.write(output)
        annotation_file.close()
        #print(l)
            
    
if __name__ == "__main__":
    # load the model you trained
    if ner_model=="cantemist":
        model = SequenceTagger.load('resources/taggers/cantemist/final-model.pt')
    if ner_model == "cantemistpt":
        model = SequenceTagger.load('resources/taggers/cantemistpt/final-model.pt')
    if ner_model == "cantemistpt_biobertpt":
        model = SequenceTagger.load('resources/taggers/cantemistpt_biobertpt/final-model.pt')
    if ner_model == "biobertpt":
        model = SequenceTagger.load('resources/taggers/biobertpt/final-model.pt')



    
    ## Create spanish sentence segmenter with Spacy
    # the sentence segmentation by spacy is non-destructive, i.e., the empty lines are considered when getting a span of a given word/entity
    nlp = Spanish()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
    
    icr_corpus = "./data/ICR_corpus/" + str(language) + "/"

    
    
    if not os.path.exists("./evaluation/NER/"):
        os.makedirs("./evaluation/NER/")
    if not os.path.exists("./evaluation/NER/es"):
        os.makedirs("./evaluation/NER/es")
    if not os.path.exists("./evaluation/NER/pt"):
        os.makedirs("./evaluation/NER/pt")



    for doc in os.listdir(icr_corpus): #For each document in icr_corpus build the respective annotation file with predicted entities
        doc_filepath = icr_corpus + doc
        build_annotation_file(doc, doc_filepath, model)

                
print(build_annotation_file(doc, doc_filepath, model))
