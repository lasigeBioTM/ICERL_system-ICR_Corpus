import sys
import obonet
import os
import ast
import re

#file_name = sys.argv[1]
def get_codes(language,file_name):
    '''
    Retrive the codes from a file in evaluation/NEL/es and evaluation/NEL/pt
    '''

    es_dir = "./evaluation/NEL/multi_ont/" + language + "/" + file_name
    

    with open(es_dir, 'r', encoding='utf-8') as es_file:
        es_content = es_file.readlines()
        es_annotatores_notes = [x for x in es_content if x.startswith('T')]
        es_codes_final = [word.replace("\n","") for line in es_annotatores_notes for word in line.split("\t")]
        es_codes_final = [x for x in es_codes_final if not re.match("^T\[0-9][0-9]",x)]
        d_es = {}

        for i in range(0,len(es_codes_final)) :
            if es_codes_final[i].isdigit():
                #print(i)
                d_es[es_codes_final[i]] = [es_codes_final[i+1],ast.literal_eval(es_codes_final[i+2])]
                

    return d_es

def evaluate(d_es, d_pt):
    true_positive = int()
    false_positive = int()
    false_negative = int()
    es_keys = list(d_es.keys())
    pt_keys = list(d_pt.keys())
    if bool(d_es) == False and bool(d_pt) == False:
        true_positive = 0
        false_positive = 0
        false_negative = 0

    elif bool(d_es) == True and bool(d_pt) == False :
        true_positive = 0
        false_positive = 0
        false_negative = len(list(d_es.keys()))
    else:
        for i in pt_keys:
            if i not in es_keys:
                false_positive = false_positive + 1
            else:
                es_entity_codes = d_es.get(i)
                es_entity = es_entity_codes[0]
                es_codes = es_entity_codes[1]
                pt_entity_codes = d_pt.get(i,['non',[]])
                pt_entity = pt_entity_codes[0]
                pt_codes = pt_entity_codes[1]
                if any(x in es_codes for x in pt_codes) == True:
                    true_positive = true_positive + 1
        for i in es_keys:
            if i not in pt_keys:
                false_negative = false_negative + 1


    return [true_positive, false_positive, false_negative]


tp = []
fp = []
fn = []
filenames = os.listdir("./evaluation/NEL/multi_ont/es")
for i in filenames:
    file_name = i
    es = get_codes("es",file_name)
    pt = get_codes("pt",file_name)
    results = evaluate(es,pt)
    tp.append(results[0])
    fp.append(results[1])
    fn.append(results[2])
    


sum_tp = sum(tp)
sum_fp = sum(fp)
sum_fn = sum(fn)

try:
        
        precision = sum_tp / (sum_tp + sum_fp)

        recall = sum_tp / (sum_tp + sum_fn)
except ZeroDivisionError:
         precision = 0
         recall = 0

try:
        f1_score = 2 * precision * recall / (precision + recall)
except ZeroDivisionError:
        f1_score = 0

print("p",precision)
print("r",recall)
print("f",f1_score)

