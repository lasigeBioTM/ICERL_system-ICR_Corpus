import os
import sys
from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import FlairEmbeddings, StackedEmbeddings, WordEmbeddings, BytePairEmbeddings, CharacterEmbeddings, TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from pre_process_NER import cantemist_to_IOB2,pt_train_to_IOB2

sys.path.append("./")

## Set the gpus to use
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"

## Convert the CANTEMIST corpus or the training files in Portuguese into IOB2 format and load it as a ColumnCorpus object 
# see: https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_6_CORPUS.md
ner_model = str(sys.argv[1])

if ner_model == 'cantemist':
    cantemist_to_IOB2('train')
    cantemist_to_IOB2('dev')
    cantemist_to_IOB2('test')
    converted_corpus_folder = './data/iob2/train_es/'
    columns = {0: 'text', 1: 'ner'}
    corpus: Corpus = ColumnCorpus(converted_corpus_folder, columns,
                              column_delimiter= "\t",
                              train_file='train.txt',
                              test_file='test.txt',
                              dev_file='dev.txt'
                              )
else:
    #pt_train_to_IOB2()
    # since the resulting file from pt_train_to_IOB2() has to be manually corrected, that file is already provided in './data/iob2/train_pt/' directory
    converted_corpus_folder = './data/iob2/train_pt/'   
    columns = {0: 'text', 1: 'ner'}
    corpus: Corpus = ColumnCorpus(converted_corpus_folder, columns,
                              column_delimiter= "\t",
                              train_file='train.txt')

## Train the model
#see: https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_7_TRAINING_A_MODEL.md

# 2. what tag do we want to predict?
tag_type = 'ner' 

# 3. make the tag dictionary from the corpus
tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type) 
print(tag_dictionary)

# 4. initialize trained embeddings

embedding_types = list()

if ner_model == 'cantemist':
    embedding_types = [WordEmbeddings('es'),
                FlairEmbeddings('es-forward'), 
                FlairEmbeddings('es-backward'),
                FlairEmbeddings('./trained_embeddings/es/fwd/checkpoint.pt'),
                FlairEmbeddings('./trained_embeddings/es/bwd/checkpoint.pt'),
                BytePairEmbeddings('es'),
                CharacterEmbeddings()]

if ner_model == 'cantemistpt':
    embedding_types = [WordEmbeddings('pt'),
                FlairEmbeddings('pt-forward'), 
                FlairEmbeddings('pt-backward'),
                FlairEmbeddings('./trained_embeddings/pt/fwd/checkpoint.pt'),
                FlairEmbeddings('./trained_embeddings/pt/bwd/checkpoint.pt'),
                BytePairEmbeddings('pt'),
                CharacterEmbeddings()]

if ner_model == 'cantemistpt_biobertpt':
    embedding_types = [WordEmbeddings('pt'),
                FlairEmbeddings('pt-forward'), 
                FlairEmbeddings('pt-backward'),
                FlairEmbeddings('./trained_embeddings/pt/fwd/checkpoint.pt'),
                FlairEmbeddings('./trained_embeddings/pt/bwd/checkpoint.pt'),
                BytePairEmbeddings('pt'),
                CharacterEmbeddings(),
                TransformerWordEmbeddings("pucpr/biobertpt-all")]
if ner_model == 'biobertpt':
    embedding_types = [
		TransformerWordEmbeddings("pucpr/biobertpt-all"),
                WordEmbeddings('pt')]



# List of available embeddings in FLAIR: https://github.com/flairNLP/flair/tree/master/resources/docs/embeddings

embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

# 5. initialize sequence tagger
tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                        embeddings=embeddings,
                                        tag_dictionary=tag_dictionary,
                                        tag_type=tag_type,
                                        use_crf=True)

# 6. initialize trainer
trainer: ModelTrainer = ModelTrainer(tagger, corpus)

#If the training ends abruplty without creating the file final-model.pt, load from last checkpoint and continue training:
#from pathlib import Path
#checkpoint = 'resources/taggers/medium/checkpoint.pt'
#trainer = ModelTrainer.load_checkpoint(checkpoint, corpus)

# 7. start training
output_dir = './resources/taggers/' + ner_model
trainer.train(output_dir,
              learning_rate=0.1,
              mini_batch_size=32,
              max_epochs=150,
              train_with_dev=True,
              monitor_train=True,
              monitor_test=True,
              checkpoint=True,
              embeddings_storage_mode='none',
              patience=3)

