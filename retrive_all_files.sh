#retrive PT training files (PubMed + SciELO)
esearch -db pubmed -query "Case Reports[Publication Type] AND POR[LA] AND Cancer[Filter]" | efetch -format xml > CancerPortuguesePubMedCaseAbstracts.xml

grep -e 'ArticleId IdType="pii"' -e 'AbstractText' CancerPortuguesePubMedCaseAbstracts.xml > CancerPortuguesePubMedCaseAbstracts.txt

sed 's/<[^>]*>//g' CancerPortuguesePubMedCaseAbstracts.txt > CancerPortuguesePubMedCaseAbstracts2.txt

awk '$1=$1' CancerPortuguesePubMedCaseAbstracts2.txt > CancerPortuguesePubMedCaseAbstracts3.txt

rm CancerPortuguesePubMedCaseAbstracts.txt
rm CancerPortuguesePubMedCaseAbstracts2.txt

#retrive PT files for training
python data_retrieval_scripts/retrieve_pt_train_files.py

#retrive PT files for embeddings
python3 data_retrieval_scripts/retrieve_pt_files_embeddings.py

#retrive ICR_corpus
python data_retrieval_scripts/retrieve_icr_corpus.py

#Download CANTEMIST corpus:
cd data
wget https://zenodo.org/record/3952175/files/cantemist.zip
unzip cantemist.zip