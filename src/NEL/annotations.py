import os
import xml.etree.ElementTree as ET
import sys

sys.path.append("./")

language = sys.argv[-1]
def parse_ner_output(ic=False):
    """Get the annotations in the NER output files (ic=False) or in the CANTEMIST dataset/ Portuguese training files(ic=True)."""

    
    filenames = list()
    evaluation = False

    if ic:
        if language == 'es':
            filenames_1 = ["./data/train-set-to-publish/cantemist-norm/"+input_file for input_file in os.listdir("./data/train-set-to-publish/cantemist-norm/") if input_file[-3:] == "ann"]
            filenames_2 = ["./data/dev-set1-to-publish/cantemist-norm/"+input_file for input_file in os.listdir("./data/dev-set1-to-publish/cantemist-norm/") if input_file[-3:] == "ann"]
            filenames_3 = ["./data/dev-set2-to-publish/cantemist-norm/"+input_file for input_file in os.listdir("./data/dev-set2-to-publish/cantemist-norm/") if input_file[-3:] == "ann"]

            filenames = []

        elif language == 'pt':
            filenames = ["./data/train_pt_files/" + input_file for input_file in os.listdir("./data/train_pt_files/") if input_file[-3:] == "ann"]


    else:
        filenames = ["./evaluation/NER/" + language + "/" + input_file for input_file in os.listdir("./evaluation/NER/"  + language + "/")]


    
    annotations = dict()
    

    for filename in filenames:
        
        with open(filename , 'r') as doc_file:
            ner_output = doc_file.readlines()
            doc_file.close()

            doc_name = str()
                
            if evaluation:
                doc_name = filename.split("./evaluation/NER/" + language + "/")[1]

                
            else:
                #print(filename)
                #if language == 'pt':
                doc_name = filename.split("/")[4]
                #if language == 'es':
                #doc_name = filename.split("/")[4]
                                
            for annotation in ner_output:
                line_data = annotation.split("\t")

                if len(line_data) == 3:
                        
                    #if ic: # The annotation ID is needed to further calculation of the information content
                    if line_data[0][0] == "#":
                        annotation_id = line_data[2].strip("\n")
                        
                        if doc_name in annotations.keys():
                            current_values = annotations[doc_name]
                            current_values.append(annotation_id)
                            annotations[doc_name] = current_values
                                        
                        else:
                            annotations[doc_name] = [annotation_id]

                    else: # The annotation text is needed for candidate retrieval
                            annotation_text = line_data[2].strip("\n")
                            #print(line_data)
                            term_number = line_data[0]
                            annotation_type = line_data[1].split(" ")[0]
                            annotation_begin = line_data[1].split(" ")[1]
                            annotation_end = line_data[1].split(" ")[2]
                            annotation_code = line_data[1].split(" ")[3]
                            annotation_data = (annotation_text, term_number, annotation_type, annotation_begin, annotation_end, annotation_code)

                            

                            if doc_name in annotations.keys():
                                current_values = annotations[doc_name]
                                current_values.append(annotation_data)
                                annotations[doc_name] = current_values
                                                
                            else:
                                annotations[doc_name] = [annotation_data]
          
    return annotations






