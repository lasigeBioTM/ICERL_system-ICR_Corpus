Install Requirements
./install_requirements

All the files needed to perform the NER and NEL tasks are in this folder, therfore the steps 1 is not mandatory. Furthermore, the files that will be retrieved from SciELO and PubMed may not be the same that were retrieved when creating this folder, therfore it is advisable to skip to step 2 to obtain the same results.

1-Preparation
Retrive files
Get the ICR_corpus, the files for the PT embeddings and the files for the training of PT NER model. From the total of embeddings files only the first 500 were used.

./retrive_all_files.sh

Pre process the files for embeddings and train them
python3 src/NER/train_flair_embeddings.py <direction> <language>

<direction> : is 'fwd' if training foward language model and 'bwd' if training backward language model.

<language> : is 'pt' for Portuguese and 'es' for Spanish

2-NER
Convert the training files to the IOB2 schema and train NER tagger.
Note 1: The resulting PT training file needs to be manually corrected to the system achive the results described. The correct PT training file is in './data/iob2/train_pt/' directory
python3 src/NER/train_ner_models.py <model>

<model> : 'cantemist' for the Spanish model and 'cantemistpt', 'cantemistpt_biobertpt' or 'biobertpt' for Portuguese

Predict entities in text (NER)
python3 src/NER/predict_ner.py <model> <language>

<model> : 'cantemist' for the Spanish model and 'cantemistpt', 'cantemistpt_biobertpt' or 'biobertpt' for Portuguese
<language> : is 'pt' for Portuguese and 'es' for Spanish

The annotation files will be in './evaluation/NER/<language>' directory

3-NEL
Find the DeCS and CIE/CID codes for the output of NER task
./norm.sh multi_ont <language>

<language> : is 'pt' for Portuguese and 'es' for Spanish

The annotation files will be in './evaluation/NEL/multi_ont/<language>' directory

4-Evaluation
Evaluate the performance of ICERL system 
python3 evaluation_pt_es.py