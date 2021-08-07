#Arguments:
#$1 <ont_number>: "multi_ont" or "single_ont"
#$2 language : es,pt

rm tmp/decs_cache.pickle
rm tmp/ecie03_cache.pickle
rm tmp/icd10cm_cache.pickle

python3 src/NEL/annotations.py $2

python3 src/NEL/pre_process_nel.py $1 $2

cd src/NEL

java ppr_for_ned_all $1

cd ../../

python3 src/NEL/post_process_nel.py $1 $2




