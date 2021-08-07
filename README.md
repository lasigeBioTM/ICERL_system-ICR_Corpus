# ICERL_system / ICR_Corpus
Code related to the development of the ICERL (Iberian Cancer-related Entity Recognition and Linking) system and ICR (Iberian Cancer-related) corpus

# Install Requirements
```
./install_requirements
```

# 1-Preparation

All the files needed to perform the NER and NEL tasks are in this folder; therefore, step 1 is not mandatory. Furthermore, the files retrieved from SciELO and PubMed may not be the same as those when creating this folder; therefore, it is advisable to skip to step 2 to obtain the same results.

## Retrieve files
Get the ICR_corpus, the files for the PT embeddings, and the files for the training of the PT NER model. From the total of embeddings files, only the first 500 were used.
```
./retrive_all_files.sh
```

## Pre process the files for embeddings and train them
```
python3 src/NER/train_flair_embeddings.py <direction> <language>
```
direction: is 'fwd' if training forward language model and 'bwd' if training backward language model.

language: is 'pt' for Portuguese and 'es' for Spanish

# 2-NER
 
## Convert the training files to the IOB2 schema and train the NER tagger.
Note: The resulting PT training files need to be manually corrected to achieve the results described. The correct PT training file is in './data/iob2/train_pt/' directory
```
python3 src/NER/train_ner_models.py <model>
```

model : 'cantemist' for the Spanish model and 'cantemistpt', 'cantemistpt_biobertpt' or 'biobertpt' for Portuguese

## Predict entities in text
```
python3 src/NER/predict_ner.py <model> <language>
```

model : 'cantemist' for the Spanish model and 'cantemistpt', 'cantemistpt_biobertpt' or 'biobertpt' for Portuguese
language : is 'pt' for Portuguese and 'es' for Spanish

The annotation files will be in './evaluation/NER/<language>' directory

# 3-NEL
## Find the DeCS and CIE/CID codes for the output of NER task
```
./norm.sh multi_ont <language>
```

language : is 'pt' for Portuguese and 'es' for Spanish

The annotation files will be in './evaluation/NEL/multi_ont/<language>' directory

## 4-Evaluation
Evaluate the performance of the ICERL system 
```
python3 evaluation_pt_es.py
```
