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
    #pt_dir = "./evaluation/NORM/multi_ont/pt/" + file_name

    with open(es_dir, 'r', encoding='utf-8') as es_file:
        es_content = es_file.readlines()
        #print(es_content)
        es_annotatores_notes = [x for x in es_content if x.startswith('T')]
        #print(es_annotatores_notes)
        #for line in es_annotatores_notes:
            #print(line)
            #for word in line.split("\t"):
             #   print(word)
        #es_codes_final = [word.replace("\n","") for line in es_annotatores_notes for word in line.split("\t") if not word.startswith(("#","A"))]
        es_codes_final = [word.replace("\n","") for line in es_annotatores_notes for word in line.split("\t")]
        #print(es_codes_final)
        #es_codes_final = [x for x in es_codes_final if not x.startswith("T")]
        es_codes_final = [x for x in es_codes_final if not re.match("^T\[0-9][0-9]",x)]
        d_es = {}
        #print('es_codes_final:',  es_codes_final)
        for i in range(0,len(es_codes_final)) :
            if es_codes_final[i].isdigit():
                #print(i)
                d_es[es_codes_final[i]] = [es_codes_final[i+1],ast.literal_eval(es_codes_final[i+2])]
                
        #print(es_codes_final)
        #print('d_es:', d_es)
        
    #with open(pt_dir, 'r', encoding='utf-8') as pt_file:
    #    pt_content = pt_file.readlines()
    #    pt_annotatores_notes = [x for x in pt_content if not x.startswith('T')]
    #    pt_codes_final = [word.replace("\n","") for line in pt_annotatores_notes for word in line.split("\t") if not word.startswith(("#","A"))]
        #print(pt_codes_final)


#S0120-06902018000400295.ann
    return d_es

def evaluate(d_es, d_pt):
    true_positive = int()
    false_positive = int()
    false_negative = int()
    es_keys = list(d_es.keys())
    pt_keys = list(d_pt.keys())
    #print(es_keys)
    #print(d_es)
    #print(d_pt)
    #if len(list(d_es.keys())) == 0 and len(list(d_pt.keys())) == 0:
    if bool(d_es) == False and bool(d_pt) == False:
        true_positive = 0
        false_positive = 0
        false_negative = 0

    #elif len(list(d_es.keys())) != 0 and len(list(d_pt.keys())) == 0:
    elif bool(d_es) == True and bool(d_pt) == False :
        #print("a")
        true_positive = 0
        false_positive = 0
        false_negative = len(list(d_es.keys()))
    else:
        #false_negative = len(list(d_es.keys())) - len(list(d_pt.keys()))
        #if false_negative < 0 :
        #    false_negative = 0
        #print(pt_keys)
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
                #print(pt_codes)
                if any(x in es_codes for x in pt_codes) == True:
                    true_positive = true_positive + 1
                #if any(x in pt_codes for x in es_codes) == False:
                #if bool(x in pt_codes for x in es_codes) == False :
                #else:
                    #false_positive = false_positive + 1
                #elif any(x in es_codes for x in pt_codes) == False:
                #    false_negative = false_negative + 1
        for i in es_keys:
            if i not in pt_keys:
                false_negative = false_negative + 1

            
                
    #print("tp:", true_positive)
    #print("fp:", false_positive)
    #print("fn:", false_negative)
    return [true_positive, false_positive, false_negative]


tp = []
fp = []
fn = []
filenames = os.listdir("./evaluation/NEL/multi_ont/es")
for i in filenames:
    file_name = i
    #print(file_name)
    es = get_codes("es",file_name)
    pt = get_codes("pt",file_name)
    
    #print(file_name, check_pt_entity(file_name,get_pt_entity(a)))
    #print("es:")
    #print(es)
    #print("pt:")
    #print(pt)
    results = evaluate(es,pt)
    #print(results)
    tp.append(results[0])
    fp.append(results[1])
    fn.append(results[2])
    
#print(tp)
#print(fp)
#print(fn)

sum_tp = sum(tp)
sum_fp = sum(fp)
sum_fn = sum(fn)

try:
        
        precision = sum_tp / (sum_tp + sum_fp)

        recall = sum_tp / (sum_tp + sum_fn)
except ZeroDivisionError:
         precision = 0
         recall = 0

    #print("p", precision)
    #print("r", recall)

   # if precision == 0 and recall == 0:
   #     f1_score = 0
   
try:
        f1_score = 2 * precision * recall / (precision + recall)
except ZeroDivisionError:
        f1_score = 0

print("p",precision)
print("r",recall)
print("f",f1_score)

