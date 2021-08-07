import os
import sys
import time
from flair.data import Dictionary
from flair.models import LanguageModel
from flair.trainers.language_model_trainer import LanguageModelTrainer, TextCorpus
from pre_process_NER import prepare_mesinesp_for_flair_embeds_training, pre_process_pt_abstracts_for_flair_embeds_training
from flair.embeddings import FlairEmbeddings

sys.path.append("./")

## Set the gpus that will be used
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"] = "3,4,5,6,7,8"

start_time = time.time()

## see tutorial: https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_9_TRAINING_LM_EMBEDDINGS.md

#language_model = FlairEmbeddings('../../trained_embeddings/mesinesp_2/bwd/best-lm2.pt').lm

## are you training a forward or backward LM?
direction = sys.argv[1]
language = sys.argv[2]

is_forward_lm = bool()

if direction == "fwd":
    is_forward_lm = True 

elif direction == "bwd":
    is_forward_lm = False

## load the default character dictionary
dictionary: Dictionary = Dictionary.load('chars')

## get your corpus, process forward and at the character level
if language == 'es':
    #prepare_mesinesp_for_flair_embeds_training() # prepare raw text from Spanish PubMed Abstracts for training
    corpus_path = "./data/mesinesp/mesinesp_2/"
    

if language == 'pt':
    pre_process_pt_abstracts_for_flair_embeds_training()
    corpus_path = "./data/pt_scielo_abstracts_embeddings/"
    

corpus = TextCorpus(corpus_path,
                    dictionary,
                    is_forward_lm,
                    character_level=True)

## instantiate your language model, set hidden size and number of layers (hidden_size=1024-small model, (hidden_size=2048-large model)
language_model = LanguageModel(dictionary,
                               is_forward_lm,
                               hidden_size=1024, 
                               nlayers=1,
                               dropout=0.1)

## train your language model
trainer = LanguageModelTrainer(language_model, corpus)

#trainer.num_workers = 4 #Flair auto-detects whether you have a GPU available. If there is a GPU, it will automatically run training there.
output_dir = str()

if is_forward_lm:
    
    if not os.path.exists('./trained_embeddings/' + language + '/fwd/'):
        os.makedirs('./trained_embeddings/' + language + '/fwd/')
    
    output_dir = './trained_embeddings/' + language + '/fwd/'

else:
    if not os.path.exists('./trained_embeddings/' + language + '/bwd/'):
        os.makedirs('./trained_embeddings/' + language + '/bwd/')

    output_dir = './trained_embeddings/' + language + '/bwd/'


# 9. continue trainer at later point
from pathlib import Path
from flair.trainers import ModelTrainer
from flair.training_utils import EvaluationMetric

language_model = LanguageModel(dictionary,
                               is_forward_lm,
                               hidden_size=1024, 
                               nlayers=1,
                               dropout=0.1)
trainer.train(output_dir,
              sequence_length=250,
              mini_batch_size=32,
              max_epochs=150,
	      patience=25,
              checkpoint=True)

