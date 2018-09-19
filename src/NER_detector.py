import os

from nltk import word_tokenize
import json
from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences
from collections import Counter
import time

from loggingmodule import getlogger
import configparser

####################### Confi file reading
config_file_loc = "../config/config.cfg"
if not os.path.isfile(config_file_loc):
    config_file_loc = "../../config/config.cfg"
config_obj = configparser.ConfigParser()

try:
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("NERDetector", "debuglevel"))
    logfilenameconfig = config_obj.get("NERDetector", "logfilename")
except Exception as e:
    raise Exception("Config file error: "+str(e))

logfilename="../logs/"
if not os.path.isdir(logfilename):
    logfilename = "../../logs/"
logfilename=logfilename+ logfilenameconfig

####################### Loggin Functionality
loggerobj = getlogger.GetLogger("NERDetector",logfilename,debugLevel)
logger = loggerobj.getlogger1()

# filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")


class NER_Detector:
    def __init__(self):
        try:
            self.weight_filename = "weights-improvement-07-0.3528.hdf5"

            st_time = time.time()
            self.filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

            with open(os.path.join(self.filepath,"NERSystem","ind2label")) as f:
                self.ind2label = json.load(f)
            with open(os.path.join(self.filepath,"NERSystem", "char_to_int")) as f:
                self.char_to_int = json.load(f)
            with open(os.path.join(self.filepath,"NERSystem", "int_to_char")) as f:
                self.int_to_char = json.load(f)
            with open(os.path.join(self.filepath,"NERSystem", "maxlen")) as f:
                self.maxlen = json.load(f)
            with open(os.path.join(self.filepath, "NERSystem","model.json"),'r') as f:
                loaded_model_json = f.read()
            self.loaded_model = model_from_json(loaded_model_json)
            self.loaded_model.load_weights(os.path.join(self.filepath,"NERSystem",self.weight_filename))
            self.loaded_model.compile(loss='categorical_crossentropy', optimizer='adam')
            with open(os.path.join(self.filepath, "skills","skills_data_mayalsoknow")) as f:
                self.skills_list = set((json.load(f)))
                self.skills_list = self.convert_to_dict(self.skills_list,"skill")
            with open(os.path.join(self.filepath,"role", "role_data")) as f:
                self.roles_list = set(json.load(f))
                self.roles_list = self.convert_to_dict(self.roles_list, "role")

            with open(os.path.join(self.filepath, "education","edu_level")) as f:
                self.edu_level = self.convert_to_dict(set(json.load(f)),"edu_level")


            with open(os.path.join(self.filepath, "education","edu_streams")) as f:
                self.edu_streams = self.convert_to_dict(set(json.load(f)),"edu_stream")

            with open(os.path.join(self.filepath,"industry", "indsutry_list")) as f:
                self.indsutry_list = self.convert_to_dict(set(json.load(f)),"ind")

            with open(os.path.join(self.filepath, "company", "company_names")) as f:
                self.company_list = list(set(json.load(f)))
                self.company_list = set(self.company_list)
                self.company_list = self.convert_to_dict(self.company_list, "company")


            with open(os.path.join(self.filepath,"locations", "locations_all")) as f:
                self.locations = list(set(json.load(f)))
                self.locations = set(self.locations)
                self.locations = self.convert_to_dict(self.locations, "loc")

            self.company_words = {"associates", "bank", "consultancy", "consultants", "inc.", "inc", "pvt.ltd.", "pvtltd.", "limited",
                 "pvtltd", "pvt.ltd", "ltd.", "ltd", "private", "pvt.", "pvt", "services", "jobs"}
            self.punct_marks = {",","'","/","?",".",">","<",":",";",'"',"{","}","[","]","\\","|","!","@","#","$","%","^","&","*","(",")","-","_","=","+","`","~","@"}
            if os.path.isfile(os.path.join(self.filepath,"NERSystem","already_mapped")) and os.stat(os.path.join(self.filepath,"NERSystem","already_mapped")).st_size > 0:
                with open(os.path.join(self.filepath,"NERSystem", "already_mapped")) as f:
                    self.already_mapped = json.load(f)
                try:
                    del self.already_mapped["abcd"]
                except:
                    pass
            else:
                self.already_mapped = {}
            self.current_length = len(self.already_mapped)
            print("NER detector intialisation time : ",(time.time()-st_time))
        except Exception as e:
            logger.error("NER_Detector __init__ error : ",str(e))
            raise Exception(str(e))

    def convert_to_dict(self,set_list,val):
        try:
            tmp_dict = {}
            for s in set_list:
                tmp_dict[s] = val
            return tmp_dict
        except Exception as e:
            print("Error while converting to dict",str(e))
            raise Exception(str(e))

    def convert_txt_to_vec(self,txt):
        try:
            new_x = []
            if len(txt)>self.maxlen:
                txt = txt[:self.maxlen]
            for c in txt:
                try:
                    new_x.append(self.char_to_int[c])
                except:
                    new_x.append(self.char_to_int["undetected"])
            return new_x
        except Exception as e:
            logger.error("NER_Detector convert_txt_to_vec error : ",str(e))
            raise Exception(str(e))

    def convert_string(self,input_string):
        try:
            input_string = input_string.lower().strip()
            input_string = input_string.replace(".","").replace(",","").replace(" ","").replace("-","")
            return input_string
        except Exception as e:
            logger.error("NER_Detector convert_string error : ",str(e))
            raise Exception(str(e))

    def categorize_txt(self,query_list):
        try:
            X_enc = []
            op = {"edu_level":[],"edu_stream":[],"o":[],"skill":[],"role":[],"ind":[],"company":[],"loc":[]}#,"designations":[]}
            for query in query_list:
                q = query.lower().replace('''"''', '''''').replace("_"," ").strip()
                already_mapped = False
                if len(q):
                    try:
                        op[self.already_mapped[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.locations[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.skills_list[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.roles_list[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.indsutry_list[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.company_list[q]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.edu_level[self.convert_string(q)]].append(q)
                        already_mapped = True
                    except:
                        pass
                    try:
                        op[self.edu_streams[self.convert_string(q)]].append(q)
                        already_mapped = True
                    except:
                        pass
                    if already_mapped == False:
                        if q.endswith(".com"):
                            op["company"].append(q)
                            already_mapped = True
                        elif len(set(word_tokenize(q)) & set(self.company_words)):
                            op["company"].append(q)
                            already_mapped = True
                        elif len(set(word_tokenize(q)) & set(self.punct_marks))==len(set(word_tokenize(q))):
                            op["o"].append(q)
                            already_mapped = True
                    if not already_mapped:
                        X_enc.append(self.convert_txt_to_vec(q))
            if len(X_enc):
                ner_op = self.get_categories_of_unmapped(X_enc)
                for k,v in ner_op.items():
                    op[v].append(k)
            for k,v in op.items():
                op[k] = list(set(v))
            if len(self.already_mapped)>(self.current_length+50000):
                with open(os.path.join(self.filepath,"NERSystem","already_mapped"),"w") as f:
                    json.dump(self.already_mapped,f)
                self.current_length = len(self.already_mapped)
            return op
        except Exception as e:
            logger.error("NER_Detector categorize_txt error : ", str(e))
            raise Exception(str(e))

    def get_categories_of_unmapped(self,X_enc):
        try:
            detector_op = {}
            X_enc_reverse = [[c for c in reversed(x)] for x in X_enc]
            X_enc_f = pad_sequences(X_enc, maxlen=self.maxlen)
            X_enc_b = pad_sequences(X_enc_reverse, maxlen=self.maxlen)
            pred = self.loaded_model.predict_classes([X_enc_f, X_enc_b])
            for i, p in enumerate(pred):
                predicted_classes = p[(self.maxlen - len(X_enc[i])):]
                predicted_labels = Counter([self.ind2label[str(m)] for m in predicted_classes])
                input_q = "".join([self.int_to_char[str(t)] for t in X_enc[i]])
                if "o" in predicted_labels.keys() and (("skill" in predicted_labels.keys() and predicted_labels["o"] == predicted_labels["skill"]) or (
                        "role" in predicted_labels.keys() and predicted_labels["o"] == predicted_labels["role"])):
                    output_q = "o"
                else:
                    output_q = max(predicted_labels, key=predicted_labels.get)
                detector_op[input_q] = output_q
            self.already_mapped.update(detector_op)
            return detector_op
        except Exception as e:
            logger.error("NER_Detector get_categories_of_unmapped error : ", str(e))
            raise Exception(str(e))


if __name__ == "__main__":
    obj = NER_Detector()
    # str_tmp = '''java,python,r,sales,marketing,advertisement,advertiser,sales executive,business development officer'''

    # print(obj.categorize_txt('''-,dtcc,tata consultancy,zxo,cfo,salesforce.com,monster,monsterindia,monster.com,monsterindia.com'''.split(",")))
    print(obj.categorize_txt(['F and B']))
    # print(obj.categorize_txt(["p2p data specialist","successfactor consultant","hana","pig","hive","sqoop","flume","apache pig","apache storm","apache solr","storm","solr"]))
